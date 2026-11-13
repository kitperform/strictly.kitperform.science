# Build report for S20

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 2 |
| `weeks.csv` | 13 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 52 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 39 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 39 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 141 |
| `performance_music.csv` | 176 |
| `songs.csv` | 147 |
| `artists.csv` | 123 |
| `judge_marks.csv` | 564 |
| `dance_off_votes.csv` | 40 |
| `dances.csv` | 16 |
| `themes.csv` | 5 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 2 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 12 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S20R01-02: eliminated couple has fewest save votes ({'S20-matt-goss': 3})
- PASS: round S20R03: eliminated couple has fewest save votes ({'S20-fleur-east': 3})
- PASS: round S20R04: eliminated couple has fewest save votes ({'S20-kym-marsh': 3})
- PASS: round S20R05: eliminated couple has fewest save votes ({'S20-molly-rainford': 3})
- PASS: round S20R06: eliminated couple has fewest save votes ({'S20-fleur-east': 3})
- PASS: round S20R07: eliminated couple has fewest save votes ({'S20-molly-rainford': 3})
- PASS: round S20R09: eliminated couple has fewest save votes ({'S20-molly-rainford': 3, 'S20-tyler-west': 1})
- PASS: round S20R10: eliminated couple has fewest save votes ({'S20-fleur-east': 3})
- PASS: round S20R11: eliminated couple has fewest save votes ({'S20-molly-rainford': 3, 'S20-kym-marsh': 1})
- PASS: round S20R12: eliminated couple has fewest save votes ({'S20-fleur-east': 3, 'S20-will-mellor': 1})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S20R01-02 (1 vs 1)
- PASS: check 5: exit_count S20R03 (1 vs 1)
- PASS: check 5: exit_count S20R04 (1 vs 1)
- PASS: check 5: exit_count S20R05 (1 vs 1)
- PASS: check 5: exit_count S20R06 (1 vs 1)
- PASS: check 5: exit_count S20R07 (1 vs 1)
- PASS: check 5: exit_count S20R08 (0 vs 0)
- PASS: check 5: exit_count S20R09 (1 vs 1)
- PASS: check 5: exit_count S20R10 (1 vs 1)
- PASS: check 5: exit_count S20R11 (1 vs 1)
- PASS: check 5: exit_count S20R12 (1 vs 1)
- PASS: check 5: exit_count S20R13 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (195 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
