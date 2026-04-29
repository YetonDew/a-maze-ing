PYTHON = python3
CONFIG = config.txt

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e . flake8 mypy build

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info
	rm -f maze.txt

lint:
	flake8 . --exclude=.venv
	mypy . --exclude '.venv' \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build
