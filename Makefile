default: test

clean: clean-build clean-pyc clean-installer
c: clean

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -f .coverage
	rm -f *.log

clean-installer:
	rm -fr output/
	rm -fr app.spec
	rm -f blunderbuss.spec
	rm -f blunderbuss.zip

clean-pyc: ## remove Python file artifacts
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +

init:
	pip install -r requirements.txt

init-dev:
	pip install -r requirements_test.txt

pyinstaller: clean
	pyinstaller --noconfirm --onefile --console \
		-n blunderbuss --uac-admin \
		app.py
	cp -r data/ dist/
	cp data/installer/*.dll dist/
	cp README.* dist/
	7z a blunderbuss.zip dist/*
	7z rn blunderbuss.zip dist blunderbuss

run-black:
	black blunderbuss

run-test:
	pytest --cov=blunderbuss --cov-report term-missing tests/

run-main:
	python -m blunderbuss.main

release: run-test release-test release-prod clean

b: run-black
m: run-main
main: init m
t: run-test
test: init-dev t
