# Build report for S08

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 12 |
| `episodes.csv` | 26 |
| `panel_seats.csv` | 60 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 33 |
| `person_aliases.csv` | 0 |
| `series_people.csv` | 34 |
| `couples.csv` | 14 |
| `couple_partnerships.csv` | 16 |
| `couple_labels.csv` | 43 |
| `couple_weeks.csv` | 168 |
| `performances.csv` | 128 |
| `performance_music.csv` | 137 |
| `songs.csv` | 120 |
| `artists.csv` | 106 |
| `judge_marks.csv` | 492 |
| `dance_off_votes.csv` | 0 |
| `dances.csv` | 16 |
| `themes.csv` | 3 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 1 |
| `crosscheck/chart_cells.csv` | 196 |
| `crosscheck/chart_legends.csv` | 9 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (14 couples)
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S08R01-02 (1 vs 1)
- PASS: check 5: exit_count S08R03 (1 vs 1)
- PASS: check 5: exit_count S08R04 (1 vs 1)
- PASS: check 5: exit_count S08R05 (1 vs 1)
- PASS: check 5: exit_count S08R06 (1 vs 1)
- PASS: check 5: exit_count S08R07 (1 vs 1)
- PASS: check 5: exit_count S08R08 (1 vs 1)
- PASS: check 5: exit_count S08R09 (1 vs 1)
- PASS: check 5: exit_count S08R10 (1 vs 1)
- PASS: check 5: exit_count S08R11 (2 vs 2)
- PASS: check 5: exit_count S08R12a (1 vs 1)
- PASS: check 5: exit_count S08R12b (0 vs 0)
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
