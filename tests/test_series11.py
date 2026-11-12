"""Acceptance tests for series 11 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t11():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(11, REPO, REPO / "data/wikipedia/parsoid/series_11.parsoid.html", manifest["Strictly_Come_Dancing_series_11"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t11):
    assert not [c for c in t11["_report"]["checks"] if not c[1]]
    assert not t11["_report"]["unresolved"] and not t11["discrepancies"] and not t11["_report"]["warnings"]


def test_swing_marathon_with_dance_off_a110(t11):
    mar = [p for p in t11["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 6 and all(p["dance_key"] == "swing" and p["week_key"] == "S11W11" for p in mar)
    assert one(t11["couple_weeks"], "couple_week_key", "S11W11-natalie-gumede")["d_week_total"] == 41
    r = one(t11["results_rounds"], "round_key", "S11R11")
    assert r["dance_off_status"] == "held" and r["exit_count"] == 1
    hyp = one([v for v in t11["dance_off_votes"] if v["results_round_key"] == "S11R11"], "vote_kind", "hypothetical_not_cast")
    assert hyp["couple_key"] == "S11-ashley-taylor-dawson"


def test_four_consecutive_dance_offs_a115(t11):
    rows = [one(t11["couple_weeks"], "couple_week_key", f"S11W{w:02d}-mark-benton") for w in (7, 8, 9, 10)]
    assert [cw["result_status"] for cw in rows] == ["bottom_two", "bottom_two", "bottom_two", "eliminated"]
    assert all(cw["danced_off"] == "true" for cw in rows)
    for k in ("S11R08", "S11R09"):  # 3-1 splits with Len voting in the majority: not pivotal
        assert one(t11["results_rounds"], "round_key", k)["casting_vote_used"] == "false"


def test_bye_and_labels_a114_a118(t11):
    cw = one(t11["couple_weeks"], "couple_week_key", "S11W07-natalie-gumede")
    assert cw["participation_status"] == "bye" and cw["bye_granted"] == "true" and cw["absence_reason"] == "illness"  # fainted in dress rehearsal
    assert one(t11["couples"], "couple_key", "S11-ashley-taylor-dawson")["chart_label"] == "Ashley & Ola"
    assert one(t11["couples"], "couple_key", "S11-sophie-ellis-bextor")["chart_label"] == "Sophie & Brendan"
    assert one(t11["couple_partnerships"], "couple_key", "S11-mark-benton")["pro_person_key"] == "iveta-lukosiute"


def test_two_show_final_a112(t11):
    sophie = one(t11["couples"], "couple_key", "S11-sophie-ellis-bextor")
    assert sophie["final_placement"] == 4 and sophie["exit_round_key"] == "S11R13a" and sophie["exit_episode_key"] == "S11W13-S2"
    assert one(t11["couple_weeks"], "couple_week_key", "S11W13-sophie-ellis-bextor")["result_status"] == "fourth"
    assert one(t11["results_rounds"], "round_key", "S11R13a")["exit_count"] == 1
    assert len([c for c in t11["couples"] if c["final_placement"] == 2]) == 2
    abbey = [p for p in t11["performances"] if p["couple_key"] == "S11-abbey-clancy" and p["week_key"] == "S11W12"]
    assert [p["stated_total"] for p in abbey] == [39, 39]  # merged score cell (A111)
    assert one(t11["couple_weeks"], "couple_week_key", "S11W13-natalie-gumede")["d_is_highest_of_week"] == "true"


def test_volumes(t11):
    assert len(t11["couples"]) == 15 and len(t11["couple_weeks"]) == 195
    assert len([p for p in t11["performances"] if p["episode_key"] == "S11W01-N1"]) == 6
    assert len(t11["panel_seats"]) == 15 * 4
