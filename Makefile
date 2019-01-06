SHELL = /bin/sh

.PHONY = init test lint

init:
	pip install pipenv
	pipenv install --dev

test:
	pipenv run pytest

lint:
	pipenv run black --check .
	pipenv run isort --recursive --diff .
	pipenv run flake8 .

fmt:
	pipenv run isort --recursive .
	pipenv run black .
