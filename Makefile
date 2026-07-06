# clean-up
clean:
	rm -rfv .mypy_cache .pytest_cache \_\_pycache\_\_

test:
	pytest -v

flake8:
	flake8

conda-activate:
	conda env create -f environment.yml
	conda activate codebase

conda-deactivate:
	conda deactivate
	conda remove -n codebase --all
