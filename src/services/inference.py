"""ML inference service wrapping a validated image-classification model."""

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

_CONTENT_TYPE_TO_FORMATS: dict[str, frozenset[str]] = {
    "image/jpeg": frozenset({"JPEG"}),
    "image/png": frozenset({"PNG"}),
    "image/webp": frozenset({"WEBP"}),
}
_ALLOWED_IMAGE_MODES = frozenset({"RGB", "RGBA", "L", "LA", "P"})


class InferenceCapacityError(RuntimeError):
    """Raised when a request cannot acquire bounded inference capacity."""


class InferenceTimeoutError(RuntimeError):
    """Raised when request wait expires while native model compute continues."""


class MalariaClassifierService:
    """Research inference adapter for an explicitly approved image model artifact."""

    def __init__(self, model_name: str = settings.MODEL_NAME) -> None:
        self.model_name: str = model_name
        self.processor: Any = None
        self.model: Any = None
        self._is_ready: bool = False
        self._id2label: dict[int, str] = {}
        self._inference_semaphore = asyncio.Semaphore(
            settings.MAX_CONCURRENT_INFERENCES
        )
        self._background_inference_tasks: set[asyncio.Task[dict[str, Any]]] = set()

    def load_model(self) -> None:
        """Load feature processor and vision transformer model weights into memory."""
        if not self.model_name.strip():
            raise RuntimeError(
                "MODEL_NAME is not configured. Provide an approved model artifact."
            )

        logger.info("Loading approved image-classification model.")
        start_time = time.perf_counter()

        try:
            load_options: dict[str, Any] = {
                "local_files_only": settings.MODEL_LOCAL_FILES_ONLY
            }
            if settings.MODEL_REVISION:
                load_options["revision"] = settings.MODEL_REVISION

            self.processor = AutoImageProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=False,
                **load_options,
            )
            self.model = AutoModelForImageClassification.from_pretrained(
                self.model_name,
                trust_remote_code=False,
                use_safetensors=True,
                **load_options,
            )
            self._id2label = self._validate_model_contract()
            self.model.eval()  # Set PyTorch model to evaluation mode
            self._is_ready = True

            elapsed = time.perf_counter() - start_time
            logger.info(
                "Approved model loaded in %.2f seconds.",
                elapsed,
            )
        except Exception as exc:
            self._is_ready = False
            logger.error(
                "Approved model load failed with %s.",
                type(exc).__name__,
            )
            raise RuntimeError("Model initialization failure.") from exc

    def _validate_model_contract(self) -> dict[int, str]:
        """Validate class count, indices and labels before accepting the model."""
        config = getattr(self.model, "config", None)
        raw_mapping = getattr(config, "id2label", None)
        if not isinstance(raw_mapping, dict) or not raw_mapping:
            raise RuntimeError("Model configuration does not define id2label.")

        try:
            id2label = {int(index): str(label) for index, label in raw_mapping.items()}
        except (TypeError, ValueError) as exc:
            raise RuntimeError("Model id2label indices must be integers.") from exc

        expected_indices = set(range(len(id2label)))
        if set(id2label) != expected_indices:
            raise RuntimeError("Model id2label indices must be contiguous from zero.")

        actual_labels = [id2label[index] for index in range(len(id2label))]
        if actual_labels != settings.MODEL_EXPECTED_LABELS:
            raise RuntimeError(
                "Model labels do not match MODEL_EXPECTED_LABELS. "
                f"Expected {settings.MODEL_EXPECTED_LABELS!r}, "
                f"received {actual_labels!r}."
            )

        num_labels = getattr(config, "num_labels", len(id2label))
        if num_labels != len(id2label):
            raise RuntimeError("Model num_labels and id2label size do not match.")

        return id2label

    def is_ready(self) -> bool:
        """Check if model and processor are initialized and ready for inference."""
        return self._is_ready and self.model is not None and self.processor is not None

    def _release_background_inference(
        self,
        task: asyncio.Task[dict[str, Any]],
    ) -> None:
        """Release capacity after a timed-out native worker actually finishes."""
        self._background_inference_tasks.discard(task)
        try:
            task.exception()
        except asyncio.CancelledError:
            pass
        self._inference_semaphore.release()

    def _predict_sync(
        self,
        image_bytes: bytes,
        declared_content_type: str | None = None,
    ) -> dict[str, Any]:
        """Decode an image and synchronously execute model inference.

        Heavy matrix operations in this method must run via ``asyncio.to_thread``.
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
                decoded_format = image.format
                if decoded_format is None:
                    raise ValueError("Decoded image format is unavailable.")
                if declared_content_type is not None:
                    expected_formats = _CONTENT_TYPE_TO_FORMATS.get(
                        declared_content_type
                    )
                    if (
                        expected_formats is None
                        or decoded_format not in expected_formats
                    ):
                        raise ValueError(
                            "Declared content type does not match decoded image format."
                        )
                if getattr(image, "n_frames", 1) != 1:
                    raise ValueError(
                        "Multi-frame or animated images are not supported."
                    )
                if image.mode not in _ALLOWED_IMAGE_MODES:
                    raise ValueError(
                        f"Image mode '{image.mode}' is not supported by the "
                        "serving contract."
                    )
                if width * height > settings.MAX_IMAGE_PIXELS:
                    raise ValueError(
                        "Decoded image exceeds the "
                        f"{settings.MAX_IMAGE_PIXELS:,}-pixel limit."
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
        with torch.inference_mode():
            outputs = self.model(**inputs)
            logits = outputs.logits
            if logits.ndim != 2 or logits.shape[0] != 1:
                raise RuntimeError("Model returned an unexpected logits shape.")
            if logits.shape[1] != len(self._id2label):
                raise RuntimeError(
                    "Model logits count does not match the validated label contract."
                )
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]

        class_probabilities: list[ClassProbability] = []
        for class_id, prob_tensor in enumerate(probs):
            label_name = self._id2label[class_id]
            prob_val = float(prob_tensor.item())
            class_probabilities.append(
                ClassProbability(label=label_name, confidence=prob_val)
            )

        # Sort probability distribution in descending order
        class_probabilities.sort(key=lambda x: x.confidence, reverse=True)
        class_probabilities = [
            ClassProbability(
                label=item.label,
                confidence=round(item.confidence, 4),
            )
            for item in class_probabilities
        ]

        top_prediction = class_probabilities[0]

        return {
            "predicted_cell_class": top_prediction.label,
            "confidence": top_prediction.confidence,
            "probabilities": class_probabilities,
        }

    async def analyze_image(
        self,
        image_bytes: bytes,
        filename: str,
        declared_content_type: str | None = None,
    ) -> PredictionResponse:
        """Analyze a cell image without blocking the event loop."""
        start_time = time.perf_counter()

        try:
            await asyncio.wait_for(
                self._inference_semaphore.acquire(),
                timeout=settings.INFERENCE_QUEUE_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            raise InferenceCapacityError(
                "Inference capacity is temporarily unavailable."
            ) from exc

        inference_task = asyncio.create_task(
            asyncio.to_thread(
                self._predict_sync,
                image_bytes,
                declared_content_type,
            )
        )
        release_capacity_here = True
        try:
            # Shield keeps resource accounting correct: cancelling the caller does not
            # stop a native PyTorch worker thread.
            prediction_data = await asyncio.wait_for(
                asyncio.shield(inference_task),
                timeout=settings.INFERENCE_EXECUTION_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            # Python cannot stop the running native thread. Keep a strong task
            # reference and retain the semaphore slot until compute really ends.
            release_capacity_here = False
            self._background_inference_tasks.add(inference_task)
            inference_task.add_done_callback(self._release_background_inference)
            raise InferenceTimeoutError(
                "Inference execution exceeded the request timeout."
            ) from exc
        except asyncio.CancelledError:
            await inference_task
            raise
        finally:
            if release_capacity_here:
                self._inference_semaphore.release()

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return PredictionResponse(
            filename=filename,
            predicted_cell_class=prediction_data["predicted_cell_class"],
            diagnosis=prediction_data["predicted_cell_class"],
            confidence=prediction_data["confidence"],
            probabilities=prediction_data["probabilities"],
            execution_time_ms=round(elapsed_ms, 2),
        )
