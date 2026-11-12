# Build report for S22

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
| `people.csv` | 37 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 39 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 17 |
| `couple_labels.csv` | 49 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 148 |
| `performance_music.csv` | 169 |
| `songs.csv` | 141 |
| `artists.csv` | 116 |
| `judge_marks.csv` | 564 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 16 |
| `themes.csv` | 5 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 6 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S22R01-02: eliminated couple has fewest save votes ({'S22-toyah-willcox': 3, 'S22-tom-dean': 1})
- PASS: round S22R03: eliminated couple has fewest save votes ({'S22-paul-merson': 3})
- PASS: round S22R04: eliminated couple has fewest save votes ({'S22-shayne-ward': 3})
- PASS: round S22R05: eliminated couple has fewest save votes ({'S22-jb-gill': 3})
- PASS: round S22R06: eliminated couple has fewest save votes ({'S22-shayne-ward': 3})
- PASS: round S22R07: eliminated couple has fewest save votes ({'S22-montell-douglas': 3})
- PASS: round S22R08: eliminated couple has fewest save votes ({'S22-shayne-ward': 2, 'S22-wynne-evans': 2})
- PASS: round S22R09: eliminated couple has fewest save votes ({'S22-montell-douglas': 3})
- PASS: round S22R10: eliminated couple has fewest save votes ({'S22-montell-douglas': 3})
- PASS: round S22R11: eliminated couple has fewest save votes ({'S22-tasha-ghouri': 3})
- PASS: round S22R12: eliminated couple has fewest save votes ({'S22-tasha-ghouri': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S22R01-02 (1 vs 1)
- PASS: check 5: exit_count S22R03 (1 vs 1)
- PASS: check 5: exit_count S22R04 (1 vs 1)
- PASS: check 5: exit_count S22R05 (1 vs 1)
- PASS: check 5: exit_count S22R06 (1 vs 1)
- PASS: check 5: exit_count S22R07 (1 vs 1)
- PASS: check 5: exit_count S22R08 (1 vs 1)
- PASS: check 5: exit_count S22R09 (1 vs 1)
- PASS: check 5: exit_count S22R10 (1 vs 1)
- PASS: check 5: exit_count S22R11 (1 vs 1)
- PASS: check 5: exit_count S22R12 (1 vs 1)
- PASS: check 5: exit_count S22R13 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: couple_weeks: one row per couple per week (195 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
