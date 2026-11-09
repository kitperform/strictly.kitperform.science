# Data access options: how we get Strictly data out of Wikipedia

*Status: recommendation, written 8 November 2026 during series 24. Based on hands-on tests of every option against the live `Strictly Come Dancing series 24` page; figures (revision ids, byte counts, timestamps) are what was observed on the day.*

## 1. Recommendation in plain terms

**Primary capture: fetch raw wikitext through the MediaWiki Action API and commit it per revision.** Implemented as `scripts/fetch-wikitext.py`, which writes `data/wikipedia/wikitext/*.wikitext` and a `MANIFEST.csv` of `pageid, revid, timestamp, sha1, captured_at`.

*Reconciliation with `docs/wikipedia-source-analysis.md` §6.6:* the parser prototypes found the heading-driven BeautifulSoup + lxml grid walker the most robust reader across all 24 series, and Parsoid HTML keeps every template name in `data-mw`. The agreed split is therefore: **wikitext is the stored canonical source (provenance, diffs, test fixtures); the Parsoid HTML of the same revision (`/api/rest_v1/page/html/{title}/{revid}`) is the parser's primary input; mwparserfromhell over the wikitext is the independent second reading used for cross-checks.** The rest of this section describes what the wikitext gives you and why it is worth storing even though the HTML walker reads most tables.

- Fetch with `action=query&prop=revisions&rvslots=main&rvprop=ids|timestamp|user|comment|sha1|size|content`. One call can return several series pages at once, and every response tells you exactly which revision you got (`revid`, `sha1`, `timestamp`). That is the provenance the data model needs: every fact can carry `source_revid` and be reproduced later.
- Parse with `wikitextparser` (tables, with rowspan/colspan resolved, and per-cell `style` attributes) plus `mwparserfromhell` (template-aware cleaning of individual cells). The wikitext is the editors' own *declarative* encoding of the corner cases the model has to represent: `{{dagger}}` = highest of the night, `{{double-dagger}}` = lowest, `{{efn|name=OutSick|...}}` = bye, `{{n/a}}` = did not dance, `style="background:#f4c7b8"` keyed to the `{{legend}}` block = eliminated, `'29 (6, 8, 7, 8)'` = total plus ordered judge marks, `== Week 7: Musicals Week (Quarter-final) ==` = week, theme, round. The rendered HTML throws most of that away or turns it into colours and symbols you have to reverse-engineer.
- Commit the fetched wikitext per revision (25-80 KB each) next to the existing HTML captures, and build the parser's test suite from those fixtures.

**Fallback and cross-check: Parsoid HTML from the Wikimedia REST API.** `https://en.wikipedia.org/api/rest_v1/page/html/{title}` gives browser-grade HTML where every template still carries a `data-mw` attribute naming it (`fontcolor`, `dagger`, `efn` and their parameters). If a table ever defeats the wikitext parser, this is the next-best source and needs no regexes on `†`. `pandas.read_html` on either HTML is a three-line sanity check of totals in a notebook, not an ingestion path.

**Independent validation datasets:** Four Tens `results.csv` (CC0, series 1-15, per-judge marks); jongiddy `output.csv` (MIT, series 1-20, totals and judge counts); the Wikipedia *List of Strictly Come Dancing contestants* page (per-couple totals/averages); StrictlyDB's published aggregate counts (read, do not scrape). Wikidata for stable identifiers (series QIDs, BBC programme ids, person QIDs) only; it holds no scores.

**Skip:** full dumps, DBpedia, EventStreams, the Enterprise API (for now), and the dead `wikipedia`/`wptools` packages.

**Live series:** poll a 500-byte `prop=info` request for `lastrevid`, fetch the wikitext only when it changes, wait ten minutes of quiet before trusting a snapshot, validate before publishing, and store "how complete is this episode" as a status column (`scheduled / scores_in / results_in / verified`) rather than inferring it in code.

**Licences:** structured data CC0 1.0 (or CC BY 4.0), code MIT, any quoted Wikipedia prose CC BY-SA 4.0 with page + revision attribution. Not ODbL. Not legal advice (section 4).

## 2. Every option compared

| Option | What it is | How to call it | Pros | Cons | Limits / cost | Tested? | Verdict |
|---|---|---|---|---|---|---|---|
| **Action API `prop=revisions`** | JSON API returning wikitext of latest or any revision with revid, parentid, timestamp, sha1, size | `api.php?action=query&prop=revisions&titles=A\|B\|C&rvprop=ids\|timestamp\|content\|sha1&rvslots=main&format=json&formatversion=2&maxlag=5` | Several pages per call; exact provenance for free; old revisions via `rvstartid`; cheap (24 pages in 1-2 calls); same text the parsers consume | You parse the wikitext yourself; content requests capped at 50 revisions/call; occasional deprecation warnings | Free. No hard read limit; serial requests, descriptive User-Agent, `maxlag=5`, back off on `{"error":{"code":"maxlag"}}`. `cache-control: private`, so cache locally | Yes: series 22/23/24 in one call (revids 1382773255, 1382773258, 1384551432); series 24 history (761 revisions) in 2 calls; forced a maxlag error | **Primary fetch** |
| **Action API `action=parse`** | Parse a page/oldid/snippet; return wikitext or HTML of the whole page or one section, section list, templates used | `api.php?action=parse&page=Strictly_Come_Dancing_series_24&prop=sections` ; `...&prop=wikitext\|revid&section=5` ; `...&prop=templates` | Pull one section (a few KB); `prop=templates` lists the templates you must handle; `byteoffset` helps diffing | Section numbers shift when weeks are added (resolve by heading text); `prop=text` is legacy parser HTML without `data-mw`; `prop=sections` deprecated in favour of `prop=tocdata` | Free; same etiquette | Yes: 20 sections on series 24 (Scoring chart = index 5); template list Dagger, Double-dagger, Efn, Legend, Fontcolor, Abbr, Nowrap, Dts, Sort, N/a | Helper only; whole pages are small enough to fetch in one go |
| **`index.php?action=raw`** | Current (or `oldid=`) wikitext as `text/x-wiki` | `index.php?title=Strictly_Come_Dancing_series_24&action=raw` (+`&oldid=NNN`) | Zero JSON; honours `If-Modified-Since` (304 seen); `Last-Modified` = revision timestamp; drops straight into the existing shell script | No revid/sha1 in the response, so provenance needs a second call; not CDN-cacheable | Free; one request per page | Yes: 63,213 bytes, `last-modified 2026-11-08T20:48:05Z`, 304 on conditional GET | Fallback / manual inspection |
| **REST `/page/html` (Parsoid)** | Parsoid HTML (spec 2.8.0): every template/extension carries `data-mw` JSON; headings wrapped in `<section data-mw-section-id>`; ETag = revision/render id | `https://en.wikipedia.org/api/rest_v1/page/html/Strictly_Come_Dancing_series_24` ; old revision `.../html/{title}/{revid}` ; revalidate with `If-None-Match` | HTML table semantics *and* template names; `content-revision-id` header; strong CDN caching with 304s; CORS `*` | 5x larger than wikitext (341 KB vs 63 KB); JSON-in-attribute is verbose; Parsoid spec may change; RESTBase is migrating to `/w/rest.php/v1/page/{title}/html` so keep the base URL configurable | Free; global rule <= 200 req/s with a unique User-Agent | Yes: 341,037 bytes, 258 `data-mw` elements, 20 sections, 304 on `If-None-Match`; template counts fontcolor 23, double-dagger 13, dagger 10, efn 4 | **Fallback / cross-check**, and the right choice if an HTML parser is kept |
| **REST `/page/summary`, `/page/mobile-html`** | `summary`: lead, pageid, revision, tid, timestamp, Wikidata QID (~1.5 KB). `mobile-html`: trimmed app rendering | `https://en.wikipedia.org/api/rest_v1/page/summary/Strictly_Come_Dancing_series_24` | `summary` is a tiny, CDN-cached "has it changed?" probe and gives the QID | `mobile-html` strips nearly all `data-mw` (3 left); `summary` has no tables | Free | Yes: revision 1384551432, wikibase_item Q139889688; mobile-html 197,926 bytes | `summary` as change probe; ignore `mobile-html` |
| **wikitext + `wikitextparser` 3.0.0 / `mwparserfromhell` 0.7.2** | Pure-Python wikitext parsing: `Section.tables[n].data()` resolves spans; `.cells()` exposes `style`; mwparserfromhell handles templates and `strip_code()` | `pip install wikitextparser mwparserfromhell`; `wtp.parse(text).sections` -> filter by title -> `.tables[0].data()`; clean cells by replacing `{{fontcolor\|c\|X}}` with X, recording `{{dagger}}`/`{{double-dagger}}`/`{{efn}}` as flags | Smallest payload; corner cases are explicit markers not visual side effects; 3/4/5-judge weeks are just tuple lengths; headings carry week/theme/round; offline, deterministic, unit-testable | Conventions drift over 22 years (series 1 and 6 week-1 tables lack a Result column; series 18/21 headers carry inline `<ref>`; series 1-6 use `{{n/a}}`/`{{sort}}`); 2-row scoring-chart header; `Table.data()` can misalign exotic tables, so validate totals against judge marks | Free, local; both libraries actively maintained (releases Oct 2026 / Jul 2025) | Yes: series 24 Week 7 parsed to 10x5 with clean rows; scoring chart 17 rows; surveyed series 1, 6, 18, 21 | **Primary parse** |
| **`pandas.read_html`** | pandas' HTML table reader (lxml/bs4), resolves spans | `pd.read_html(io.StringIO(html), attrs={'class':'wikitable'})` on stored or Parsoid HTML | Three lines to a MultiIndex DataFrame; good for notebooks and total reconciliation | Loses colours, bold, template identity; daggers survive only as `'34†'`; footnotes as `'[b]'`; headers become `'Scores[1]'`; week tables have empty captions so `match=` fails | Free, local | Yes on `data/wikipedia/series/024/...html`: scoring chart shape (15, 16) | Notebooks and cross-checks only |
| **Wrapper packages** (`wikipedia`, `Wikipedia-API`, `wptools`, `pymediawiki`, `mwclient`, `pywikibot`) | Convenience clients over the Action API | `mwclient.Site('en.wikipedia.org', clients_useragent=UA).pages[title].text()` | `mwclient`/`pywikibot` do continuation, maxlag and UA for you | `wikipedia` (2014) and `wptools` (2018) are dead and text-only; `Wikipedia-API`/`pymediawiki` flatten tables; `pywikibot` is heavy for 24 pages; none parse tables | Free | Not tested (PyPI metadata checked) | Optional; 30 lines of `requests` is enough |
| **Wikidata** (SPARQL, `wbgetentities`) | Knowledge graph: show Q8070684 (UK; Q7623643 is the South African show), one item per series Q7623644 ... Q139889688 linked by P179 with P1545 ordinal | `curl -G -H 'Accept: text/csv' --data-urlencode 'query=SELECT ?item ?itemLabel ?ordinal WHERE { ?item wdt:P179 wd:Q8070684 . OPTIONAL { ?item p:P179 ?st . ?st pq:P1545 ?ordinal } SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } }' https://query.wikidata.org/sparql` | Stable ids for series, BBC programme ids (P827, e.g. m0031xbx), Fandom ids (P6262), some cast QIDs (P161) for person enrichment | No episode/week/dance/score data at all; cast coverage partial and skewed to recent series; labels inconsistent | Free; 60 s SPARQL timeout (hit once) | Yes: 24 season rows; property counts P161 76, P710 17, P1113 13, P1346 2 | Identifiers and person enrichment only |
| **DBpedia** | RDF extraction of infoboxes, one resource per series | `curl -H 'Accept: text/turtle' https://dbpedia.org/data/Strictly_Come_Dancing_series_21.ttl` | Has series 22-24; records the Wikipedia oldid it was derived from | Infobox only; snapshot lags months; CC BY-SA | Free, best effort | Yes: series 21 TTL (25 episodes, 2023-09-16 to 2023-12-16) | Skip |
| **Wikimedia dumps / Enterprise HTML dumps** | Full-site XML (wikitext) twice a month; Enterprise NDJSON HTML dumps | Download `enwiki-latest-pages-articles-multistream.xml.bz2` + index, seek to 24 titles | Reproducible, dated corpus | 27.0 GB bz2 for 24 pages; Enterprise mirror stalled at run 20250320 (140 GB); up to two weeks stale, useless for the airing series | Free download; disk and bandwidth | Listings only | Skip; storing (revid, sha1, wikitext) per fetch gives better reproducibility |
| **Wikimedia Enterprise API** (free tier, Structured Contents beta) | Commercial-grade API: on-demand HTML/wikitext and beta pre-parsed JSON (sections, tables, references) | Sign up at enterprise.wikimedia.com, token, on-demand endpoint per title | 50,000 lookups/month free; pre-parsed tables might remove a step | Beta; account needed; table schema undocumented and unverified for these pages; realtime is paid; a dependency the project does not need | Free tier: 50k on-demand, 30 snapshot + 1,500 chunk requests/month | Not tested | One-hour experiment later |
| **EventStreams (SSE)** | Firehose of all wiki changes with 7-31 day replay | `curl -N -A "$UA" 'https://stream.wikimedia.org/v2/stream/recentchange?since=2026-11-08T20:40:00Z'` then filter on `server_name` and `title` client-side | Edits arrive ~1 s after they happen with old/new revid and the section-naming edit summary | ~36 events/s across all wikis, no server-side filter, 15-minute reconnects, needs a daemon; overkill for one page edited 10-60 times on a Saturday | Free | Yes: 364 events in 10 s; replay found the series-24 edit (1384544441 -> 1384551315) | Not recommended; keep in mind for second-level finals-night updates |
| **History Atom feed / `prop=info`** | Atom of the 10 newest revisions; `prop=info` returns `touched` and `lastrevid` in ~500 bytes | `index.php?title=Strictly_Come_Dancing_series_24&action=history&feed=atom` ; `api.php?action=query&prop=info&titles=Strictly_Come_Dancing_series_24&format=json&formatversion=2` | Tiny, standard, cron-friendly; `lastrevid` is exactly the key to snapshot on | Atom feed is 157 KB because of embedded diffs and only 10 entries | Free | Yes: `lastrevid 1384551432`, `touched 2026-11-08T20:48:05Z`, length 63213 | **`prop=info` is the recommended change probe** |

### URL crib sheet

Replace `$UA` with the project User-Agent (name, version, URL, contact email). All of these were called on 8 November 2026.

```sh
UA="strictly.kitperform.science/0.2 (https://github.com/kitperform/strictly.kitperform.science; contact@example)"

# Latest wikitext + provenance for several series in one call (PRIMARY)
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Strictly_Come_Dancing_series_22|Strictly_Come_Dancing_series_23|Strictly_Come_Dancing_series_24&rvprop=ids|timestamp|user|comment|sha1|size|content&rvslots=main&format=json&formatversion=2&maxlag=5'

# Revision history of one page (repeat with &rvcontinue=<continue.rvcontinue> until it stops)
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Strictly_Come_Dancing_series_24&rvprop=ids|timestamp|user|comment|size|sha1&rvlimit=max&format=json&formatversion=2&maxlag=5'

# Wikitext of one old revision (for "as it looked on Sunday night" snapshots and parser back-tests)
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=parse&oldid=1376862102&prop=wikitext|revid&format=json&formatversion=2'
curl -fsSL -A "$UA" 'https://en.wikipedia.org/w/index.php?title=Strictly_Come_Dancing_series_24&action=raw&oldid=1376862102'

# Section map, one section's wikitext, templates used
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=parse&page=Strictly_Come_Dancing_series_24&prop=tocdata&format=json&formatversion=2'
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=parse&page=Strictly_Come_Dancing_series_24&prop=wikitext|revid&section=5&format=json&formatversion=2'
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=parse&page=Strictly_Come_Dancing_series_24&prop=templates&format=json&formatversion=2'

# Change probe (~500 bytes)
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/api.php?action=query&prop=info&titles=Strictly_Come_Dancing_series_24&format=json&formatversion=2&maxlag=5'
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/api/rest_v1/page/summary/Strictly_Come_Dancing_series_24'

# Raw wikitext with a conditional request (304 when unchanged)
curl -sSL -A "$UA" -H 'If-Modified-Since: Sun, 08 Nov 2026 20:48:05 GMT' -o /dev/null -w '%{http_code}\n' 'https://en.wikipedia.org/w/index.php?title=Strictly_Come_Dancing_series_24&action=raw'

# Parsoid HTML (FALLBACK), current and a specific revision; ETag revalidation
curl -fsSL --compressed -A "$UA" -D - 'https://en.wikipedia.org/api/rest_v1/page/html/Strictly_Come_Dancing_series_24' -o series_24.parsoid.html
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/api/rest_v1/page/html/Strictly_Come_Dancing_series_24/1376862102'
curl -sSL -A "$UA" -H 'If-None-Match: W/"1384551432/<tid>/view"' -o /dev/null -w '%{http_code}\n' 'https://en.wikipedia.org/api/rest_v1/page/html/Strictly_Come_Dancing_series_24'
# Same Parsoid HTML from MediaWiki core REST (RESTBase successor)
curl -fsSL --compressed -A "$UA" 'https://en.wikipedia.org/w/rest.php/v1/page/Strictly_Come_Dancing_series_24/html'

# Wikidata: one item; all series of the UK show
curl -fsSL -A "$UA" 'https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q139889688&format=json'
curl -fsSL -A "$UA" -G -H 'Accept: text/csv' --data-urlencode 'query=SELECT ?item ?itemLabel ?ordinal WHERE { ?item wdt:P179 wd:Q8070684 . OPTIONAL { ?item p:P179 ?st . ?st pq:P1545 ?ordinal } SERVICE wikibase:label { bd:serviceParam wikibase:language "en" } } ORDER BY xsd:integer(?ordinal)' https://query.wikidata.org/sparql

# Human-friendly watch in a feed reader
# https://en.wikipedia.org/w/index.php?title=Strictly_Come_Dancing_series_24&action=history&feed=atom
```

Etiquette that applies to all of them (from [API:Etiquette](https://www.mediawiki.org/wiki/API:Etiquette) and the [User-Agent policy](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy)): one request at a time, a descriptive User-Agent with a contact, `Accept-Encoding: gzip` (`curl --compressed`), `maxlag=5` on unattended jobs, and sleep a second or two between calls. The REST API states a global ceiling of 200 requests/s; this project will make fewer than 200 a *day*.

## 3. Existing datasets and projects

| Dataset / project | Coverage | Format | Licence | Freshness | Useful for |
|---|---|---|---|---|---|
| [Four Tens: strictly-come-dancing-results](https://github.com/four-tens/strictly-come-dancing-results) | Series 1-15 complete: 1,734 dance rows with per-judge marks in fixed columns (`score_craig` ... `score_shirley`, 0 = absent), song, running order, total; `celebrities.csv`, `professionals.csv` with a few series-16 rows. No results, dance-offs or eliminations | CSV (`results.csv` 154 KB) + `validate.py` | **CC0 1.0** | Last commit 2018-08-22; abandoned | Best independent per-judge cross-check for series 1-15 (spot checks match Wikipedia: S1 W1 Natasha & Brendan 27 (5,7,8,7); S6 W1 Tom & Camilla 28 (6,7,8,7)). CC0 means it could even seed the dataset. Known defects: "Argentina Tango" typo, absent judges coded 0, some 0-total rows for unscored dances |
| [jongiddy/strictly-data](https://github.com/jongiddy/strictly-data) | Series 1-20: 2,346 rows of series, week, celebrity, professional, dance, total, `score_count`, average, note. Totals only | CSV + Rust Wikipedia scraper | **MIT** (code and output) | Last push 2023-07-13 | Second cross-check of totals and judge counts for series 16-20 where Four Tens stops; its `test-data/` edge cases are worth reading before writing our parser |
| [awbirdsall/strictly-come-data](https://awbirdsall.github.io/strictly-come-data/posts/data-prep) | Analysis of Four Tens data extended to series 16; posts on data prep, scraping dance-offs, score prediction | Jupyter / blog | Not stated | 2018-2019 | Documents the Four Tens defects and a dance-off scraping approach; design reference, not a source |
| [Ultimate Strictly](https://www.ultimatestrictly.com/) | Now an editorial fan site on the current series; the per-series tables Four Tens cited return 404 | HTML articles | All rights reserved | Articles 7-8 Nov 2026 | Manual sanity check only; historically Four Tens' upstream |
| [StrictlyDB](https://strictlydb.com/statistics/series/) | All 24 series: claims 528 shows, 2,832 dances, 345 couples, 13 judges, 339 celebrities, 67 pros, 1,758 songs; per-series averages, counts of 10s and perfect scores | WordPress site with login; no export or API | Copyright reserved; relies on s.30 CDPA fair dealing; no reuse licence | Live | Its published aggregates are a reconciliation target for our Pandas totals. Do not scrape or redistribute |
| [Wikipedia: List of Strictly Come Dancing contestants](https://en.wikipedia.org/wiki/List_of_Strictly_Come_Dancing_contestants) | Every contestant with partner, finish, dance count, highest/lowest/total/average (Bruno-absent weeks re-weighted); lists 60+ pros | Wikitext tables (same APIs) | CC BY-SA 4.0 | Live | Cheap cross-check of per-couple aggregates computed from per-performance rows |
| Wikidata season items [Q7623644 ... Q139889688](https://www.wikidata.org/wiki/Q139889688) | 24 season items with ordinal, BBC programme id, Fandom id, partial cast members; no episodes or scores | JSON/RDF | **CC0** | Live but sparse | Stable external ids for Series, Celebrity, ProfessionalDancer, Judge (store the QID in Drupal) and person metadata |
| [BBC /programmes JSON](https://www.bbc.co.uk/programmes/b006m8dq.json) | Brand metadata (first broadcast 2004-05-15T18:15:00+01:00, 874 episodes aggregated); per-series pids (e.g. m0031xbx) and episode pages with transmission dates and synopses; `episodes/guide.json` returns 404 | JSON and HTML with ld+json | BBC terms; no bulk reuse licence | Live | Authoritative transmission dates and episode titles for Episode if Wikipedia's `{{dts}}` dates ever disagree; no scores |
| [Strictly Fandom wiki](https://strictlycomedancing.fandom.com/wiki/Series_24) | Series pages exist but are narrative only (no scores or weeks in the raw text) | MediaWiki | CC BY-SA 3.0 | Live | Not useful for results |
| Kaggle / data.world / Hugging Face | No UK Strictly dataset found; only the Czech "StarDance" on Kaggle | n/a | n/a | n/a | Confirms the gap: this project would be the first current open dataset |

## 4. Licensing

**Not legal advice.** This is a lay reading of the Wikimedia Terms of Use, the Creative Commons licence texts and the UK/EU case law commonly cited on database protection. If the project ever earns money or attracts a complaint, get a solicitor to read this section.

### What CC BY-SA 4.0 covers on the Wikipedia pages

Wikipedia text is licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). That licence protects *creative expression*: the prose ("Each couple performed one unlearned dance. Shirley Ballas had the casting vote"), footnote wording ("This couple was excused from competing due to illness or injury, and was granted a bye to the following week"), theme descriptions, and arguably the selection and arrangement of the tables. If you copy that expression you must attribute, keep the licence notice, and release modified text under CC BY-SA 4.0 or later, marked as modified. The [Wikimedia Terms of Use, section 7](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) say re-users may attribute with a hyperlink or URL to the page (or a stable copy), or by listing the authors.

What CC BY-SA does **not** cover is the facts themselves. Who danced what, to which song, on which date, and what marks the judges gave are facts that happened on television. In UK and EU law copyright needs the author's own intellectual creation (*Infopaq*, 2009; *Football Dataco v Yahoo!*, 2012, on football fixture lists), and a Wikipedia editor who types in "29 (6, 8, 7, 8)" has created nothing original. Extracting the facts is therefore free of the ShareAlike obligation.

### What the UK database right means

Separately from copyright, the UK has a *sui generis* database right (Copyright and Rights in Databases Regulations 1997, originally from the EU Database Directive): 15 years of protection for a database where there was substantial investment in *obtaining, verifying or presenting* its contents. Two points matter here:

1. **Wikipedia as a database.** The Terms of Use state that contributors waive any sui generis database rights covered by CC BY-SA 4.0, and the licence itself (section 4) expressly licenses database rights where they exist. The Terms give the example that "facts you contribute to the projects may be reused freely without attribution". So bulk extraction of the factual content from the series pages is clean.
2. **Our own database.** Our extraction, validation and modelling plausibly counts as substantial investment in obtaining and verifying, so a UK database right in *our* dataset would arise automatically (*British Horseracing Board v William Hill*, 2004, excludes investment in *creating* the data, but that is the BBC's investment, not ours). We do not want that right to bite anyone using the JSON:API or the CSVs, so we waive or license it explicitly. Since Brexit the right is UK-only in any case.

### Recommended licences

| Layer | Licence | Why |
|---|---|---|
| Structured data (CSV/Parquet fact tables, lookup tables, Drupal content) | **CC0 1.0** (or CC BY 4.0 if attribution matters to you) | We re-use facts, not expression, so no ShareAlike obligation is inherited. CC0 is what Four Tens chose and is the least friction for Pandas/R users and for Drupal JSON:API consumers. CC0 also waives our own database right |
| Code (fetch scripts, parser, Drupal module and Recipe) | **MIT** (or Apache-2.0) | Keep it separate from the data licence; both are standard for Kit Perform repos |
| Quoted Wikipedia prose (any field that copies page text verbatim: episode intros, `efn` note text, theme descriptions) | **CC BY-SA 4.0**, attributed to the page URL and revision id | It is Wikipedia's expression. Preferred route for the declarative model: do not copy it at all, normalise it into enumerated codes (`note_type = bye_injury`, `casting_vote_judge = ballas`). Where the original wording is worth keeping, put it in a clearly labelled `source_note` field with `source_url` and `source_revid`, and license the site's text layer CC BY-SA 4.0 |

**Do not use ODbL** for the data. Creative Commons lists only the Free Art License 1.3 and GPLv3 as one-way compatible with BY-SA 4.0, so any BY-SA input could not be relicensed as ODbL, and ODbL's share-alike would burden every downstream analyst. CC BY-SA on the whole database is likewise stricter than the facts require.

### Attribution practice

- Every Series and Episode record (and every fact row that can carry it) stores `source_url` (`https://en.wikipedia.org/wiki/Strictly_Come_Dancing_series_N`), `source_revid` and `source_fetched_at`. A `source_revision` lookup table (pageid, revid, parentid, timestamp, user, comment, sha1, size, fetched_at) means Pandas can answer "which Wikipedia revision is this score from?" with a join.
- Site footer and JSON:API root: "Results data compiled from Wikipedia (CC BY-SA 4.0): facts re-used; descriptive notes quoted under CC BY-SA 4.0 with links to the source revisions. Data released under CC0 1.0; code MIT."
- Link to the BBC as the original broadcaster by name only (nominative use). No BBC logos, the Strictly logotype or glitterball imagery: those are trademarks and nothing above licenses them.
- Keep a `LICENCE-data`, `LICENCE-code` and `ATTRIBUTION.md` in the repo so the three layers are obvious to anyone who clones it.

## 5. Live-series strategy

### What was observed on series 24

The page `Strictly Come Dancing series 24` was created on 2026-05-14 and had 761 revisions by 8 November. Edits come in bursts on Saturday evenings as scores are typed in live (66 edits on 2026-10-10, 51 on 2026-09-26, 46 on 2026-10-24, 33 on 2026-10-31), a smaller Sunday burst for results (10 on 2026-11-01), then a Monday trickle (8). Edit summaries name the section touched (`/* Week 8 */`, `/* Dance chart */`, `/* Scoring chart */`).

Two things follow for the model, not just the pipeline:

1. **Editors pre-create the next week.** On 8 November the Week 8 table already existed with 9 couples and some dances and songs filled in, but blank Scores and Result cells, hours before the show aired. So "the week exists" is not "the week is complete". Completeness has to be a status on the Episode (and on each Performance), as data: `scheduled` (table exists, no scores), `scores_in` (all Scores cells parse and totals equal the sum of marks), `results_in` (all Result cells non-empty, dance-off recorded), `verified` (a stable revision has been reviewed and promoted). "Planned but not danced" is the natural reading of a `scheduled` performance that never gets a score.
2. **Half-edited tables are normal during a burst.** A fetch mid-burst can legitimately see a row whose total does not match its marks or whose Result is still blank at 22:00 on Saturday. The pipeline must validate and keep serving the last good revision rather than publishing garbage.

By contrast, series 1 had 24 revisions in two years. Old series need weekly, not hourly, attention.

### Recommended pipeline

1. **Change probe.** Poll `action=query&prop=info&titles=Strictly_Come_Dancing_series_24` (about 500 bytes) or the REST `/page/summary` and compare `lastrevid` with the stored one. Nothing is fetched when nothing changed. For belt and braces, `action=raw` honours `If-Modified-Since` and the REST HTML honours `If-None-Match` (both returned 304 in testing), so even a full fetch costs nothing when the page is unchanged.
2. **Cadence (UK time), during the series (September to December):** every 15 minutes from 18:00 to 23:59 on Saturday and Sunday; hourly Monday to Friday. Off-season: daily for the latest series. All older series: weekly. Add `maxlag=5` and a 1-2 second sleep; on a `maxlag` error wait five seconds and retry. In GitHub Actions this is three cron lines; locally it is a launchd/cron job.
3. **On change, fetch and store the revision.** `prop=revisions&rvprop=ids|timestamp|user|comment|sha1|size|content&rvslots=main` for the page, then write `data/wikipedia/wikitext/024/<revid>.wikitext` and `<revid>.json` (metadata including `fetched_at`). Keep `user` and `comment`: they let you trace vandalism or later corrections. Sizing: 63 KB per revision; polling every 15 minutes captures perhaps 20-30 revisions on a busy Saturday, not all 60, so a whole series is a few MB. If the repo grows uncomfortable, keep only revisions where the *parsed* output changed (compare a hash of the parsed fact tables) and record the skipped revids in the metadata.
4. **Debounce.** Do not treat a revision as stable until there has been no new revision for about ten minutes. Parse immediately for monitoring, but only promote a snapshot to "stable" after the quiet period.
5. **Validate before publishing.** Row total equals the sum of judge marks; the number of marks equals the number of judges in the panel table for that episode; no unknown templates; after Sunday night every Result cell for the aired week is non-empty; derived scoring-chart totals match the page's own Scoring chart. On failure, keep serving the previous good revision and flag for review.
6. **Week-by-week snapshots.** For each aired week fetch the Sunday-night (or Monday-morning) revision via `action=parse&oldid=` or `/page/html/{title}/{revid}` and store it. This is what lets the parser's tests replay series 22 and 23 week by week and is the basis for "as it looked at the time" provenance.
7. **Drupal.** A cron-driven migration (Python writes CSV/JSON keyed on natural keys, Migrate reads it) with the migration high-water mark set to the revid, so re-running is idempotent. Only `verified` or `results_in` rows reach the public site; `scheduled` rows may be shown as "coming up".

EventStreams works (an edit event arrived one second after revision 1384551315) and supports `since=` replay, but it is a client-filtered firehose with 15-minute reconnects. Not worth a daemon for one page. The Atom history feed is a pleasant thing to put in a feed reader on a Saturday night.

## 6. What this means for the existing captures and `scripts/fetch-wikipedia.sh`

### Keep the HTML captures

`data/wikipedia/series/0NN/*.html` (8.1 MB for 24 series plus the main article) stays. Rendered HTML is what a human opens to check a table, it is what `pandas.read_html` reads for cross-checks, and the Parsoid fallback is HTML too. The existing captures are also already provenanced, if indirectly: the page's embedded `mw.config` carries the revision, e.g. the series 24 capture holds `"wgRevisionId":1384551432`, which is the same revision the API tests saw. A one-off pass can extract that into a sidecar `.json` for every existing capture:

```sh
grep -o '"wgRevisionId":[0-9]*' data/wikipedia/series/024/Strictly_Come_Dancing_series_24.html
```

### Add wikitext and revision metadata

New layout, alongside the HTML:

```
data/wikipedia/
  main/Strictly_Come_Dancing.html
  series/024/Strictly_Come_Dancing_series_24.html        # rendered HTML (as now)
  series/024/Strictly_Come_Dancing_series_24.html.json   # sidecar: revid, fetched_at, url (new)
  wikitext/024/1384551432.wikitext                        # raw wikitext of that revision (new)
  wikitext/024/1384551432.json                            # pageid, revid, parentid, timestamp, user, comment, sha1, size, fetched_at (new)
  wikitext/024/LATEST                                     # the revid most recently fetched (new)
```

Two changes to the script's behaviour: fetch the wikitext through the Action API so the revid, sha1 and timestamp come with it; and add an `--if-changed` mode that compares `prop=info` `lastrevid` with `LATEST` and skips the download when nothing has moved, which is what the live-series cron will call.

### Sketch of the extended script

Dependencies: `curl` and `python3` (standard library only). Single quotes around the Python keep the shell out of it.

```sh
#!/usr/bin/env sh
# Fetch (or refresh) the Wikipedia captures this project is built on:
#   1. rendered HTML        data/wikipedia/series/0NN/Strictly_Come_Dancing_series_N.html (+ .json sidecar)
#   2. raw wikitext         data/wikipedia/wikitext/0NN/<revid>.wikitext
#   3. revision metadata    data/wikipedia/wikitext/0NN/<revid>.json
#   4. latest pointer       data/wikipedia/wikitext/0NN/LATEST
#
# Usage:
#   scripts/fetch-wikipedia.sh                 # main article + series 1..LATEST
#   scripts/fetch-wikipedia.sh 23 24           # only these series
#   scripts/fetch-wikipedia.sh --if-changed 24 # fetch only if Wikipedia's lastrevid differs from LATEST
#
# Etiquette: https://www.mediawiki.org/wiki/API:Etiquette and
# https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
set -eu

LATEST=24
UA="strictly.kitperform.science/0.2 (https://github.com/kitperform/strictly.kitperform.science; contact@example)"
API="https://en.wikipedia.org/w/api.php"
ROOT="$(cd "$(dirname "$0")/.." && pwd)/data/wikipedia"
IF_CHANGED=0

if [ "${1:-}" = "--if-changed" ]; then IF_CHANGED=1; shift; fi

now_utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# Call the Action API; retry once on maxlag (the server asks us to wait).
api() {
  url="$API?$1&format=json&formatversion=2&maxlag=5"
  out=$(curl -fsSL --compressed -A "$UA" "$url")
  case "$out" in
    *'"code":"maxlag"'*) sleep 5; out=$(curl -fsSL --compressed -A "$UA" "$url") ;;
  esac
  printf '%s' "$out"
}

# $1 = title -> prints Wikipedia's current lastrevid
lastrevid() {
  api "action=query&prop=info&titles=$1" | python3 -I -c \
    'import json,sys; print(json.load(sys.stdin)["query"]["pages"][0]["lastrevid"])'
}

# $1 = title, $2 = destination HTML path. Rendered page plus a sidecar with the embedded revid.
fetch_html() {
  mkdir -p "$(dirname "$2")"
  curl -fsSL -A "$UA" "https://en.wikipedia.org/wiki/$1" -o "$2"
  revid=$(grep -o '"wgRevisionId":[0-9]*' "$2" | head -1 | cut -d: -f2)
  printf '{"title": "%s", "url": "https://en.wikipedia.org/wiki/%s", "revid": %s, "fetched_at": "%s"}\n' \
    "$1" "$1" "${revid:-null}" "$(now_utc)" > "$2.json"
  printf '%8d bytes  %s (revid %s)\n' "$(wc -c < "$2")" "$2" "${revid:-?}"
  sleep 1
}

# $1 = title, $2 = destination directory. Latest revision's wikitext + metadata via prop=revisions.
fetch_wikitext() {
  mkdir -p "$2"
  api "action=query&prop=revisions&titles=$1&rvprop=ids|timestamp|user|comment|sha1|size|content&rvslots=main" \
  | python3 -I -c '
import json, sys, pathlib, datetime
d = json.load(sys.stdin)
if "error" in d:
    sys.exit("API error: %s" % d["error"])
page = d["query"]["pages"][0]
rev = page["revisions"][0]
out = pathlib.Path(sys.argv[1])
revid = rev["revid"]
(out / f"{revid}.wikitext").write_text(rev["slots"]["main"]["content"], encoding="utf-8")
meta = {
    "title": page["title"], "pageid": page["pageid"],
    "revid": revid, "parentid": rev.get("parentid"),
    "timestamp": rev["timestamp"], "user": rev.get("user"), "comment": rev.get("comment"),
    "sha1": rev["sha1"], "size": rev["size"],
    "url": "https://en.wikipedia.org/w/index.php?title=%s&oldid=%d" % (page["title"].replace(" ", "_"), revid),
    "fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}
(out / f"{revid}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
(out / "LATEST").write_text(f"{revid}\n")
print("%8d bytes  %s/%d.wikitext (%s by %s)" % (rev["size"], out, revid, rev["timestamp"], rev.get("user")))
' "$2"
  sleep 1
}

if [ "$#" -eq 0 ]; then
  fetch_html "Strictly_Come_Dancing" "$ROOT/main/Strictly_Come_Dancing.html"
  fetch_wikitext "Strictly_Come_Dancing" "$ROOT/wikitext/main"
  set -- $(seq 1 "$LATEST")
fi

for n in "$@"; do
  padded=$(printf '%03d' "$n")
  title="Strictly_Come_Dancing_series_$n"
  wtdir="$ROOT/wikitext/$padded"
  if [ "$IF_CHANGED" -eq 1 ] && [ -f "$wtdir/LATEST" ]; then
    current=$(lastrevid "$title")
    if [ "$current" = "$(cat "$wtdir/LATEST")" ]; then
      printf 'unchanged  series %s (revid %s)\n' "$n" "$current"
      sleep 1
      continue
    fi
  fi
  fetch_wikitext "$title" "$wtdir"
  fetch_html "$title" "$ROOT/series/$padded/$title.html"
done
```

Notes on the sketch:

- It fetches one title per call for simplicity. Batching several titles into one `titles=A|B|C` request is allowed (that is how the three-series test was done) and would cut the full run to a handful of calls; the per-title loop is clearer and 24 calls with a one-second sleep is well within etiquette.
- The `--if-changed` probe plus the `LATEST` pointer is all the live-series cron needs: `scripts/fetch-wikipedia.sh --if-changed 24` every 15 minutes on Saturday and Sunday evenings, hourly in the week. The parse-validate-promote steps from section 5 sit downstream in Python and read `wikitext/024/<revid>.wikitext`.
- A later `fetch-revision.sh <series> <revid>` (using `action=parse&oldid=` or `action=raw&oldid=`) fills in the week-by-week historical snapshots for series 22-24 described in section 5, step 6.
- If the Parsoid fallback is ever needed, add a `fetch_parsoid` function hitting `https://en.wikipedia.org/api/rest_v1/page/html/$title` with `-D` to capture the `ETag`/`content-revision-id` headers into the sidecar, and keep the base URL in a variable because RESTBase is being replaced by `/w/rest.php/v1/page/{title}/html`.
- The HTML sidecar and the wikitext metadata both record a `revid`, so a mismatch between the two (page edited in the second between the two requests) is visible rather than silent; the wikitext metadata is the one the fact tables should reference.

## Sources

The research behind this document called each of these on 8 November 2026:

- `https://en.wikipedia.org/w/api.php` with `action=query&prop=revisions`, `action=query&prop=info`, `action=parse` (`prop=sections|wikitext|text|templates`, `section=5`, `oldid=1376862102`)
- `https://en.wikipedia.org/w/index.php?title=Strictly_Come_Dancing_series_24&action=raw` (304 on `If-Modified-Since`) and `&action=history&feed=atom`
- `https://en.wikipedia.org/api/rest_v1/page/{html,summary,mobile-html}/Strictly_Come_Dancing_series_24`, `/page/html/.../1376862102`, `/?spec`
- `https://stream.wikimedia.org/v2/stream/recentchange` (10-second sample and `since=` replay)
- `https://query.wikidata.org/sparql`, `https://www.wikidata.org/w/api.php?action=wbgetentities`
- `https://dbpedia.org/data/Strictly_Come_Dancing_series_21.ttl`
- `https://dumps.wikimedia.org/enwiki/latest/`, `https://dumps.wikimedia.org/other/enterprise_html/runs/`, `https://enterprise.wikimedia.com/api/`
- GitHub API and raw files for four-tens/strictly-come-dancing-results and jongiddy/strictly-data; awbirdsall.github.io; ultimatestrictly.com; strictlydb.com (statistics and copyright pages); bbc.co.uk/programmes/b006m8dq.json; strictlycomedancing.fandom.com; Hugging Face datasets search; PyPI metadata for the Python packages named above
- `https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use` (section 7), `https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content`, `https://en.wikipedia.org/wiki/Database_right`, `https://creativecommons.org/share-your-work/licensing-considerations/compatible-licenses/`, `https://opendatacommons.org/licenses/odbl/summary/`
- Local: `scripts/fetch-wikipedia.sh`, `data/wikipedia/series/024/Strictly_Come_Dancing_series_24.html`, `data-model.md`, `data-modelling-thinking.md`
