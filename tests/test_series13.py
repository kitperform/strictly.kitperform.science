"""Acceptance tests for series 13 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t13():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(13, REPO, REPO / "data/wikipedia/parsoid/series_13.parsoid.html", manifest["Strictly_Come_Dancing_series_13"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t13):
    assert not [c for c in t13["_report"]["checks"] if not c[1]]
    assert not t13["_report"]["unresolved"] and not t13["discrepancies"] and not t13["_report"]["warnings"]


def test_two_show_final_a132_a133(t13):
    eps = {e["episode_key"]: e for e in t13["episodes"]}
    assert eps["S13W13-S1"]["sub_label"] == "show1" and eps["S13W13-S1"]["episode_kind"] == "performance"
    assert eps["S13W13-S2"]["sub_label"] == "show2" and eps["S13W13-S2"]["episode_kind"] == "performance_and_results"
    assert "S13W13-P" not in eps and "S13W13-R" not in eps and eps["S13W13-S2"]["air_date"] == "2015-12-19"
    a = one(t13["results_rounds"], "round_key", "S13R13a")
    assert a["round_kind"] == "intermediate_final_exit" and a["elimination_mechanism_actual"] == "lowest_public_vote" and a["exit_count"] == 1 and a["decided_at_episode_key"] == "S13W13-S2"
    b = one(t13["results_rounds"], "round_key", "S13R13b")
    assert b["round_kind"] == "final_placing" and b["exit_count"] == 0 and b["label"] == "Show 2"
    katie = one(t13["couple_weeks"], "couple_week_key", "S13W13-katie-derham")
    assert katie["result_status"] == "fourth" and katie["results_round_key"] == "S13R13a" and katie["at_risk"] == "false"
    assert one(t13["couple_weeks"], "couple_week_key", "S13W13-jay-mcguiness")["results_round_key"] == "S13R13b"
    c = one(t13["couples"], "couple_key", "S13-katie-derham")
    assert c["exit_kind"] == "finalist" and c["final_placement"] == 4 and c["exit_round_key"] == "S13R13a" and c["exit_episode_key"] == "S13W13-S2" and c["exit_date_kind"] == "combined_episode"
    georgia = [p for p in t13["performances"] if p["couple_key"] == "S13-georgia-may-foote" and p["week_key"] == "S13W13"]
    assert [(p["episode_key"][-2:], p["stated_total"], p["selection_role"]) for p in georgia] == [
        ("S1", 36, "repeat_judges_choice"), ("S1", 36, "showdance"), ("S2", 40, "repeat_favourite")]
    assert not [p for p in t13["performances"] if p["couple_key"] == "S13-katie-derham" and p["episode_key"] == "S13W13-S2"]
    assert one(t13["format_rules"], "format_rule_key", "S13W13-S1-FR")["episode_key"] == "S13W13-S1"
    assert len([c for c in t13["couples"] if c["final_placement"] == 2]) == 2


def test_two_night_week_one_and_combined_round_a129_a134(t13):
    assert len([p for p in t13["performances"] if p["episode_key"] == "S13W01-N1"]) == 6
    assert len([p for p in t13["performances"] if p["episode_key"] == "S13W01-N2"]) == 9
    r = one(t13["results_rounds"], "round_key", "S13R01-02")
    assert r["votes_carried_over"] == "true" and r["exit_count"] == 1
    assert one(t13["couples"], "couple_key", "S13-iwan-thomas")["exit_round_key"] == "S13R01-02"


def test_marathon_and_votes_a130_a135(t13):
    mar = [p for p in t13["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 7 and all(p["dance_key"] == "quickstep" for p in mar)
    assert one(t13["couple_weeks"], "couple_week_key", "S13W10-helen-george")["d_week_total"] == 46
    hyp = one([v for v in t13["dance_off_votes"] if v["results_round_key"] == "S13R09"], "vote_kind", "hypothetical_not_cast")
    assert hyp["judge_slug"] == "len-goodman" and hyp["couple_key"] == "S13-jamelia"
    assert one(t13["results_rounds"], "round_key", "S13R12")["casting_vote_used"] == "false"  # 1-3 with Len voting


def test_volumes(t13):
    assert len(t13["performances"]) == 148 and len(t13["judge_marks"]) == 564 and len(t13["panel_seats"]) == 60
    assert one(t13["couples"], "chart_label", "Jamelia & Tristan")["celebrity_display_name"] == "Jamelia"
