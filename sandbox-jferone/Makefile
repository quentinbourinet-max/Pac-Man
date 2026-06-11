# BASIC SANDBOX MAKEFILE
# Resp : @jferone

PYTHON		= python3
MAIN		= src/main.py
#CONFIG		= src/config.json

run:
	$(PYTHON) $(MAIN)
#	$(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN)

install:
	pip install pygame-ce pytmx

lint:
	flake8 .
	mypy . --warn-return-any \
			--warn-unused-ignores \
			--ignore-missing-imports \
			--disallow-untyped-defs \
			--check-untyped-defs

lint-strict:
	flake8 .
	mypy --strict .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc"       -delete

.PHONY: all install run debug clean lint lint-strict
