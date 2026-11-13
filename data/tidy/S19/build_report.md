# Build report for S19

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 2 |
| `weeks.csv` | 13 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 54 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 38 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 38 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 123 |
| `performance_music.csv` | 137 |
| `songs.csv` | 121 |
| `artists.csv` | 104 |
| `judge_marks.csv` | 492 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 16 |
| `themes.csv` | 3 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 12 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S19R01-02: eliminated couple has fewest save votes ({'S19-katie-mcglynn': 3, 'S19-nina-wadia': 1})
- PASS: round S19R03: eliminated couple has fewest save votes ({'S19-judi-love': 3, 'S19-katie-mcglynn': 1})
- PASS: round S19R04: eliminated couple has fewest save votes ({'S19-judi-love': 3})
- PASS: round S19R05: eliminated couple has fewest save votes ({'S19-rhys-stephenson': 3})
- PASS: round S19R06: eliminated couple has fewest save votes ({'S19-adam-peaty': 3})
- PASS: round S19R07: eliminated couple has fewest save votes ({'S19-tilly-ramsay': 3})
- PASS: round S19R08: eliminated couple has fewest save votes ({'S19-tilly-ramsay': 3})
- PASS: round S19R09: eliminated couple has fewest save votes ({'S19-rhys-stephenson': 3})
- PASS: round S19R10: eliminated couple has fewest save votes ({'S19-rhys-stephenson': 3})
- PASS: round S19R11: eliminated couple has fewest save votes ({'S19-aj-odudu': 3})
- PASS: round S19R12: eliminated couple has fewest save votes ({'S19-john-whaite': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S19R01-02 (1 vs 1)
- PASS: check 5: exit_count S19R03 (1 vs 1)
- PASS: check 5: exit_count S19R04 (1 vs 1)
- PASS: check 5: exit_count S19R05 (1 vs 1)
- PASS: check 5: exit_count S19R06 (1 vs 1)
- PASS: check 5: exit_count S19R07 (1 vs 1)
- PASS: check 5: exit_count S19R08 (1 vs 1)
- PASS: check 5: exit_count S19R09 (1 vs 1)
- PASS: check 5: exit_count S19R10 (1 vs 1)
- PASS: check 5: exit_count S19R11 (1 vs 1)
- PASS: check 5: exit_count S19R12 (1 vs 1)
- PASS: check 5: exit_count S19R13 (0 vs 0)
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
