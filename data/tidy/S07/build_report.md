# Build report for S07

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 4 |
| `weeks.csv` | 14 |
| `episodes.csv` | 18 |
| `panel_seats.csv` | 72 |
| `results_rounds.csv` | 14 |
| `results_round_weeks.csv` | 14 |
| `people.csv` | 37 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 37 |
| `couples.csv` | 16 |
| `couple_partnerships.csv` | 16 |
| `couple_labels.csv` | 48 |
| `couple_weeks.csv` | 224 |
| `performances.csv` | 146 |
| `performance_music.csv` | 151 |
| `songs.csv` | 138 |
| `artists.csv` | 117 |
| `judge_marks.csv` | 586 |
| `dance_off_votes.csv` | 49 |
| `dances.csv` | 17 |
| `themes.csv` | 1 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 224 |
| `crosscheck/chart_legends.csv` | 11 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (16 couples)
- PASS: round S07R01: eliminated couple has fewest save votes ({'S07-martina-hingis': 2, 'S07-rav-wilding': 2})
- PASS: round S07R02: eliminated couple has fewest save votes ({'S07-craig-kelly': 3})
- PASS: round S07R03: eliminated couple has fewest save votes ({'S07-lynda-bellingham': 3})
- PASS: round S07R04: eliminated couple has fewest save votes ({'S07-lynda-bellingham': 2, 'S07-craig-kelly': 2})
- PASS: round S07R05: eliminated couple has fewest save votes ({'S07-zoe-lucker': 3})
- PASS: round S07R06: eliminated couple has fewest save votes ({'S07-jade-johnson': 3})
- PASS: round S07R07: eliminated couple has fewest save votes ({'S07-ali-bastian': 3, 'S07-zoe-lucker': 1})
- PASS: round S07R08: eliminated couple has fewest save votes ({'S07-ricky-groves': 3})
- PASS: round S07R09: eliminated couple has fewest save votes ({'S07-ricky-groves': 2, 'S07-phil-tufnell': 2})
- PASS: round S07R10: eliminated couple has fewest save votes ({'S07-laila-rouass': 3})
- PASS: round S07R11: eliminated couple has fewest save votes ({'S07-ricky-whittle': 3})
- PASS: round S07R12: eliminated couple has fewest save votes ({'S07-ricky-whittle': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S07R01 (1 vs 1)
- PASS: check 5: exit_count S07R02 (1 vs 1)
- PASS: check 5: exit_count S07R03 (1 vs 1)
- PASS: check 5: exit_count S07R04 (1 vs 1)
- PASS: check 5: exit_count S07R05 (1 vs 1)
- PASS: check 5: exit_count S07R06 (1 vs 1)
- PASS: check 5: exit_count S07R07 (1 vs 1)
- PASS: check 5: exit_count S07R08 (1 vs 1)
- PASS: check 5: exit_count S07R09 (1 vs 1)
- PASS: check 5: exit_count S07R10 (1 vs 1)
- PASS: check 5: exit_count S07R11 (1 vs 1)
- PASS: check 5: exit_count S07R12 (1 vs 1)
- PASS: check 5: exit_count S07R13 (1 vs 1)
- PASS: check 5: exit_count S07R14 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (224 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
