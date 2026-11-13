PY ?= ./venv/bin/python
SERIES ?= $(shell seq 1 24)

.PHONY: build package validate test all clean-dist

build:            ## parse every series into data/tidy/S<nn>/
	@for n in $(SERIES); do $(PY) -m strictly_parser $$n > /dev/null || { echo "series $$n failed"; exit 1; }; done; echo "built series: $(SERIES)"

package:          ## concatenate into data/package/ and build dist/ (SQLite, Parquet, zip)
	$(PY) -m strictly_parser.package

validate:         ## frictionless validate over the package (pip install frictionless)
	./venv/bin/frictionless validate data/package/datapackage.json

test:
	$(PY) -m pytest -q tests

all: build package test

clean-dist:
	rm -rf dist
