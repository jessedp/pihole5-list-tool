clean-pyc:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force  {} + 

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive __pycache__/
	rm --force --recursive *.egg-info

build: clean-build lint
	# pyi-makespec  --onefile pihole5-list-tool.py
	

lint:
	black --target-version py37 ph5lt
	pylint ph5lt

test: clean-pyc lint
	coverage run -m pytest
	# coverage report --include=ph5lt\/*
	#  python3 -m pytest

covreport: 
	coverage report --include=ph5lt\/* -m

run:
	python3 -m ph5lt

update:
	python3 -m pip install --user --upgrade setuptools wheel

package: build
	python3 setup.py sdist bdist_wheel

publishTest: package
	python3 -m twine upload --repository testpypi dist/* 

installTest:
	pip3 install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pihole5-list-tool --upgrade

uninstall:
	pip3 uninstall pihole5-list-tool

publish: package
	python3 -m twine upload dist/* 

reqs:
	pip3 install -r requirements.txt

