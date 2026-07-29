# Mock gap analysis

Mocks могут скрыть:

- отсутствие model repository/weights/license;
- инвертированные `id2label`;
- несовместимый processor/input size/normalization;
- несовместимость transformers/PyTorch;
- pickle/remote-code risk;
- реальную latency, native threads и memory amplification;
- numerical drift между платформами;
- domain shift и clinical false negatives.

Поэтому green CI означает «software contract verified», но не
«model/clinical system verified». Real-model smoke обязан быть отдельным
release gate после утверждения artifact manifest.
