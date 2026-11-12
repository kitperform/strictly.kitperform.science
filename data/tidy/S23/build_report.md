# Build report for S23

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 13 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 53 |
| `results_rounds.csv` | 11 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 40 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 40 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 134 |
| `performance_music.csv` | 139 |
| `songs.csv` | 133 |
| `artists.csv` | 98 |
| `judge_marks.csv` | 512 |
| `dance_off_votes.csv` | 40 |
| `dances.csv` | 16 |
| `themes.csv` | 5 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 228 |
| `crosscheck/chart_legends.csv` | 0 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S23R01-02: eliminated couple has fewest save votes ({'S23-chris-robshaw': 3})
- PASS: round S23R03: eliminated couple has fewest save votes ({'S23-balvinder-sopal': 3})
- PASS: round S23R04: eliminated couple has fewest save votes ({'S23-balvinder-sopal': 2, 'S23-chris-robshaw': 2})
- PASS: round S23R05: eliminated couple has fewest save votes ({'S23-amber-davies': 3})
- PASS: round S23R06: eliminated couple has fewest save votes ({'S23-balvinder-sopal': 3})
- PASS: round S23R07: eliminated couple has fewest save votes ({'S23-la-voix': 3})
- PASS: round S23R08: eliminated couple has fewest save votes ({'S23-balvinder-sopal': 3})
- PASS: round S23R09-10: eliminated couple has fewest save votes ({'S23-alex-kingston': 1, 'S23-balvinder-sopal': 3})
- PASS: round S23R11: eliminated couple has fewest save votes ({'S23-amber-davies': 3})
- PASS: round S23R12: eliminated couple has fewest save votes ({'S23-amber-davies': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S23R01-02 (1 vs 1)
- PASS: check 5: exit_count S23R03 (1 vs 1)
- PASS: check 5: exit_count S23R04 (1 vs 1)
- PASS: check 5: exit_count S23R05 (1 vs 1)
- PASS: check 5: exit_count S23R06 (1 vs 1)
- PASS: check 5: exit_count S23R07 (1 vs 1)
- PASS: check 5: exit_count S23R08 (1 vs 1)
- PASS: check 5: exit_count S23R09-10 (1 vs 1)
- PASS: check 5: exit_count S23R11 (1 vs 1)
- PASS: check 5: exit_count S23R12 (1 vs 1)
- PASS: check 5: exit_count S23R13 (0 vs 0)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: couple_weeks: one row per couple per week (195 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
