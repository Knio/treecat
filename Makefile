
publish:
	rm dist/ -r
	python3 setup.py sdist
	python3 setup.py bdist_wheel
	python3 -m twine upload dist/*

