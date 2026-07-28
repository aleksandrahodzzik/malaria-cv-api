# Upload threat matrix

| Threat/input | Boundary | Test/evidence | Status | Residual control |
|---|---|---|---|---|
| Oversized HTTP body with Content-Length | ASGI middleware | early 413 test | CONTROLLED | reverse proxy should duplicate limit |
| Streamed body without Content-Length | ASGI receive wrapper | chunked test | CONTROLLED | slow-read timeout external |
| False small Content-Length | ASGI receive wrapper | code path counts actual bytes | CONTROLLED | proxy parser consistency |
| Encoded file > limit | route chunk reader | 413 test | CONTROLLED | peak copy remains bounded |
| Empty file | route | 400 test | CONTROLLED | — |
| MIME spoof | worker decode | PNG declared JPEG rejected | CONTROLLED | decoded format is authority |
| Filename extension mismatch | display metadata | PNG named `.jpg` accepted | DELIBERATE | extension never selects decoder |
| Corrupt image | Pillow verify | corrupt test | CONTROLLED | safe public error |
| Truncated JPEG | Pillow verify/load | truncated fixture | CONTROLLED | — |
| Huge dimensions/decompression bomb | pixel area before load | patched pixel-limit test | CONTROLLED | Pillow/library advisories still apply |
| Animated/multi-frame WEBP | frame count | animated fixture | CONTROLLED | rejected |
| Grayscale | mode allowlist + RGB convert | parameterized test | CONTROLLED | training equivalence still model-specific |
| RGBA/alpha | mode allowlist + RGB convert | parameterized test | CONTROLLED | alpha compositing semantics not externally validated |
| CMYK | mode allowlist | CMYK fixture | CONTROLLED | rejected fail-closed |
| 16-bit/unusual mode | mode allowlist | static branch | CONTROLLED/PARTIAL | add explicit fixtures when approved input contract exists |
| EXIF orientation | metadata | code inspection | OPEN/MEDIUM | no auto-rotation; define model preprocessing contract |
| ICC profile/metadata | pixel processor path | code inspection | PARTIAL | metadata not sent to model; decoded color may vary |
| Path traversal filename | sanitizer | Windows/Unix path test | CONTROLLED | filename is display-only |
| Unicode filename | Unicode sanitizer | Cyrillic fixture | CONTROLLED | bounded length |
| Temporary file cleanup | `finally: await file.close()` | code/test path | CONTROLLED | process crash cleanup delegated to OS |
| Many tiny multipart parts | parser default max 1000 | Starlette source inspection | OPEN/MEDIUM | proxy/request parser part-count policy |
| Temporary disk exhaustion | 1 MiB spool threshold | Starlette source inspection | OPEN/HIGH | isolated tmpfs/quota and global admission |
| Concurrent memory amplification | bytearray/bytes/PIL/tensor | analytical model | OPEN/HIGH | global body/inference admission |
| Slow upload | server/proxy | no timeout evidence | OPEN/HIGH | ingress read/header timeout |
| Polyglot/trailing bytes | Pillow verify | partial | OPEN/LOW | stronger parser/content policy if threat model requires |

## Memory model

Для encoded payload размера `B`:

```text
route_copy_peak ≈ spool(B) + bytearray(B) + bytes(B)
```

Перед inference `bytearray` удаляется, но кратковременный peak может достигать
примерно `3B` плюс parser overhead. Далее:

```text
decoded_RGB ≈ width * height * 3
tensor ≈ batch * channels * Hmodel * Wmodel * bytes_per_element
```

При `N` параллельных uploads:

```text
UploadPeak ≈ N * (3B + decoded_RGB + tensor) + parser/framework overhead
```

Semaphore ограничивает inference, но не весь upload/parsing этап. Поэтому
public deployment требует global request admission до приёма больших bodies.
