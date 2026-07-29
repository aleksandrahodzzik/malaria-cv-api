# Фаза 16 — clinical workflow и human factors

## Current intended use

Research/educational prototype для классификации заранее вырезанной клетки.
Не screening, triage, CDS или autonomous diagnosis. Intended population,
microscope, stain, acquisition protocol и обученный оператор не определены.

## Safe workflow target

1. Авторизованный обученный оператор регистрирует specimen/slide pseudonym.
2. Acquisition QC подтверждает stain, optics, focus, scale и coverage.
3. Детектор/сегментатор выдаёт cells и quality flags.
4. Classifier допускает отказ при uncertainty/OOD.
5. Locked aggregator формирует slide screening result только при minimum count.
6. Специалист просматривает positives, low-quality и rejected cases.
7. Patient result связывается с reference laboratory workflow, а не выводится
   из одной клетки.
8. Audit event фиксирует версии без image/PII.
9. Ошибка/неопределённость ведёт к повторному образцу или reference method.

## Automation bias controls

- термин `predicted_cell_class`, не `diagnosis`;
- показывать limitations и `requires_review` рядом с result;
- confidence не называть вероятностью болезни;
- не использовать цвет/анимацию как единственный сигнал;
- показывать quality/uncertainty отдельно;
- human override требует reason, но не блокируется алгоритмом;
- измерять agreement, override quality, time-to-review и missed-error rate.
