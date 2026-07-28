# Dataset Datasheet — NIH/NLM reference resources

Дата проверки: 2026-07-28
Назначение: reference only; связь с текущей моделью не установлена.

## 1. Cropped cell classification dataset

Официальный NLM index содержит:

- `cell_images.zip`, 353,452,851 bytes;
- `patientid_cellmapping_parasitized.csv`;
- `patientid_cellmapping_uninfected.csv`;
- reference classification code.

Источник:
https://data.lhncbc.nlm.nih.gov/public/Malaria/

Peer-reviewed первоисточник Rajaraman et al. сообщает:

- 27,558 segmented cell images;
- 13,779 parasitized и 13,779 uninfected;
- Giemsa-stained thin smears;
- 150 P. falciparum-infected и 50 healthy patients;
- Chittagong Medical College Hospital, Bangladesh;
- smartphone camera through microscope;
- expert annotation at MORU, Bangkok;
- de-identification и NLM IRB#12972;
- patient-level five-fold cross-validation в исследовании;
- resized model inputs в зависимости от architecture.

Источник:
https://pmc.ncbi.nlm.nih.gov/articles/PMC5907772/

### Важное ограничение

Статья описывает конкретное исследование и его split. Публичный ZIP и mapping
files требуют отдельного snapshot/checksum audit перед повторным
использованием. Их наличие не доказывает split неизвестной Hugging Face модели.

## 2. Whole thin-smear detection dataset

Это отдельный resource, не `cell_images.zip`.

Официальный ReadMe сообщает:

- 193 patients;
- 5 images per patient;
- Giemsa-stained thin smears;
- P. falciparum patients и healthy controls;
- smartphone acquisition;
- expert annotation;
- de-identification;
- NLM IRB#12972;
- RGB, 5312 × 2988;
- polygon и point annotation sets;
- patient-directory organization.

Источник:
https://data.lhncbc.nlm.nih.gov/public/Malaria/NIH-NLM-ThinBloodSmearsPf/ReadMe.pdf

Этот resource подходит для исследования detection/segmentation, но не является
готовым доказательством для текущего single-cell classifier.

## 3. Datasheet fields

| Field | Cropped cells | Whole thin smear | Status |
|---|---|---|---|
| Owner/archive | NLM/NIH | NLM/NIH | VERIFIED |
| Geography | Bangladesh | Bangladesh | VERIFIED |
| Site | Chittagong Medical College Hospital | same | VERIFIED |
| Smear/stain | Giemsa thin smear | Giemsa thin smear | VERIFIED |
| Species | P. falciparum positives | P. falciparum | VERIFIED |
| Patient count | 150 infected + 50 healthy in article | 193 in ReadMe | VERIFIED per distinct resource |
| Cell count | 27,558 | not a cell-crop dataset | VERIFIED |
| Whole images | upstream images not packaged as same unit | 5 per patient | PARTIAL |
| Expert annotation | reported | reported | VERIFIED |
| Number of annotators | one expert slide reader reported | one expert reported | PARTIAL |
| Inter-rater agreement | not reported in reviewed evidence | not reported | UNKNOWN |
| Adjudication | not reported | not reported | UNKNOWN |
| Consent details | not established by reviewed artifacts | not established | UNKNOWN |
| IRB | NLM IRB#12972 | NLM IRB#12972 | VERIFIED |
| De-identification | reported | reported | VERIFIED |
| Exact data license | not established from index/article alone | ReadMe requests attribution | UNKNOWN/PARTIAL |
| Commercial permission | not established | not established | UNKNOWN |
| Collection dates | not established | not established | UNKNOWN |
| Age/sex/subgroups | not established | not established | UNKNOWN |
| Prevalence | constructed balanced cell benchmark | patient mix differs | NOT deployment prevalence |
| Immutable checksum | not recorded in project | not recorded | MISSING |

## 4. Applicability

The cropped dataset is relevant to task A, but external applicability remains
limited by one geography/site, one stain family, P. falciparum focus, expert
segmentation/crops and artificial 50/50 cell balance.

It is not direct evidence for:

- whole-slide inference;
- thick-smear workflow;
- parasite density;
- other species;
- new camera/stain/site;
- patient diagnosis;
- current unknown model.
