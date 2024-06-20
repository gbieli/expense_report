format:
	poetry run black .
	poetry run isort .

static-test:
	poetry run flake8 .
	poetry run bandit -r .

unittest:
	poetry run pytest

audit:
	poetry show -o
	poetry audit
	poetry run licensecheck

poetry-sync:
	poetry lock
	poetry install --sync
