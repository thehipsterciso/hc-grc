# hc-grc — Reproducibility Guide

**This document explains how to reproduce any artifact from the hc-grc registry.** It covers
reading registry entries, pulling containers, setting seeds, running recorded commands, and
verifying results. It also clarifies what "byte-reproducible" means in this program and what it
does not cover.

---

## What reproducibility means in hc-grc

Reproducibility has two different meanings depending on the type of artifact:

### Computational artifacts: byte-reproducible

**Embeddings, statistics, classifiers, and numerical tables** are deterministic. Given the same
input data and random seed, they will produce byte-identical output hashes. These are verified by
recomputing them in the certified container and checking that the content hash matches the
recorded value.

**This covers:** S3 method validation results, S5 embeddings, S6 instrument validity metrics, S7
statistical findings, dimensionality estimates, cluster assignments, any numerical output.

### LLM-produced artifacts: transcript-reproducible

**Text produced by LLM agents** (e.g., adversary reviews, stance synthesis, research narratives) is
not deterministic. The same agent with the same inputs will produce *slightly different* text on
each run due to sampling in the model. These artifacts are reproducible in the sense that we can
inspect the **full reasoning transcript** and the **adversary certificate** that accompanied it.

**This covers:** agent reviews, analyses, writing, reasoning chains. They are reproducible by
reading the conversation history and the certificate, not by recomputing to a hash match.

**Single source of truth:** For LLM artifacts, the transcript and the certificate (signed by the
same-discipline adversary) *are* the reproducibility record. Byte-reproducibility of text would
require re-running the exact same LLM call under controlled temperature/seed, which defeats the
purpose of independent adversarial review.

---

## Reading a registry entry's reproduction block

Each registered artifact includes a **reproduction block** with these fields:

```yaml
reproduction:
  method: "computational" | "transcript"
  
  # For computational artifacts only:
  seed: <integer or null if deterministic without seed>
  container_digest: "sha256:abc123..."
  command: "python scripts/train-embeddings.py --framework scf --model ada ..."
  input_hashes:
    corpus: "sha256:..."
    config: "sha256:..."
  output_content_hash: "sha256:xyz789..."
  
  # For LLM artifacts:
  method: "transcript"
  transcript_ref: "transcripts/S7/nist-800-53/data-scientist-2026-06-15.md"
  certificate_ref: "certs/S7/nist-800-53/data-scientist-adv-2026-06-15.json"
```

**Key fields:**

- **seed:** Random seed used; `null` if the process is deterministic without seeding (rare).
- **container_digest:** The exact Docker image used (immutable reference by content hash, not tag).
- **command:** The exact command line that was run, with all arguments.
- **input_hashes:** Content hashes of input files, configs, and data. If any input hash differs,
  the results will differ.
- **output_content_hash:** The SHA256 hash of the artifact's content. After reproduction, you
  verify that your recomputed artifact matches this hash.
- **transcript_ref:** For LLM artifacts, the path to the agent's conversation transcript.
- **certificate_ref:** The certificate signed by the same-discipline adversary, with rejection
  reasons (if any) and final approval.

---

## How to reproduce a computational artifact

### Step 1: Clone the repository and check out the correct commit

```bash
git clone https://github.com/thehipsterciso/hc-grc.git
cd hc-grc
git checkout <commit-hash>
```

Every registry entry records the exact git commit it was created under.

### Step 2: Pull and verify the container by digest

Do **not** use the tag. Use the digest (content hash), which is immutable:

```bash
docker pull "sha256:abc123..." 2>&1 | grep "Pulling from" || \
  docker pull "ubuntu@sha256:abc123..."
```

Or, if the digest is recorded with a registry prefix:

```bash
docker pull "gcr.io/project/image@sha256:abc123..."
```

Verify the digest after pulling:

```bash
docker image inspect "sha256:abc123..." --format='{{.RepoDigests}}'
```

It should return the same digest.

### Step 3: Set random seeds

If the reproduction block specifies a seed, set it before running the command. Use the provided
helper script:

```bash
python scripts/repro/seeds.py --seed 42 --process-name embedding-training
```

This writes the seed to the environment or config file where the process expects it. Consult the
registry entry's `seed_location` field (e.g., `env:RNG_SEED` or `config:random_seed`).

Alternatively, set it directly:

```bash
export RNG_SEED=42
```

### Step 4: Run the recorded command

Run the exact command from the reproduction block, inside the container:

```bash
docker run --rm -v $(pwd):/work "sha256:abc123..." \
  bash -c "cd /work && python scripts/train-embeddings.py --framework scf --model ada ..."
```

Include all arguments exactly as recorded.

### Step 5: Verify the output hash

After the command completes, compute the SHA256 hash of the output artifact:

```bash
sha256sum <output-file>
```

Compare it to the `output_content_hash` in the registry:

```bash
echo "Expected: <value-from-registry>"
echo "Computed: $(sha256sum <output-file> | cut -d' ' -f1)"
```

If they match: **Reproduction successful.** The artifact is byte-reproducible.

If they differ: Check the reproduction block's `known_differences` field. Some artifacts (e.g.,
those involving floating-point precision across platforms or different BLAS libraries) may have
expected diffs. If the diff is not documented, this is a reproducibility failure — file an issue.

---

## How to reproduce an LLM artifact (transcript)

LLM artifacts are not re-run; they are inspected. This is by design: re-running would generate new
text, not reproduce the original.

### Step 1: Read the transcript

Locate the transcript file from the `transcript_ref`:

```bash
cat transcripts/S7/nist-800-53/data-scientist-2026-06-15.md
```

This contains the full conversation: the agent's reasoning, the adversary's questions, any
revisions, and the final artifact.

### Step 2: Read the certificate

Locate the certificate from `certificate_ref`:

```bash
cat certs/S7/nist-800-53/data-scientist-adv-2026-06-15.json
```

The certificate includes:
- **verdict:** ACCEPT or REJECT.
- **stance:** Which adversarial stance was used (e.g., `falsification-probe`).
- **findings:** What the adversary checked and found.
- **limitations:** Known limitations of the artifact.
- **model_info:** Model used (e.g., `sonnet`), adversary model (e.g., `opus`).
- **rounds:** How many revision cycles occurred.

### Step 3: Verify the chain of custody

- Check that the same-discipline adversary signed the certificate (e.g., `data-scientist-adversary`
  signed the `data-scientist`'s work).
- Check that the verdict is ACCEPT.
- If REJECT is recorded, the artifact is not in the registry — this should not happen. If it does,
  file an issue.

### Step 4: Evaluate against the certificate's findings

Read the adversary's recorded findings (e.g., "method selection justified", "threshold set before
data"), not the artifact in isolation. The certificate's approval is your reproducibility check.

---

## Dockerfile digest pinning

The `repro/Dockerfile` uses `FROM python:3.11-slim`. This tag is floating — Docker may resolve it
to a different image across builds as the upstream image is patched.

**The Dockerfile must be pinned by digest before first production use.** An unpinned Dockerfile
means `docker build` can produce a different image on different days, which breaks byte-level
reproducibility for all computational artifacts.

### Pinning process

Run the `pin-docker-digest` GitHub Actions workflow (`.github/workflows/pin-docker-digest.yml`).
It is a manual `workflow_dispatch` workflow that:

1. Pulls the current `python:3.11-slim` image.
2. Retrieves its content-addressable digest (`sha256:...`).
3. Opens a PR that replaces the `FROM` line with `FROM python:3.11-slim@sha256:<digest>`.

Review the PR, verify the digest against the Docker Hub manifest, and merge. The pin is a
deliberate human action — do not automate merging the pin PR.

To do this manually instead:

```bash
docker pull python:3.11-slim
docker inspect python:3.11-slim --format='{{index .RepoDigests 0}}'
# Returns: python@sha256:<digest>
# Edit repro/Dockerfile: replace FROM python:3.11-slim with FROM python:3.11-slim@sha256:<digest>
```

After pinning, if you update the pin (e.g., after a security patch), recompute the smoke hash:

```bash
docker build -t hc-grc-repro repro/
docker run --rm hc-grc-repro bash repro/smoke/run_trivial.sh | sha256sum
# Update repro/smoke/expected_output.sha256
```

---

## Special case: P0 smoke test reproduction

**P0** is the autonomy harness setup and self-test. Reproducing it verifies that the entire
system boots and accepts/rejects artifacts correctly.

### Prerequisites

```bash
git clone https://github.com/thehipsterciso/hc-grc.git
cd hc-grc
git checkout main  # or the P0 commit
```

### Clone and verify prerequisites

1. **Docker:** Running and authenticated to any needed registries.
2. **Python:** 3.11+.
3. **Claude Code CLI:** Installed and authenticated.
4. **Git:** Authenticated to GitHub.

### Run the P0 test

```bash
python scripts/p0-smoke-test.py
```

This script:
1. Spins up the coordinator.
2. Spawns the `agent-organizer`.
3. Runs a trivial task (e.g., "count the number of markdown files in `docs/`").
4. Spawns the paired adversary (`first-principles-thinking-adversary`, `falsification-probe`
   stance).
5. Tests accept flow (good artifact accepted, certificate generated).
6. Tests reject flow (seeded-bad artifact rejected, reason recorded).
7. Checks that a rejected artifact is not registered.
8. Prints a summary.

Expected output:

```
P0 Smoke Test Results
====================
✓ Coordinator spawned
✓ Agent organizer configured roster
✓ Good artifact: ACCEPTED (certificate at ...)
✓ Bad artifact: REJECTED (reason: unsupported claim without evidence)
✓ Registry contains 1 artifact (rejected artifact not registered)
✓ Certificate ledger contains 2 entries (accept + reject)

All checks passed. System is autonomous and self-rejecting.
```

### Troubleshooting P0

| Issue | Check |
|-------|-------|
| "Coordinator failed to spawn" | Docker running? Claude Code CLI authenticated? |
| "Agent not found" | Run `scripts/sync-agents.sh` to copy agents to `.claude/agents/`. |
| "Certificate rejected" | Check `.claude/error-coordinator/ledger.json` for the rejection reason. |
| "Registry empty" | Check that the ACCEPT verdict was signed by an adversary, not conditionally approved. |

---

## Distinction: correlated vs independent evidence

**Important:** When reproducing findings, note whether they share inputs:

- **Independent computational artifacts:** Different input data, different methods, different
  stages. Reproduction of both strengthens evidence.
- **Correlated artifacts:** Share the same embedding (S5) or same framework corpus (S4). They are
  robust *within that embedding/corpus* but not independently verified. The certificate carries
  this as a limitation.
- **Cross-framework replication (S9):** Different frameworks, same pre-registration, independent
  method choices. This is the strongest reproducibility check.

The registry entry includes a `correlated_artifacts` field that lists other findings that share
inputs with this one.

---

## Reproducibility checklist

For any artifact you reproduce:

- [ ] Git commit matches the registry entry.
- [ ] Container digest pulled and verified.
- [ ] Random seed set (if applicable) and recorded.
- [ ] Command run exactly as specified.
- [ ] Output hash matches (for computational) or certificate is signed (for LLM).
- [ ] No undocumented differences.
- [ ] For findings: correlated artifacts are noted, not called independent.

If any check fails, the artifact is not reproducible — file an issue with the registry entry's
ID and the failure details.

---

## Reproducibility is not validation

Reproducibility means you can re-create the artifact. It does not mean the artifact is correct or
significant. That is what the adversary certificate does: it certifies that the artifact was
produced under stated conditions, by stated actors, with stated limitations. The certificate is
your quality gate, not the hash.

Read the certificate first. If it says ACCEPT with no significant limitations, reproduction will
verify that you trust the same things the adversary trusted.
