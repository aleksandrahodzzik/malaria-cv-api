# Release lineage contract

Каждый release manifest должен содержать:

- source repository + commit SHA;
- CI run ID and immutable action SHAs;
- Python ABI/platform;
- requirements lock digest and SBOM digest;
- model registry, immutable revision, format, SHA-256, license decision;
- preprocessing/calibration schema version and checksum;
- container digest, signature and provenance statement;
- deployment environment/revision/time;
- validation report and approved intended use;
- rollback target.

Startup должен fail closed при несовпадении model/config manifest.
