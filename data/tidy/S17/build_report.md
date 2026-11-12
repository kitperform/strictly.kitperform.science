# Build report for S17

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 2 |
| `weeks.csv` | 13 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 53 |
| `results_rounds.csv` | 12 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 37 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 38 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 17 |
| `couple_labels.csv` | 46 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 131 |
| `performance_music.csv` | 144 |
| `songs.csv` | 126 |
| `artists.csv` | 103 |
| `judge_marks.csv` | 524 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 18 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 9 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S17R01-02: eliminated couple has fewest save votes ({'S17-david-james': 3})
- PASS: round S17R03: eliminated couple has fewest save votes ({'S17-david-james': 3})
- PASS: round S17R04: eliminated couple has fewest save votes ({'S17-emma-thynn-marchioness-of-bath': 3})
- PASS: round S17R05: eliminated couple has fewest save votes ({'S17-mike-bushell': 3})
- PASS: round S17R06: eliminated couple has fewest save votes ({'S17-mike-bushell': 2, 'S17-catherine-tyldesley': 2})
- PASS: round S17R07: eliminated couple has fewest save votes ({'S17-mike-bushell': 3})
- PASS: round S17R08: eliminated couple has fewest save votes ({'S17-michelle-visage': 3})
- PASS: round S17R09: eliminated couple has fewest save votes ({'S17-saffron-barker': 3})
- PASS: round S17R10: eliminated couple has fewest save votes ({'S17-karim-zeroual': 3})
- PASS: round S17R11: eliminated couple has fewest save votes ({'S17-alex-scott': 2, 'S17-chris-ramsey': 2})
- PASS: round S17R12: eliminated couple has fewest save votes ({'S17-karim-zeroual': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S17R01-02 (1 vs 1)
- PASS: check 5: exit_count S17R03 (1 vs 1)
- PASS: check 5: exit_count S17R04 (1 vs 1)
- PASS: check 5: exit_count S17R05 (1 vs 1)
- PASS: check 5: exit_count S17R06 (1 vs 1)
- PASS: check 5: exit_count S17R07 (1 vs 1)
- PASS: check 5: exit_count S17R08 (1 vs 1)
- PASS: check 5: exit_count S17R09 (1 vs 1)
- PASS: check 5: exit_count S17R10 (1 vs 1)
- PASS: check 5: exit_count S17R11 (1 vs 1)
- PASS: check 5: exit_count S17R12 (1 vs 1)
- PASS: check 5: exit_count S17R13 (0 vs 0)
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
