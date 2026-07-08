# §makefile:EXEC --------------------------------------------------------------

CONFIG ?= data/config.json

run:
	uv run python pac-man.py $(CONFIG)

debug:
	uv run python -m pdb pac-man.py $(CONFIG)

# §makefile:ENV ---------------------------------------------------------------

.PHONY: install install-lint clean lint lint-strict

clean:
	rm -rf \
	__pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ \
	.mypy_cache \
	.pytest_cache

install:
	uv sync

install-lint:
	uv add --dev flake8 mypy

# §makefile:LINT --------------------------------------------------------------

MYPY_FLAGS = \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

lint:
	uv run flake8 src/ pac-man.py
	uv run mypy $(MYPY_FLAGS) pac-man.py src/

lint-strict:
	uv run flake8 src/ pac-man.py
	uv run mypy --strict --ignore-missing-imports pac-man.py src/
