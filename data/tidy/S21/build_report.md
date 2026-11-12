# Build report for S21

## Tables

| table | rows |
|---|---|
| `series.csv` | 1 |
| `format_rules.csv` | 3 |
| `weeks.csv` | 13 |
| `episodes.csv` | 25 |
| `panel_seats.csv` | 52 |
| `results_rounds.csv` | 11 |
| `results_round_weeks.csv` | 13 |
| `people.csv` | 37 |
| `person_aliases.csv` | 4 |
| `series_people.csv` | 37 |
| `couples.csv` | 15 |
| `couple_partnerships.csv` | 15 |
| `couple_labels.csv` | 45 |
| `couple_weeks.csv` | 195 |
| `performances.csv` | 129 |
| `performance_music.csv` | 145 |
| `songs.csv` | 131 |
| `artists.csv` | 103 |
| `judge_marks.csv` | 516 |
| `dance_off_votes.csv` | 40 |
| `dances.csv` | 16 |
| `themes.csv` | 4 |
| `venues.csv` | 2 |
| `source_captures.csv` | 2 |
| `discrepancies.csv` | 0 |
| `crosscheck/chart_cells.csv` | 225 |
| `crosscheck/chart_legends.csv` | 10 |

## Checks

- PASS: judge order sentence found (4 judges)
- PASS: couples parsed (15 couples)
- PASS: round S21R01-02: eliminated couple has fewest save votes ({'S21-nikita-kanda': 3})
- PASS: round S21R03: eliminated couple has fewest save votes ({'S21-zara-mcdermott': 3})
- PASS: round S21R04: eliminated couple has fewest save votes ({'S21-eddie-kadi': 3})
- PASS: round S21R05: eliminated couple has fewest save votes ({'S21-zara-mcdermott': 3})
- PASS: round S21R06: eliminated couple has fewest save votes ({'S21-adam-thomas': 3})
- PASS: round S21R07: eliminated couple has fewest save votes ({'S21-angela-rippon': 3})
- PASS: round S21R08: eliminated couple has fewest save votes ({'S21-angela-rippon': 3})
- PASS: round S21R09: eliminated couple has fewest save votes ({'S21-bobby-brazier': 3})
- PASS: round S21R10: eliminated couple has fewest save votes ({'S21-layton-williams': 3})
- PASS: round S21R11-12: eliminated couple has fewest save votes ({'S21-annabel-croft': 1, 'S21-bobby-brazier': 3})
- PASS: weeks with tables ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
- PASS: scoring chart totals equal weekly totals (0 discrepancies)
- PASS: check 1: marks sum to stated total (0 mismatches [])
- PASS: check 2: every mark has a seat (0)
- PASS: check 5: exit_count S21R01-02 (1 vs 1)
- PASS: check 5: exit_count S21R03 (1 vs 1)
- PASS: check 5: exit_count S21R04 (1 vs 1)
- PASS: check 5: exit_count S21R05 (1 vs 1)
- PASS: check 5: exit_count S21R06 (1 vs 1)
- PASS: check 5: exit_count S21R07 (1 vs 1)
- PASS: check 5: exit_count S21R08 (1 vs 1)
- PASS: check 5: exit_count S21R09 (1 vs 1)
- PASS: check 5: exit_count S21R10 (1 vs 1)
- PASS: check 5: exit_count S21R11-12 (1 vs 1)
- PASS: check 5: exit_count S21R13 (0 vs 0)
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
