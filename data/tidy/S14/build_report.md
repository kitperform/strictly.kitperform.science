# Build report for S14

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 2 |
| `weeks.csv` | 13 |
| `episodes.csv` | 26 |
| `panel_seats.csv` | 56 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 36 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 37 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 17 |
| `couple_labels.csv` | 46 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 134 |
| `performance_music.csv` | 139 |
| `songs.csv` | 123 |
| `artists.csv` | 99 |
| `judge_marks.csv` | 512 |
| `dance_off_votes.csv` | 40 |
| `dances.csv` | 15 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 9 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S14R03: eliminated couple has fewest save votes ({'S14-laura-whitmore': 3, 'S14-tameka-empson': 1})
- PASS: round S14R04: eliminated couple has fewest save votes ({'S14-anastacia': 3})
- PASS: round S14R05: eliminated couple has fewest save votes ({'S14-daisy-lowe': 3})
- PASS: round S14R06: eliminated couple has fewest save votes ({'S14-daisy-lowe': 3})
- PASS: round S14R07: eliminated couple has fewest save votes ({'S14-ore-oduba': 3})
- PASS: round S14R08: eliminated couple has fewest save votes ({'S14-greg-rutherford': 3, 'S14-daisy-lowe': 1})
- PASS: round S14R09: eliminated couple has fewest save votes ({'S14-claudia-fragapane': 3})
- PASS: round S14R10: eliminated couple has fewest save votes ({'S14-robert-rinder': 3})
- PASS: round S14R11: eliminated couple has fewest save votes ({'S14-ore-oduba': 3})
- PASS: round S14R12: eliminated couple has fewest save votes ({'S14-danny-mac': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S14R01-02 (1 vs 1)
- PASS: check 5: exit_count S14R03 (1 vs 1)
- PASS: check 5: exit_count S14R04 (1 vs 1)
- PASS: check 5: exit_count S14R05 (1 vs 1)
- PASS: check 5: exit_count S14R06 (1 vs 1)
- PASS: check 5: exit_count S14R07 (1 vs 1)
- PASS: check 5: exit_count S14R08 (1 vs 1)
- PASS: check 5: exit_count S14R09 (1 vs 1)
- PASS: check 5: exit_count S14R10 (1 vs 1)
- PASS: check 5: exit_count S14R11 (1 vs 1)
- PASS: check 5: exit_count S14R12 (1 vs 1)
- PASS: check 5: exit_count S14R13 (0 vs 0)
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
