# Build report for S10

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 12 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 56 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 33 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 33 |
| `couples.csv` | 14 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 42 |
| `couple_weeks.csv` | 168 |
| `performances.csv` | 125 |
| `performance_music.csv` | 126 |
| `songs.csv` | 118 |
| `artists.csv` | 88 |
| `judge_marks.csv` | 500 |
| `dance_off_votes.csv` | 40 |
| `dances.csv` | 15 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 196 |
| `crosscheck/chart_legends.csv` | 6 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (14 couples)
- PASS: round S10R01-02: eliminated couple has fewest save votes ({'S10-richard-arnold': 3})
- PASS: round S10R03: eliminated couple has fewest save votes ({'S10-michael-vaughan': 3, 'S10-jerry-hall': 1})
- PASS: round S10R04: eliminated couple has fewest save votes ({'S10-colin-salmon': 3})
- PASS: round S10R05: eliminated couple has fewest save votes ({'S10-richard-arnold': 3})
- PASS: round S10R06: eliminated couple has fewest save votes ({'S10-kimberley-walsh': 3})
- PASS: round S10R07: eliminated couple has fewest save votes ({'S10-nicky-byrne': 3})
- PASS: round S10R08: eliminated couple has fewest save votes ({'S10-michael-vaughan': 3})
- PASS: round S10R09: eliminated couple has fewest save votes ({'S10-nicky-byrne': 3})
- PASS: round S10R10: eliminated couple has fewest save votes ({'S10-denise-van-outen': 3})
- PASS: round S10R11: eliminated couple has fewest save votes ({'S10-denise-van-outen': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S10R01-02 (1 vs 1)
- PASS: check 5: exit_count S10R03 (1 vs 1)
- PASS: check 5: exit_count S10R04 (1 vs 1)
- PASS: check 5: exit_count S10R05 (1 vs 1)
- PASS: check 5: exit_count S10R06 (1 vs 1)
- PASS: check 5: exit_count S10R07 (1 vs 1)
- PASS: check 5: exit_count S10R08 (1 vs 1)
- PASS: check 5: exit_count S10R09 (1 vs 1)
- PASS: check 5: exit_count S10R10 (1 vs 1)
- PASS: check 5: exit_count S10R11 (1 vs 1)
- PASS: check 5: exit_count S10R12a (1 vs 1)
- PASS: check 5: exit_count S10R12b (0 vs 0)
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
