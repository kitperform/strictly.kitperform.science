# Build report for S05

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 12 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 48 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 12 |
| `people.csv` | 32 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 32 |
| `couples.csv` | 14 |
| `couple_partnerships.csv` | 14 |
| `couple_labels.csv` | 42 |
| `couple_weeks.csv` | 168 |
| `performances.csv` | 116 |
| `performance_music.csv` | 105 |
| `songs.csv` | 99 |
| `artists.csv` | 85 |
| `judge_marks.csv` | 404 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 16 |
| `themes.csv` | 0 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 168 |
| `crosscheck/chart_legends.csv` | 7 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (14 couples)
- PASS: round S05R01: eliminated couple has fewest save votes ({'S05-brian-capron': 1, 'S05-kenny-logan': 3})
- PASS: round S05R02: eliminated couple has fewest save votes ({'S05-letitia-dean': 3, 'S05-stephanie-beacham': 1})
- PASS: round S05R03: eliminated couple has fewest save votes ({'S05-john-barnes': 3})
- PASS: round S05R04: eliminated couple has fewest save votes ({'S05-gabby-logan': 1, 'S05-penny-lancaster': 3})
- PASS: round S05R05: eliminated couple has fewest save votes ({'S05-john-barnes': 3})
- PASS: round S05R06: eliminated couple has fewest save votes ({'S05-matt-di-angelo': 3, 'S05-penny-lancaster': 1})
- PASS: round S05R07: eliminated couple has fewest save votes ({'S05-john-barnes': 3})
- PASS: round S05R08: eliminated couple has fewest save votes ({'S05-kelly-brook': 3})
- PASS: round S05R09: eliminated couple has fewest save votes ({'S05-letitia-dean': 3})
- PASS: round S05R10: eliminated couple has fewest save votes ({'S05-alesha-dixon': 3})
- PASS: round S05R11: eliminated couple has fewest save votes ({'S05-matt-di-angelo': 3, 'S05-gethin-jones': 1})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S05R01 (1 vs 1)
- PASS: check 5: exit_count S05R02 (1 vs 1)
- PASS: check 5: exit_count S05R03 (1 vs 1)
- PASS: check 5: exit_count S05R04 (1 vs 1)
- PASS: check 5: exit_count S05R05 (1 vs 1)
- PASS: check 5: exit_count S05R06 (1 vs 1)
- PASS: check 5: exit_count S05R07 (1 vs 1)
- PASS: check 5: exit_count S05R08 (1 vs 1)
- PASS: check 5: exit_count S05R09 (1 vs 1)
- PASS: check 5: exit_count S05R10 (1 vs 1)
- PASS: check 5: exit_count S05R11 (1 vs 1)
- PASS: check 5: exit_count S05R12 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (168 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
