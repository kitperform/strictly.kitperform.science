"""Acceptance tests for series 10 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t10():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(10, REPO, REPO / "data/wikipedia/parsoid/series_10.parsoid.html", manifest["Strictly_Come_Dancing_series_10"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t10):
    assert not [c for c in t10["_report"]["checks"] if not c[1]]
    assert not t10["_report"]["unresolved"] and not t10["discrepancies"] and not t10["_report"]["warnings"]


def test_dance_fusion_week_a101(t10):
    w10 = [p for p in t10["performances"] if p["week_key"] == "S10W10"]
    assert len(w10) == 6 and all(p["performance_kind"] == "fusion" and p["dance_secondary_key"] for p in w10)
    denise = one(t10["performances"], "performance_key", "S10W10-P-denise-van-outen-jive")
    assert denise["dance_key"] == "jive" and denise["dance_secondary_key"] == "quickstep" and denise["dance_raw"] == "Jive & Quickstep" and denise["stated_total"] == 35
    lisa = one(t10["performances"], "performance_key", "S10W10-P-lisa-riley-cha-cha-cha")
    assert lisa["dance_secondary_key"] == "tango"
    assert one(t10["weeks"], "week_key", "S10W10")["dance_brief_raw"] == "One fusion dance"


def test_pre_week_one_replacement_a105(t10):
    ps = sorted((p for p in t10["couple_partnerships"] if p["couple_key"] == "S10-johnny-ball"), key=lambda p: p["week_from"])
    assert [(p["pro_person_key"], p["week_from"], p["week_to"], p["partnership_kind"], p["reason"]) for p in ps] == [
        ("aliona-vilani", 0, 0, "pre_series_only", "injury"), ("iveta-lukosiute", 1, 2, "replacement_pre_week1", "injury")]
    roster = one(t10["series_people"], "series_person_key", "S10-aliona-vilani-professional")
    assert roster["roster_status"] == "paired_withdrew_pre_week1" and roster["paired_with_person_key"] == "johnny-ball" and roster["replaced_by_person_key"] == "iveta-lukosiute"
    assert one(t10["performances"], "performance_key", "S10W01-N1-johnny-ball-waltz")["performing_pro_slug"] == "iveta-lukosiute" if any(p["performance_key"] == "S10W01-N1-johnny-ball-waltz" for p in t10["performances"]) else True
    assert all(p["performing_pro_slug"] == "iveta-lukosiute" for p in t10["performances"] if p["couple_key"] == "S10-johnny-ball")


def test_final_in_nested_subsections_a100(t10):
    eps = {e["episode_key"]: e for e in t10["episodes"]}
    assert eps["S10W12-S1"]["sub_label"] == "show1" and eps["S10W12-S2"]["episode_kind"] == "performance_and_results"
    a = one(t10["results_rounds"], "round_key", "S10R12a")
    assert a["elimination_mechanism_actual"] == "lowest_combined_points_stated" and a["exit_count"] == 1
    dani = one(t10["couples"], "couple_key", "S10-dani-harmer")
    assert dani["final_placement"] == 4 and dani["exit_round_key"] == "S10R12a"
    assert one(t10["couple_weeks"], "couple_week_key", "S10W12-dani-harmer")["result_status"] == "fourth"
    louis = [p for p in t10["performances"] if p["couple_key"] == "S10-louis-smith" and p["week_key"] == "S10W12"]
    assert [p["selection_role"] for p in louis] == ["repeat_judges_choice", "showdance", "repeat_favourite"]
    kim = [p for p in t10["performances"] if p["couple_key"] == "S10-kimberley-walsh" and p["episode_key"] == "S10W12-S1"]
    assert [p["stated_total"] for p in kim] == [39, 39]  # merged score cell
    assert len([c for c in t10["couples"] if c["final_placement"] == 2]) == 2


def test_wembley_and_votes_a101_a102(t10):
    assert one(t10["episodes"], "episode_key", "S10W07-P")["venue_key"] == "wembley-arena"
    assert one(t10["themes"], "theme_key", "wembley")["is_location_theme"] == "true"
    hyp = one([v for v in t10["dance_off_votes"] if v["results_round_key"] == "S10R04"], "vote_kind", "hypothetical_not_cast")
    assert hyp["judge_slug"] == "len-goodman" and hyp["couple_key"] == "S10-sid-owen"
    assert one(t10["results_rounds"], "round_key", "S10R03")["casting_vote_used"] == "false"  # 3-1 with Len voting


def test_volumes(t10):
    assert len(t10["couples"]) == 14 and len(t10["weeks"]) == 12 and len(t10["couple_weeks"]) == 14 * 12
    assert len([p for p in t10["performances"] if p["episode_key"] == "S10W01-N1"]) == 6
    assert len([p for p in t10["performances"] if p["episode_key"] == "S10W01-N2"]) == 8
    assert len(t10["performances"]) == 125 and len(t10["judge_marks"]) == 500
