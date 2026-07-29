# Supply-chain audit

## Verified improvements

- GitHub Actions имеют `permissions: contents: read`;
- checkout не сохраняет credentials;
- checkout/setup-python/upload-artifact pinned to full immutable SHAs;
- job timeout, concurrency cancellation и short artifact retention;
- CycloneDX SBOM и wheelhouse SHA manifest существуют;
- remote production model требует immutable revision.

Проверенные 2026-07-28 action commits:

- `actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803`;
- `actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1`;
- `actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f`.

## Remaining STOP conditions

- production model, license, checksum and approved registry absent;
- dependency inputs pinned by versions/constraints but not all hashes;
- base image digest absent;
- no signed container/attestation policy;
- no automated secret scan/container scan/model manifest verification.

## Required chain

`source commit -> hash lock -> tested model revision+sha256 -> container digest
-> SBOM -> provenance attestation -> signature -> deployment revision`.

Prediction audit record must reference aliases/checksums, never patient data or
local paths.
