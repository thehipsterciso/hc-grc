# Transcript: documentation-engineer — Arbiter Agent Definition
**Date:** 2026-06-08
**Stage:** P0
**Agent:** documentation-engineer/claude-sonnet-4-6@hc-macbook-pro.local (Tier-1 producer)
**Task:** Create agents/adversarial-review/arbiter.md
**Status:** COMPLETED. PENDING ADVERSARY REVIEW (documentation-engineer-adversary/claude-opus-4-8@hc-macbook-pro.local).

## Files Written
- `agents/adversarial-review/arbiter.md`

## Definition of Done
1. Trigger condition (3 rounds) defined ✓
2. Input specification defined ✓
3. Decision protocol (assess each defect, PASS/REJECT, no new defects) defined ✓
4. Hard constraint override rule present ✓
5. Certificate format with deadlock_summary defined ✓
6. Model assignment: claude-opus-4-8, fresh context ✓

## Summary
Trigger: 3 rounds without resolution. Inputs: original artifact + DoD, all 3 producer submissions, all 3 adversary certificates. Protocol: independently assess each defect as blocking or defensible — PASS if all waived, REJECT forces producer to choose a different approach. Hard constraints (CLAUDE.md) cannot be waived. Certificate includes DEADLOCK_SUMMARY with WAIVE|UPHOLD disposition per defect.
