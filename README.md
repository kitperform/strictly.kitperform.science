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
- `data/tidy/S01/` to `data/tidy/S24/` — the parser's output per series: one CSV per table plus `build_report.md` with the integrity checks
- `tests/` — pytest acceptance tests pinning known facts of every series, 1 to 24 (withdrawals, byes, instant dances, rotating casting votes, the triple dance-off, carried-over weeks, finals)
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
python -m strictly_parser 24          # writes data/tidy/S24/*.csv and build_report.md (any series 1 to 23 likewise)
python -m pytest -q tests             # acceptance tests against the series 24 capture
```

The parser reads `data/wikipedia/parsoid/series_24.parsoid.html` (fetched at the revision recorded in `data/wikipedia/wikitext/MANIFEST.csv`) and the tables in `curated/`. It exits non-zero if any integrity check in the report fails. Re-fetch with `scripts/fetch-wikitext.py 24 --parsoid 24` and re-run to pick up a new week.

Every series from 1 to 24 builds with all integrity checks passing. Known limits of the current dataset:

- couple-less routines (professional group numbers, the series 8 troupe) and the Christmas and charity specials are not loaded, by decision;
- presenter and musical-guest appearances are not loaded (the schema exists; see the data model's open questions);
- a few derived columns listed in the data model (`d_tally_class`, `d_round_total`, `uuid`) are not yet emitted;
- pre-series departures get roster rows only when the page names a replacement in the same or the next sentence (Nairn → Cope, Dyer → Davies, Laing → Fletcher, Windsor → Whiddon, Slater → Garnis, Lowe → Vilani); a departure with no named replacement (for example Kevin Clifton leaving before series 18) has no row yet;
- a planned routine is loaded as a `not_performed` performance only when the week prose says the couple "was due to dance" it (series 23 Stefan Dennis, La Voix); music in those rows is not split into songs;
- exit and absence reasons come from a keyword vocabulary over the prose (`reason_from`); a sentence that names two causes keeps the more specific one (medical advice over illness, injury over illness);
- each new series needs rows in `curated/series_meta.csv`, `series_panels.csv` and `format_rules.csv`.

## Packaged dataset

`python -m strictly_parser.package` (or `make package`) concatenates the per-series folders into one dataset:

- `data/package/<table>.csv`: one CSV per table across all 24 series, committed. Reference tables (people, songs, artists, dances, themes, venues) are deduplicated on their key.
- `data/package/datapackage.json`: a [Frictionless Data Package](https://datapackage.org) with field types, primary and foreign keys, the documented vocabularies as enum constraints and the Wikipedia revision ids as `sources`. `make validate` runs `frictionless validate` over it.
- `data/package/package_report.md`: row counts and the package-level checks (keys unique, foreign keys resolve, enum values documented, typed columns parse).
- `dist/strictly.sqlite`, `dist/parquet/*.parquet`, `dist/strictly-csv.zip`: not committed; rebuilt by the same command.

```python
import pandas as pd
jm = pd.read_csv("data/package/judge_marks.csv")          # or pd.read_parquet("dist/parquet/judge_marks.parquet")
jm[(jm.judge_slug == "craig-revel-horwood") & (jm["mark"] == 10)].sort_values(["series_number", "d_perf_seq"]).head(1)
```

`examples/cross_series_queries.py` has a dozen cross-series commentary queries (judge generosity by series, winners who were once in the bottom two, the one bye that became a withdrawal, most-danced songs); `tests/test_package.py` keeps a few of those facts under test.

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
