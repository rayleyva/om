.PHONY: docs

init:
	pip install -r requirements.txt

clean:
	rm -rf dist/

test:
	py.test test_om.py

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
