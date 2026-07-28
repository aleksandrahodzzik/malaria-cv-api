# Hugging Face HTTP evidence

Проверено: 2026-07-28, Europe/Warsaw
Исторический model ID: `trpakov/vit-malaria-classification`.

## Exact repository

Все запросы выполнялись без Hugging Face credentials.

| URL | HTTP | Exit | Interpretation |
|---|---:|---:|---|
| `https://huggingface.co/api/models/trpakov/vit-malaria-classification` | 401 | 0 | Public metadata недоступна |
| `https://huggingface.co/trpakov/vit-malaria-classification` | 401 | 0 | Public model page недоступна |
| `.../resolve/main/config.json` | 401 | 0 | Config недоступен |
| `.../resolve/main/preprocessor_config.json` | 401 | 0 | Processor config недоступен |
| `.../resolve/main/model.safetensors` | 401 | 0 | Safetensors недоступен |
| `.../resolve/main/pytorch_model.bin` | 401 | 0 | PyTorch binary недоступен |
| `.../resolve/main/README.md` | 401 | 0 | Model card недоступна |
| `.../resolve/main/.gitattributes` | 401 | 0 | LFS metadata недоступна |

Существенный response:

```text
HTTP/1.1 401 Unauthorized
X-Error-Message: Invalid username or password.
WWW-Authenticate: Bearer realm="Authentication required"

{"error":"Invalid username or password."}
```

`401` не позволяет без credentials различить:

- private repository;
- gated repository;
- скрытый/удалённый repository;
- поведение API для отсутствующего repo.

Поэтому корректный вывод:

```text
NOT PUBLICLY REPRODUCIBLE
```

а не абсолютное историческое утверждение «репозиторий никогда не существовал».

## Public author list

Команда:

```text
curl https://huggingface.co/api/models?author=trpakov&limit=100&full=true
```

Результат `HTTP 200` содержит только:

```text
trpakov/vit-face-expression
  sha=ef0bc6fc34241b6587e7e009e7711357be28c024
  license=apache-2.0

trpakov/vit-pneumonia
  sha=5fad4126599713ea8ca0663ad829dfae02c61138
  license=apache-2.0
```

Вторая вариация через официальный `huggingface_hub.HfApi`:

```text
['trpakov/vit-face-expression', 'trpakov/vit-pneumonia']
```

Исторически заявленный malaria repository в public author list отсутствует.
Нельзя использовать pneumonia или face-expression model как замену.

## Real loader probe

Команда:

```text
MalariaClassifierService(
  "trpakov/vit-malaria-classification"
).load_model()
```

Результат:

```text
ExitCode: 1
DurationMs: 9731
RepositoryNotFoundError / 401 Unauthorized
preprocessor_config.json unavailable
RuntimeError: Model initialization failure
```

Весовые файлы не скачивались.

## Local cache

Не обнаружены:

```text
%USERPROFILE%\.cache\huggingface\hub
%LOCALAPPDATA%\huggingface\hub
workspace\.cache\huggingface\hub
workspace\models
*.safetensors
*.pt
*.onnx
```

## Verdict

```text
public page            = NOT AVAILABLE
public API metadata    = NOT AVAILABLE
author public listing  = DOES NOT CONTAIN MODEL
config                 = UNKNOWN/UNAVAILABLE
processor config       = UNKNOWN/UNAVAILABLE
weights                = UNKNOWN/UNAVAILABLE
license                = UNKNOWN
model card             = UNKNOWN
revision               = UNKNOWN
checksum               = NOT COMPUTABLE
local cache            = ABSENT
real loader            = FAIL
```
