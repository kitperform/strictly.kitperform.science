# strictly.kitperform.science — Strictly Open

Goal: to be the most structured, versatile, up-to-date and open Strictly Come Dancing results data resource known to us.

Part of the [Kit Perform](https://github.com/kitperform) family of performance-analytics projects.

## What is in this repo

- `data-model.md` — the current (first-pass) normalised data model, derived from reading the Wikipedia series pages
- `data-modelling-thinking.md` — notes comparing the hand-devised model with a Google Gemini suggestion
- `data/wikipedia/` — raw `curl` captures of the Wikipedia pages (main article plus one page per series) that everything is derived from
- `scraping-evaluation.ipynb`, `four-tens-experimentation.ipynb` — early Jupyter experiments (merged in from the former `strictly-jupyter` fork)

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
