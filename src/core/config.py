"""Application configuration module using Pydantic Settings."""

import re
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-variable override support."""

    # Project Information
    PROJECT_NAME: str = Field(
        default="Malaria Cell Classification Microservice", description="Project name"
    )
    VERSION: str = Field(default="1.4.0", description="API version")
    DESCRIPTION: str = Field(
        default=(
            "Research-only API prototype for classifying pre-cropped microscopic "
            "blood-cell images. Not for diagnosis or treatment decisions."
        ),
        description="API Description",
    )
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    ENVIRONMENT: Literal["development", "test", "production"] = Field(
        default="development",
        description="Runtime environment profile",
    )

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Bind host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Bind port")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    LOG_LEVEL: Literal["INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Minimum application log level",
    )

    # ML Model Configuration
    MODEL_NAME: str = Field(
        default="",
        description=(
            "Approved local model path or Hugging Face model identifier. "
            "No model is configured by default."
        ),
    )
    MODEL_SOURCE_ID: str = Field(
        default="",
        description=(
            "Stable registry identifier recorded in the local manifest. Required "
            "when MODEL_NAME is a local deployment path."
        ),
    )
    MODEL_REVISION: str | None = Field(
        default=None,
        description="Immutable model revision or commit SHA",
    )
    MODEL_MANIFEST_PATH: str = Field(
        default="",
        description=(
            "Path to the locally controlled model_manifest.json trust document. "
            "When empty for a local model, <MODEL_NAME>/model_manifest.json is used."
        ),
    )
    MODEL_MANIFEST_SHA256: str | None = Field(
        default=None,
        description="Optional SHA-256 trust anchor for model_manifest.json",
    )
    MODEL_REQUIRE_MANIFEST: bool = Field(
        default=True,
        description="Require artifact, label, input and license manifest verification",
    )
    MODEL_LOCAL_FILES_ONLY: bool = Field(
        default=False,
        description="Forbid model downloads and load only approved local cache/files",
    )
    MODEL_EXPECTED_LABELS: list[str] = Field(
        default=["Parasitized", "Uninfected"],
        min_length=2,
        description="Exact class labels required by the serving contract",
    )
    MAX_CONCURRENT_INFERENCES: int = Field(
        default=1,
        ge=1,
        le=32,
        description="Maximum inference jobs admitted concurrently per process",
    )
    INFERENCE_QUEUE_TIMEOUT_SECONDS: float = Field(
        default=2.0,
        ge=0.1,
        le=300.0,
        description="Maximum wait for an inference slot before returning busy",
    )
    INFERENCE_EXECUTION_TIMEOUT_SECONDS: float = Field(
        default=30.0,
        ge=0.1,
        le=3600.0,
        description=(
            "Maximum request wait for model compute. A timed-out native thread "
            "continues holding its inference slot until it actually finishes"
        ),
    )

    # Security & Input Constraints
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum image upload size in megabytes",
    )
    MAX_MULTIPART_OVERHEAD_BYTES: int = Field(
        default=1_048_576,
        ge=65_536,
        le=10_485_760,
        description=(
            "Maximum multipart framing overhead admitted in addition to the "
            "configured image-file limit"
        ),
    )
    MAX_SLIDE_UPLOAD_SIZE_MB: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum total multipart request size for slide summaries",
    )
    ALLOWED_CONTENT_TYPES: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        description="Allowed MIME types for uploaded cell images",
    )
    MAX_IMAGE_PIXELS: int = Field(
        default=25_000_000,
        ge=1,
        le=100_000_000,
        description="Maximum decoded image area, in pixels",
    )
    MAX_FILENAME_LENGTH: int = Field(
        default=255,
        ge=32,
        le=1024,
        description="Maximum sanitized filename length returned by the API",
    )
    CORS_ORIGINS: list[str] = Field(
        default=[],
        description="Explicit browser origins allowed to call the API",
    )
    API_KEY_REQUIRED: bool = Field(
        default=False,
        description="Require X-API-Key on inference endpoints",
    )
    API_KEYS: list[SecretStr] = Field(
        default=[],
        description="Accepted API keys. Values are treated as secrets.",
    )
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable per-client inference request quotas",
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=60,
        ge=1,
        le=100_000,
        description="Maximum inference requests admitted per sliding window",
    )
    RATE_LIMIT_WINDOW_SECONDS: float = Field(
        default=60.0,
        ge=0.1,
        le=86_400.0,
        description="Sliding-window duration in seconds",
    )
    RATE_LIMIT_MAX_KEYS: int = Field(
        default=10_000,
        ge=100,
        le=1_000_000,
        description="Maximum number of client buckets retained per process",
    )

    # Pre-inference microscopy quality-control policy. These thresholds are
    # conservative engineering defaults, not clinically validated cut-offs.
    QC_ENABLED: bool = Field(default=True)
    QC_MIN_WIDTH: int = Field(default=32, ge=8, le=4096)
    QC_MIN_HEIGHT: int = Field(default=32, ge=8, le=4096)
    QC_MAX_WIDTH: int = Field(default=2048, ge=32, le=16_384)
    QC_MAX_HEIGHT: int = Field(default=2048, ge=32, le=16_384)
    QC_MAX_ASPECT_RATIO: float = Field(default=2.0, ge=1.0, le=10.0)
    QC_MIN_CONTRAST_STD: float = Field(default=8.0, ge=0.0, le=128.0)
    QC_MIN_LAPLACIAN_VARIANCE: float = Field(
        default=12.0,
        ge=0.0,
        le=100_000.0,
    )
    QC_MIN_STAIN_PIXEL_RATIO: float = Field(default=0.03, ge=0.0, le=1.0)

    # Slide-summary resource and sampling boundaries.
    SLIDE_MIN_CELLS: int = Field(default=10, ge=2, le=10_000)
    SLIDE_MAX_CELLS: int = Field(default=100, ge=2, le=10_000)
    MAX_SLIDE_ID_LENGTH: int = Field(default=128, ge=8, le=512)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_security_invariants(self) -> Self:
        """Reject ambiguous production and cross-origin configurations."""
        if len(set(self.MODEL_EXPECTED_LABELS)) != len(self.MODEL_EXPECTED_LABELS):
            raise ValueError("MODEL_EXPECTED_LABELS must contain unique labels.")
        if any(not label.strip() for label in self.MODEL_EXPECTED_LABELS):
            raise ValueError("MODEL_EXPECTED_LABELS cannot contain blank labels.")
        if "*" in self.CORS_ORIGINS:
            raise ValueError("Wildcard CORS origins are not supported.")
        if self.API_KEY_REQUIRED and not self.API_KEYS:
            raise ValueError("API_KEY_REQUIRED needs at least one configured API key.")
        if self.SLIDE_MIN_CELLS > self.SLIDE_MAX_CELLS:
            raise ValueError("SLIDE_MIN_CELLS cannot exceed SLIDE_MAX_CELLS.")
        if self.QC_MIN_WIDTH > self.QC_MAX_WIDTH:
            raise ValueError("QC_MIN_WIDTH cannot exceed QC_MAX_WIDTH.")
        if self.QC_MIN_HEIGHT > self.QC_MAX_HEIGHT:
            raise ValueError("QC_MIN_HEIGHT cannot exceed QC_MAX_HEIGHT.")
        if self.MODEL_MANIFEST_SHA256 is not None and not re.fullmatch(
            r"[0-9a-fA-F]{64}",
            self.MODEL_MANIFEST_SHA256,
        ):
            raise ValueError("MODEL_MANIFEST_SHA256 must contain 64 hexadecimal chars.")
        if self.MODEL_NAME.strip() and (
            self.MODEL_REVISION is None
            or not re.fullmatch(r"[0-9a-fA-F]{40}", self.MODEL_REVISION)
        ):
            raise ValueError(
                "Configured models require an exact 40-character commit revision."
            )
        if (
            self.ENVIRONMENT == "production"
            and self.MODEL_NAME.strip()
            and not self.MODEL_REQUIRE_MANIFEST
        ):
            raise ValueError("Production cannot disable model manifest verification.")
        if (
            self.ENVIRONMENT == "production"
            and self.MODEL_NAME.strip()
            and self.MODEL_REQUIRE_MANIFEST
            and not self.MODEL_MANIFEST_SHA256
        ):
            raise ValueError(
                "Production models require MODEL_MANIFEST_SHA256 as a trust anchor."
            )
        if (
            self.ENVIRONMENT == "production"
            and self.MODEL_NAME.strip()
            and Path(self.MODEL_NAME).is_absolute()
            and not self.MODEL_SOURCE_ID.strip()
        ):
            raise ValueError("Production local models require MODEL_SOURCE_ID.")
        return self


# Instantiate global settings singleton
settings = Settings()
