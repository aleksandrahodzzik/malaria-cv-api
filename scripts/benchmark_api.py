"""Reproducible T0/T1 ASGI benchmark without a real model.

This script deliberately does not report real-model inference performance.
Run it from the repository root:

    python -m scripts.benchmark_api
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import platform
import statistics
import sys
import time
from dataclasses import asdict
from typing import Any

import httpx
from PIL import Image

from src.main import app
from src.schemas.payload import ClassProbability, PredictionResponse
from src.validation.capacity import summarize_latency


class SyntheticClassifier:
    """Immediate deterministic response used only for HTTP overhead measurement."""

    def is_ready(self) -> bool:
        return True

    async def analyze_image(
        self,
        image_bytes: bytes,
        filename: str,
        declared_content_type: str | None = None,
    ) -> PredictionResponse:
        if not image_bytes or declared_content_type != "image/png":
            raise ValueError("Unexpected synthetic benchmark input.")
        return PredictionResponse(
            filename=filename,
            predicted_cell_class="Parasitized",
            diagnosis="Parasitized",
            confidence=0.75,
            probabilities=[
                ClassProbability(label="Parasitized", confidence=0.75),
                ClassProbability(label="Uninfected", confidence=0.25),
            ],
            execution_time_ms=0.0,
        )


def _png_bytes(size: int = 128) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (size, size), color=(120, 80, 100)).save(buffer, format="PNG")
    return buffer.getvalue()


async def _run_scenario(
    client: httpx.AsyncClient,
    *,
    name: str,
    concurrency: int,
    requests: int,
    analyze: bool,
) -> dict[str, Any]:
    semaphore = asyncio.Semaphore(concurrency)
    payload = _png_bytes()

    async def one_request() -> tuple[float, int]:
        async with semaphore:
            started = time.perf_counter()
            if analyze:
                response = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("cell.png", payload, "image/png")},
                )
            else:
                response = await client.get("/health")
            return (time.perf_counter() - started) * 1000, response.status_code

    for _ in range(10):
        await one_request()
    wall_started = time.perf_counter()
    results = await asyncio.gather(*(one_request() for _ in range(requests)))
    wall_seconds = time.perf_counter() - wall_started
    latencies = [latency for latency, _ in results]
    statuses = [status for _, status in results]
    summary = asdict(summarize_latency(latencies))
    summary.update(
        {
            "scenario": name,
            "tier": "T1_SYNTHETIC" if analyze else "T0_NO_MODEL_FRAMEWORK",
            "concurrency": concurrency,
            "requests": requests,
            "throughput_requests_per_second": requests / wall_seconds,
            "error_rate": sum(status >= 400 for status in statuses) / requests,
            "status_codes": {
                str(status): statuses.count(status) for status in sorted(set(statuses))
            },
            "rss_bytes": "NOT_MEASURED",
            "cpu": "NOT_MEASURED",
            "model_time": "NOT_APPLICABLE",
        }
    )
    return summary


async def main() -> None:
    logging.getLogger().setLevel(logging.CRITICAL)
    app.state.classifier_service = SyntheticClassifier()
    app.state.model_error_code = None
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://benchmark.local",
        timeout=30,
    ) as client:
        scenarios = [
            await _run_scenario(
                client,
                name="health",
                concurrency=1,
                requests=100,
                analyze=False,
            )
        ]
        for concurrency in (1, 2, 4, 8, 16):
            scenarios.append(
                await _run_scenario(
                    client,
                    name="synthetic_analyze",
                    concurrency=concurrency,
                    requests=100,
                    analyze=True,
                )
            )

    print(
        json.dumps(
            {
                "status": "NON_MODEL_BASELINE_ONLY",
                "python": sys.version,
                "platform": platform.platform(),
                "clock": "time.perf_counter",
                "repetitions": 100,
                "warmup": 10,
                "warning": (
                    "T0/T1 results exclude model loading, PIL/model preprocessing, "
                    "PyTorch compute, real RSS/CPU, network and reverse proxy."
                ),
                "median_scenario_mean_ms": statistics.median(
                    scenario["mean"] for scenario in scenarios
                ),
                "scenarios": scenarios,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
