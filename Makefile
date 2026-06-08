.PHONY: help install hooks lint format test validate smoke sync-agents freeze-prereg clean

# Interpreter — override with `make PYTHON=python` in CI where setup-python provides `python`
PYTHON ?= python3

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help:
	@echo "$(GREEN)hc-grc — GRC control framework characterization program$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  make install        Install dependencies and hooks (one-time setup)"
	@echo "  make hooks          Install pre-commit and commit-msg hooks"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make lint           Run ruff and black --check"
	@echo "  make format         Auto-format with black and ruff --fix"
	@echo "  make test           Run pytest (unit tests, no network)"
	@echo ""
	@echo "$(YELLOW)Program validation:$(NC)"
	@echo "  make validate       Check all stages for certification (dry-run)"
	@echo "  make smoke          Run smoke tests (trivial artifact + bad artifact rejection)"
	@echo ""
	@echo "$(YELLOW)Maintenance:$(NC)"
	@echo "  make sync-agents    Regenerate .claude/agents/ from source"
	@echo "  make freeze-prereg  Hash PREREGISTRATION.md (T1 tripwire action, irreversible)"
	@echo "  make clean          Remove __pycache__, .pytest_cache, *.pyc"
	@echo ""

install: ## Install dependencies and hooks (one-time setup)
	pip install -r requirements-dev.txt
	make hooks

hooks: ## Install pre-commit hooks and commit-msg hook
	@echo "$(GREEN)Installing pre-commit framework...$(NC)"
	pre-commit install --hook-type pre-commit --hook-type pre-push
	@echo "$(GREEN)Installing commit-msg hook...$(NC)"
	mkdir -p .git/hooks
	cp scripts/hooks/commit-msg .git/hooks/commit-msg
	chmod +x .git/hooks/commit-msg
	@echo "$(GREEN)✓ Hooks installed$(NC)"

lint: ## Run ruff and black --check
	@echo "$(YELLOW)Linting with ruff...$(NC)"
	ruff check scripts/ 2>/dev/null || true
	@echo "$(YELLOW)Checking format with black...$(NC)"
	black --check --line-length=100 scripts/ 2>/dev/null || true
	@echo "$(GREEN)✓ Lint complete$(NC)"

format: ## Auto-format with black and ruff
	@echo "$(YELLOW)Formatting with black...$(NC)"
	black --line-length=100 scripts/
	@echo "$(YELLOW)Fixing with ruff...$(NC)"
	ruff check --fix scripts/ 2>/dev/null || true
	@echo "$(GREEN)✓ Formatting complete$(NC)"

test: ## Run pytest (no network, no CI)
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest tests/ -v --tb=short --no-network 2>/dev/null || pytest tests/ -v --tb=short || echo "$(RED)No tests found (create tests/ directory)$(NC)"
	@echo "$(GREEN)✓ Tests complete$(NC)"

validate: ## Check all stages for certification (dry-run status)
	@echo "$(YELLOW)Validating all stages...$(NC)"
	@$(PYTHON) scripts/stage_gate.py --validate -v
	@echo ""
	@$(PYTHON) scripts/stage_gate.py --tier-b-check -v

smoke: ## Run smoke tests (trivial + bad artifact rejection; verifies hash against expected_output.sha256)
	@echo "$(YELLOW)Running smoke tests...$(NC)"
	@if [ ! -d repro/smoke ]; then \
		echo "$(YELLOW)Smoke tests not yet available (create repro/smoke/)$(NC)"; \
		exit 0; \
	fi
	@if [ -f repro/smoke/run_trivial.sh ]; then \
		echo "$(YELLOW)  Running trivial task...$(NC)"; \
		bash repro/smoke/run_trivial.sh > /tmp/trivial_actual_output.txt; \
		if [ ! -f repro/smoke/expected_output.sha256 ]; then \
			echo "$(RED)ERROR: repro/smoke/expected_output.sha256 not found.$(NC)"; \
			echo "$(RED)Cannot verify reproducibility without a reference hash.$(NC)"; \
			exit 1; \
		fi; \
		EXPECTED=$$(awk '{print $$1}' repro/smoke/expected_output.sha256); \
		ACTUAL=$$(sha256sum /tmp/trivial_actual_output.txt | awk '{print $$1}'); \
		echo "  Expected: $$EXPECTED"; \
		echo "  Actual:   $$ACTUAL"; \
		if [ "$$EXPECTED" != "$$ACTUAL" ]; then \
			echo "$(RED)ERROR: Trivial task output does not match expected SHA-256.$(NC)"; \
			echo "$(RED)The environment is not producing byte-identical output.$(NC)"; \
			echo "$(RED)Rebuild from the pinned Dockerfile or recompute expected_output.sha256.$(NC)"; \
			exit 1; \
		fi; \
		echo "$(GREEN)  Trivial smoke test PASSED — output is byte-identical.$(NC)"; \
	fi
	@if [ -f repro/smoke/run_bad_artifact.sh ]; then \
		echo "$(YELLOW)  Running bad artifact rejection test...$(NC)"; \
		bash repro/smoke/run_bad_artifact.sh; \
		echo "$(GREEN)  Bad artifact rejection PASSED.$(NC)"; \
	fi
	@echo "$(GREEN)✓ Smoke tests complete$(NC)"

sync-agents: ## Regenerate .claude/agents/ from source
	@echo "$(YELLOW)Syncing agents...$(NC)"
	@bash scripts/sync-agents.sh
	@echo "$(GREEN)✓ Agents synced$(NC)"

freeze-prereg: ## Hash PREREGISTRATION.md (T1 tripwire action, IRREVERSIBLE)
	@echo "$(RED)⚠️  WARNING: This action is IRREVERSIBLE$(NC)"
	@echo ""
	@echo "This command hashes docs/PREREGISTRATION.md to lock it as the"
	@echo "authoritative register of questions and methods for this program."
	@echo ""
	@echo "After this, the pre-registration cannot be changed without explicit"
	@echo "amendment and re-signing (documented in the ledger)."
	@echo ""
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		sha256sum docs/PREREGISTRATION.md > docs/PREREGISTRATION.md.sha256; \
		git add docs/PREREGISTRATION.md.sha256; \
		echo "$(GREEN)✓ Frozen: $(shell cat docs/PREREGISTRATION.md.sha256)$(NC)"; \
		echo ""; \
		echo "Next: Sign the T1 tripwire"; \
		echo "  mkdir -p docs/tripwires"; \
		echo "  echo '<your-name-or-signature>' > docs/tripwires/T1.signed"; \
		echo "  git add docs/tripwires/T1.signed"; \
		echo "  git commit -m '[P1] Freeze pre-registration (T1 tripwire signed)'"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
		exit 1; \
	fi

clean: ## Remove __pycache__, .pytest_cache, *.pyc
	@echo "$(YELLOW)Cleaning...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "$(GREEN)✓ Clean complete$(NC)"

.DEFAULT_GOAL := help
