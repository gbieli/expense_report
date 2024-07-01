format:
	poetry run black .
	poetry run isort .

static-test:
	poetry run flake8 .
	poetry run bandit -r .

unittest:
	poetry run pytest --cov --cov-fail-under=96 --junit-xml=reports/junit_report.xml

pre-commit:
	make format
	make static-test
	make unittest

audit:
	poetry show -o
	poetry audit
	poetry run licensecheck

poetry-sync:
	poetry lock
	poetry install --sync
