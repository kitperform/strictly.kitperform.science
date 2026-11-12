# Curated inputs

Small hand-maintained tables for facts the Wikipedia series page does not state
in a parseable form. Every row is data the parser reads; nothing here is code.
Each file says where the fact came from so it can be checked.

| File | What it holds |
|---|---|
| `series_meta.csv` | Per-series facts from the main article or editorial judgement: home venue, head judge, casting-vote mode |
| `series_panels.csv` | Who is a regular judge in each series and whether they are head judge (seat order is read from the page) |
| `format_rules.csv` | FormatRule rows (series default plus week/episode overrides) with the page sentence that states them |
| `couple_labels.csv` | Couple labels that cannot be resolved from first names alone (typos, mid-series relabels) |
| `dances.csv` | Dance lookup with family and known aliases |
| `venues.csv` | Venue lookup |
| `couples.csv` | Per-couple facts the tables do not carry (couple_kind for same-sex couples) |
| `chart_colours.csv` | What each Scoring-chart cell colour means when a page has no footnotes (A249) |
