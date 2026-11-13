# Build report for S06

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 6 |
| `weeks.csv` | 14 |
| `episodes.csv` | 29 |
| `panel_seats.csv` | 56 |
| `results_rounds.csv` | 14 |
| `results_round_weeks.csv` | 15 |
| `people.csv` | 36 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 36 |
| `couples.csv` | 16 |
| `couple_partnerships.csv` | 16 |
| `couple_labels.csv` | 48 |
| `couple_weeks.csv` | 224 |
| `performances.csv` | 148 |
| `performance_music.csv` | 121 |
| `songs.csv` | 113 |
| `artists.csv` | 94 |
| `judge_marks.csv` | 464 |
| `dance_off_votes.csv` | 48 |
| `dances.csv` | 17 |
| `themes.csv` | 0 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 4 |
| `crosscheck/chart_cells.csv` | 240 |
| `crosscheck/chart_legends.csv` | 8 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (16 couples)
- PASS: round S06R01: eliminated couple has fewest save votes ({'S06-phil-daniels': 2, 'S06-don-warrington': 2})
- PASS: round S06R02: eliminated couple has fewest save votes ({'S06-jodie-kidd': 3})
- PASS: round S06R03: eliminated couple has fewest save votes ({'S06-mark-foster': 3})
- PASS: round S06R04: eliminated couple has fewest save votes ({'S06-heather-small': 3})
- PASS: round S06R05: eliminated couple has fewest save votes ({'S06-heather-small': 3})
- PASS: round S06R06: eliminated couple has fewest save votes ({'S06-andrew-castle': 3})
- PASS: round S06R07: eliminated couple has fewest save votes ({'S06-heather-small': 3})
- PASS: round S06R08: eliminated couple has fewest save votes ({'S06-rachel-stevens': 3})
- PASS: round S06R09: eliminated couple has fewest save votes ({'S06-lisa-snowdon': 3, 'S06-cherie-lunghi': 1})
- PASS: round S06R10: eliminated couple has fewest save votes ({'S06-lisa-snowdon': 3})
- PASS: round S06R11: eliminated couple has fewest save votes ({'S06-rachel-stevens': 3})
- PASS: round S06R12: eliminated couple has fewest save votes ({'S06-lisa-snowdon': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S06R01 (1 vs 1)
- PASS: check 5: exit_count S06R02 (1 vs 1)
- PASS: check 5: exit_count S06R03 (1 vs 1)
- PASS: check 5: exit_count S06R04 (1 vs 1)
- PASS: check 5: exit_count S06R05 (1 vs 1)
- PASS: check 5: exit_count S06R06 (1 vs 1)
- PASS: check 5: exit_count S06R07 (1 vs 1)
- PASS: check 5: exit_count S06R08 (1 vs 1)
- PASS: check 5: exit_count S06R09 (1 vs 1)
- PASS: check 5: exit_count S06R10 (1 vs 1)
- PASS: check 5: exit_count S06R11 (1 vs 1)
- PASS: check 5: exit_count S06R12 (1 vs 1)
- PASS: check 5: exit_count S06R13 (0 vs 0)
- PASS: check 5: exit_count S06R13-14 (1 vs 1)
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
