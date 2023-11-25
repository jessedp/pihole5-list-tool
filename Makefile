clean-pyc:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force  {} + 

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive __pycache__/
	rm --force --recursive *.egg-info

lint:
	poetry run black --target-version py37 ph5lt
	poetry run pylint ph5lt

test: clean-pyc lint
	poetry run coverage run -m pytest
	# coverage report --include=ph5lt\/*
	#  python3 -m pytest

covreport: 
	poetry run coverage report --include=ph5lt\/* -m

run:
	poetry run  python3 -m ph5lt

update:
	poetry update

build: clean-build lint
	poetry build

package: build
	poetry build

publishTest: package
	poetry publish -r testpypi

# run outside of the venv/poetry
installTest:
	pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pihole5-list-tool --upgrade

# run outside of the venv/poetry
uninstall:
	pip3 uninstall pihole5-list-tool

publish: package
	poetry publish

reqs:
	poetry install

