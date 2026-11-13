# Build report for S13

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
| `performances.csv` | 148 |
| `performance_music.csv` | 155 |
| `songs.csv` | 137 |
| `artists.csv` | 110 |
| `judge_marks.csv` | 564 |
| `dance_off_votes.csv` | 44 |
| `dances.csv` | 15 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 225 |
| `crosscheck/chart_legends.csv` | 9 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S13R01-02: eliminated couple has fewest save votes ({'S13-jamelia': 3})
- PASS: round S13R03: eliminated couple has fewest save votes ({'S13-ainsley-harriott': 3})
- PASS: round S13R04: eliminated couple has fewest save votes ({'S13-kirsty-gallacher': 3})
- PASS: round S13R05: eliminated couple has fewest save votes ({'S13-jamelia': 3})
- PASS: round S13R06: eliminated couple has fewest save votes ({'S13-jamelia': 3})
- PASS: round S13R07: eliminated couple has fewest save votes ({'S13-kellie-bright': 3})
- PASS: round S13R08: eliminated couple has fewest save votes ({'S13-jamelia': 3})
- PASS: round S13R09: eliminated couple has fewest save votes ({'S13-peter-andre': 3})
- PASS: round S13R10: eliminated couple has fewest save votes ({'S13-kellie-bright': 3})
- PASS: round S13R11: eliminated couple has fewest save votes ({'S13-georgia-may-foote': 3})
- PASS: round S13R12: eliminated couple has fewest save votes ({'S13-anita-rani': 1, 'S13-katie-derham': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S13R01-02 (1 vs 1)
- PASS: check 5: exit_count S13R03 (1 vs 1)
- PASS: check 5: exit_count S13R04 (1 vs 1)
- PASS: check 5: exit_count S13R05 (1 vs 1)
- PASS: check 5: exit_count S13R06 (1 vs 1)
- PASS: check 5: exit_count S13R07 (1 vs 1)
- PASS: check 5: exit_count S13R08 (1 vs 1)
- PASS: check 5: exit_count S13R09 (1 vs 1)
- PASS: check 5: exit_count S13R10 (1 vs 1)
- PASS: check 5: exit_count S13R11 (1 vs 1)
- PASS: check 5: exit_count S13R12 (1 vs 1)
- PASS: check 5: exit_count S13R13a (1 vs 1)
- PASS: check 5: exit_count S13R13b (0 vs 0)
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
