"""Deterministic quality-control policy tests."""

from unittest.mock import patch

import pytest
from PIL import Image, ImageFilter

from src.services.qc import (
    QCMetrics,
    QCReason,
    QualityControlError,
    evaluate_image_quality,
    laplacian_variance,
)


def crisp_smear_like_image(width: int = 64, height: int = 64) -> Image.Image:
    """Create a deterministic high-frequency pink/purple test pattern."""
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y_pos in range(height):
        for x_pos in range(width):
            pixels[x_pos, y_pos] = (
                (210, 90, 170) if (x_pos // 4 + y_pos // 4) % 2 else (245, 210, 225)
            )
    return image


def test_crisp_stain_like_image_passes_and_exposes_metrics() -> None:
    result = evaluate_image_quality(crisp_smear_like_image())
    assert result.passed is True
    assert result.clinically_validated is False
    assert result.policy_version == "engineering-qc-v1"
    assert result.metrics.laplacian_variance > 100
    assert result.metrics.stain_pixel_ratio == 1.0
    assert result.metrics.as_dict()["width"] == 64


def test_blurred_image_is_rejected() -> None:
    blurred = crisp_smear_like_image().filter(ImageFilter.GaussianBlur(radius=5))
    with pytest.raises(QualityControlError) as caught:
        evaluate_image_quality(blurred)
    assert QCReason.BLURRY_IMAGE in caught.value.reasons
    assert caught.value.primary_reason in {
        QCReason.BLURRY_IMAGE.value,
        QCReason.INVALID_CONTRAST.value,
    }


@pytest.mark.parametrize("color", [(255, 255, 255), (0, 0, 0), (128, 128, 128)])
def test_blank_images_have_explicit_contrast_and_blur_reasons(
    color: tuple[int, int, int],
) -> None:
    with pytest.raises(QualityControlError) as caught:
        evaluate_image_quality(Image.new("RGB", (64, 64), color=color))
    assert QCReason.INVALID_CONTRAST in caught.value.reasons
    assert QCReason.BLURRY_IMAGE in caught.value.reasons
    assert QCReason.NON_MICROSCOPIC_PAYLOAD in caught.value.reasons


def test_green_high_frequency_payload_is_non_microscopic() -> None:
    image = Image.new("RGB", (64, 64))
    pixels = image.load()
    for y_pos in range(64):
        for x_pos in range(64):
            pixels[x_pos, y_pos] = (
                (20, 220, 20) if (x_pos + y_pos) % 2 else (180, 250, 180)
            )
    with pytest.raises(QualityControlError) as caught:
        evaluate_image_quality(image)
    assert QCReason.NON_MICROSCOPIC_PAYLOAD in caught.value.reasons


@pytest.mark.parametrize("size", [(8, 64), (64, 8), (4096, 64), (64, 4096)])
def test_resolution_and_aspect_ratio_bounds(size: tuple[int, int]) -> None:
    image = crisp_smear_like_image(*size)
    with pytest.raises(QualityControlError) as caught:
        evaluate_image_quality(image)
    assert QCReason.INVALID_RESOLUTION in caught.value.reasons


def test_laplacian_variance_handles_tiny_image() -> None:
    assert laplacian_variance(Image.new("L", (2, 2))) == 0.0


def test_thresholds_are_configurable_without_changing_algorithm() -> None:
    image = crisp_smear_like_image()
    with (
        patch("src.services.qc.settings.QC_MIN_LAPLACIAN_VARIANCE", 100_000.0),
        pytest.raises(QualityControlError) as caught,
    ):
        evaluate_image_quality(image)
    assert caught.value.reasons == (QCReason.BLURRY_IMAGE,)


def test_metrics_dataclass_has_stable_numeric_shape() -> None:
    metrics = QCMetrics(10, 20, 2.0, 3.0, 4.0, 0.5)
    assert metrics.as_dict() == {
        "width": 10,
        "height": 20,
        "aspect_ratio": 2.0,
        "contrast_std": 3.0,
        "laplacian_variance": 4.0,
        "stain_pixel_ratio": 0.5,
    }
