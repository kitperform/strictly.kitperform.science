# Build report for S04

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 12 |
| `episodes.csv` | 23 |
| `panel_seats.csv` | 48 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 12 |
| `people.csv` | 32 |
| `person_aliases.csv` | 0 |
| `series_people.csv` | 32 |
| `couples.csv` | 14 |
| `couple_partnerships.csv` | 14 |
| `couple_labels.csv` | 42 |
| `couple_weeks.csv` | 168 |
| `performances.csv` | 110 |
| `performance_music.csv` | 97 |
| `songs.csv` | 92 |
| `artists.csv` | 81 |
| `judge_marks.csv` | 380 |
| `dance_off_votes.csv` | 0 |
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
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S04R01 (1 vs 1)
- PASS: check 5: exit_count S04R02 (1 vs 1)
- PASS: check 5: exit_count S04R03 (1 vs 1)
- PASS: check 5: exit_count S04R04 (1 vs 1)
- PASS: check 5: exit_count S04R05 (1 vs 1)
- PASS: check 5: exit_count S04R06 (1 vs 1)
- PASS: check 5: exit_count S04R07 (1 vs 1)
- PASS: check 5: exit_count S04R08 (1 vs 1)
- PASS: check 5: exit_count S04R09 (1 vs 1)
- PASS: check 5: exit_count S04R10 (1 vs 1)
- PASS: check 5: exit_count S04R11 (1 vs 1)
- PASS: check 5: exit_count S04R12 (0 vs 0)
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
