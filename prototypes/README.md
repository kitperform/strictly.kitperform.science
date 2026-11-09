# Parser prototypes

Proof-of-concept scripts from the November 2026 source analysis
(`docs/wikipedia-source-analysis.md`, §6). They are research instruments, not
the production parser: each one answers "what does this library do with the
Wikipedia series pages, and where does it break?". Run them from the
repository root; every path is resolved relative to this folder's parent, so
the current working directory does not matter.

## Set-up

```sh
python3.12 -m venv venv
source venv/bin/activate
pip install beautifulsoup4 lxml html5lib pandas requests mwparserfromhell
```

Tested with Python 3.12, beautifulsoup4 4.15, lxml 6.1, pandas 3.1,
mwparserfromhell 0.7.2. Run the scripts with `python -I` so that nothing is
imported from the data directories.

## Inputs

| Input | Default location | Override | How to obtain |
|---|---|---|---|
| Rendered HTML per series | `data/wikipedia/series/0NN/Strictly_Come_Dancing_series_N.html` | `SDC_HTML_DIR` | `scripts/fetch-wikipedia.sh` (in the repo) |
| Raw wikitext per series | `data/wikipedia/wikitext/series_N.wikitext` | `SDC_WIKITEXT_DIR` | see below |
| Parsoid REST HTML (optional, series 24) | `data/wikipedia/parsoid/series_24.parsoid.html` | `SDC_PARSOID_HTML` | see below; falls back to the series 24 read-view capture, which is also Parsoid output |
| Output folder | `prototypes/out/` (git-ignored, created on demand) | `SDC_OUT_DIR` | — |

Fetching wikitext (replace the User-Agent with your own contact details, as
Wikipedia's policy asks):

```sh
UA="strictly.kitperform.science/0.1 (https://github.com/kitperform/strictly.kitperform.science)"
mkdir -p data/wikipedia/wikitext
for n in $(seq 1 24); do
  curl -fsSL -A "$UA" "https://en.wikipedia.org/w/index.php?title=Strictly_Come_Dancing_series_$n&action=raw" \
    -o "data/wikipedia/wikitext/series_$n.wikitext"
  sleep 1
done
```

For provenance (revision id, sha1, timestamp) prefer the Action API,
`action=query&prop=revisions&rvslots=main&rvprop=ids|timestamp|sha1|content`,
and record the ids next to the files. Parsoid REST HTML:

```sh
mkdir -p data/wikipedia/parsoid
curl -fsSL -A "$UA" "https://en.wikipedia.org/api/rest_v1/page/html/Strictly_Come_Dancing_series_24" \
  -o data/wikipedia/parsoid/series_24.parsoid.html
```

## Scripts

### `sdc_common.py` (library, not run directly)

Shared helpers: path resolution (`REPO`, `HTML_DIR`, `WIKITEXT_DIR`,
`OUT_DIR`, `html_path(n)`, `wikitext_path(n)`, `parsoid_path()`, `out_dir()`),
the rowspan/colspan-aware `table_grid()` expander that marks copied cells,
`cell_text()` (strips `[a]`/`[12]` reference markers, turns `<br>` into ` | `,
keeps dagger characters), `parse_score()` for `27 (5, 7, 8, 7)`, and
`split_music()` for `"Song" — Artist`. Works unchanged on legacy-parser HTML
(series 1–21 captures) and Parsoid HTML (series 22–24 captures).

### `poc1_read_html.py` — pandas.read_html

```sh
python -I prototypes/poc1_read_html.py 6 24
```

Loads every table on the page with `pandas.read_html(flavor="lxml")`,
classifies each by header text (couples, scoring_chart, average, weekly,
dance_chart, ratings, other) and prints a sample of each kind plus the
non-standard cells it finds. Produces console output only. Demonstrates that
the weekly tables come out clean but links, background colours and the
matrix-table structure are lost (23 tables on series 6, 17 on series 24).

### `poc2_bs4_weeks.py` — BeautifulSoup week walker (the recommended path)

```sh
python -I prototypes/poc2_bs4_weeks.py 1 6 9 12 21 24
```

Walks from each `<h3 id="Week_N…">` heading to the next heading, expands each
wikitable with `table_grid`, maps columns by header text, parses the score,
dance, music (song/artist), theme column and result (with background colour),
captures Night 1/Night 2 and Show 1/Show 2 sub-labels, and parses the
"Judges' votes to save/eliminate" list. Writes
`prototypes/out/bs4_weeks_series_N.csv` (one row per dance performed) and
`prototypes/out/bs4_votes_series_N.csv` (one row per judge vote), and prints
the judge-count distribution, distinct results/backgrounds and an anomaly
list. Expected counts: S6 120 rows/48 votes, S9 131/0, S12 147/45, S24 97/24.

### `poc3_mwparser.py` — mwparserfromhell on the wikitext

```sh
python -I prototypes/poc3_mwparser.py 6 9 24
```

Needs the wikitext folder. Parses the `Week N` sections with
mwparserfromhell, handles the series 22–24 quirks (header row without `|-`,
empty `|+` caption line), unwraps `{{nowrap}}`/`{{fontcolor}}`/`{{small}}`,
keeps dagger markers, and records wikilink targets for dances, songs and
artists plus `{{efn}}` names and `bgcolor` per cell. Writes
`prototypes/out/mw_weeks_series_N.csv` and prints a template census of the
Scoring chart. Expected counts match poc2 (S6 120, S9 131, S24 97) when the
wikitext is the same revision as the HTML.

### `poc4_parsoid.py` — what Parsoid `data-mw` adds

```sh
python -I prototypes/poc4_parsoid.py
```

Inspects a Parsoid HTML file (REST capture if present, otherwise the
repository's series 24 capture) and prints the template census from
`data-mw`, an `{{efn}}` footnote decoded in place (name + body), the dagger
alt text, the `<section data-mw-section-id>` headings and a `rel="mw:WikiLink"`
example, then contrasts the legacy series 6 capture (no `data-mw`, dagger alt
lost, footnote body only via `#cite_note`, `{{NA}}` as `class="table-na"`).
Console output only.

### `identity.py` — identity resolution across all 24 series

```sh
python -I prototypes/identity.py
```

Needs the wikitext for series 1–24. Parses every Couples table (celebrity and
professional link targets, display names, mid-series replacement notes,
status, including rows that share a rowspan Status cell), collects the
Scoring-chart row labels `X & Y`, resolves each label to a couple by first
token with surname-initial handling, and prints: unresolved or
nickname-resolved labels, same-first-name collisions per series, professional
link targets whose display name varies (Karen Clifton/Karen Hauer),
celebrity display/link mismatches, mid-series replacements and unlinked
professionals. Writes `prototypes/out/couples_all_series.csv` (339 rows).

### `count_rows.py` — rough census

```sh
python -I prototypes/count_rows.py            # uses data/wikipedia/wikitext
python -I prototypes/count_rows.py some/dir    # or an explicit folder
```

Regex-only estimate of weeks, couples, performances and judge marks per series
from the wikitext (about 2,800 performances and 11,200 marks across series
1–24). Useful for sizing; the counts are approximate and over-count couples
slightly because header rows are included.

## What the prototypes established

- `pandas.read_html` is only good for reconciling weekly totals.
- BeautifulSoup + lxml, walking by heading and expanding every table with one
  grid function, handles both HTML dialects with one code path.
- mwparserfromhell adds link targets and template names but needs its own
  rowspan logic and trips on the series 22–24 table syntax.
- Parsoid HTML (REST or the 2026 read-view captures) gives footnote names,
  dagger alt text and canonical link titles for free; re-capturing series
  1–21 would make the whole corpus Parsoid.
- Identity must be keyed on wiki-link targets with a per-series label map and
  an explicit override list; see `docs/wikipedia-source-analysis.md` §4.
