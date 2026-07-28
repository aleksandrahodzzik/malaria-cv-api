# Verification report

Дата: 2026-07-28
Final local environment: Windows, Python 3.12.0

## 1. Automated checks

| Check | Result | Evidence |
|---|---|---|
| Ruff formatter | PASS | 15 files formatted |
| Ruff lint | PASS | All checks passed |
| Mypy strict | PASS | 13 source files |
| Pytest | PASS | 28 passed |
| Coverage | PASS | 84.89%, threshold 80% |
| Branch coverage | enabled | `pyproject.toml` |
| pip check | PASS | No broken requirements |
| compileall | PASS | `src`, `tests` |
| JavaScript syntax | PASS | `node --check src/ui/app.js` |
| Git whitespace | PASS | `git diff --check` |
| Secret pattern scan | PASS | no known token/private-key patterns |
| README mojibake scan | PASS | no target patterns |
| Docker | NOT_EXECUTED | executable absent |
| Make targets | NOT_EXECUTED | executable absent |
| pip-audit | NOT_EXECUTED | package absent |
| Real model smoke | BLOCKED | approved artifact absent |

## 2. Test coverage

28 tests проверяют:

- UI и static assets;
- CSP/security headers;
- generated/preserved/replaced request ID;
- capabilities;
- readiness ready/not configured;
- research-only successful response;
- filename sanitation;
- 400/404/413/415/422/500/503 envelopes;
- internal exception non-disclosure;
- Retry-After;
- corrupt images;
- exact/inverted label contract;
- explicit model requirement;
- revision/local-only loader options;
- real tensor/logits transformation на synthetic model double;
- bounded inference queue;
- CORS/production settings invariants;
- OpenAPI response/error/deprecation contract.

Unit tests всё ещё не являются real-model evidence.

## 3. Browser verification

Использован headless installed Google Chrome через Playwright, без внешней
сети. Local UI assets/API были перехвачены deterministic mock responses.

### Desktop unavailable state

- viewport: 1440×1100;
- title и H1 корректны;
- status: `Модель не настроена`;
- analyze disabled;
- body width = viewport width;
- resources только same-origin;
- единственная console network error — ожидаемый HTTP 503 readiness.

### Mobile

- viewport: 390×844;
- body width = viewport width;
- horizontal overflow отсутствует;
- navigation/status/cards видимы;
- layout переходит в одну колонку.

### Ready + success journey

- viewport: 1280×900;
- readiness: `Готова к анализу`;
- PNG выбирается;
- preview/file card появляется;
- analyze выполняется;
- result: `Parasitized`, `88.08%`;
- два semantic `<progress>`;
- uncalibrated warning видим;
- console errors: `0`.

## 4. Three-pass review

### Review A — correctness

Найдено и исправлено:

- старые tests не отражали новый response;
- OpenAPI не документировал 415/422/500;
- strict Mypy требовал точных middleware/header types;
- settings нуждались в production invariants.

Status: PASS для доступного mocked/software scope.

### Review B — security/reliability

Найдено и исправлено:

- untrusted request ID;
- internal exception disclosure;
- unsafe label fallback;
- unbounded per-process admission;
- semaphore release при cancel до окончания native thread;
- ambiguous remote production model revision;
- wildcard CORS;
- two-worker default.

Осталось: auth/global quotas, transitive hashes, SBOM/scans, real load test.

Status: CONDITIONAL PASS для local research prototype.

### Review C — UX/clinical safety

Найдено и исправлено:

- UI отсутствовал;
- README mojibake;
- diagnosis semantics;
- missing unavailable/loading/error/success states;
- CSP конфликтовал с inline score width; заменено semantic `<progress>`;
- result focus и mobile layout проверены.

Осталось: formal WCAG audit; deprecated `diagnosis` alias; clinical evidence.

Status: PASS для research-only UI, NO-GO для clinical UX.

## 5. Artifact consistency

- Master prompt существует отдельно.
- Phase1 README links разрешаются.
- Feature CSV имеет единый header и 14 unique Feature IDs.
- Production docs используют version `1.1.0`.
- Default model configuration пустая и честно документирована.
- Git baseline был clean; текущие изменения относятся к этой задаче.
- Commit/push/deploy не выполнялись.

## 6. Final gates

| Gate | Result |
|---|---|
| Inventory | PASS |
| Architecture reconstruction | PASS |
| UI functional audit | PASS |
| Backend functional audit | PASS |
| Controlled implementation | PASS |
| Static/unit/API verification | PASS |
| Browser UI verification | PASS |
| Docker verification | NOT_EXECUTED |
| Real model gate | FAIL/BLOCKED |
| Clinical evidence gate | FAIL/BLOCKED |

Финальная формулировка: software prototype materially improved and verified;
real malaria classification and clinical deployment remain NO-GO.

## 7. Актуальные технические ориентиры

- FastAPI lifespan:
  https://fastapi.tiangolo.com/advanced/events/
- FastAPI custom/validation exception handlers:
  https://fastapi.tiangolo.com/tutorial/handling-errors/
- W3C WCAG 2.2:
  https://www.w3.org/TR/WCAG22/
- OWASP API4:2023 Unrestricted Resource Consumption:
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/

Они использованы как engineering guidance, а не как заявление formal
compliance.
