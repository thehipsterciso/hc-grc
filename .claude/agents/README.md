# .claude/agents — runtime agent set (generated)

Claude Code auto-loads project subagents from this directory. These `.md` files are **generated**,
not hand-edited. Do not edit them here.

- **Producers / orchestration / backstop** (~28) are copied from the pinned framework submodule:
  `upstream/awesome-claude-code-subagents/categories/**`.
- **Adversaries** (8) are copied from `agents/adversarial-review/` (the native, human-readable home).

Regenerate after updating the submodule or editing an adversary:

```bash
bash scripts/sync-agents.sh
```

## Alternative: install the framework as a plugin marketplace

Instead of the copied producer agents, you can use the framework natively (it ships as the
`voltagent-subagents` marketplace):

```
/plugin marketplace add ./upstream/awesome-claude-code-subagents
/plugin install voltagent-meta voltagent-data-ai voltagent-research voltagent-dev-exp voltagent-biz voltagent-qa-sec
```

If you do that, delete the producer copies here to avoid duplicate names (keep the `*-adversary.md`
files — those are ours and not in the marketplace).
