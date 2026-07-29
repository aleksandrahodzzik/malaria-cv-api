# Security threat model — canonical

## Highest scenarios

1. Anonymous valid-image flood exhausts inference queue/CPU/RAM.
2. Compressed/malformed images amplify decoder resources.
3. Mutable or compromised model/dependency changes labels/code.
4. Querying extracts model behavior.
5. Filename/exception/token/image leaks into telemetry.
6. Adversarial/domain-shift input yields confident unsafe result.

## Existing controls

Body/pixel/format limits, bounded inference, safe errors/request IDs,
allowlisted JSON logs, no-store, CORS opt-in, non-root container and full-SHA
CI actions.

## Missing controls

Gateway authentication/authorization, per-principal/global quotas, container
resource/security context, full hash lock/base digest, artifact
signature/attestation, protected metrics/alerts and model QC/OOD rejection.

Full STRIDE and attack scenarios: `phase13/`.
