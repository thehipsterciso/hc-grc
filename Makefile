PYTHON := python3.11
VENV   := .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

.DEFAULT_GOAL := help

.PHONY: help venv install test lint format clean acquire eda reproduce check-docs

help:
	@echo "Available targets:"
	@echo "  venv        Create virtual environment"
	@echo "  install     Install pinned dependencies"
	@echo "  test        Run all tests"
	@echo "  lint        Run ruff linter"
	@echo "  format      Run black formatter"
	@echo "  clean       Remove generated files (not raw data)"
	@echo "  acquire     Run data acquisition scripts"
	@echo "  eda         Run EDA notebook"
	@echo "  reproduce   Full pipeline: acquire → process → analyze"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

test:
	$(PY) -m pytest tests/ -v --tb=short

lint:
	$(VENV)/bin/ruff check src/ tests/

format:
	$(VENV)/bin/black --line-length 100 src/ tests/ notebooks/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf data/interim/* data/processed/*
	@echo "Raw data preserved. Experiments and models preserved."

acquire:
	$(PY) src/data/acquire.py

eda:
	$(VENV)/bin/jupyter nbconvert --to notebook --execute notebooks/02_eda.ipynb \
		--output notebooks/02_eda_executed.ipynb

reproduce: acquire
	$(PY) src/data/process.py
	$(MAKE) eda
	@echo "Reproduce complete. Check reports/ for outputs."

check-docs:
	@echo "Running documentation drift check against working tree changes..."
	@git diff --name-only origin/main...HEAD > /tmp/changed_files.txt 2>/dev/null || \
		git diff --name-only HEAD > /tmp/changed_files.txt
	@CHANGED_FILES_PATH=/tmp/changed_files.txt python3 scripts/check_doc_drift.py
