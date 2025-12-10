PYTHON ?= python3
VENV ?= .venv

.PHONY: install init-db run demo-db test lint

install:
\t$(PYTHON) -m venv $(VENV)
\t$(VENV)/bin/pip install -U pip
\t$(VENV)/bin/pip install -r requirements.txt

init-db:
\t$(PYTHON) -m src.db --init

demo-db:
\t$(PYTHON) -m src.db --demo

run:
\t$(PYTHON) -m src.search_and_apply_demo

test:
\t$(PYTHON) -m pytest -q
