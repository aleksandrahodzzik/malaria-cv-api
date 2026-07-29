"""Pre-inference engineering QC for pre-cropped microscopy cell images.

The checks in this module are deterministic rejection safeguards. They are not
a clinically validated OOD detector and must not be represented as one.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from statistics import fmean, pvariance

from PIL import Image, ImageStat

from src.core.config import settings


class QCReason(StrEnum):
    """Stable machine-readable QC rejection codes."""

    BLURRY_IMAGE = "BLURRY_IMAGE"
    NON_MICROSCOPIC_PAYLOAD = "NON_MICROSCOPIC_PAYLOAD"
    INVALID_CONTRAST = "INVALID_CONTRAST"
    INVALID_RESOLUTION = "INVALID_RESOLUTION"


@dataclass(frozen=True, slots=True)
class QCMetrics:
    """Inspectable deterministic measurements used by the QC policy."""

    width: int
    height: int
    aspect_ratio: float
    contrast_std: float
    laplacian_variance: float
    stain_pixel_ratio: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QCResult:
    """Successful QC outcome."""

    passed: bool
    metrics: QCMetrics
    policy_version: str = "engineering-qc-v1"
    clinically_validated: bool = False


class QualityControlError(ValueError):
    """One or more deterministic pre-inference checks rejected the image."""

    def __init__(self, reasons: list[QCReason], metrics: QCMetrics) -> None:
        self.reasons = tuple(dict.fromkeys(reasons))
        self.metrics = metrics
        super().__init__(", ".join(reason.value for reason in self.reasons))

    @property
    def primary_reason(self) -> str:
        return self.reasons[0].value


def _analysis_copy(image: Image.Image, max_side: int = 256) -> Image.Image:
    analysis = image.convert("RGB")
    analysis.thumbnail((max_side, max_side))
    return analysis


def laplacian_variance(image: Image.Image) -> float:
    """Compute variance of a 4-neighbour discrete Laplacian on grayscale pixels."""
    grayscale = _analysis_copy(image).convert("L")
    width, height = grayscale.size
    if width < 3 or height < 3:
        return 0.0
    pixels = list(grayscale.getdata())
    responses: list[float] = []
    for y_pos in range(1, height - 1):
        row = y_pos * width
        for x_pos in range(1, width - 1):
            center = pixels[row + x_pos]
            response = (
                4 * center
                - pixels[row + x_pos - 1]
                - pixels[row + x_pos + 1]
                - pixels[row - width + x_pos]
                - pixels[row + width + x_pos]
            )
            responses.append(float(response))
    return pvariance(responses) if len(responses) > 1 else 0.0


def _stain_pixel_ratio(image: Image.Image) -> float:
    """Estimate the fraction of chromatic pink/purple/blue smear-like pixels."""
    rgb = _analysis_copy(image)
    pixels = list(rgb.getdata())
    if not pixels:
        return 0.0

    stain_like = 0
    for red, green, blue in pixels:
        maximum = max(red, green, blue)
        minimum = min(red, green, blue)
        chroma = maximum - minimum
        sufficiently_colored = chroma >= 18 and 25 <= maximum <= 250
        pink_or_purple = red >= green * 1.05 or blue >= green * 1.05
        if sufficiently_colored and pink_or_purple:
            stain_like += 1
    return stain_like / len(pixels)


def evaluate_image_quality(image: Image.Image) -> QCResult:
    """Evaluate configured engineering QC and raise a structured rejection."""
    width, height = image.size
    aspect_ratio = max(width / height, height / width) if width and height else 0.0
    grayscale = _analysis_copy(image).convert("L")
    contrast_values = ImageStat.Stat(grayscale).stddev
    contrast_std = fmean(contrast_values) if contrast_values else 0.0
    metrics = QCMetrics(
        width=width,
        height=height,
        aspect_ratio=round(aspect_ratio, 4),
        contrast_std=round(contrast_std, 4),
        laplacian_variance=round(laplacian_variance(image), 4),
        stain_pixel_ratio=round(_stain_pixel_ratio(image), 4),
    )
    reasons: list[QCReason] = []
    if (
        width < settings.QC_MIN_WIDTH
        or height < settings.QC_MIN_HEIGHT
        or width > settings.QC_MAX_WIDTH
        or height > settings.QC_MAX_HEIGHT
        or aspect_ratio > settings.QC_MAX_ASPECT_RATIO
    ):
        reasons.append(QCReason.INVALID_RESOLUTION)
    if metrics.contrast_std < settings.QC_MIN_CONTRAST_STD:
        reasons.append(QCReason.INVALID_CONTRAST)
    if metrics.laplacian_variance < settings.QC_MIN_LAPLACIAN_VARIANCE:
        reasons.append(QCReason.BLURRY_IMAGE)
    if metrics.stain_pixel_ratio < settings.QC_MIN_STAIN_PIXEL_RATIO:
        reasons.append(QCReason.NON_MICROSCOPIC_PAYLOAD)

    if reasons:
        raise QualityControlError(reasons, metrics)
    return QCResult(passed=True, metrics=metrics)
