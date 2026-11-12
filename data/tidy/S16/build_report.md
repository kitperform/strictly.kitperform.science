# Build report for S16

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
| `people.csv` | 35 |
| `person_aliases.csv` | 6 |
| `series_people.csv` | 35 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 149 |
| `performance_music.csv` | 168 |
| `songs.csv` | 137 |
| `artists.csv` | 123 |
| `judge_marks.csv` | 568 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 19 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 210 |
| `crosscheck/chart_legends.csv` | 6 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S16R01-02: eliminated couple has fewest save votes ({'S16-lee-ryan': 3})
- PASS: round S16R03: eliminated couple has fewest save votes ({'S16-charles-venn': 3})
- PASS: round S16R04: eliminated couple has fewest save votes ({'S16-charles-venn': 3})
- PASS: round S16R05: eliminated couple has fewest save votes ({'S16-vick-hope': 1, 'S16-seann-walsh': 3})
- PASS: round S16R06: eliminated couple has fewest save votes ({'S16-graeme-swann': 3})
- PASS: round S16R07: eliminated couple has fewest save votes ({'S16-ranj-singh': 1, 'S16-charles-venn': 3})
- PASS: round S16R08: eliminated couple has fewest save votes ({'S16-danny-john-jules': 1, 'S16-graeme-swann': 3})
- PASS: round S16R09: eliminated couple has fewest save votes ({'S16-graeme-swann': 3})
- PASS: round S16R10: eliminated couple has fewest save votes ({'S16-ashley-roberts': 3})
- PASS: round S16R11: eliminated couple has fewest save votes ({'S16-ashley-roberts': 3})
- PASS: round S16R12: eliminated couple has fewest save votes ({'S16-ashley-roberts': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S16R01-02 (1 vs 1)
- PASS: check 5: exit_count S16R03 (1 vs 1)
- PASS: check 5: exit_count S16R04 (1 vs 1)
- PASS: check 5: exit_count S16R05 (1 vs 1)
- PASS: check 5: exit_count S16R06 (1 vs 1)
- PASS: check 5: exit_count S16R07 (1 vs 1)
- PASS: check 5: exit_count S16R08 (1 vs 1)
- PASS: check 5: exit_count S16R09 (1 vs 1)
- PASS: check 5: exit_count S16R10 (1 vs 1)
- PASS: check 5: exit_count S16R11 (1 vs 1)
- PASS: check 5: exit_count S16R12 (1 vs 1)
- PASS: check 5: exit_count S16R13 (0 vs 0)
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
