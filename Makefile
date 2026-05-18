.PHONY: help install fmt lint typecheck test test-live build models check-spec clean

help:
	@echo "make install     - editable install with dev deps"
	@echo "make fmt         - format with ruff"
	@echo "make lint        - lint with ruff"
	@echo "make typecheck   - mypy --strict on src/talonic"
	@echo "make test        - pytest (unit + cli + models)"
	@echo "make test-live   - pytest tests/live/ --live (needs TALONIC_API_KEY)"
	@echo "make models      - regenerate src/talonic/_models/ from openapi.json"
	@echo "make check-spec  - regen + diff (CI drift check)"
	@echo "make build       - sdist + wheel into dist/"
	@echo "make clean       - remove build artefacts"

install:
	pip install -e ".[dev]"
	pre-commit install

fmt:
	ruff format src tests $$(test -d scripts && echo scripts)
	ruff check --fix src tests $$(test -d scripts && echo scripts)

lint:
	ruff format --check src tests $$(test -d scripts && echo scripts)
	ruff check src tests $$(test -d scripts && echo scripts)

typecheck:
	mypy src/talonic

test:
	pytest -q --ignore=tests/live

test-live:
	pytest tests/live --live -v

models:
	python scripts/generate_models.py

check-spec:
	python scripts/check_spec.py

build:
	python -m build

clean:
	rm -rf build dist *.egg-info src/talonic.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
