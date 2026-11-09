# Wikipedia source analysis: the *Strictly Come Dancing* series pages

Status: research write-up, November 2026. Covers the English Wikipedia pages
`Strictly_Come_Dancing_series_1` … `_24` as captured in `data/wikipedia/series/0NN/`
(series 1–21 captured in 2024, series 22–24 on 8 November 2026) and the live
wikitext of all 24 pages fetched on 8 November 2026. Series 24 was in progress
(weeks 1–7 complete, week 8 pre-populated) at the time of writing.

The underlying evidence is the research set behind these documents: the table
catalogue in this document, `docs/series-summaries.md` and the per-series
modelling notes folded into `docs/wikipedia-anomaly-register.md`. The anomaly register (A001–A257) is the acceptance test
for the data model; this document is the acceptance test for the **parser**:
it records what the pages contain, how every cell is encoded, where facts hide
outside tables, and what each parsing library did with them.

Contents

1. [What a series page contains; primary facts versus derivable cross-checks](#1-what-a-series-page-contains)
2. [Catalogue of table types, era variants and cell encodings](#2-catalogue-of-table-types)
3. [Key facts that live outside tables](#3-key-facts-that-live-outside-tables)
4. [Identity resolution rules, aliases and overrides](#4-identity-resolution)
5. [Two HTML dialects and the snapshot/revision discipline](#5-two-html-dialects-and-snapshot-discipline)
6. [Parser prototype results and the recommended approach](#6-parser-prototype-results)
7. [Per-series summary table](#7-per-series-summary)

---

## 1. What a series page contains

Every series page follows the same skeleton, with small drift in heading
wording and level:

| Section (H2 unless stated) | Present in | What it holds |
|---|---|---|
| Lead + `{{Infobox television season}}` | all | presenters, judges (not in seating order), `first_aired`, `last_aired`, `num_episodes` |
| Format | all | prose describing the elimination mechanism, dance-off and (S22+) tie-break rule |
| Professional dancers | S11–S23 (H2); S24 as H3 under a new **Production** H2; absent S1–S10 (S8 has a **Dance troupe** H2 instead) | prose only: who left/joined, who was left unpartnered, pre-series replacements |
| Couples | all | the one table that defines Celebrity, Professional, Couple and final Status |
| Scoring chart | all | weekly-totals matrix with colour-coded statuses, daggers and footnotes |
| Average chart (H3 under Scoring chart) | all | rank by mean score over 40-point dances |
| Weekly scores | all | italic judge-order sentence, then one H3 per week (`Week N`, `Week N: Theme`, `Week N: Theme (Quarter-final)`); from S15 sometimes a `Launch show` H3 with no table |
| Dance chart | all | one cell per dance per couple per week |
| Reception | S7, S12, S19 | prose |
| Ratings | all | episode dates and audience figures |
| References, External links | all | — |

### Primary facts (parse these as inputs)

1. **Couples table**: celebrity and professional identity (wiki-link targets),
   per-series display names, mid-series professional replacement with week
   ranges, final status/placing, exit date.
2. **Weekly scores tables**: every performance (couple, week, night/show,
   running order = row order, dance, song, artist or source work, theme
   column), every judge mark in the stated order (3/4/5 judges), the Result
   cell (Safe / Bottom two / Bottom three / Eliminated / Withdrew / placings),
   marathon and instant-dance rank points, unscored performances.
3. **The prose around each weekly table**: judge-order override, casting-vote
   holder (S23+), byes, withdrawals, "no elimination" statements, musical
   guests, theme and round from the heading.
4. **Judges' votes to save / to eliminate lists**: dance-off participants and
   each judge's vote, including "Did not vote, but would have voted to save
   X" (absent in S1–S4, which had no dance-off, and omitted on the S8 and S9
   pages, which had none either).
5. **Ratings table**: transmission dates of performance and results shows,
   audience figures, launch/preview shows.
6. **Infobox and the italic judge-order sentence**: presenters, judge panel,
   air dates, episode count.
7. **Specials**: not on the series pages at all (see §2.9).

### Derivable facts (parse only as cross-checks / regression tests)

- **Scoring chart**: weekly total = sum of that week's per-dance totals;
  bold green dagger = maximum of the week; italic red double-dagger =
  minimum; lightblue = Result "Bottom two"; `#f4c7b8` = "Eliminated";
  gold/silver/tan/`#d1c571` = placings; `Pl.` = Couples-table status order.
  The only quasi-unique data are the 50-point-week flag in a header
  footnote, cumulative final-show sums, and the bye/withdrawal cells (which
  are also stated in prose).
- **Average chart**: total points, number of dances and mean over
  40-point-scale dances only (marathon points, 30-point and 50-point weeks
  excluded; S15 rescales its 30-point week). The S24 `Place` column
  duplicates Couples status.
- **Dance chart**: dance per couple per week. Only the struck-through
  planned-but-undanced dances (S23–S24) add information.

The three derivable tables are cheap to parse with the same grid expander,
and every disagreement found so far pointed at a wiki data quirk worth
recording rather than at a parser bug (S6 `|28| 28` cells, S9 shared score
cells, S24 "Greame" typo, S23 lightgreen cells with no footnote). Parse them,
diff them against values regenerated from the fact tables, and store the
diff; never merge them into the primary facts.

---

## 2. Catalogue of table types

All data tables are `class="wikitable"` (usually `sortable`; Dance chart is
`unsortable`). Select tables by caption, header text or the preceding heading,
never by index: `pandas.read_html` found 23 tables on the S6 page and 17 on
S24 because infobox, image galleries, legend blocks and the navbox also count.

### 2.1 Couples table

- **Section**: `==Couples==` (S1 has a stray space: `== Couples==`).
- **Structure**: header `Celebrity | Notability (unsortable) | Professional partner | Status`;
  one row per couple; `! scope="row" | [[Celebrity link]]` as the row header
  (sometimes inside `{{nowrap}}`); no caption. Order: eliminated first,
  winner last (S1–S23); S24 lists eliminated couples then the "Participating"
  couples alphabetically.
- **Era variants**: identical columns in all 24 series; only the Status
  vocabulary changes. `Third place` (tan) S2, S3, S8, S9; `Fourth place`
  (`#d1c571`) S10–S13; `Withdrew` (lightgreen) S4, S5, S6, S7, S14, S17, S18,
  S19, S20, S21, S23; `Runners-up`/`Co-runners-up` shared via `rowspan=2/3`
  S10–S13, S15, S16, S18, S20, S21, S22, S23; `Participating` (lightblue) S24.
- **Cell encodings**:
  - `! scope="row" | [[Jason Wood (comedian)|Jason Wood]]` — identity is the
    link target, display may differ (39 mismatches across S1–S24, see §4).
  - `| [[Brendan Cole]]<br />{{small|''[[Ian Waite]] (Week 4)''}}` (S8),
    `[[Robin Windsor]]<br><small>''Brendan Cole (Week 9)''</small>` (S9),
    `[[Brendan Cole]]<br/>{{small|Gorka Márquez (Week 5)}}` (S14),
    `[[Neil Jones (dancer)|Neil Jones]]<br />''{{small|Kevin Clifton (Weeks 6–7)}}''` (S17),
    `[[Amy Dowden]] ''(Weeks 1–6)''<br>[[Lauren Oakley]] ''(Weeks 7–13)''` (S22)
    — professional substitution/replacement, split on `<br>`, parse
    `Week N` / `Weeks a–b`.
  - `| Andrew Cuerden` (S3) — a professional with no article; pro identity
    cannot require a link.
  - `| bgcolor="f4c7b8" | Eliminated 1st<br /><small>on 22 May 2004</small>`
    — status + colour + date; date wrappers vary: `<br /><small>on …</small>`,
    `{{small|on 23 October 2023}}`, `<small>{{nowrap|on 4 October 2026}}</small>`.
    `bgcolor` is written with and without `#`, and as `style="background:#f4c7b8;"` in S24.
    S2 Roger Black "Eliminated 6th" has no date.
  - `| bgcolor="lightgreen" | Withdrew<br />{{small|on 23 October 2023}}` —
    withdrawal; the date can be a weekday announcement (S5 Monday 26 Nov 2007;
    S14 Tue 11 Oct 2016; S17 Wed 30 Oct 2019; S18 Thu 12 Nov 2020; S23 Mon 20 Oct 2025).
  - `| bgcolor="silver" rowspan=2 | Runners-up<br/><small>on 21 December 2013</small>`
    — joint placing; the following row(s) have only three cells.
  - Winners in `'''bold'''` on gold.
- **Rowspan trap**: shared Status cells (S11, S12, S13, S15, S16, S18, S20, S21, S22, S23).
- **Parse difficulty**: easy. Primary source for Celebrity, Professional,
  Couple and final placing. Cross-check: "Eliminated Nth" order must match
  the Scoring chart `Pl.` column and the week of the `#f4c7b8` cell.

### 2.2 Professional dancers section

Prose only in every series that has it (S11–S24; S8 "Dance troupe"). It is
the only place that records pros without a partner (S8 Darren Bennett, Ian
Waite; S14 Chloe Hewitt, Neil Jones; S16 Luba Mushtuk, Johannes Radebe; S17
Gorka Márquez, Graziano Di Prima; S18 Neil Jones, Nadiya Bychkova, Graziano
Di Prima, Nancy Xu; S21 Amy Dowden; S24 Johannes Radebe, who became a host) and
pre-series replacements (§3.6). Treat as a curated input: collect the
wikilinks as a candidate roster and hand-check.

### 2.3 Scoring chart (weekly totals matrix)

- **Section**: `==Scoring chart==`; caption `''Strictly Come Dancing'' (series N) - Weekly scores`
  (hyphen or en dash). Preceded by a `{{legend}}` colour key and followed by
  `{{notelist}}` (`;Notes` in S1–S3).
- **Structure**: `! rowspan=2 scope=col | Couple`, `! rowspan=2 | {{Abbr|Pl.|Place}}`
  (S21 expands to "Placement"), `! colspan=N | Week`, second header row with
  week numbers including combined columns. Body: `! scope="row" | Natasha & Brendan`
  (S6 uses bare `!Tom & Camilla` with no scope), `| 1st`, one cell per week.
  Eliminated couples' remaining weeks are a single filler cell
  `colspan=K bgcolor="darkgray" |` (S1 uses `rowspan`; `style="background:darkgrey"`
  in S3, S6, S7, S9, S20; "darkgrey" S13–S14 vs "darkgray" S15–S18).
- **Column variants**:
  - `Couple | Pl. | 1 | 2 | 1+2 | 3 … N` — combined week-1-and-2 column
    (S1, S8–S24: week 1 had no elimination).
  - `… | 13 | 14 | 13+14` (S6: semi-final votes rolled into the final);
    `11+12` (S21: Nigel Harman withdrew, no week-11 elimination);
    `9+10` (S23: La Voix withdrew during week 9).
  - `… | 12{{efn|name=GuestJudge}} | 13{{efn}} | 14{{efn}}` (S7) and
    `3{{efn|…50-point scale…}}` (S12): whole column out of 50 because of a
    guest judge — the flag is in the **header cell footnote**.
  - Finals split into `Show 1 | Show 2` sub-columns under a third header
    row (S7–S13).
  - `Pl.` values `1st`…`16th`; `rowspan=2|2nd` / `rowspan=3|2nd` for joint
    runners-up (S10–S13, S15, S16, S18, S20–S23); blank for couples still
    competing (S24); stray `align=center|` in some Pl. cells.
- **Cell grammar** (the full set observed):
  - `| 27` — plain weekly total (out of 40; 30 or 50 in odd weeks).
  - `| {{fontcolor|#004600|'''31'''}}{{dagger|alt=This was the highest score of the night.}}`
    — highest of the week (bold green + †). S22–S24: `{{fontcolor|var(--color-success)|'''34'''}}`;
    S22 daggers have no alt text; S23 alt variants "highest joint-score" /
    "lowest joint-score" on the 1+2 column. Ties: all tied cells flagged
    (S24 week 1 three-way tie for lowest).
  - `| {{fontcolor|#800000|''19''}}{{double-dagger|alt=This was the lowest score of the night.}}`
    — lowest of the week (italic red + ‡); `var(--color-error)` and no alt in S24.
  - `| bgcolor="lightblue" | 26{{efn|name=Bottom2}}` — bottom two, saved.
    The first occurrence in source order carries the note text; the S24 week-6
    legend has an extra note "Week 6 had the bottom three couples competing".
    Also `style="background:lightblue;"` (S4, S14, S24).
  - `| bgcolor="#f4c7b8" | 32{{efn|name=Elim}}` — eliminated this week.
  - `| {{sort|67|}} | 31+36={{fontcolor|#004600|'''67'''}}{{dagger|…}}` —
    multi-dance week; `{{sort}}` (or once `data-sort-value=33 |`) precedes the
    cell attributes; `35+38+37=110` for three dances.
  - `| {{sort|156|}} bgcolor="gold" | +39+40=156{{efn|This couple finished in first place.}}`
    — final Show 2 column: a leading `+` means "added to the Show 1 total"
    (S9, S11, S12, S13: `+38=116`, `+39=110`).
  - `| {{sort|37|}} bgcolor="f4c7b8" | 35+2=37{{efn|name=Elim}}` — judges'
    total plus marathon or instant-dance rank points (S8 `39+5+39=83`, S9
    `39+7=46`, S11 `37+3=40`, S12 `39+3=42`, S13 `38+3=41`, S22 `33+1=34`, S23 `40+1=41`).
  - `| {{NA}}` — did not dance this week by format (half-field weeks S4–S7).
    Renders `<td class="table-na" data-sort-value="">—</td>`. S6 Tom & Camilla
    uses literal `|—` and the malformed `|28| 28` / `|33| —`, where the text
    before the second pipe is parsed as (invalid) attributes and dropped;
    mwparserfromhell exposes `attrs=['33'] contents='—'`.
  - `| bgcolor="fff383" | {{efn|name=OutSick|This couple was excused from competing due to illness or injury, and was granted a [[Bye (sports)|bye]] to the following week.}}`
    — bye: empty yellow cell. Note name varies: `OutSick` (S7, S8, S11, S14,
    S19, S20, S22, S24), `Sick` (S17), `Sickie` (S21); S19 Tom & Amy is
    `colspan=2 bgcolor=fff383` spanning columns `2` and `1+2`; S23 cells are bare
    `bgcolor="fff383" |` with **no footnote at all**.
  - `| bgcolor="lightgreen" | {{efn|name=Quitter|This couple withdrew from the competition.}}`
    — withdrew: green cell in the week the exit was announced; empty unless
    the couple danced that week (S20 Tony & Katya: `24` with a double-dagger).
    Note name varies: anonymous (S4, S6, S17), `WD` (S19), `Quitter` (S21),
    `Withdrew`, none (S23).
  - `| colspan="6" bgcolor="darkgray" |` — filler, never a value.
  - `| bgcolor="dlc571" | 39+35=74{{efn|name=Elim}}` — **typo** of `#d1c571`
    (letter l for digit 1) for Fourth place; invalid CSS colour (S10 ×2, S11, S12, S13).
  - `! scope="col" |12{{efn|name=GuestJudge|The couples were scored on a 50-point scale due to the presence of a guest judge.}}`
    — header footnote marking a 50-point column.
- **Legend**: `{{legend|#f4c7b8|Eliminated}}` renders
  `<div class="legend"><span class="legend-color" style="background-color:#f4c7b8">`.
  Parse it once per page and decode `bgcolor` values from it rather than
  hard-coding; S23 has no Bottom2/Elim footnotes, so **colour is the only
  status signal there**.
- **Rowspan/colspan traps**: `Pl.` rowspan for ties; filler colspan/rowspan;
  withdrawn couples' rows end early and subsequent grey cells belong to another
  row's rowspan; three header rows in S7–S13 finals.
- **Parse difficulty**: hard. Derivable; use as a cross-check.

### 2.4 Average chart

- **Section**: `===Average chart===` under Scoring chart. Preamble "This table
  only counts for dances scored on a traditional 40-point scale." (S18:
  30-point; S12 adds that Donny Osmond's week-3 scores were removed).
- **Columns**: `Couple | Rank by average | Total points | Number of dances | Total average`
  (S1–S23); S24 adds `Place` after Rank, uses integer ranks instead of ordinals,
  and shares `Number of dances` across eight rows with `rowspan=8`.
- **Encodings**: `rowspan` merges identical adjacent values (ties on Rank and
  Average: S3 tied 11th, S5 ties 3rd/4th/8th, S12 `rowspan=2|1st` Caroline/Frankie,
  S15 10th/12th, S20 joint 2nd at 35.4 with different totals 567/566; S4 writes
  "5th" twice with no rowspan and no skipped rank); one-decimal mean (`33.0`);
  `! scope="row" | Greame & Lauren` (S24) is a typo for Graeme.
- **Parse difficulty**: easy. Fully derivable; an excellent regression test
  (recompute mean over 40-point dances per couple).

### 2.5 Weekly scores tables (one per week, night or show)

- **Sections**: `==Weekly scores==` then `===Week N===`, `===Week N: Theme===`,
  `===Week N: Theme (Quarter-final)===`, `===Week N: Semi-final===`, `===Week N: Final===`
  (spelling drifts: Quarterfinal/Quarter-final, Semifinal/Semi-final).
  Sub-shows: `====Show 1====`/`====Show 2====` H4 (S9, S10 finals);
  `;Show 1` / `;Night 1 (Friday)` definition-list labels (S7, S8, S11–S14);
  `===Launch show===` with prose only (S15, S21, S22, S23).
- **Structure**: `class="wikitable sortable" style="text-align:center; width:90%"`
  (100 % in S22–S24). Header `Couple | Scores | Dance | Music [| Theme] [| Result]`;
  the header is `Scores` in all 24 series. One body row **per dance**:
  `! scope="row" | Natasha & Brendan` (rowspan = number of dances; the Result
  cell carries the same rowspan), `| 27 (5, 7, 8, 7)`, `| Cha-cha-cha`,
  `| "[[Song]]" — [[Artist]]`, `| Safe` or `| bgcolor="f4c7b8" | Eliminated`.
  "Couples are listed in the order they performed" — running order is row order.
- **Era variants**:
  - No Result column in no-elimination weeks (S1 wk1, S24 wk1, every
    Night 1/Night 2 table) and in S6 wk13.
  - S4–S7 wks 1–2: half the field per week (the others listed only in the
    chart as `{{NA}}`); S7–S14 wk1 split into `;Night 1 (Friday)` / `;Night 2 (Saturday)`
    tables (S7 also wk3; S8 wk11 semi-final over two nights); S7–S13 finals
    two tables under Show 1 / Show 2.
  - Theme column from S9: `Broadway musical` (S9 wk3), `Film` (Movie Week
    S9, S12–S16, S18–S21, S24), `Musical` (S11, S13–S16, S18–S20, S22, S23;
    S15 header has `class="unsuitable"`, a typo for unsortable), `Country`
    (S12 wk10), `Celebrating [[BBC]]` (S20 wk5), `Icon` (S22 wk7, S23 wk5,
    S24 wk4). When a theme column is present the Music cell holds the song only.
  - S22–S24: `<ref>` citations inside header cells (`Scores<ref name=Week1Scores>`
    renders as `Scores[39]`), first row not preceded by `|-`, empty `|+`
    caption line (S24 wks 3–8), S24 wk8 half-filled.
- **Cell encodings**:
  - `| 27 (5, 7, 8, 7)` — total then per-judge marks in the order given by
    the italic preamble (or a per-week override). Sum matched the total in
    every row tested (S1, S6, S9, S12, S21, S24). Sometimes wrapped in `{{nowrap}}`.
  - `| 42 (8, 9, 8, 9, 8)` — five judges, out of 50 (S7 wks 12–14 Darcey
    Bussell; S12 wk3 Donny Osmond).
  - `| 22 (6, 8, 8)` — three judges, out of 30 (S15 wk5 Bruno absent; all of S18).
  - `| rowspan="2" | 39 (9, 10, 10, 10)` — one score cell spanning two or
    three dance rows when a couple scored identically for each (S5 wk11
    Alesha; S9 wk11 Harry, S9 final Chelsee; S10 wk12; S11 wk12; S12 wk13;
    S13 final Show 1 ×3; S15 wk12 Joe; S16 final Ashley & Faye `rowspan=3`;
    S18 wk8 Jamie; S21 final Bobby `rowspan=3`; S23 final George `rowspan=3`,
    S23 wk12 Balvinder, Karen `rowspan=2`). Expand to each dance; never treat as a total.
  - `| 1` … `| 7` on the second row of a `rowspan=2` couple — marathon or
    instant-dance **rank points**, not judge marks; the Dance cell is
    `rowspan=N | Swing-a-thon<br>''(Swing Marathon)''` (or Waltz-a-thon,
    Quickstep-a-thon, Cha-Cha-Challenge, Paso doble-thon, Lindy Hop-a-thon,
    Samba-thon, "Instant dance") and Music is `colspan=2 rowspan=N`. Detect
    by the Dance cell, not by the score shape.
  - `| No scores<br>received` or empty `|` — performed but unscored (S1 wk5
    group dance; S6 wk10 John & Kristina's waltz after withdrawing; S2–S6
    showdances). The 2024 HTML says "No scores received" where the 2026
    wikitext is empty; `bgcolor="lightgray"` in S4–S5. Map to NULL, never 0.
  - `| "[[Chain of Fools]]" — [[Aretha Franklin]]` — song — artist with a
    spaced em dash (100 % of S1/S6 cells); variants `— ''from [[Grease (musical)|Grease]]''`
    (source work, not performer), `X feat. Y`, `A & B`, two songs
    `"S1" — A / "S2" — B` (S24 wk3), three songs with `<br>` and
    `All from ''La La Land''` (S21). Link targets give song/artist identity.
  - `| "[[Beauty and the Beast (Disney song)|Beauty and the Beast]]"` plus a
    Film cell `''[[Beauty and the Beast (1991 film)|…]]''` — theme weeks.
    The theme cell may be blank for some couples.
  - `| bgcolor="lightblue" | Bottom two` / `Bottom three` (S24 wk6 only).
  - `| rowspan=3 bgcolor="gold" | '''Winners'''`, `bgcolor=silver | Runners-up`
    (`Runners-Up` + `bgcolor="Gold"` in S21), `tan | Third place`,
    `dlc571 | Fourth place`, `lightgreen | Withdrew` (S6 wk10). Final-table
    silver cells span 6 or 9 rows, and are split when couples are listed in
    performance order (S22). Normalise case and `#`.
  - `! scope="row" | Christopher & Hanna<br>Claire & John<br>…` with empty
    Scores, `Group<br>Viennese waltz` and `colspan="2"` Music swallowing the
    Result column (S1 wk5) — unscored group dance row.
  - `! scope="row" | Anita & Brendan` (S9 wk9) versus `Anita & Robin` (wks
    1–8); `JB & Amy` then `JB & Lauren` (S22); `Alex & Kevin` (S17 wks 6–7);
    `Anastacia & Gorka` (S14 wk5) — the label follows the dancing pro.
  - Stray extra cell (S9 wk10 Jason).
- **Parse difficulty**: moderate. **The primary input** for Performance,
  Score, Result, running order and theme.

### 2.6 Judges' votes to save / to eliminate (dance-off result list)

- **Where**: directly after the weekly table inside the week section, S5–S7
  and S10–S24 (171 lists). Absent S1–S4 (no dance-off), S8–S9 (format had
  none), week-1 no-elimination weeks, finals, S6 wk13, S7 wk13, S14 wk2
  (dance-off cancelled), S20 wk8 (bottom-two couple withdrew), S21 wk11, S23 wk9.
- **Structure**: wikitext `;Judges' votes to save<ref …/>` renders
  `<dl><dt>Judges' votes to save</dt></dl><ul><li>Surname: Couple</li>…</ul>`.
  Heading variants: trailing colon (×8), "Judges votes" without apostrophe
  (×4, e.g. S12 wk12), curly apostrophe (×1), leading space (×1), and bold
  `'''Judges' votes to eliminate'''` in a `<p>` for the S24 wk6 triple dance-off.
- **Item grammar**:
  - `*Horwood: Lisa & Brendan` — judge **surname only** (`Horwood`,
    `Revel Horwood`, `Phillips`, `Goodman`, `Dixon`, `Bussell`, `Tonioli`,
    `Ballas`, `Mabuse`, `Du Beke`; guests `Osmond`, `Ribeiro`, `Erivo`).
  - `*Goodman: ''Did not vote, but would have voted to save Jamelia & Tristan''`
    — the head/casting judge was not needed (45+ occurrences). The
    hypothetical vote sometimes names the **eliminated** couple (S6 wks 4–5,
    S13 wk9, S16 wk3, S18 wk4): store verbatim.
  - `*Goodman: Don & Lilia ''(Since the other judges were not unanimous, Len Goodman, as head judge, made the final decision to save Don & Lilia.)''`
    — explicit casting vote (S6 wk1, S15 wk7, S17 wks 6, 11). But S12 wks 5,
    11, 12, S22 wk8, S23 wk4 and S24 wk7 were also 2–2 and are recorded as four
    plain votes with no marker: decisiveness must be inferred from the counts
    plus the casting-vote holder.
  - `* Mabuse: ''Did not vote, but would have voted to eliminate Lawrence & Jowita.''`
    — S24 wk6: votes are to **eliminate**, bottom three.
  - Order: head judge last in S5–S22; in S23–S24 the rotating casting-vote
    judge is last and the order of the other three varies week to week.
- **Parse difficulty**: moderate. Primary fact for dance-off participants,
  votes and casting vote; cross-check against "Bottom two" Result cells; the
  eliminated couple is the one not saved.

### 2.7 Dance chart

- **Section**: `==Dance chart==`, preceded by a bullet list "The couples
  performed the following each week:" (dance-selection rules per week, e.g.
  "Weeks 1–11: One unlearned dance").
- **Structure**: `class="wikitable unsortable" style="font-size:85%"`;
  caption; two header rows (`Couple` rowspan=2, `Week` colspan, week numbers
  with colspan=2/3 for multi-dance weeks); one cell per dance.
- **Encodings**: filler `colspan=K bgcolor=darkgray` (S1–S21) or `lightgrey`
  (S22–S24); `rowspan=5 | Group<br>Viennese waltz` (S1) or per-row `Group Rueda`
  (S6); `rowspan="6" | Waltz<br>Marathon` shared cell (S12); `{{nowrap|Cha-cha}}-cha`;
  `{{Abbr|Contemp.|Contemporary}}` for Couple's Choice (S16+);
  `| bgcolor="lightgrey" | <s>''Cha-cha-cha''</s>{{efn|name=OutSick|…}}` —
  **planned dance not performed** (S24 Delta & Kai wk4; S23 Samba, Waltz;
  S14 Will Young's Viennese waltz; S11 wk7 Jive kept for Natalie Gumede);
  S6 wk10 `lightblue | Waltz{{efn|No scores were received for this dance.}}`;
  S24 header declares `colspan=15` but lists 13 numbers (pandas yields
  `Unnamed: 14_level_1`).
- **Parse difficulty**: moderate. Derivable except the planned-but-undanced flag.

### 2.8 Ratings table

- **Section**: `==Ratings==`.
- **Columns**: `Episode | Date | Official rating (millions) | Weekly rank for BBC One | Weekly rank for all UK TV`;
  `+ Share` in S8, S10–S16, S18–S20. Rows `Week N`, `Week N results`,
  `Week 1 (Night 1)`/`(Night 2)` (S8–S14), `Launch show` (S6+; S5 `Preview`),
  final row `! Series average` / `Series average<br>(excl. launch show)` built
  from `!` header cells with `{{N/A}}`.
- **Encodings**: the only tables written with inline `||` cells:
  `| {{dts|15 May}} || 4.61 || 20 || 40`; `{{dts}}` carries the day and month
  only (year from the infobox; S1 and S2 both aired in 2004), rendering as
  `<span data-sort-value="2004-05-15">15 May</span>`; `{{n/a}}` in some Share
  cells; curly-quote `scope` attributes; S24 future rows pre-filled with dates
  and empty ratings; S1 "Week 5" is dated 13 June while the Couples table says
  12 June.
- **Parse difficulty**: easy. **Primary** for episode transmission dates
  (performance vs results show) and audience figures.

### 2.9 Specials (not on the series pages)

Christmas, Children in Need, Sport Relief and the 20th-anniversary specials
are on `List of Strictly Come Dancing specials`
(captured as `data/wikipedia/wikitext/List_of_Strictly_Come_Dancing_specials.wikitext`;
not yet in `data/wikipedia/`). Tables there: 2004–2009
`Celebrity | Position on Strictly | Professional | Judges' scores | Dance [| Song]`
written as single-line `||` rows; 2010+ `Celebrity | Occupation | Professional | Judges' scores | Dance | Song [| Pantomime]`;
winner marked by a **row-level** `|- style="background:gold"` (2024 has a
malformed `|- style background=“background:silver;”`); scores written without
spaces `37 (8,10,9,10)`; a judge-order sentence per year; no Result column and
no row headers. Model specials as a distinct competition type with one "week".

### 2.10 Noise tables and the legend

Infobox (2-column key/value), `{{Multiple image}}` galleries, `<div class="legend">`
blocks (not tables, but useful) and the `{{Strictly Come Dancing}}` navbox.
Skip them; select data tables by caption/header/heading.

### 2.11 Notation summary

| Notation | Meaning | Wikitext | Rendered (legacy / Parsoid) |
|---|---|---|---|
| † bold green | highest total of the week | `{{fontcolor\|#004600\|'''31'''}}{{dagger\|alt=…}}`; `var(--color-success)` S22+ | `<span style="color: #004600;"><b>31</b></span>†` (alt lost) / `<span … data-mw='{"template":{"target":{"wt":"fontcolor"}…'>` + `<span data-mw='…"dagger"…"alt"…'>†</span>` |
| ‡ italic red | lowest total of the week | `{{fontcolor\|#800000\|''19''}}{{double-dagger\|alt=…}}`; no alt in S24 | `<span style="color: #800000;"><i>19</i></span>‡` |
| lightblue | bottom two / bottom three (S24 wk6) / "Participating" (S24 Couples) | `bgcolor="lightblue"` or `style="background:lightblue;"` | `<td bgcolor="lightblue">26<sup class="reference">[b]</sup></td>` |
| `f4c7b8` / `#f4c7b8` | eliminated | `bgcolor` or `style=background` | `<td bgcolor="f4c7b8">` |
| gold / silver / tan / `#d1c571` (typo `dlc571`) | Winners / Runners-up (Co-runners-up) / Third / Fourth | `bgcolor="gold"` (`Gold` S21) | — |
| lightgreen (empty or with "Withdrew") | withdrew | `bgcolor="lightgreen" \| {{efn\|name=Quitter\|…}}` (name varies or absent) | `<td bgcolor="lightgreen"><sup class="reference">[c]</sup></td>` |
| `fff383` (empty) | bye (excused, scores carried) | `bgcolor="fff383" \| {{efn\|name=OutSick\|…}}`; `colspan=2` S19; no efn S23 | `<td bgcolor="fff383"><sup class="mw-ref reference" data-mw='{"attrs":{"name":"OutSick"…'>[b]</sup></td>` |
| darkgray / darkgrey / lightgrey, colspan=K | already out of the competition | `colspan="6" bgcolor="darkgray" \|` | `<td colspan="6" bgcolor="darkgray"></td>` → pandas NaN |
| `{{NA}}` / `—` | did not dance by format (S4–S7 wks 1–2/1–4) | `\| {{NA}}`, `\|—`, malformed `\|33\| —` | `<td class="table-na" data-sort-value="">—</td>` |
| `a+b=c`, `a+b+c=t`, `+a+b=t`, `35+2=37` | multi-dance sum; leading `+` = cumulative with Show 1; small addend = rank points | `{{sort\|67\|}} \| 31+36=…` | `<td data-sort-value="67&#160;!">31+36=<span …><b>67</b></span>†</td>` |
| `[a]` `[b]` superscripts | explanatory footnotes (group lower-alpha): Bottom2, Elim, OutSick/Sick/Sickie, WD/Quitter/Withdrew, GuestJudge, "finished in first place" | `{{efn\|name=Bottom2}}` … `{{notelist}}` | legacy `<sup id="cite_ref-Bottom2_6-0" class="reference"><a href="#cite_note-Bottom2-6">[b]</a></sup>` with body in `<li id="cite_note-Bottom2-6">`; Parsoid `<sup class="mw-ref reference" typeof="mw:Extension/ref" data-mw='{…"name":"OutSick"…"body"…}'>` |
| `[12]` superscripts | citations, including inside header cells S22–S24 | `Scores<ref name="Week1Scores">…</ref>` | `Scores<sup class="reference">[39]</sup>` → pandas column `Scores[39]` |
| `<s>''Dance''</s>` | planned dance not performed | `bgcolor="lightgrey" \| <s>''Cha-cha-cha''</s>{{efn\|…}}` | `<s><i>Cha-cha-cha</i></s>` → pandas `Cha-cha-cha[a]` |
| "No scores received" / empty Scores | performed, unscored | `\| No scores<br>received` or `\|` | `<td>No scores<br>received</td>` |
| 5 or 3 marks in parentheses | 50-point or 30-point week | `42 (8, 9, 8, 9, 8)` | plain text |
| `;Night 1 (Friday)` / `;Show 1` / `====Show 1====` | sub-show labels | | `<dl><dt>Night 1 (Friday)</dt></dl>` or `<div class="mw-heading mw-heading4"><h4 id="Show_1">` |
| `{{dts\|15 May}}` | sortable date without year (Ratings) | | `<span data-sort-value="2004-05-15" style="white-space:nowrap">15 May</span>` |
| Status date | results-show date of exit | `Eliminated 1st<br /><small>on 22 May 2004</small>` | pandas inserts a space ("Eliminated 1st on 22 May 2004"); BS4 `get_text()` does not ("Eliminated 1ston 22 May 2004") |

---

## 3. Key facts that live outside tables

### 3.1 The judge-order sentence

Every page has an italic sentence immediately under `==Weekly scores==`:
"*Unless indicated otherwise, individual judges' scores in the charts below
(given in parentheses) are listed in this order from left to right: …*".
Any week with a different panel repeats the sentence as the first line of that
week's subsection. The infobox `judges` field is **not** in this order, and the
dance-off vote lists use a third order (head judge last). Observed orders:

| Series | Default order (left to right) | Per-week overrides |
|---|---|---|
| 1–6 | Craig Revel Horwood, Arlene Phillips, Len Goodman, Bruno Tonioli | none |
| 7 | Craig, Len, Alesha Dixon, Bruno | wks 12–14: Craig, Darcey Bussell, Len, Alesha, Bruno (5 judges, /50) |
| 8 | Craig, Len, Alesha, Bruno | none |
| 9 | Craig, Len, Alesha, Bruno | wk6: Craig, Jennifer Grey, Alesha, Bruno (Grey replaced Len; still /40) |
| 10–11 | Craig, Darcey, Len, Bruno | none |
| 12 | Craig, Darcey, Len, Bruno | wk3: Craig, Darcey, Donny Osmond, Len, Bruno (5 judges, /50) |
| 13–14 | Craig, Darcey, Len, Bruno | none |
| 15 | Craig, Darcey, Shirley Ballas, Bruno | wk5: Craig, Darcey, Shirley (3 judges, /30) |
| 16 | Craig, Darcey, Shirley, Bruno | wk5: Craig, Darcey, Shirley, Alfonso Ribeiro |
| 17 | Craig, Motsi Mabuse, Shirley, Bruno | wk5: Craig, Motsi, Shirley, Alfonso Ribeiro |
| 18 | Craig, Shirley, Motsi (3 judges, /30 all series) | wks 4–5: Craig, Shirley, Anton Du Beke |
| 19 | Craig, Motsi, Shirley, Anton Du Beke | wk9: Cynthia Erivo for Craig; wk10: Erivo for Motsi |
| 20–24 | Craig, Motsi, Shirley, Anton | none (S23 wk3 Erivo was a non-scoring mentor) |

The head judge is never first (3rd in S1–S17, 2nd in S18). The scale (30/40/50)
is simply 10 × the number of marks in the cell; the Scoring chart repeats the
50-point flag as a header footnote in S7 and S12 only.

### 3.2 Casting-vote prose

- S5–S22: Format section states the head judge (Len Goodman S5–S14, Shirley
  Ballas S15–S22) has the last and deciding vote ("if needed" from S21). Only
  the vote lists reveal when it was used.
- S23–S24: the casting vote **rotates**; each week's preamble says "X had the
  casting vote this week". Observed: S23 wk2 Mabuse, wk3 Ballas, wk4 Horwood,
  wk5 Du Beke, wk6 Ballas, wk7 Mabuse, wk8 Horwood, wk10 Ballas, wk11 Mabuse,
  wk12 Horwood; S24 wk2 Horwood, wk3 Du Beke, wk4 Ballas, wk5 Du Beke, wk6
  Mabuse, wk7 Ballas.

### 3.3 Dates exist only in Ratings and in Couples status cells

Weekly sections carry **no dates**. The Ratings table is the only source of
performance-show and results-show dates (`{{dts|D Month}}`, year from the
infobox), including the irregular ones: S7 wks 1–2 Friday nights; S8–S14
`Week 1 (Night 1)` Friday / `(Night 2)` Saturday; S20 wk11 Fri 2 Dec + Sat 3 Dec
and wk12 Sun 11 Dec + Mon 12 Dec (World Cup); results shows for no-elimination
weeks S21 wk11 and S23 wk9 but never for week 1 (S5–S6 excepted). The Couples
table status cell gives the results-show date of each exit (Saturday S1–S4,
S7; Sunday S5–S6, S8+), and withdrawal dates that are not show dates.
Infobox `first_aired` is the launch show from S6; `num_episodes` counts
launch + performance + results shows (S18 says 17, Ratings lists 18).

### 3.4 Byes, withdrawals and "no elimination" in prose and footnotes

The week preamble says who "was granted a bye" or "withdrew", and whether
there was no elimination (S1 wk1, S6 wk13, S7 wk13 no dance-off, S14 wk2
dance-off cancelled, S20 wk8 no dance-off, S21 wk11, S23 wk9). The same fact
is encoded as a coloured, usually footnoted, empty cell in the Scoring chart
(§2.3) and as the **absence of a row** in the weekly table. Withdrawals never
cancelled that week's elimination except where the withdrawal itself emptied
the bottom two (S21 wk11, S23 wk9). Bye and withdrawal footnote text is
Wikipedia prose (CC BY-SA): normalise to enumerated codes rather than copying.

### 3.5 Professional substitutions in `<small>` notes

Mid-series substitutions are written into the Couples table professional cell
as `<br />{{small|Name (Week N)}}` (S8 Ian Waite wk4 for Brendan Cole; S9
Brendan Cole wk9 for Robin Windsor; S14 Gorka Márquez wk5 for Brendan Cole;
S17 Kevin Clifton wks 6–7 for Neil Jones) or as two linked names with week
ranges (S22 Amy Dowden wks 1–6 / Lauren Oakley wks 7–13). S9 wk7 Brendan Cole
dancing for the injured Artem Chigvintsev (Holly) is in **prose and the weekly
row header only**. Weekly tables use the substitute's first name; the charts
keep the original (or `Amy/Lauren`).

### 3.6 Pre-series replacements and partner swaps (prose only)

S10 Johnny Ball: Aliona Vilani injured → Iveta Lukošiūtė; S11 Emma Slater →
Anya Garnis, Natalie Lowe → Aliona Vilani; S12 Robin Windsor → Trent Whiddon;
S17 Jamie Laing → Kelvin Fletcher (5–7 Sep 2019); S23 Kristian Nairn → Lewis
Cope (21 Aug 2025) and Dani Dyer, paired with Nikita Kuzmin at the launch show,
→ Amber Davies (23–26 Sep 2025). None of these appears in any table.

### 3.7 Other prose-only facts

Format section: elimination mechanism (ranking points, no dance-off S1–S4 and
S8–S9; dance-off otherwise; S22+ tie rule for ranking points). Theme and round
in the H3 heading (`Week 10: Movie Night (Quarter-final)`). Venues (Blackpool
Tower Ballroom, Wembley Arena, Elstree) in prose or heading. Musical guests
per week (S3, S6, S13+). Hosts' absences and guest hosts. Final format prose
("judges' choice", "showdance", "favourite", S17 "winner decided by public
vote alone"). The judges' leaderboard points and public vote are **never
published** on Wikipedia.

---

## 4. Identity resolution

### 4.1 Rules that worked (identity.py, 339 couples, S1–S24)

1. The **Couples table is the source of identity**. Key Celebrity and
   Professional on the **wiki-link target** (canonical article title, e.g.
   `Robert Rinder`, `Christine Lampard`, `Jason Wood (comedian)`); keep the
   display text as the per-series label. 339 distinct celebrities and 69
   distinct professionals by link.
2. Chart and weekly-table labels are `Celebrity & Professional` first names,
   celebrity always on the left. Split on `&`; match the left token against
   the display first word of celebrities **of that series**, the right token
   against professionals of that series; require exactly one couple. Never
   resolve a bare first name without its role (S3 Darren Gough vs Darren
   Bennett; S7 Natalie Cassidy vs Natalie Lowe; S23 Karen Carney vs Karen
   Hauer would collide). No two professionals share a first name within a
   series in S1–S24.
3. Strip a trailing initial before matching, then disambiguate on the surname
   initial: S7 `Ricky G. & Erin` / `Ricky W. & Natalie`; S17 `Emma B. & Anton`
   / `Emma W. & Aljaž`; S20 `Ellie S. & Nikita` / `Ellie T. & Johannes`;
   S21 `Angela R. & Kai` / `Angela S. & Carlos`.
4. Match on the **display** first word, not the link: `Judge Rinder & Oksana`,
   `Dr. Ranj & Janette`, `Rev. Richard & Dianne`, `Dr. Punam & Gorka`,
   `HRVY & Janette`, `JJ & Amy`, `DJ Spoony & Ola`, `La Voix & …`, mononyms
   Goldie and Lulu.
5. Keep the Couple id stable across professional changes and record the
   dancing professional on each Performance (S8, S9, S14, S17, S22).
6. Fail loudly on unresolved labels; keep an explicit per-series override map
   rather than fuzzy matching. Judges in vote lists are surnames; map through
   the series panel.
7. Take link-based identity from **one** snapshot per series: the 2024 HTML
   and the 2026 wikitext are different revisions and link targets can move.

### 4.2 Alias and override lists discovered

**Celebrity display ≠ link target (39 cases; sample)**

| Display (label first word) | Link target |
|---|---|
| Jason Wood | Jason Wood (comedian) |
| Judge Rinder | Robert Rinder |
| Christine Bleakley | Christine Lampard |
| Penny Lancaster-Stewart | Penny Lancaster |
| Dr. Ranj Singh | Ranj Singh |
| HRVY | Hrvy |
| Dev Griffin | Dev (DJ) |
| Emma Weymouth | Emma Thynn, Marchioness of Bath |
| Rev. Richard Coles, Dr. Punam Krishan | Richard Coles, Punam Krishan |

**Professional aliases (merge into one Person)**

| Variant | Canonical | Where |
|---|---|---|
| Karen Clifton (link and display) | Karen Hauer | S14–S17 |
| Camilla Sacre-Dallerup | Camilla Dallerup | S6 (label still "Camilla") |
| Anton du Beke | Anton Du Beke | specials page casing |
| Andrew Cuerden (unlinked) | name-only key | S3 |
| Gorka Marquez / Gorka Márquez, Aljaž with/without diacritics | one entity | S14+, S17 |

**Not aliases (traps)**: Hanna Karttunen (S1) and Hanna Haarala (S3) are
different people both labelled "Hanna"; Matt Dawson (celebrity, S4) and
Matthew Cutler (pro); Anton Du Beke is both a competing professional and a
judge in S18; celebrity Craig vs judge Craig.

**Label overrides (per series)**

| Series | Label | Resolve to | Reason |
|---|---|---|---|
| 9 | Anita & Brendan (wk9) | Anita Dobson & Robin Windsor couple | substitute pro |
| 9 | Holly & Brendan (wk7) | Holly Valance & Artem Chigvintsev couple | substitute pro (prose only) |
| 8 | Michelle & Ian (wk4) | Michelle Williams & Brendan Cole couple | substitute pro |
| 14 | Anastacia & Gorka (wk5) | Anastacia & Brendan Cole couple | substitute pro |
| 17 | Alex & Kevin (wks 6–7) | Alex Scott & Neil Jones couple | substitute pro |
| 22 | JB & Amy/Lauren (charts), JB & Lauren (wks 7–13) | JB Gill couple | replacement pro |
| 24 | Greame & Lauren (Average chart) | Graeme & Lauren | Wikipedia typo |
| various | Zöe/Zoë, Julien/Julian | same celebrity | spelling drift between tables |
| S22+ Couples | `{{nowrap\|Georgia &}} Giovanni` | Georgia & Giovanni | split label |

**Judge surname labels in vote lists**: `Horwood` (S5–S15, S18–S23) and
`Revel Horwood` (S16–S17, S24; the two research passes disagree about S22–S23,
so accept both everywhere); `Du Beke`; guests `Osmond` (S12 wk3), `Ribeiro`
(S16–S17 wk5), `Erivo` (S19 wks 9–10).

---

## 5. Two HTML dialects and snapshot discipline

### 5.1 What is in `data/wikipedia/`

| Series | Revision id | Page last edited | MediaWiki | Dialect markers |
|---|---|---|---|---|
| 1 | 1244627635 | 8 Sep 2024 | 1.43.0-wmf.22 | legacy: 3 `data-mw`, 0 `<section>` |
| 2 | 1244627751 | 8 Sep 2024 | 1.43.0-wmf.21 | legacy |
| 3 | 1244627935 | 8 Sep 2024 | 1.43.0-wmf.21 | legacy |
| 4 | 1242127749 | 25 Aug 2024 | 1.43.0-wmf.22 | legacy |
| 5 | 1242295044 | 26 Aug 2024 | 1.43.0-wmf.20 | legacy |
| 6 | 1216322036 | 30 Mar 2024 | 1.43.0-wmf.21 | legacy |
| 7 | 1224668913 | 19 May 2024 | 1.43.0-wmf.21 | legacy |
| 8 | 1240736843 | 17 Aug 2024 | 1.43.0-wmf.21 | legacy |
| 9 | 1220931343 | 26 Apr 2024 | 1.43.0-wmf.20 | legacy |
| 10 | 1242785187 | 28 Aug 2024 | 1.43.0-wmf.20 | legacy |
| 11 | 1241312935 | 20 Aug 2024 | 1.43.0-wmf.22 | legacy |
| 12 | 1216321922 | 30 Mar 2024 | 1.43.0-wmf.21 | legacy |
| 13 | 1243175757 | 30 Aug 2024 | 1.43.0-wmf.21 | legacy |
| 14 | 1242199763 | 25 Aug 2024 | 1.43.0-wmf.21 | legacy |
| 15 | 1240834304 | 17 Aug 2024 | 1.43.0-wmf.22 | legacy |
| 16 | 1240512477 | 15 Aug 2024 | 1.43.0-wmf.20 | legacy |
| 17 | 1240502497 | 15 Aug 2024 | 1.43.0-wmf.21 | legacy |
| 18 | 1240818000 | 17 Aug 2024 | 1.43.0-wmf.22 | legacy |
| 19 | 1245406239 | 12 Sep 2024 | 1.43.0-wmf.22 | legacy |
| 20 | 1240480200 | 15 Aug 2024 | 1.43.0-wmf.20 | legacy |
| 21 | 1234408899 | 14 Jul 2024 | 1.43.0-wmf.21 | legacy (`wgRevisionId": 1234408899` with a space) |
| 22 | 1382773255 | 30 Oct 2026 | 1.48.0-wmf.3 | Parsoid read view: 385 `data-mw`, 25 `<section>` |
| 23 | 1382773258 | 30 Oct 2026 | 1.48.0-wmf.3 | Parsoid: 366 `data-mw`, 25 `<section>` |
| 24 | 1384551432 | 8 Nov 2026 20:48 | 1.48.0-wmf.3 | Parsoid: 259 `data-mw`, 20 `<section>` |
| main | 1383712594 | — | 1.48.0-wmf.3 | Parsoid: 759 `data-mw` |

The revision id is in the page's `mw.config` JSON (`"wgRevisionId":NNN`;
S21 has a space after the colon, so match `wgRevisionId"\s*:\s*(\d+)`), and
the capture time is the file's commit date. The S22–S24 wikitext fetched on
8 Nov 2026 is the **same** revision as the S22–S24 HTML; the S1–S21 wikitext
is two years newer than the HTML and differs materially (S3 scoring-chart final
column is broken live; S6 live page has a `13+14` column and scored showdances
that the capture lacks; S1 wk5 and S2–S3 showdance cells are empty live but
"No scores received" in the captures; S13 `dlc571` and S17 "NOTE" are post-2024 edits).

### 5.2 Legacy parser HTML (S1–S21, MediaWiki 1.43)

- Templates are flattened: `{{fontcolor}}` → `<span style="color: #004600;">`,
  `{{dagger|alt=…}}` → bare `†` (**alt text lost**), `{{NA}}` → `<td class="table-na">—</td>`.
- Footnotes: `<sup id="cite_ref-Bottom2_6-0" class="reference"><a href="#cite_note-Bottom2-6">[b]</a></sup>`;
  body only reachable via `<li id="cite_note-Bottom2-6">` under `{{notelist}}`;
  the efn **name** survives only inside the id.
- No `<section>` wrappers; headings are `<div class="mw-heading mw-heading3"><h3 id="Week_3:_Blackpool_Week">`.
- Links are ordinary `<a href="/wiki/Title" title="Title">`.
- 3 `data-mw` attributes on the whole page, 0 `mw:Transclusion`.

### 5.3 Parsoid HTML (S22–S24 read view, MediaWiki 1.48; also the REST endpoint)

- `<div class="mw-content-ltr mw-parser-output" data-mw-parsoid-version="0.25.0.0-alpha1">`.
- Every transclusion carries `typeof="mw:Transclusion"` and a `data-mw` JSON
  attribute naming the template and its parameters: a cell rendering as `34 †`
  has two spans, `{{fontcolor|var(--color-success)|'''34'''}}` and
  `{{dagger|alt=This was the highest score of the night.}}`. S24 census from
  `data-mw`: cite web 53, dts 25, fontcolor 23, double-dagger 13, dagger 10,
  nowrap 9, efn 4, notelist 2.
- Footnotes: `<sup class="mw-ref reference" typeof="mw:Extension/ref" data-mw='{"attrs":{"name":"OutSick","group":"lower-alpha"},"body":{…},"parts":[{"template":{"target":{"wt":"efn"},"params":{"name":{"wt":"OutSick"},"1":{"wt":"This couple was excused…"}}}}]}'>`
  — a bye cell (`bgcolor=fff383`, visible text `[b]`) is decodable in place.
- `<section data-mw-section-id="N">` wraps every heading with its content;
  heading ids `Week_1`, `Week_2:_Movie_Week`, … make week slicing trivial.
- Links: `<a rel="mw:WikiLink" href="./Will_Best" title="Will Best">`.
- The REST variant (`/api/rest_v1/page/html/{title}`, HTML/2.8.0, 341 KB for
  S24 vs 63 KB wikitext) has no skin chrome, a `<base href>`, ids on every
  element and `ETag = W/"<revid>/<tid>/view"`; the read-view variant includes
  the skin. Selectors must not depend on ids.
- What is shared by both dialects and therefore safe to build on:
  `<div class="mw-heading">` + `<hN id>`, `<table class="wikitable">`,
  `<dl><dt>`, `<ul><li>`, `bgcolor`/`style`, `rowspan`/`colspan`, `<sup>` containing
  "reference" in its class, `<td class="table-na">`.

### 5.4 Recommended snapshot and revision discipline

1. **Re-fetch all 24 series pages (and the specials page) in one pass** so the
   repository holds a single dialect at a single point in time; the current
   mix of 2024 legacy and 2026 Parsoid captures is a parser-testing asset but
   a poor base for the dataset. Re-fetching S1–S21 now will yield Parsoid HTML.
2. **Store wikitext alongside HTML**, fetched through
   `action=query&prop=revisions&rvslots=main&rvprop=ids|timestamp|sha1|content`
   (several titles per call, `maxlag=5`, descriptive User-Agent), at
   `data/wikipedia/wikitext/series_N.wikitext` with a sidecar recording
   `pageid`, `revid`, `sha1`, `timestamp` and fetch time. The REST HTML
   endpoint honours `If-None-Match` and `action=raw` honours
   `If-Modified-Since`, so refreshes cost nothing when unchanged.
3. **Record provenance per fact**: page title, `revid`, capture timestamp and
   the section/table it came from. Every Series/Episode/Performance row
   carries `source_revid`. Never mix revisions within one series.
4. **Pin and debounce the live series**: S24 saw 761 revisions by 8 Nov 2026,
   66 of them on one Saturday evening; editors pre-create next week's table
   with blank Scores and Result cells. Accept a snapshot as stable only after
   ~10 minutes with no new revision, and define "week complete" as "all
   Scores cells parse and all Result cells are non-empty" — an Episode status
   field (scheduled / scores_in / results_in / verified), not code.
5. **Keep week-by-week historical revisions** for the airing series
   (`action=parse&oldid=` or REST `/page/html/{title}/{revid}`) to back-test
   the parser on half-edited states; back-fill S22–S23 the same way.
6. **Run the parser on both dialects in CI** (the current S6 and S24 captures
   are the fixtures) until S1–S21 are re-captured, then keep one legacy fixture
   for regression.
7. **Licensing**: facts are not copyrightable; prose (footnote wording,
   preambles) is CC BY-SA 4.0. Store note text only in clearly labelled
   `source_note` fields with page URL + revid, and normalise everything else to codes.

---

## 6. Parser prototype results

Scripts are in `prototypes/` (see `prototypes/README.md`); they were run on
Python 3.12 with beautifulsoup4 4.15, lxml 6.1, pandas 3.1 and
mwparserfromhell 0.7.2. Row counts below were reproduced from the repository
root after the paths were made relative.

### 6.1 `pandas.read_html` on the captured HTML (poc1_read_html.py)

Tested on S6 (legacy, 23 tables found) and S24 (Parsoid, 17 tables).

Worked: weekly tables come out as clean five-column frames with rowspans
expanded (14 in S6, 8 in S24); Couples, Average chart (S24 six columns with
`Place`, ties copied down) and Ratings parse cleanly; the score strings
`27 (5, 7, 8, 7)` are intact; Parsoid and legacy HTML parse identically.

Broke: (a) Scoring chart and Dance chart get a 2–3 level MultiIndex and cells
such as `35+38=73‡[a]`, `35[b]`, `[b]` (a bye cell is just its footnote
letter), `—` for `{{NA}}`, NaN for filler; (b) duplicate week columns become
`11`, `11.1` and S24's over-declared colspan yields `Unnamed: 14_level_1`;
(c) **all link targets and all `bgcolor`/`style` are lost**, i.e. identity and
every status colour; (d) S22–S24 header refs become `Scores[39]`;
(e) group-dance rows shift because of colspan and marathon rows yield `1`…`7`
as Scores; (f) the Ratings "Series average" row becomes a data row;
(g) pandas 3 keeps NaN as float under `astype(str)`; (h) tables cannot be
selected by index (23 vs 17).

Verdict: fine for a quick total reconciliation of the weekly tables; unusable
as the main path.

### 6.2 BeautifulSoup + lxml week walker (poc2_bs4_weeks.py, sdc_common.py)

Approach: iterate `<h3 id^="Week_">` (inside `<div class="mw-heading">`),
collect siblings until the next h2/h3 (descending into `<section>` for
Parsoid REST output), expand every wikitable with a rowspan/colspan grid
(`table_grid`, marking copied cells), map columns by header text with `[n]`
refs stripped, parse score/music/result, read `bgcolor` or `style`
background, pick up `<dl>`/`<h4>` Night/Show labels, and parse the
`<dl><dt>Judges' votes…</dt></dl><ul>` list.

Results: S1 55 performance rows, 0 votes; S6 120 rows (116 with four marks,
every per-judge list summed to its total), 48 votes including the S6 wk1
head-judge parenthetical, results {Safe, Bottom two, Eliminated, Withdrew,
Third place, Runners-up, Winners} with backgrounds {lightblue, f4c7b8,
lightgreen, tan, silver, gold}; S9 131 rows with Night 1/Night 2 and Show 1/
Show 2 labels captured from `<dl>`/`<h4>`, 0 votes (no dance-off); S12 147
rows, 127 four-judge + 14 five-judge detected automatically, 45 votes; S21 129
rows, 40 votes; S24 97 rows (88 scored), 24 votes including three "Did not
vote" flags, 27 rows with a Film/Icon theme column, "Bottom three" captured.
**The same code handled legacy and Parsoid HTML**; only the footnote `<sup>`
class differs ("reference" vs "mw-ref reference").

Broke, and the fixes: (a) `get_text(" ", strip=True)` turns
`"Song" — Artist` into `" Song " —Artist`; use `get_text("")` keeping
whitespace nodes, then collapse spaces; (b) group-dance rows copy the colspan
Music cell into Result — ignore colspanned cells in Result; (c) marathon rows
give Scores `1`…`7` under a rowspan couple — detect via the Dance cell and
store as rank points; (d) shared score cells (`rowspan=2` across two dances)
are silently duplicated to both dances and must be flagged; (e) "No scores |
received" (the `<br>` rendered as a separator) and empty in-progress cells are
non-scores; (f) launch-show sections have no table and S1–S4, S8, S9 have no
vote lists, so eliminations there come from Result cells; (g) result labels
drift (`Runners-Up`, `Gold`, `#f4c7b8` vs `f4c7b8`) and need normalisation;
(h) the HTML snapshot is a different revision from the wikitext.

### 6.3 mwparserfromhell 0.7.2 on the raw wikitext (poc3_mwparser.py)

Approach: `get_sections(levels=[3])` matching `Week N`, `filter_tags(tag="table")`,
iterate tr/th/td Tags, `strip_code` after template handling (efn removed,
dagger → †, fontcolor/nowrap/small unwrapped, `{{sort}}` dropped, `{{NA}}` → N/A),
capture link targets and `bgcolor` per cell.

Results: S6 120 rows identical in substance to the BS4 run; S9 131; S24 97
(after fixes). Unique wins: wikilink targets for dance (`Sing, Sing, Sing
(With a Swing)`), song and artist per cell; efn **names** (Bottom2, Elim,
OutSick, Quitter) and dagger markers as structured data; a template census per
scoring chart (S6: fontcolor 31, dagger 19, double-dagger 15, na 26, efn 25,
sort 9; S24: fontcolor 21, dagger 9, double-dagger 12, efn 2); the malformed
S6 `|33| —` cell is visible as `attrs=['33'] contents='—'` instead of
rendering silently.

Broke: (a) S22–S24 tables have no `|-` before the header row, so the header
th Tags sit directly in `table.contents` and must be collected as an implicit
first row; (b) the empty caption line `|+` (S24 wks 3–8) parses as a top-level
`td` Tag with contents `|+\n`, polluting that implicit row — S24 went from 30
to 97 rows once the empty `|+` lines were stripped; (c) `strip_code()` deletes
templates wholesale, so `{{nowrap|Christopher & Hanna}}` → `''` and
`{{small|on 23 October 2023}}` → `''` until unwrapped; (d) rowspan handling is
manual: continuation rows have fewer cells and when the Score cell is also
rowspan (S9) the columns mis-align ("Viennese waltz" landed in Scores) — a
proper grid expander is needed; (e) Ratings rows use inline `||` cells,
`{{dts}}` and `{{N/A}}` header cells and need a separate path; (f) slower, and
the project would have to commit wikitext snapshots.

### 6.4 Parsoid HTML inspection (poc4_parsoid.py)

Compared the S24 REST Parsoid capture with the repository's S6 (legacy) and
S24 (read-view Parsoid) captures. Parsoid keeps the template layer: efn name
and body per `<sup>`, dagger alt text, canonical link titles, explicit
`<section>` blocks. Legacy HTML has none of that: dagger alt lost, efn bodies
only via `#cite_note` ids, `{{NA}}` recognisable only by `class="table-na"`.
The repository's own S22–S24 captures **are** Parsoid output, so the project
already mixes two dialects (§5).

### 6.5 Identity resolution (identity.py)

339 couples parsed from the 24 wikitext pages (S1 8, S2 10, S18 12, others
12–16); every Scoring-chart label resolved except `JB & Amy/Lauren` (S22);
collision report: celebrity/celebrity Ricky (S7), Emma (S17), Ellie (S20),
Angela (S21); celebrity/pro Darren (S3), Natalie (S7), Karen (S23); pro name
change Karen Clifton/Karen Hauer; 39 display/link mismatches; 5 mid-series pro
replacements; 1 unlinked pro. Pitfalls: all-`th` header rows parsed as
couples until skipped; rows sharing a rowspan Status cell have only three
cells and were dropped until handled; `{{nowrap}}` labels came back empty from
`strip_code`; `Greame & Lauren` and `Amy/Lauren` need overrides.

### 6.6 Recommended approach

1. **Primary parser: BeautifulSoup + lxml over Parsoid HTML**, built around
   headings rather than table indexes. `pandas.read_html` loses links and
   colours; mwparserfromhell needs a hand-written grid expander and chokes on
   the S22–S24 header/caption quirks. Parsoid HTML (REST
   `/api/rest_v1/page/html/{title}/{revid}`, or the read view for S22+) keeps
   the template layer: `data-mw` gives efn names, dagger alt text and
   canonical link titles for free, so the same walker serves every series
   once S1–S21 are re-captured as Parsoid for a known revision. The legacy
   HTML captures stay in the repo as regression fixtures only.
   *Decision (reconciles this document with `docs/data-access-options.md`):*
   the **stored canonical capture is the raw wikitext** fetched through the
   Action API (it carries `revid`, `sha1` and `timestamp`, and is what gets
   committed per revision; see `scripts/fetch-wikitext.py` and
   `data/wikipedia/wikitext/MANIFEST.csv`); the **parser's primary input is
   the Parsoid HTML of that same revision**. The two are fetched together.
2. **Keep mwparserfromhell over the stored wikitext as the independent second
   reading** for cross-checks (template census per chart, efn names, link
   targets) and as the fallback if a table ever defeats the HTML walker.
3. **One rowspan/colspan-aware grid expander for every table**
   (`sdc_common.table_grid`), marking rowspan- and colspan-copied cells, so
   multi-dance rows inherit couple and result, group-dance rows do not inherit
   a bogus Result, and shared score cells are flagged.
4. **Column mapping by header text** with ref markers stripped; any header
   beyond Couple/Scores/Dance/Music/Result is a theme attribute.
5. **Score grammar** `^(\d+)\s*\(\s*(\d+(?:\s*,\s*\d+)*)\s*\)$` (no spaces for
   specials); assert sum == total; 3/4/5 marks is data, not an error; judge
   order = series sentence overridden by any italic per-week sentence; the
   scale is 10 × marks. Non-score cells: empty, "No scores received", bare
   integers on marathon/instant-dance rows (detected by the Dance cell).
6. **Music**: `get_text("")`, collapse whitespace, split once on `\s[—–]\s`,
   recognise `from ''X''` as a source work, split multi-song cells on ` / ` or
   `<br>`, keep the raw text.
7. **Identity** as in §4: link-target keys, per-series display labels, alias
   table, explicit per-series override map, fail loudly.
8. **Colour → meaning from the page's own `{{legend}}` block**, with the
   footnote name as corroboration when present (S23 has none).
9. **Validation layer**: regenerate the Scoring chart, Average chart and Dance
   chart from Performances and diff them against the parsed derivable tables;
   assert Couples Status order == elimination week order, Bottom two ==
   dance-off participants, votes majority == eliminated couple.
10. **Specials** via a separate routine over the specials page (row-style
    winner, unspaced scores, "Position on Strictly" column).

---

## 7. Per-series summary

Dates are first and last live/competition shows unless stated (launch shows in
brackets). "Head" marks the head judge. Judge count is the number of marks per
score cell. "Dance-off" summarises the series rule and its exceptions.

| S | Dates | Judges (score order) | Judges | Couples | Weeks | Dance-off rule | Results-show pattern |
|---|---|---|---|---|---|---|---|
| 1 | 15 May – 3 Jul 2004 | Craig Revel Horwood, Arlene Phillips, Len Goodman (head), Bruno Tonioli | 4 | 8 | 8 | None: ranking points, lowest of bottom two out; no elimination wk1 (1+2 column) | One Saturday show per week; separate results episode only for the final |
| 2 | 23 Oct – 11 Dec 2004 | as S1 | 4 | 10 | 8 | None (ranking points); elimination every week | Same-night Saturday results show from wk2 |
| 3 | 15 Oct – 17 Dec 2005 | as S1 | 4 | 12 | 10 | None (ranking points) | Same-night Saturday results |
| 4 | 7 Oct – 23 Dec 2006 | as S1 | 4 | 14 | 12 | None (last series without); half-field wks 1–2; Tarbuck withdrew wk3 | Same-night Saturday results |
| 5 | 6 Oct (preview 29 Sep) – 22 Dec 2007 | as S1 | 4 | 14 | 12 | Dance-off introduced; Len casting vote; half-field wks 1–2 | Sunday results show (final Saturday) |
| 6 | 20 Sep (launch 13 Sep) – 20 Dec 2008 | as S1 | 4 | 16 | 14 | Dance-off, Len casting; none in wk13 (tie bug, 13+14 column); split weeks 1–4 | Sunday results |
| 7 | 18 Sep – 19 Dec 2009 | Craig, Len (head), Alesha Dixon, Bruno; Darcey Bussell guest wks 12–14 | 4 (5 wks 12–14) | 16 | 14 | Dance-off, Len casting; none in wk13; Jade bye wk9, withdrew wk10 | Saturday only; wks 1–2 Friday + Saturday nights, half field |
| 8 | 1 Oct (launch 11 Sep) – 18 Dec 2010 | Craig, Len (head), Alesha, Bruno | 4 | 14 | 12 | **No dance-off** (bottom two still announced); double elimination wk11 | Sunday results; wk1 Night 1/Night 2, no elimination; wk11 two nights; final two shows |
| 9 | 30 Sep (launch 10 Sep) – 17 Dec 2011 | Craig, Len (head), Alesha, Bruno; Jennifer Grey for Len wk6 | 4 | 14 | 12 | **No dance-off**; double elimination wk11 | Sunday results; wk1 two nights; final two shows (Blackpool) |
| 10 | 5 Oct (launch 15 Sep) – 22 Dec 2012 | Craig, Darcey Bussell, Len (head), Bruno | 4 | 14 | 12 | Dance-off reinstated, Len casting; final 4 couples, Show 1 elimination to 4th | Sunday results; wk1 two nights; final two shows |
| 11 | 27 Sep (launch 7 Sep) – 21 Dec 2013 | as S10 | 4 | 15 | 13 | Dance-off, Len casting; Swing-a-thon wk11 | Sunday; wk1 two nights; final two shows |
| 12 | 26 Sep (launch 7 Sep) – 20 Dec 2014 | as S10; Donny Osmond guest wk3 | 4 (5 wk3) | 15 | 13 | Dance-off, Len casting (used wks 5, 11, 12); Waltz-a-thon wk11 | Sunday; wk1 two nights; final two shows |
| 13 | 25 Sep (launch 5 Sep) – 19 Dec 2015 | as S10 | 4 | 15 | 13 | Dance-off, Len casting; Quickstep-a-thon wk10 | Sunday from wk2; wk1 two nights; final two shows |
| 14 | 23 Sep (launch 3 Sep) – 17 Dec 2016 | as S10 (Len's last) | 4 | 15 | 13 | Dance-off, Len casting; wk2 dance-off cancelled (public vote); Will Young withdrew wk4; Cha-Cha-Challenge wk10 | Sunday from wk2; wk1 two nights; final one show |
| 15 | 23 Sep (launch 9 Sep) – 16 Dec 2017 | Craig, Darcey, Shirley Ballas (head), Bruno | 4 (3 wk5) | 15 | 13 | Dance-off, Ballas casting (2–2 wk7); Paso doble-thon wk10; final 4 with 3 joint runners-up | Sunday from wk2; wk1 single Saturday; Launch show H3 |
| 16 | 22 Sep (launch 8 Sep) – 15 Dec 2018 | as S15; Alfonso Ribeiro for Bruno wk5 | 4 | 15 | 13 | Dance-off, Ballas casting; Lindy Hop-a-thon wk10; Couple's Choice introduced | Sunday from wk2 |
| 17 | 21 Sep (launch 7 Sep) – 14 Dec 2019 | Craig, Motsi Mabuse, Shirley (head), Bruno; Ribeiro wk5 | 4 | 15 | 13 | Dance-off, Ballas casting (2–2 wks 6, 11); Will Bayley bye wk6, withdrew wk7; no marathon | Sunday from wk2 |
| 18 | 24 Oct (launch 17 Oct) – 19 Dec 2020 | Craig, Shirley (head), Motsi; Anton Du Beke for Motsi wks 4–5 | 3 | 12 | 9 | Dance-off, Ballas casting; Nicola & Katya withdrew wk4; COVID series, no Blackpool/marathon | Sunday from wk2 |
| 19 | 25 Sep (launch 18 Sep) – 18 Dec 2021 | Craig, Motsi, Shirley (head), Anton Du Beke; Cynthia Erivo wk9 (for Craig), wk10 (for Motsi) | 4 | 15 | 13 | Dance-off, Ballas casting; 3 byes, 2 withdrawals (AJ before the final → 2-couple final) | Sunday from wk2 |
| 20 | 24 Sep (launch 23 Sep) – 17 Dec 2022 | as S19 | 4 | 15 | 13 | Dance-off, Ballas casting; wk8 bottom two but no dance-off (Tony withdrew); final 4, 3 runners-up | Sunday from wk2; wk11 Fri/Sat, wk12 Sun/Mon |
| 21 | 23 Sep (launch 16 Sep) – 16 Dec 2023 | as S19 | 4 | 15 | 13 | Dance-off, Ballas casting "if needed"; wk11 no elimination (Nigel withdrew; 11+12 column); Amanda bye wk5, withdrew wk6 | Sunday from wk2 (results show even for wk11) |
| 22 | 21 Sep (launch 14 Sep) – 14 Dec 2024 | as S19 | 4 | 15 | 13 | Dance-off, Ballas casting (2–2 wk8); Samba-thon wk10; Amy Dowden → Lauren Oakley wks 7–13 | Sunday from wk2 |
| 23 | 27 Sep (launch 20 Sep) – 20 Dec 2025 | as S19; Erivo non-scoring mentor wk3 | 4 | 15 | 13 | Dance-off, **rotating casting vote** (stated weekly); wk9 no elimination (La Voix; 9+10 column); instant-dance points wk10; 2 pre-series replacements | Sunday from wk2 (results show even for wk9) |
| 24 | 26 Sep (launch 19 Sep) – 19 Dec 2026 (in progress) | as S19 | 4 | 15 | 13 planned (7 complete) | Dance-off, rotating casting vote; wk6 **bottom three**, "votes to eliminate"; byes wk4, wk7 | Sunday from wk2; Movie Week moved to wk2, Icons wk4 |
