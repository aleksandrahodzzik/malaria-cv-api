"""ML Inference Service wrapping HuggingFace ViT Model for Malaria Cell Classification."""

import asyncio
import io
import logging
import time
from typing import Any

import torch
from PIL import Image, UnidentifiedImageError
from transformers import AutoImageProcessor, AutoModelForImageClassification

from src.core.config import settings
from src.schemas.payload import ClassProbability, PredictionResponse

logger = logging.getLogger("malaria_api.inference")


class MalariaClassifierService:
    """Production ML Inference service for classifying malaria blood smear cells."""

    def __init__(self, model_name: str = settings.MODEL_NAME) -> None:
        self.model_name: str = model_name
        self.processor: Any = None
        self.model: Any = None
        self._is_ready: bool = False

    def load_model(self) -> None:
        """Load feature processor and vision transformer model weights into memory."""
        logger.info(f"Loading HuggingFace vision model: '{self.model_name}'...")
        start_time = time.perf_counter()

        try:
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(
                self.model_name
            )
            self.model.eval()  # Set PyTorch model to evaluation mode
            self._is_ready = True

            elapsed = time.perf_counter() - start_time
            logger.info(
                f"Successfully loaded '{self.model_name}' in {elapsed:.2f} seconds."
            )
        except Exception as exc:
            self._is_ready = False
            logger.error(f"Failed to load HuggingFace model '{self.model_name}': {exc}")
            raise RuntimeError(f"Model initialization failure: {exc}") from exc

    def is_ready(self) -> bool:
        """Check if model and processor are initialized and ready for inference."""
        return self._is_ready and self.model is not None and self.processor is not None

    def _predict_sync(self, image_bytes: bytes) -> dict[str, Any]:
        """Decode an image and synchronously execute model inference.

        This method performs heavy matrix operations and must be offloaded via `asyncio.to_thread()`.
        """
        if not self.is_ready():
            raise RuntimeError(
                "Model is not initialized. Please ensure lifespan startup complete."
            )

        try:
            # verify() forces PIL to validate the encoded file rather than trusting
            # only its header. Re-open it afterwards because verify() consumes it.
            with Image.open(io.BytesIO(image_bytes)) as image:
                image.verify()

            with Image.open(io.BytesIO(image_bytes)) as image:
                width, height = image.size
                if width * height > settings.MAX_IMAGE_PIXELS:
                    raise ValueError(
                        f"Decoded image exceeds the {settings.MAX_IMAGE_PIXELS:,}-pixel limit."
                    )
                # load() performs decoding in this worker thread. convert() also
                # normalizes RGBA and grayscale inputs for the image processor.
                image.load()
                rgb_image = image.convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError(f"Invalid image file: {exc}") from exc

        # Feature extraction & tensor conversion
        inputs = self.processor(images=rgb_image, return_tensors="pt")

        # PyTorch forward pass without gradient computation
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        # Extract classification labels from model configuration id2label mapping
        id2label: dict[int, str] = getattr(
            self.model.config,
            "id2label",
            {0: "Parasitized", 1: "Uninfected"},
        )

        class_probabilities: list[ClassProbability] = []
        for class_id, prob_tensor in enumerate(probs):
            label_name = id2label.get(class_id, f"CLASS_{class_id}")
            prob_val = float(prob_tensor.item())
            class_probabilities.append(
                ClassProbability(label=label_name, confidence=round(prob_val, 4))
            )

        # Sort probability distribution in descending order
        class_probabilities.sort(key=lambda x: x.confidence, reverse=True)

        top_prediction = class_probabilities[0]

        return {
            "diagnosis": top_prediction.label,
            "confidence": top_prediction.confidence,
            "probabilities": class_probabilities,
        }

    async def analyze_image(
        self, image_bytes: bytes, filename: str
    ) -> PredictionResponse:
        """Asynchronously analyze cell image byte payload without blocking the event loop."""
        start_time = time.perf_counter()

        # Image decoding and PyTorch execution are both kept off the event loop.
        prediction_data = await asyncio.to_thread(self._predict_sync, image_bytes)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return PredictionResponse(
            filename=filename,
            diagnosis=prediction_data["diagnosis"],
            confidence=prediction_data["confidence"],
            probabilities=prediction_data["probabilities"],
            execution_time_ms=round(elapsed_ms, 2),
        )
