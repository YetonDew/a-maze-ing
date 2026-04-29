PYTHON := .venv/bin/python
PIP := .venv/bin/pip
FLAKE8 := .venv/bin/flake8
MYPY := .venv/bin/mypy

.PHONY: install run debug clean lint lint-strict

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache .ruff_cache build dist
	find . -name '*.pyc' -delete

lint:
	$(FLAKE8) .
	$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(FLAKE8) .
	$(MYPY) . --strict
