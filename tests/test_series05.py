"""Acceptance tests for series 5, the first dance-off series (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t5():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(5, REPO, REPO / "data/wikipedia/parsoid/series_5.parsoid.html", manifest["Strictly_Come_Dancing_series_5"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t5):
    assert not [c for c in t5["_report"]["checks"] if not c[1]]
    assert not t5["_report"]["unresolved"] and not t5["_report"]["warnings"]
    assert {d["discrepancy_key"] for d in t5["discrepancies"]} == {"CoupleWeek|S05W01-kate-garraway|participation_status|1"}
    assert one(t5["couple_weeks"], "couple_week_key", "S05W01-kate-garraway")["participation_status"] == "not_scheduled"


def test_preview_and_sunday_results_a038_a039(t5):
    eps = {e["episode_key"]: e for e in t5["episodes"]}
    assert eps["S05-PV"]["episode_kind"] == "preview" and eps["S05-PV"]["air_date"] == "2007-09-29" and "S05-L" not in eps
    assert eps["S05W01-P"]["air_date"] == "2007-10-06" and eps["S05W01-R"]["air_date"] == "2007-10-07" and eps["S05W01-R"]["episode_kind"] == "results"
    assert one(t5["couples"], "couple_key", "S05-brian-capron")["exit_episode_key"] == "S05W01-R"


def test_first_dance_offs_a040(t5):
    r1 = one(t5["results_rounds"], "round_key", "S05R01")
    assert r1["dance_off_status"] == "held" and r1["casting_vote_slug"] == "len-goodman" and r1["casting_vote_used"] == "false"  # 3-1 with Len voting
    votes = [v for v in t5["dance_off_votes"] if v["results_round_key"] == "S05R01"]
    assert len(votes) == 4 and one(votes, "judge_slug", "craig-revel-horwood")["couple_key"] == "S05-brian-capron"
    assert one([v for v in t5["dance_off_votes"] if v["results_round_key"] == "S05R03"], "judge_slug", "len-goodman")["vote_kind"] == "hypothetical_not_cast"
    assert one(t5["format_rules"], "format_rule_key", "S05-FR")["dance_off_used"] == "true"


def test_men_then_women_a033(t5):
    fr = {r["format_rule_key"]: r for r in t5["format_rules"]}
    assert fr["S05W01-FR"]["field_subset"] == "male_celebrities" and fr["S05W02-FR"]["field_subset"] == "female_celebrities"
    assert one(t5["couple_weeks"], "couple_week_key", "S05W01-alesha-dixon")["participation_status"] == "group_only"
    assert one(t5["couple_weeks"], "couple_week_key", "S05W02-kenny-logan")["participation_status"] == "group_only"
    assert one(t5["results_rounds"], "round_key", "S05R01")["exit_count"] == 1 and one(t5["results_rounds"], "round_key", "S05R02")["exit_count"] == 1


def test_kelly_brook_a037(t5):
    c = one(t5["couples"], "couple_key", "S05-kelly-brook")
    assert c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S05W09" and c["exit_reason"] == "bereavement" and c["exit_timing"] == "before_live_show" and c["final_placement"] == 6
    assert one(t5["couple_weeks"], "couple_week_key", "S05W08-kelly-brook")["result_status"] == "bottom_two"
    assert one(t5["couple_weeks"], "couple_week_key", "S05W09-kelly-brook")["result_status"] == "withdrew"
    assert one(t5["results_rounds"], "round_key", "S05R09")["exit_count"] == 1


def test_final_four_routines_a036(t5):
    alesha = [p for p in t5["performances"] if p["couple_key"] == "S05-alesha-dixon" and p["week_key"] == "S05W12"]
    assert [p["selection_role"] for p in alesha] == ["repeat_favourite_ballroom", "repeat_favourite_latin", "same_song", "showdance"]
    assert alesha[3]["scoring_mode"] == "unscored" and alesha[3]["stated_total"] == ""
    assert one(t5["couple_weeks"], "couple_week_key", "S05W12-alesha-dixon")["d_week_total"] == 112
    assert one(t5["couples"], "couple_key", "S05-alesha-dixon")["final_placement"] == 1
    assert one(t5["format_rules"], "format_rule_key", "S05-FR")["showdance_scored"] == "no"


def test_merged_cell_and_logans_a035_a041(t5):
    alesha11 = [p for p in t5["performances"] if p["couple_key"] == "S05-alesha-dixon" and p["week_key"] == "S05W11"]
    assert [p["stated_total"] for p in alesha11] == [38, 38]
    assert one(t5["couples"], "chart_label", "Gabby & James")["couple_key"] == "S05-gabby-logan"
    assert one(t5["couples"], "chart_label", "Kenny & Ola")["couple_key"] == "S05-kenny-logan"
    assert len(t5["couples"]) == 14 and len(t5["weeks"]) == 12 and len(t5["couple_weeks"]) == 14 * 12
