# Build report for S15

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
| `people.csv` | 34 |
| `person_aliases.csv` | 6 |
| `series_people.csv` | 34 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 149 |
| `performance_music.csv` | 162 |
| `songs.csv` | 136 |
| `artists.csv` | 112 |
| `judge_marks.csv` | 556 |
| `dance_off_votes.csv` | 43 |
| `dances.csv` | 15 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 9 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S15R01-02: eliminated couple has fewest save votes ({'S15-chizzy-akudolu': 1, 'S15-brian-conley': 3})
- PASS: round S15R03: eliminated couple has fewest save votes ({'S15-simon-rimmer': 3})
- PASS: round S15R04: eliminated couple has fewest save votes ({'S15-davood-ghadami': 3})
- PASS: round S15R05: eliminated couple has fewest save votes ({'S15-simon-rimmer': 2})
- PASS: round S15R06: eliminated couple has fewest save votes ({'S15-mollie-king': 3})
- PASS: round S15R07: eliminated couple has fewest save votes ({'S15-mollie-king': 2, 'S15-aston-merrygold': 2})
- PASS: round S15R08: eliminated couple has fewest save votes ({'S15-jonnie-peacock': 3})
- PASS: round S15R09: eliminated couple has fewest save votes ({'S15-debbie-mcgee': 3})
- PASS: round S15R10: eliminated couple has fewest save votes ({'S15-alexandra-burke': 3})
- PASS: round S15R11: eliminated couple has fewest save votes ({'S15-alexandra-burke': 3})
- PASS: round S15R12: eliminated couple has fewest save votes ({'S15-gemma-atkinson': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S15R01-02 (1 vs 1)
- PASS: check 5: exit_count S15R03 (1 vs 1)
- PASS: check 5: exit_count S15R04 (1 vs 1)
- PASS: check 5: exit_count S15R05 (1 vs 1)
- PASS: check 5: exit_count S15R06 (1 vs 1)
- PASS: check 5: exit_count S15R07 (1 vs 1)
- PASS: check 5: exit_count S15R08 (1 vs 1)
- PASS: check 5: exit_count S15R09 (1 vs 1)
- PASS: check 5: exit_count S15R10 (1 vs 1)
- PASS: check 5: exit_count S15R11 (1 vs 1)
- PASS: check 5: exit_count S15R12 (1 vs 1)
- PASS: check 5: exit_count S15R13 (0 vs 0)
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
