# Build report for S11

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 13 |
| `episodes.csv` | 27 |
| `panel_seats.csv` | 60 |
| `results_rounds.csv` | 13 |
| `results_round_weeks.csv` | 14 |
| `people.csv` | 34 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 34 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 146 |
| `performance_music.csv` | 150 |
| `songs.csv` | 135 |
| `artists.csv` | 112 |
| `judge_marks.csv` | 560 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 16 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 225 |
| `crosscheck/chart_legends.csv` | 8 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S11R01-02: eliminated couple has fewest save votes ({'S11-julien-macdonald': 3})
- PASS: round S11R03: eliminated couple has fewest save votes ({'S11-julien-macdonald': 3})
- PASS: round S11R04: eliminated couple has fewest save votes ({'S11-rachel-riley': 3})
- PASS: round S11R05: eliminated couple has fewest save votes ({'S11-patrick-robinson': 3})
- PASS: round S11R06: eliminated couple has fewest save votes ({'S11-abbey-clancy': 3})
- PASS: round S11R07: eliminated couple has fewest save votes ({'S11-mark-benton': 3})
- PASS: round S11R08: eliminated couple has fewest save votes ({'S11-fiona-fullerton': 1, 'S11-mark-benton': 3})
- PASS: round S11R09: eliminated couple has fewest save votes ({'S11-ben-cohen': 1, 'S11-mark-benton': 3})
- PASS: round S11R10: eliminated couple has fewest save votes ({'S11-ashley-taylor-dawson': 3})
- PASS: round S11R11: eliminated couple has fewest save votes ({'S11-patrick-robinson': 3})
- PASS: round S11R12: eliminated couple has fewest save votes ({'S11-natalie-gumede': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S11R01-02 (1 vs 1)
- PASS: check 5: exit_count S11R03 (1 vs 1)
- PASS: check 5: exit_count S11R04 (1 vs 1)
- PASS: check 5: exit_count S11R05 (1 vs 1)
- PASS: check 5: exit_count S11R06 (1 vs 1)
- PASS: check 5: exit_count S11R07 (1 vs 1)
- PASS: check 5: exit_count S11R08 (1 vs 1)
- PASS: check 5: exit_count S11R09 (1 vs 1)
- PASS: check 5: exit_count S11R10 (1 vs 1)
- PASS: check 5: exit_count S11R11 (1 vs 1)
- PASS: check 5: exit_count S11R12 (1 vs 1)
- PASS: check 5: exit_count S11R13a (1 vs 1)
- PASS: check 5: exit_count S11R13b (0 vs 0)
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
