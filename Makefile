

testall: \
	mypy \
	unittest


mypy:
	mypy ygo_client --strict --ignore-missing-imports


unittest:
	python -m unittest tests