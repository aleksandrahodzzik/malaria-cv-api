# Варианты controlled model storage

## Критерии и веса

```text
Integrity       0.25
Access control  0.20
Offline         0.15
Rollback        0.15
Auditability    0.15
Cost            0.10
```

Оценки от 1 до 5; больше — лучше.

| Option | Integrity | Access | Offline | Rollback | Audit | Cost | Weighted score |
|---|---:|---:|---:|---:|---:|---:|---:|
| A. Private Hugging Face + immutable revision | 4 | 5 | 3 | 5 | 5 | 4 | 4.35 |
| B. Signed object storage + SHA-256 manifest | 5 | 5 | 5 | 4 | 5 | 3 | 4.65 |
| C. Signed OCI model artifact/layer | 5 | 5 | 5 | 5 | 5 | 3 | 4.80 |
| D. Internal model registry | 5 | 5 | 4 | 5 | 5 | 2 | 4.55 |
| E. Read-only local mounted directory | 4 | 4 | 5 | 3 | 3 | 5 | 3.95 |

## Решение

Target для container deployment:

```text
C. signed OCI model artifact
+ immutable digest
+ separate signed model manifest
+ local-only runtime
```

Допустимый минимальный research/development вариант:

```text
E. read-only mounted artifact
+ SHA-256 manifest
+ license record
+ model card
+ explicit version directory
```

Private Hugging Face подходит как source registry только если CI:

1. получает artifact по immutable commit SHA;
2. проверяет expected file list и SHA-256;
3. не включает `trust_remote_code`;
4. создаёт release manifest/SBOM;
5. production runtime не имеет implicit network fallback.

## Minimum manifest

```text
model_id
revision/digest
artifact files
SHA-256 per file
architecture
processor contract
id2label/label2id
license
training provenance
evaluation provenance
known limitations
approver
approval timestamp
rollback target
```
