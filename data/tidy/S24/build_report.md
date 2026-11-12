# Build report for S24

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 13 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 28 |
| `results_rounds.csv` | 6 |
| `results_round_weeks.csv` | 7 |
| `people.csv` | 38 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 38 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 46 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 94 |
| `performance_music.csv` | 95 |
| `songs.csv` | 95 |
| `artists.csv` | 65 |
| `judge_marks.csv` | 352 |
| `dance_off_votes.csv` | 24 |
| `dances.csv` | 15 |
| `themes.csv` | 3 |
| `venues.csv` | 1 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 165 |
| `crosscheck/chart_legends.csv` | 3 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S24R01-02: eliminated couple has fewest save votes ({'S24-jaime-winstone': 3})
- PASS: round S24R03: eliminated couple has fewest save votes ({'S24-shaun-wright-phillips': 3, 'S24-melanie-walters': 1})
- PASS: round S24R04: eliminated couple has fewest save votes ({'S24-bethany-antonia': 3})
- PASS: round S24R05: eliminated couple has fewest save votes ({'S24-jaime-winstone': 3, 'S24-shaun-wright-phillips': 1})
- PASS: round S24R06: eliminated couple most named to eliminate ({'S24-lawrence-robb': 3})
- PASS: round S24R07: eliminated couple has fewest save votes ({'S24-cach-mercer': 2, 'S24-bethany-antonia': 2})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S24R01-02 (1 vs 1)
- PASS: check 5: exit_count S24R03 (1 vs 1)
- PASS: check 5: exit_count S24R04 (1 vs 1)
- PASS: check 5: exit_count S24R05 (1 vs 1)
- PASS: check 5: exit_count S24R06 (1 vs 1)
- PASS: check 5: exit_count S24R07 (1 vs 1)
- PASS: check 12: performance keys unique
- PASS: check 11: partnerships contiguous
- PASS: couple_weeks: one row per couple per week (195 rows)
- PASS: no unresolved couple labels ([])
- PASS: daggers agree with derived highest/lowest ([])

## Warnings

- none

## Unresolved labels

- none
