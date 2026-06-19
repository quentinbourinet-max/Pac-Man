# §makefile:ENV ===============================================================

.PHONY: install install-lint clean lint lint-strict

clean:
	rm -rf \
	__pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ \
	.mypy_cache \
	.pytest_cache

# install:
# 	uv sync --extra dev

install-lint:
	pip install flake8 mypy

# §makefile:EXEC ==============================================================

run:
	python3 src/

debug:
	python3 -m pdb src/

# §makefile:NORMS =============================================================

MYPY_FLAGS = \
			--warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs

lint:
	flake8 .
	mypy $(MYPY_FLAGS) src main.py

lint-strict:
	flake8 .
	mypy --strict src main.py
