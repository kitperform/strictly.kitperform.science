# Build report for S02

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 1 |
| `weeks.csv` | 8 |
| `episodes.csv` | 14 |
| `panel_seats.csv` | 32 |
| `results_rounds.csv` | 8 |
| `results_round_weeks.csv` | 8 |
| `people.csv` | 24 |
| `person_aliases.csv` | 1 |
| `series_people.csv` | 24 |
| `couples.csv` | 10 |
| `couple_partnerships.csv` | 10 |
| `couple_labels.csv` | 30 |
| `couple_weeks.csv` | 80 |
| `performances.csv` | 67 |
| `performance_music.csv` | 67 |
| `songs.csv` | 61 |
| `artists.csv` | 55 |
| `judge_marks.csv` | 256 |
| `dance_off_votes.csv` | 0 |
| `dances.csv` | 10 |
| `themes.csv` | 1 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 80 |
| `crosscheck/chart_legends.csv` | 10 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (10 couples)
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S02R01 (1 vs 1)
- PASS: check 5: exit_count S02R02 (1 vs 1)
- PASS: check 5: exit_count S02R03 (1 vs 1)
- PASS: check 5: exit_count S02R04 (1 vs 1)
- PASS: check 5: exit_count S02R05 (1 vs 1)
- PASS: check 5: exit_count S02R06 (1 vs 1)
- PASS: check 5: exit_count S02R07 (1 vs 1)
- PASS: check 5: exit_count S02R08 (1 vs 1)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (80 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
