.SILENT:

# clean-up
clean:
	rm -rfv .mypy_cache .pytest_cache \_\_pycache\_\_

testrun:
	conda run -n codebase pytest -v

flake8:
	flake8

install-editable:
	pip install -e .
