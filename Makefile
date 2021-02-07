qa:
	isort --profile black . && black . && flake8

clean:
	rm -rf dist

release: clean
	python3 setup.py sdist && python3 -m twine upload dist/*
