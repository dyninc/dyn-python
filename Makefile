PACKAGE=dyn

.PHONY: clean

init:
	pip install -r test-requirements.txt

style:
	flake8 $(PACKAGE)

ci: init style

publish:
	python setup.py register
	python setup.py sdist upload
	rm -fr build dist .egg $(PACKAGE).egg-info

clean:
	rm -rf $(PACKAGE)/*.pyc
	rm -rf $(PACKAGE)/__pycache__
	rm -rf tests/__pycache__
	rm -rf $(PACKAGE).egg-info

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"