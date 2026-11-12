# strictly.kitperform.science — Strictly Open

Goal: to be the most structured, versatile, up-to-date and open Strictly Come Dancing results data resource known to us.

Part of the [Kit Perform](https://github.com/kitperform) family of performance-analytics projects.

## What is in this repo

- `data-model.md` — the first-pass normalised data model, derived from reading the Wikipedia series pages (superseded by `docs/data-model-v2.md`, kept for the record)
- `data-modelling-thinking.md` — notes comparing the hand-devised model with a Google Gemini suggestion
- `docs/` — the research and design documents (see below)
- `data/wikipedia/series/0NN/` — rendered HTML captures of the Wikipedia page for each series (1–24), plus `data/wikipedia/main/` for the main article
- `data/wikipedia/wikitext/` — raw wikitext of the same pages fetched through the MediaWiki Action API, with `MANIFEST.csv` recording page id, revision id, revision timestamp and sha1 for every capture
- `data/wikipedia/parsoid/` — Parsoid HTML of series 24 at the same revision as its wikitext
- `scripts/fetch-wikipedia.sh` (HTML) and `scripts/fetch-wikitext.py` (wikitext + manifest, optional `--parsoid N`) — reproducible fetchers
- `strictly_parser/` — the Phase 0 parser: turns a captured series page into the tidy CSV dataset defined in `docs/data-model-v2.md` section 10
- `curated/` — small hand-maintained tables for facts the page does not state (head judge, format rules, label typos, dance families); see `curated/README.md`
- `data/tidy/S12/` to `data/tidy/S24/` — the parser's output per series: one CSV per table plus `build_report.md` with the integrity checks
- `tests/` — pytest acceptance tests pinning known facts of series 12 to 24 (withdrawals, byes, instant dances, rotating casting votes, the triple dance-off, carried-over weeks, finals)
- `prototypes/` — parser prototypes that established the approach (`prototypes/README.md`)
- `scraping-evaluation.ipynb`, `four-tens-experimentation.ipynb` — early Jupyter experiments (merged in from the former `strictly-jupyter` fork)

## Documentation

| Document | What it covers |
|---|---|
| [`docs/data-model-v2.md`](docs/data-model-v2.md) | The proposed data model: entities, fields, enumerations, rule tables, worked examples, coverage of every catalogued corner case, Drupal and CSV mappings, open questions |
| [`docs/wikipedia-source-analysis.md`](docs/wikipedia-source-analysis.md) | What a series page contains, every table type and its quirks, identity resolution, the two HTML dialects, parser prototype results and the recommended parsing approach |
| [`docs/wikipedia-anomaly-register.md`](docs/wikipedia-anomaly-register.md) | 257 catalogued anomalies (A001–A257) across series 1–24 with their Wikipedia encoding and modelling implication |
| [`docs/series-summaries.md`](docs/series-summaries.md) | One structured summary per series: format, judges, scoring, notable events |
| [`docs/data-access-options.md`](docs/data-access-options.md) | How to get Wikipedia data without screen-scraping rendered pages, existing datasets, licensing, live-series tracking |
| [`docs/architecture-and-hosting.md`](docs/architecture-and-hosting.md) | Drupal modelling, API options for Pandas, ingestion pipeline, hosting options and costs, traffic strategy, domain layout, local development, roadmap |

## Project stage

The project is in early-stage discovery.

- Work done so far:
  - Researched other existing projects: Four Tens, StrictlyDB. Verdict: open source projects such as Four Tens have some analysis, but are not up-to-date. StrictlyDB is a website, which is closed-source and the data doesn't appear to be open.
  - Analysis of Wikipedia data. Verdict: very comprehensive and complete. Some data can be derived from other sections, so not all of it needs processing.
  - Produced a highly normalised data model based on analysis of Wikipedia data: [`data-model.md`](data-model.md)
  - Evaluated scraping tools: Scrapy and Beautiful Soup. Verdict: use Beautiful Soup. Initially got carried away with the virtue of Scrapy based on reading, but Beautiful Soup fits much better. Bertie had recommended this as well.
  - Avoiding the "run before walk" problem: started preparing to evaluate other projects in Jupyter but not got that far.
  - Thinking about what questions I want to answer, some notes in [`scraping-evaluation.ipynb`](scraping-evaluation.ipynb), also:
    - what makes a successful contestant
    - has scoring inflated over the years
    - who is more generous with scores
    - how much does the judges' vote versus the viewer vote help contestants progress

- Next steps:
  - add the following as tickets into GitHub projects and do them:
    - explore other projects applying Pandas to get a feel for analysis and further insight into what questions I want to answer
      - continue with [`four-tens-experimentation.ipynb`](four-tens-experimentation.ipynb)
    - prototype Beautiful Soup code to scrape data into the database model, start experimenting
      - write code to link tables via foreign keys
    - give a lightning talk at PyData Southampton on TBD

## Running the parser

```sh
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m strictly_parser 24          # writes data/tidy/S24/*.csv and build_report.md (12 to 23 likewise)
python -m pytest -q tests             # acceptance tests against the series 24 capture
```

The parser reads `data/wikipedia/parsoid/series_24.parsoid.html` (fetched at the revision recorded in `data/wikipedia/wikitext/MANIFEST.csv`) and the tables in `curated/`. It exits non-zero if any integrity check in the report fails. Re-fetch with `scripts/fetch-wikitext.py 24 --parsoid 24` and re-run to pick up a new week.

Known limits before series 1 to 23 can be built (from the code review of the Phase 0 parser):

- per-week judge-order overrides drive seats, marks, absent and replacement rows and the scoring scale (series 18 and 19 cover three judges, a substitute professional and a remote non-scoring judge); five-judge weeks (series 7) are untested;
- marathons and instant dances have a `group_key`; group routines and multi-couple row headers (series 1 to 8) have no `performer_group` path yet;
- `competed_unscored` is not yet set for a couple whose every routine in a week was unscored (series 6);
- legacy (non-Parsoid) HTML has no `<section>` wrappers, so series 1 to 21 need Parsoid re-captures at their manifest revisions (`scripts/fetch-wikitext.py N --parsoid N`) or a sibling-walking fallback;
- each new series needs rows in `curated/series_meta.csv`, `series_panels.csv` and `format_rules.csv`.

## Local setup

```sh
python3 -m venv venv          # on Ubuntu: sudo apt install python3 python3-pip python3.12-venv first
source venv/bin/activate
pip install jupyter beautifulsoup4 lxml pandas
jupyter notebook
deactivate
```

The virtual environment is deliberately not committed (see `.gitignore`); recreate it with the commands above.

Notes on which environment to use: https://stackoverflow.com/a/47559925/227926

## History

This repo was briefly forked as `strictly-jupyter`; that fork has been merged back here and this is now the single home for the project.
