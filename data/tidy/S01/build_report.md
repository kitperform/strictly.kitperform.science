# Build report for S01

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 2 |
| `weeks.csv` | 8 |
| `episodes.csv` | 9 |
| `panel_seats.csv` | 32 |
| `results_rounds.csv` | 7 |
| `results_round_weeks.csv` | 8 |
| `people.csv` | 20 |
| `person_aliases.csv` | 0 |
| `series_people.csv` | 20 |
| `couples.csv` | 8 |
| `couple_partnerships.csv` | 8 |
| `couple_labels.csv` | 24 |
| `couple_weeks.csv` | 64 |
| `performances.csv` | 59 |
| `performance_music.csv` | 61 |
| `songs.csv` | 51 |
| `artists.csv` | 47 |
| `judge_marks.csv` | 216 |
| `dance_off_votes.csv` | 0 |
| `dances.csv` | 11 |
| `themes.csv` | 1 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 1 |
| `crosscheck/chart_cells.csv` | 72 |
| `crosscheck/chart_legends.csv` | 6 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (8 couples)
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S01R01-02 (1 vs 1)
- PASS: check 5: exit_count S01R03 (1 vs 1)
- PASS: check 5: exit_count S01R04 (1 vs 1)
- PASS: check 5: exit_count S01R05 (1 vs 1)
- PASS: check 5: exit_count S01R06 (1 vs 1)
- PASS: check 5: exit_count S01R07 (1 vs 1)
- PASS: check 5: exit_count S01R08 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: check 14: one seat or absent row per regular judge per episode ([])
- PASS: couple_weeks: one row per couple per week (64 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
