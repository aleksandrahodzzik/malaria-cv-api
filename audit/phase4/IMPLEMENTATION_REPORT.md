# Phase 4 implementation report

Дата: 2026-07-28

## Реализовано

1. `LegacyRouteDeprecationMiddleware`:
   - legacy aliases остаются совместимыми;
   - исключены из canonical OpenAPI;
   - получают `Deprecation: true`;
   - получают `Link` на `/api/v1` successor.
2. Readiness больше не раскрывает абсолютный путь local model artifact.
3. CORS methods/headers ограничены явным набором.
4. Image serving contract:
   - declared MIME сопоставляется с decoded format;
   - multi-frame/animated изображения отклоняются;
   - CMYK/unusual modes отклоняются;
   - grayscale/RGBA нормализуются в RGB;
   - decoded pixel limit проверяется до `load()`.
5. Model loader:
   - `trust_remote_code=False`;
   - `use_safetensors=True`.
6. Execution timeout:
   - отдельный `INFERENCE_EXECUTION_TIMEOUT_SECONDS`;
   - стабильный `504 INFERENCE_TIMEOUT`;
   - native task сохраняет semaphore slot до реального окончания.
7. Удалены недоказанные `security-hardened` claims из Docker/Makefile.
8. Добавлены adversarial и concurrency tests.

## Почему timeout устроен именно так

Нельзя безопасно написать:

```text
timeout -> cancel asyncio wrapper -> release semaphore
```

`asyncio.to_thread` не останавливает PyTorch/native compute. Немедленный
release позволил бы новым запросам войти в compute и нарушил бы configured
capacity.

Реализованный invariant:

```text
client timeout
-> 504
-> worker continues
-> capacity remains occupied
-> callback releases only after worker done
```

## Не реализовано намеренно

- Не добавлена случайная replacement model.
- Filename extension не используется как security boundary.
- Не заявлена клиническая вероятность.
- Не добавлен in-memory application rate limiter, потому что он не является
  global control при нескольких workers/replicas.
- Не выдуманы Docker/load-test результаты.

## Проверка

Targeted gate после реализации:

```text
39 passed
Ruff: PASS
Mypy strict: PASS
```

Финальный gate после завершения фаз 3–5:

```text
43 passed
coverage 87.96%
Ruff/Mypy/compileall/pip check: PASS
две clean-room constrained-установки: exact 66/66 match
```
