clean:
	- rm -rf book/_build

build: clean
	uv run jupyter-book build book/

pdf:
	jupyter-book build book/ --builder pdflatex

pipinstall:
	uv pip install -r pyproject.toml
	uv pip install -e .

test-textmining:
	py.test --cov=src/codingforscience/textmining  --cov-report term-missing -v src/codingforscience/textmining

test-property:
	py.test -v --hypothesis-show-statistics src/codingforscience/property_based_testing

test-simple:
	py.test src/codingforscience/simple_testing
