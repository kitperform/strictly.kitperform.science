"""Acceptance tests for series 1, the original eight-couple series of 2004 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t1():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(1, REPO, REPO / "data/wikipedia/parsoid/series_1.parsoid.html", manifest["Strictly_Come_Dancing_series_1"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t1):
    assert not [c for c in t1["_report"]["checks"] if not c[1]]
    assert not t1["_report"]["unresolved"] and not t1["_report"]["warnings"]


def test_spring_2004_dates_a007(t1):
    s = t1["series"][0]
    assert s["year_start"] == 2004 and s["first_live_date"] == "2004-05-15" and s["final_date"] == "2004-07-03" and s["launch_date"] == ""
    assert one(t1["episodes"], "episode_key", "S01W02-P")["episode_kind"] == "performance_and_results"
    assert one(t1["episodes"], "episode_key", "S01W08-R")["episode_kind"] == "results"


def test_week_one_and_two_combined_a001(t1):
    r = one(t1["results_rounds"], "round_key", "S01R01-02")
    assert r["week_keys"] == "S01W01|S01W02" and r["elimination_mechanism_actual"] == "ranking_points_no_dance_off" and r["votes_carried_over"] == "" and r["exit_count"] == 1
    assert all(cw["result_status"] == "carried_forward" for cw in t1["couple_weeks"] if cw["week_key"] == "S01W01")
    assert one(t1["couples"], "couple_key", "S01-jason-wood")["exit_round_key"] == "S01R01-02"
    assert one(t1["format_rules"], "format_rule_key", "S01W01-FR")["week_has_elimination"] == "false"


def test_week_five_date_conflict_a004(t1):
    ep = one(t1["episodes"], "episode_key", "S01W05-P")
    assert ep["air_date"] == "2004-06-12" and ep["air_date_source"] == "couples_table" and ep["source_kind"] == "disputed" and ep["episode_kind"] == "performance_and_results"
    d = one(t1["discrepancies"], "natural_key", "S01W05-P")
    assert d["value_a"] == "2004-06-12" and d["value_b"] == "2004-06-13" and d["resolution"] == "prefer_a"
    claire = one(t1["couples"], "couple_key", "S01-claire-sweeney")
    assert claire["exit_week_key"] == "S01W05" and claire["exit_episode_key"] == "S01W05-P" and claire["exit_date_kind"] == "combined_episode"


def test_group_viennese_waltz_a003(t1):
    grp = [p for p in t1["performances"] if p["week_key"] == "S01W05" and p["performance_kind"] == "group_unscored"]
    assert len(grp) == 5 and all(p["dance_key"] == "viennese-waltz" and p["episode_key"] == "S01W05-P" and p["group_key"] == "S01W05-P-G1" for p in grp)
    assert one(t1["performances"], "performance_key", "S01W05-P-natasha-kaplinsky-samba")["stated_total"] == 37
    assert one(t1["couple_weeks"], "couple_week_key", "S01W05-natasha-kaplinsky")["d_week_total"] == 37


def test_scored_showdance_final_a006(t1):
    natasha = [p for p in t1["performances"] if p["couple_key"] == "S01-natasha-kaplinsky" and p["week_key"] == "S01W08"]
    assert [(p["selection_role"], p["stated_total"]) for p in natasha] == [("repeat_favourite_ballroom", 36), ("repeat_favourite_latin", 31), ("showdance", 35)]
    assert [m["mark"] for m in t1["judge_marks"] if m["performance_key"] == "S01W08-P-natasha-kaplinsky-showdance"] == [8, 9, 9, 9]
    assert one(t1["couple_weeks"], "couple_week_key", "S01W08-natasha-kaplinsky")["d_week_total"] == 102
    r = one(t1["results_rounds"], "round_key", "S01R08")
    assert r["round_kind"] == "final_placing" and r["exit_count"] == 0 and r["decided_at_episode_key"] == "S01W08-R"
    assert one(t1["format_rules"], "format_rule_key", "S01-FR")["showdance_scored"] == "yes"


def test_volumes_and_blackpool_a002(t1):
    assert one(t1["episodes"], "episode_key", "S01W03-P")["venue_key"] == "blackpool-tower-ballroom"
    assert len(t1["couples"]) == 8 and len(t1["weeks"]) == 8 and len(t1["couple_weeks"]) == 64
    assert len([p for p in t1["performances"] if p["scoring_mode"] == "judge_marks"]) == 54 and len(t1["judge_marks"]) == 216
    assert one(t1["couples"], "chart_label", "Christopher & Hanna")["professional_display_name"] == "Hanna Karttunen"
