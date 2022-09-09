lint:
	python -m isort .
	python -m black .

test:
	python -m pytest .
