# Математика агрегации

## Beta-binomial

Для `K | p ~ Binomial(m,p)` и `p ~ Beta(alpha,beta)`:

- `E[K] = m * alpha/(alpha+beta)`;
- `Var[K] = m*p_bar*(1-p_bar)*(1+(m-1)rho)`;
- `rho = 1/(alpha+beta+1)`.

Множитель `1+(m-1)rho` показывает, почему клетки одного слайда нельзя считать
независимыми пациентами. Утилита `beta_binomial_moments` проверяет параметры и
возвращает moments для дизайна исследования.

## Минимальное число клеток

При независимом обнаружении заражённой клетки с вероятностью `p_detect`,
нижняя планировочная граница:

`m >= log(1-target_probability) / log(1-p_detect)`.

Это не clinical guarantee: корреляция, неполное покрытие и detector miss
увеличивают необходимый объём. Итоговый минимум должен следовать из
patient-level исследования и WHO-compatible acquisition protocol.

## Acceptance gates

- пациент является единицей resampling;
- все клетки/поля одного пациента принадлежат одному split;
- есть minimum field/cell coverage и quality rejection;
- оценены patient-level Se/Sp с cluster bootstrap CI;
- агрегатор и threshold заморожены до test set;
- отчёт содержит low-parasitemia strata и species/stage limitations.
