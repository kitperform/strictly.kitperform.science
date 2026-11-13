"""Acceptance tests for series 4 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t4():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(4, REPO, REPO / "data/wikipedia/parsoid/series_4.parsoid.html", manifest["Strictly_Come_Dancing_series_4"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t4):
    assert not [c for c in t4["_report"]["checks"] if not c[1]]
    assert not t4["_report"]["unresolved"] and not t4["_report"]["warnings"]
    assert {d["discrepancy_key"] for d in t4["discrepancies"]} == {"CoupleWeek|S04W02-jimmy-tarbuck|participation_status|1"}


def test_split_launch_a027(t4):
    fr = {r["format_rule_key"]: r for r in t4["format_rules"]}
    assert fr["S04W01-FR"]["field_subset"] == "half_a" and fr["S04W02-FR"]["field_subset"] == "half_b"
    assert len([p for p in t4["performances"] if p["week_key"] == "S04W01" and p["episode_key"]]) == 7
    mambo = [p for p in t4["performances"] if p["week_key"] == "S04W01" and p["performance_kind"] == "group_unscored"]
    assert len(mambo) == 7 and all(p["dance_key"] == "mambo" and p["episode_key"] == "" and p["group_key"] == "S04W01-G1" for p in mambo)
    carol1 = one(t4["couple_weeks"], "couple_week_key", "S04W01-carol-smillie")
    assert carol1["participation_status"] == "group_only" and carol1["result_status"] == "exempt" and carol1["results_round_key"] == ""
    assert one(t4["couple_weeks"], "couple_week_key", "S04W02-matt-dawson")["participation_status"] == "group_only"
    for k in ("S04R01", "S04R02"):
        r = one(t4["results_rounds"], "round_key", k)
        assert r["exit_count"] == 1 and r["elimination_mechanism_actual"] == "ranking_points_no_dance_off" and r["dance_off_status"] == "not_in_format"
    assert not t4["dance_off_votes"]


def test_jimmy_tarbuck_a030(t4):
    c = one(t4["couples"], "couple_key", "S04-jimmy-tarbuck")
    assert c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S04W03" and c["exit_reason"] == "medical_advice" and c["exit_timing"] == "before_live_show"
    assert c["exit_episode_key"] == "" and c["exit_date_kind"] == "announcement" and c["final_placement"] == 12
    assert one(t4["couple_weeks"], "couple_week_key", "S04W01-jimmy-tarbuck")["result_status"] == "bottom_two"
    assert one(t4["couple_weeks"], "couple_week_key", "S04W02-jimmy-tarbuck")["participation_status"] == "not_scheduled"  # no group cell in the Dance chart (rule W2)
    assert not [p for p in t4["performances"] if p["couple_key"] == "S04-jimmy-tarbuck" and p["week_key"] == "S04W02"]
    assert one(t4["couple_weeks"], "couple_week_key", "S04W03-jimmy-tarbuck")["result_status"] == "withdrew"
    assert one(t4["results_rounds"], "round_key", "S04R03")["exit_count"] == 1  # DJ Spoony still eliminated
    assert one(t4["couples"], "couple_key", "S04-dj-spoony")["chart_label"] == "DJ Spoony & Ola"


def test_results_inside_the_show_and_final_a029(t4):
    eps = {e["episode_key"]: e for e in t4["episodes"]}
    assert eps["S04W06-P"]["episode_kind"] == "performance_and_results" and "S04W06-R" not in eps
    assert eps["S04W05-R"]["episode_kind"] == "results"
    mark = [p for p in t4["performances"] if p["couple_key"] == "S04-mark-ramprakash" and p["week_key"] == "S04W12"]
    assert [p["selection_role"] for p in mark] == ["repeat_favourite_ballroom", "repeat_favourite_latin", "same_song", "showdance"]
    assert mark[3]["scoring_mode"] == "unscored"
    assert one(t4["couple_weeks"], "couple_week_key", "S04W12-mark-ramprakash")["d_week_total"] == 110
    semi = [p for p in t4["performances"] if p["couple_key"] == "S04-mark-ramprakash" and p["week_key"] == "S04W11"]
    assert {p["dance_key"] for p in semi} >= {"argentine-tango"}
    assert len(t4["couples"]) == 14 and len(t4["weeks"]) == 12 and len(t4["couple_weeks"]) == 168
