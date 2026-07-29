"""Queueing, memory and latency-summary helpers for capacity planning."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist, fmean, stdev


@dataclass(frozen=True)
class LatencySummary:
    """Descriptive latency summary for one explicitly named benchmark tier."""

    count: int
    mean: float
    standard_deviation: float
    confidence_interval_95: tuple[float, float]
    p50: float
    p90: float
    p95: float
    p99: float


def utilization(
    *,
    arrival_rate: float,
    service_rate_per_worker: float,
    workers: int,
) -> float:
    """Return rho=lambda/(c*mu)."""
    _validate_rates(arrival_rate, service_rate_per_worker, workers)
    return arrival_rate / (workers * service_rate_per_worker)


def little_law(*, throughput: float, mean_time_in_system: float) -> float:
    """Return mean population L=lambda*W."""
    if throughput < 0 or mean_time_in_system < 0:
        raise ValueError("throughput and time must be non-negative.")
    return throughput * mean_time_in_system


def erlang_c(
    *,
    arrival_rate: float,
    service_rate_per_worker: float,
    workers: int,
) -> dict[str, float]:
    """M/M/c approximation for stable systems.

    This is a planning model, not a replacement for measured service times,
    bounded-queue behavior, or native-thread effects.
    """
    rho = utilization(
        arrival_rate=arrival_rate,
        service_rate_per_worker=service_rate_per_worker,
        workers=workers,
    )
    if rho >= 1:
        raise ValueError("Erlang-C requires a stable system with utilization < 1.")
    offered_load = arrival_rate / service_rate_per_worker
    partial_sum = sum(
        offered_load**index / math.factorial(index) for index in range(workers)
    )
    final_term = offered_load**workers / (math.factorial(workers) * (1 - rho))
    probability_wait = final_term / (partial_sum + final_term)
    queue_wait = probability_wait / (workers * service_rate_per_worker - arrival_rate)
    service_time = 1 / service_rate_per_worker
    return {
        "utilization": rho,
        "probability_wait": probability_wait,
        "mean_queue_wait": queue_wait,
        "mean_service_time": service_time,
        "mean_time_in_system": queue_wait + service_time,
        "mean_requests_in_system": little_law(
            throughput=arrival_rate,
            mean_time_in_system=queue_wait + service_time,
        ),
    }


def ram_estimate(
    *,
    workers: int,
    model_per_worker: int,
    runtime_per_worker: int,
    activation_peak_per_worker: int,
    shared: int,
    upload_buffers: int,
    safety_margin: int,
) -> int:
    """Return conservative bytes required by a process-local model topology."""
    values = (
        workers,
        model_per_worker,
        runtime_per_worker,
        activation_peak_per_worker,
        shared,
        upload_buffers,
        safety_margin,
    )
    if min(values) < 0 or workers == 0:
        raise ValueError("Memory inputs must be non-negative and workers positive.")
    return (
        workers * (model_per_worker + runtime_per_worker + activation_peak_per_worker)
        + shared
        + upload_buffers
        + safety_margin
    )


def summarize_latency(samples: list[float]) -> LatencySummary:
    """Summarize non-negative latency samples with a normal mean CI."""
    if not samples or any(not math.isfinite(value) or value < 0 for value in samples):
        raise ValueError("Finite non-negative latency samples are required.")
    count = len(samples)
    mean = fmean(samples)
    deviation = stdev(samples) if count > 1 else 0.0
    if count > 1:
        half_width = NormalDist().inv_cdf(0.975) * deviation / math.sqrt(count)
    else:
        half_width = 0.0
    ordered = sorted(samples)
    return LatencySummary(
        count=count,
        mean=mean,
        standard_deviation=deviation,
        confidence_interval_95=(
            max(0.0, mean - half_width),
            mean + half_width,
        ),
        p50=_quantile(ordered, 0.50),
        p90=_quantile(ordered, 0.90),
        p95=_quantile(ordered, 0.95),
        p99=_quantile(ordered, 0.99),
    )


def _quantile(ordered: list[float], probability: float) -> float:
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _validate_rates(
    arrival_rate: float,
    service_rate_per_worker: float,
    workers: int,
) -> None:
    if arrival_rate < 0 or service_rate_per_worker <= 0 or workers <= 0:
        raise ValueError(
            "arrival_rate must be non-negative; service rate and workers positive."
        )
