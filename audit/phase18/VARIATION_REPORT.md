# Вариационная проверка

Проверка выполнена независимыми слоями:

1. Static semantics: Ruff + strict mypy.
2. Dynamic behavior: 77 unit/API/property-style cases.
3. Branch coverage: 88.61%, выше gate 80%.
4. Dependency consistency: `pip check`.
5. Import/bytecode: `compileall`.
6. Concurrency variation: T1 при c=1/2/4/8/16.
7. Corruption variation: 10 families, severity identity и seeded determinism.
8. Document structure: prompt headings/fences, CSV parser, local links.
9. Supply-chain syntax will additionally be verified by GitHub Actions after push.

## Known non-variations

- нет second OS/container result;
- нет real-model CPU/GPU result;
- нет representative patient/slide cohort;
- нет multi-site/stain/microscope variation;
- нет clinical/human-factors study.

Именно поэтому final verdict остаётся NO-GO для production/clinical deployment,
несмотря на зелёные software gates.
