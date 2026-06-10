# Reproducibility

Artifacts supporting independent replication of HC-GRC analyses.

Populated by the Provenance Agent and run manifests. See:
- `infrastructure/RUN_MANIFEST.md` — per-run execution record schema
- `infrastructure/PROVENANCE_MODEL.md` — W3C PROV-DM mapping and PROV-O serialization
- `protocol/PREREGISTRATION_LEDGER.md` — timestamped pre-registration record

Per-run provenance artifacts (manifest.json, PROV-O .ttl) are written to `runs/<run_id>/` at execution time.
