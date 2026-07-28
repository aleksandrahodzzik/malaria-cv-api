"""Application configuration module using Pydantic Settings."""

from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-variable override support."""

    # Project Information
    PROJECT_NAME: str = Field(
        default="Malaria Cell Classification Microservice", description="Project name"
    )
    VERSION: str = Field(default="1.2.0", description="API version")
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

    # ML Model Configuration
    MODEL_NAME: str = Field(
        default="",
        description=(
            "Approved local model path or Hugging Face model identifier. "
            "No model is configured by default."
        ),
    )
    MODEL_REVISION: str | None = Field(
        default=None,
        description="Immutable model revision or commit SHA",
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
        if (
            self.ENVIRONMENT == "production"
            and self.MODEL_NAME.strip()
            and not self.MODEL_LOCAL_FILES_ONLY
            and not self.MODEL_REVISION
        ):
            raise ValueError(
                "Production remote models require an immutable MODEL_REVISION."
            )
        return self


# Instantiate global settings singleton
settings = Settings()
