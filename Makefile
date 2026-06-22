# §makefile:EXEC --------------------------------------------------------------

CONFIG ?= data/config.json

run:
	python3 pac-man.py $(CONFIG)

debug:
	python3 -m pdb pac-man.py $(CONFIG)

# §makefile:ENV ---------------------------------------------------------------

.PHONY: install install-lint clean lint lint-strict

install:
	pip install ./mazegenerator-*.whl
	pip install pygame

install-lint:
	pip install flake8 mypy

clean:
	rm -rf \
	__pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ \
	.mypy_cache \
	.pytest_cache

# §makefile:LINT --------------------------------------------------------------

MYPY_FLAGS = \
			--warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs

lint:
	flake8 .
	mypy $(MYPY_FLAGS) pac-man.py src/

lint-strict:
	flake8 .
	mypy --strict pac-man.py src/
