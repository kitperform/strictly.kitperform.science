# Build report for S18

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 2 |
| `weeks.csv` | 9 |
| `episodes.csv` | 17 |
| `panel_seats.csv` | 36 |
| `results_rounds.csv` | 8 |
| `results_round_weeks.csv` | 9 |
| `people.csv` | 28 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 29 |
| `couples.csv` | 12 |
| `couple_partnerships.csv` | 12 |
| `couple_labels.csv` | 36 |
| `couple_weeks.csv` | 108 |
| `performances.csv` | 87 |
| `performance_music.csv` | 95 |
| `songs.csv` | 80 |
| `artists.csv` | 64 |
| `judge_marks.csv` | 261 |
| `dance_off_votes.csv` | 21 |
| `dances.csv` | 17 |
| `themes.csv` | 2 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 120 |
| `crosscheck/chart_legends.csv` | 7 |

## Checks

- PASS: judge order sentence found (3 judges)
- PASS: couples parsed (12 couples)
- PASS: round S18R01-02: eliminated couple has fewest save votes ({'S18-jamie-laing': 2})
- PASS: round S18R03: eliminated couple has fewest save votes ({'S18-nicola-adams': 2})
- PASS: round S18R04: eliminated couple has fewest save votes ({'S18-maisie-smith': 2})
- PASS: round S18R05: eliminated couple has fewest save votes ({'S18-maisie-smith': 2})
- PASS: round S18R06: eliminated couple has fewest save votes ({'S18-clara-amfo': 1, 'S18-jamie-laing': 2})
- PASS: round S18R07: eliminated couple has fewest save votes ({'S18-jamie-laing': 2, 'S18-jj-chalmers': 1})
- PASS: round S18R08: eliminated couple has fewest save votes ({'S18-jamie-laing': 2, 'S18-ranvir-singh': 1})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S18R01-02 (1 vs 1)
- PASS: check 5: exit_count S18R03 (1 vs 1)
- PASS: check 5: exit_count S18R04 (1 vs 1)
- PASS: check 5: exit_count S18R05 (1 vs 1)
- PASS: check 5: exit_count S18R06 (1 vs 1)
- PASS: check 5: exit_count S18R07 (1 vs 1)
- PASS: check 5: exit_count S18R08 (1 vs 1)
- PASS: check 5: exit_count S18R09 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (108 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
