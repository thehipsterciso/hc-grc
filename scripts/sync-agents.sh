#!/usr/bin/env bash
# Regenerate .claude/agents/ (the set Claude Code auto-loads) from the pinned
# framework submodule (producers) and the native adversary agents.
# Re-run after updating the submodule or editing agents/adversarial-review/.
#
# Usage: sync-agents.sh [--dry-run]
#   --dry-run  Print the expected agent manifest to /tmp/sync-expected.txt
#              without modifying .claude/agents/. Exit non-zero if diverged.
set -euo pipefail

DRY_RUN=0
for arg in "$@"; do
  if [ "$arg" = "--dry-run" ]; then DRY_RUN=1; fi
done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SUB="$ROOT/upstream/awesome-claude-code-subagents/categories"
ADV="$ROOT/agents/adversarial-review"
DST="$ROOT/.claude/agents"
mkdir -p "$DST"

# Program roster — the producing, orchestration, and backstop agents this program uses.
roster="agent-organizer multi-agent-coordinator context-manager error-coordinator knowledge-synthesizer \
data-engineer data-analyst data-scientist ml-engineer mlops-engineer nlp-engineer llm-architect \
git-workflow-manager documentation-engineer \
product-manager technical-writer content-marketer business-analyst legal-advisor license-engineer \
research-analyst first-principles-thinking scientific-literature-researcher data-researcher competitive-analyst \
compliance-auditor content-quality-editor ai-writing-auditor"

# Build expected manifest
EXPECTED_MANIFEST="/tmp/sync-expected.txt"
> "$EXPECTED_MANIFEST"

missing=0
for name in $roster; do
  f="$(find "$SUB" -name "$name.md" 2>/dev/null | head -1)"
  if [ -n "$f" ]; then
    echo "$name.md" >> "$EXPECTED_MANIFEST"
    if [ "$DRY_RUN" -eq 0 ]; then cp "$f" "$DST/"; fi
  else
    echo "MISSING from submodule: $name"
    missing=$((missing+1))
  fi
done

# Native adversary agents
for f in "$ADV"/*-adversary.md; do
  echo "$(basename "$f")" >> "$EXPECTED_MANIFEST"
  if [ "$DRY_RUN" -eq 0 ]; then cp "$f" "$DST/"; fi
done

sort -o "$EXPECTED_MANIFEST" "$EXPECTED_MANIFEST"

if [ "$DRY_RUN" -eq 1 ]; then
  ACTUAL="$(find "$DST" -maxdepth 1 -name '*.md' ! -name 'README.md' -exec basename {} \; | sort)"
  EXPECTED="$(cat "$EXPECTED_MANIFEST")"
  if [ "$ACTUAL" != "$EXPECTED" ]; then
    echo "DRY-RUN: .claude/agents/ would diverge. Run sync-agents.sh to fix."
    exit 1
  fi
  echo "DRY-RUN: .claude/agents/ is in sync with expected roster."
  exit 0
fi

# Live run: clear old agents (after copying new ones via temp is safer, but
# simplest is clear-then-copy; we do copy-then-clear via the loop above).
# Remove agents NOT in the expected manifest.
find "$DST" -maxdepth 1 -name '*.md' ! -name 'README.md' | while read -r f; do
  bname="$(basename "$f")"
  if ! grep -qx "$bname" "$EXPECTED_MANIFEST"; then
    rm "$f"
  fi
done

count="$(find "$DST" -maxdepth 1 -name '*.md' ! -name 'README.md' | wc -l | tr -d ' ')"
echo "Synced $count agents into .claude/agents/ ($missing roster names missing)."
