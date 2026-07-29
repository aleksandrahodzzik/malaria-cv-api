"""Deterministic offline image corruptions for robustness studies."""

from __future__ import annotations

import io
import random
from collections.abc import Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

SUPPORTED_CORRUPTIONS = frozenset(
    {
        "gaussian_blur",
        "brightness_dark",
        "brightness_light",
        "contrast",
        "jpeg_compression",
        "rotation",
        "scale",
        "crop_shift",
        "occlusion",
        "color_cast",
        "pixel_noise",
    }
)


def apply_corruption(
    image: Image.Image,
    corruption: str,
    severity: int,
    *,
    seed: int = 20260728,
) -> Image.Image:
    """Apply a declared corruption without changing the production pipeline."""
    if corruption not in SUPPORTED_CORRUPTIONS:
        raise ValueError(f"Unsupported corruption: {corruption}.")
    if not 0 <= severity <= 5:
        raise ValueError("severity must be within [0, 5].")

    source = image.convert("RGB")
    if severity == 0:
        return source.copy()

    if corruption == "gaussian_blur":
        return source.filter(ImageFilter.GaussianBlur(radius=severity * 0.6))
    if corruption == "brightness_dark":
        return ImageEnhance.Brightness(source).enhance(1 - severity * 0.14)
    if corruption == "brightness_light":
        return ImageEnhance.Brightness(source).enhance(1 + severity * 0.20)
    if corruption == "contrast":
        return ImageEnhance.Contrast(source).enhance(max(0.1, 1 - severity * 0.16))
    if corruption == "jpeg_compression":
        return _jpeg_roundtrip(source, quality=max(5, 95 - severity * 18))
    if corruption == "rotation":
        return source.rotate(severity * 9, resample=Image.Resampling.BILINEAR)
    if corruption == "scale":
        factor = max(0.2, 1 - severity * 0.14)
        reduced = source.resize(
            (
                max(1, round(source.width * factor)),
                max(1, round(source.height * factor)),
            ),
            Image.Resampling.BILINEAR,
        )
        return reduced.resize(source.size, Image.Resampling.BILINEAR)
    if corruption == "crop_shift":
        return _crop_shift(source, severity)
    if corruption == "occlusion":
        return _occlude(source, severity)
    if corruption == "color_cast":
        return _color_cast(source, severity)
    return _pixel_noise(source, severity, seed)


def corruption_suite(
    image: Image.Image,
    *,
    severities: Iterable[int] = range(6),
    seed: int = 20260728,
) -> dict[tuple[str, int], Image.Image]:
    """Generate the full deterministic matrix for an offline benchmark."""
    return {
        (corruption, severity): apply_corruption(
            image,
            corruption,
            severity,
            seed=seed,
        )
        for corruption in sorted(SUPPORTED_CORRUPTIONS)
        for severity in severities
    }


def _jpeg_roundtrip(image: Image.Image, *, quality: int) -> Image.Image:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    with Image.open(buffer) as decoded:
        decoded.load()
        return decoded.convert("RGB")


def _crop_shift(image: Image.Image, severity: int) -> Image.Image:
    shift_x = min(image.width - 1, round(image.width * severity * 0.04))
    shift_y = min(image.height - 1, round(image.height * severity * 0.03))
    cropped = image.crop((shift_x, shift_y, image.width, image.height))
    return cropped.resize(image.size, Image.Resampling.BILINEAR)


def _occlude(image: Image.Image, severity: int) -> Image.Image:
    result = image.copy()
    width = max(1, round(image.width * severity * 0.08))
    height = max(1, round(image.height * severity * 0.08))
    left = (image.width - width) // 2
    top = (image.height - height) // 2
    ImageDraw.Draw(result).rectangle(
        (left, top, left + width, top + height),
        fill=(0, 0, 0),
    )
    return result


def _color_cast(image: Image.Image, severity: int) -> Image.Image:
    red_gain = 1 + severity * 0.10
    blue_gain = max(0.4, 1 - severity * 0.08)
    red, green, blue = image.split()
    red = red.point(lambda value: min(255, round(value * red_gain)))
    blue = blue.point(lambda value: min(255, round(value * blue_gain)))
    return Image.merge("RGB", (red, green, blue))


def _pixel_noise(image: Image.Image, severity: int, seed: int) -> Image.Image:
    generator = random.Random(seed + severity)
    amplitude = severity * 5
    result = image.copy()
    pixels = result.load()
    for y_coordinate in range(result.height):
        for x_coordinate in range(result.width):
            current = pixels[x_coordinate, y_coordinate]
            pixels[x_coordinate, y_coordinate] = tuple(
                min(255, max(0, channel + generator.randint(-amplitude, amplitude)))
                for channel in current
            )
    return result
