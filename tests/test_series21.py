"""Acceptance tests for series 21 (complete series; revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t21():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(21, REPO, REPO / "data/wikipedia/parsoid/series_21.parsoid.html", manifest["Strictly_Come_Dancing_series_21"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t21):
    assert not [c for c in t21["_report"]["checks"] if not c[1]]
    assert not t21["_report"]["unresolved"] and not t21["discrepancies"] and not t21["_report"]["warnings"]


def test_nigel_harman_withdrawal_a230(t21):
    c = one(t21["couples"], "couple_key", "S21-nigel-harman")
    assert c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S21W11" and c["exit_timing"] == "before_live_show" and c["exit_reason"] == "injury" and c["final_placement"] == 5
    r = one(t21["results_rounds"], "round_key", "S21R11-12")
    assert r["label"] == "11+12" and r["week_keys"] == "S21W11|S21W12" and r["combined_reason"] == "withdrawal_carry_over" and r["votes_carried_over"] == "false" and r["exit_count"] == 1
    assert "S21R11" not in {x["round_key"] for x in t21["results_rounds"]}
    assert one(t21["couple_weeks"], "couple_week_key", "S21W11-bobby-brazier")["result_status"] == "carried_forward"
    bobby12 = one(t21["couple_weeks"], "couple_week_key", "S21W12-bobby-brazier")
    assert bobby12["result_status"] == "bottom_two" and bobby12["results_round_key"] == "S21R11-12"
    assert one(t21["couples"], "couple_key", "S21-annabel-croft")["exit_round_key"] == "S21R11-12"
    w11 = [p for p in t21["performances"] if p["week_key"] == "S21W11"]
    assert len(w11) == 4 and all(p["theme_column_label"] == "Musical" for p in w11)  # five couples left, Nigel withdrew


def test_amanda_abbington_a232_a233(t21):
    bye = one(t21["couple_weeks"], "couple_week_key", "S21W05-amanda-abbington")
    assert bye["participation_status"] == "bye" and bye["bye_granted"] == "true" and bye["absence_reason"] == "medical_advice"
    wd = one(t21["couple_weeks"], "couple_week_key", "S21W06-amanda-abbington")
    assert wd["participation_status"] == "absent_withdrawn" and wd["result_status"] == "withdrew" and wd["results_round_key"] == ""
    c = one(t21["couples"], "couple_key", "S21-amanda-abbington")
    assert c["exit_week_key"] == "S21W06" and c["final_placement"] == 11 and c["exit_timing"] == "before_live_show"
    assert one(t21["results_rounds"], "round_key", "S21R06")["exit_count"] == 1  # Zara still eliminated that week


def test_two_angelas_and_final_a231(t21):
    assert one(t21["couples"], "couple_key", "S21-angela-scanlon")["chart_label"] == "Angela S. & Carlos"
    assert one(t21["couples"], "couple_key", "S21-angela-rippon")["chart_label"] == "Angela R. & Kai"
    bobby = [p for p in t21["performances"] if p["couple_key"] == "S21-bobby-brazier" and p["week_key"] == "S21W13"]
    assert [p["stated_total"] for p in bobby] == [39, 39, 39]
    assert len([c for c in t21["couples"] if c["final_placement"] == 2]) == 2
    assert one(t21["couples"], "couple_key", "S21-ellie-leach")["final_placement"] == 1
    assert one(t21["couple_weeks"], "couple_week_key", "S21W13-ellie-leach")["d_is_lowest_of_week"] == "true"


def test_volumes_and_rules(t21):
    assert len(t21["performances"]) == 129 and len(t21["judge_marks"]) == 516 and len(t21["couple_weeks"]) == 195
    assert all(r["casting_vote_slug"] == "shirley-ballas" and r["casting_vote_source_kind"] == "inherited" for r in t21["results_rounds"] if r["round_kind"] == "standard")
    assert one(t21["format_rules"], "format_rule_key", "S21-FR")["rank_tie_policy"] == "unstated"
    assert one(t21["episodes"], "episode_key", "S21W09-P")["venue_key"] == "blackpool-tower-ballroom"


def test_amy_dowden_unpartnered_a237(t21):
    amy = one(t21["series_people"], "series_person_key", "S21-amy-dowden-professional")
    assert amy["roster_status"] == "unpartnered" and amy["reason"] == "illness"
    pm = [m for m in t21["performance_music"] if m["performance_key"] == "S21W05-P-adam-thomas-couples-choice"]
    assert len(pm) == 3 and {m["artist_key"] for m in pm} == {"backstreet-boys"}  # 'All by Backstreet Boys' applies to every song
