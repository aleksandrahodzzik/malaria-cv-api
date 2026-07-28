"""Application configuration module using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Production application settings with environment variable override support."""

    # Project Information
    PROJECT_NAME: str = Field(
        default="Malaria Cell Classification Microservice", description="Project name"
    )
    VERSION: str = Field(default="1.0.0", description="API version")
    DESCRIPTION: str = Field(
        default="High-performance MedTech microservice for microscopic blood smear cell classification.",
        description="API Description",
    )
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Bind host")
    PORT: int = Field(default=8000, description="Bind port")
    DEBUG: bool = Field(default=False, description="Debug mode flag")

    # ML Model Configuration
    MODEL_NAME: str = Field(
        default="trpakov/vit-malaria-classification",
        description="HuggingFace Vision Transformer model identifier",
    )
    CONFIDENCE_THRESHOLD: float = Field(
        default=0.5,
        description="Confidence threshold for infected classification",
    )

    # Security & Input Constraints
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10, description="Maximum image upload size in Megabytes"
    )
    ALLOWED_CONTENT_TYPES: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        description="Allowed MIME types for uploaded cell images",
    )
    MAX_IMAGE_PIXELS: int = Field(
        default=25_000_000,
        description="Maximum decoded image area, in pixels",
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


# Instantiate global settings singleton
settings = Settings()
