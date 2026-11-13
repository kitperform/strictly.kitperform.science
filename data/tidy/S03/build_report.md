# Build report for S03

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 1 |
| `weeks.csv` | 10 |
| `episodes.csv` | 18 |
| `panel_seats.csv` | 40 |
| `results_rounds.csv` | 10 |
| `results_round_weeks.csv` | 10 |
| `people.csv` | 28 |
| `person_aliases.csv` | 0 |
| `series_people.csv` | 28 |
| `couples.csv` | 12 |
| `couple_partnerships.csv` | 12 |
| `couple_labels.csv` | 36 |
| `couple_weeks.csv` | 120 |
| `performances.csv` | 90 |
| `performance_music.csv` | 93 |
| `songs.csv` | 84 |
| `artists.csv` | 76 |
| `judge_marks.csv` | 348 |
| `dance_off_votes.csv` | 0 |
| `dances.csv` | 12 |
| `themes.csv` | 0 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 119 |
| `crosscheck/chart_legends.csv` | 4 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (12 couples)
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S03R01 (1 vs 1)
- PASS: check 5: exit_count S03R02 (1 vs 1)
- PASS: check 5: exit_count S03R03 (1 vs 1)
- PASS: check 5: exit_count S03R04 (1 vs 1)
- PASS: check 5: exit_count S03R05 (1 vs 1)
- PASS: check 5: exit_count S03R06 (1 vs 1)
- PASS: check 5: exit_count S03R07 (1 vs 1)
- PASS: check 5: exit_count S03R08 (1 vs 1)
- PASS: check 5: exit_count S03R09 (1 vs 1)
- PASS: check 5: exit_count S03R10 (1 vs 1)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (120 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
