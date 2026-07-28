# Concurrency and capacity model

## Наблюдаемые параметры

```text
logical CPU                    = 12
torch intra-op threads         = 6
torch inter-op threads         = 6
Gunicorn workers default       = 1
MAX_CONCURRENT_INFERENCES      = 1
queue timeout default          = 2.0 s
execution timeout default      = 30.0 s
```

## Topology

```text
GlobalComputeConcurrency =
  workers * per_process_slots
  = 1 * 1
  = 1
```

Оценочная верхняя граница native compute concurrency:

```text
NativeThreadUpperBound ≈
  workers
  * per_process_slots
  * max(torch_intraop_threads, BLAS_threads)

≈ 1 * 1 * max(6, BLAS_threads)
```

`BLAS_threads` не был независимо измерен. Поэтому `6` — не доказанный жёсткий
upper bound.

Если оператор без benchmark изменит workers на `W`:

```text
model copies = W
global inference slots = W * MAX_CONCURRENT_INFERENCES
native threads ≈ W * MAX_CONCURRENT_INFERENCES * torch_threads
```

Это создаёт CPU oversubscription и линейное размножение model RSS.

## Queue

Admission:

```text
wait semaphore <= INFERENCE_QUEUE_TIMEOUT_SECONDS
```

При превышении возвращается:

```text
503 SERVICE_UNAVAILABLE
Retry-After: 2
```

Compute wait:

```text
wait shielded worker task <= INFERENCE_EXECUTION_TIMEOUT_SECONDS
```

При превышении:

```text
client response = 504 INFERENCE_TIMEOUT
native task      = continues
semaphore slot   = retained until actual completion
```

## Cancellation invariant

Критический invariant:

```text
request cancelled
!=
native PyTorch thread stopped
```

Проверенный acceptance criterion:

```text
cancel request
-> request task not complete while worker blocked
-> semaphore remains locked
-> release worker
-> CancelledError propagates
-> semaphore unlocks
```

## Little’s Law

```text
L = λW
```

При одном compute slot стабильность требует:

```text
λ < 1 / E[S]
```

где `E[S]` — среднее время реального inference. Поскольку approved model
отсутствует, `E[S]`, p95/p99, throughput и safe arrival rate неизвестны.

## Verdict

```text
event loop offload: VERIFIED
bounded per-process admission: VERIFIED
correct cancellation accounting: VERIFIED
correct timeout accounting: VERIFIED
scalability: NOT TESTABLE WITH CURRENT EVIDENCE
```
