# Build report for S12

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 13 |
| `episodes.csv` | 27 |
| `panel_seats.csv` | 61 |
| `results_rounds.csv` | 13 |
| `results_round_weeks.csv` | 14 |
| `people.csv` | 35 |
| `person_aliases.csv` | 5 |
| `series_people.csv` | 35 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 147 |
| `performance_music.csv` | 148 |
| `songs.csv` | 135 |
| `artists.csv` | 104 |
| `judge_marks.csv` | 578 |
| `dance_off_votes.csv` | 45 |
| `dances.csv` | 15 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 225 |
| `crosscheck/chart_legends.csv` | 7 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S12R01-02: eliminated couple has fewest save votes ({'S12-jennifer-gibney': 3})
- PASS: round S12R03: eliminated couple has fewest save votes ({'S12-simon-webbe': 3})
- PASS: round S12R04: eliminated couple has fewest save votes ({'S12-mark-wright': 3})
- PASS: round S12R05: eliminated couple has fewest save votes ({'S12-thom-evans': 2, 'S12-simon-webbe': 2})
- PASS: round S12R06: eliminated couple has fewest save votes ({'S12-alison-hammond': 3})
- PASS: round S12R07: eliminated couple has fewest save votes ({'S12-caroline-flack': 3})
- PASS: round S12R08: eliminated couple has fewest save votes ({'S12-sunetra-sarker': 3})
- PASS: round S12R09: eliminated couple has fewest save votes ({'S12-sunetra-sarker': 3, 'S12-steve-backshall': 1})
- PASS: round S12R10: eliminated couple has fewest save votes ({'S12-mark-wright': 3})
- PASS: round S12R11: eliminated couple has fewest save votes ({'S12-pixie-lott': 2, 'S12-simon-webbe': 2})
- PASS: round S12R12: eliminated couple has fewest save votes ({'S12-mark-wright': 2, 'S12-jake-wood': 2})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S12R01-02 (1 vs 1)
- PASS: check 5: exit_count S12R03 (1 vs 1)
- PASS: check 5: exit_count S12R04 (1 vs 1)
- PASS: check 5: exit_count S12R05 (1 vs 1)
- PASS: check 5: exit_count S12R06 (1 vs 1)
- PASS: check 5: exit_count S12R07 (1 vs 1)
- PASS: check 5: exit_count S12R08 (1 vs 1)
- PASS: check 5: exit_count S12R09 (1 vs 1)
- PASS: check 5: exit_count S12R10 (1 vs 1)
- PASS: check 5: exit_count S12R11 (1 vs 1)
- PASS: check 5: exit_count S12R12 (1 vs 1)
- PASS: check 5: exit_count S12R13a (1 vs 1)
- PASS: check 5: exit_count S12R13b (0 vs 0)
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
