PY ?= ./venv/bin/python
SERIES ?= $(shell seq 1 24)

.PHONY: build package validate recipe drupal-setup drupal-apply drupal-update test all clean-dist

build:            ## parse every series into data/tidy/S<nn>/
	@for n in $(SERIES); do $(PY) -m strictly_parser $$n > /dev/null || { echo "series $$n failed"; exit 1; }; done; echo "built series: $(SERIES)"

package:          ## concatenate into data/package/ and build dist/ (SQLite, Parquet, zip)
	$(PY) -m strictly_parser.package

validate:         ## frictionless validate over the package (pip install frictionless)
	./venv/bin/frictionless validate data/package/datapackage.json

recipe:           ## regenerate recipes/strictly from the dataset schema
	$(PY) scripts/generate_drupal_recipe.py

drupal-setup:     ## local Drupal 11 in DDEV (one-off)
	scripts/drupal-local.sh setup

drupal-apply:     ## apply the recipe and load the dataset into the local site
	scripts/drupal-local.sh apply

drupal-update:    ## re-run the migrations after make build package recipe
	scripts/drupal-local.sh update

test:
	$(PY) -m pytest -q tests

all: build package recipe test

clean-dist:
	rm -rf dist
