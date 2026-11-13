"""Acceptance tests for series 2, the second series of 2004 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t2():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(2, REPO, REPO / "data/wikipedia/parsoid/series_2.parsoid.html", manifest["Strictly_Come_Dancing_series_2"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t2):
    assert not [c for c in t2["_report"]["checks"] if not c[1]]
    assert not t2["_report"]["unresolved"] and not t2["discrepancies"] and not t2["_report"]["warnings"]


def test_two_series_in_2004(t2):
    s = t2["series"][0]
    assert s["series_number"] == 2 and s["year_start"] == 2004 and s["first_live_date"] == "2004-10-23" and s["final_date"] == "2004-12-11"
    eps = {e["episode_key"]: e for e in t2["episodes"]}
    assert eps["S02W01-P"]["episode_kind"] == "performance_and_results" and "S02W01-R" not in eps
    assert eps["S02W02-R"]["air_date"] == "2004-10-30" and eps["S02W02-P"]["air_date"] == "2004-10-30"  # results on the same Saturday
    assert eps["S02W04-P"]["episode_kind"] == "performance_and_results"


def test_blackpool_samba_week_a016(t2):
    assert one(t2["episodes"], "episode_key", "S02W05-P")["venue_key"] == "blackpool-tower-ballroom"
    w5 = [p for p in t2["performances"] if p["week_key"] == "S02W05"]
    assert len(w5) == 6 and all(p["dance_key"] == "samba" and p["selection_role"] == "prescribed" for p in w5)


def test_final_with_third_place_a018(t2):
    r = one(t2["results_rounds"], "round_key", "S02R08")
    assert r["round_kind"] == "final_placing" and r["exit_count"] == 1 and r["decided_at_episode_key"] == "S02W08-R"
    julian = one(t2["couples"], "couple_key", "S02-julian-clary")
    assert julian["final_placement"] == 3 and julian["exit_kind"] == "finalist" and julian["exit_round_key"] == "S02R08"
    assert one(t2["couple_weeks"], "couple_week_key", "S02W08-julian-clary")["result_status"] == "third"
    jill = [p for p in t2["performances"] if p["couple_key"] == "S02-jill-halfpenny" and p["week_key"] == "S02W08"]
    assert [(p["selection_role"], p["scoring_mode"]) for p in jill] == [("repeat_favourite_ballroom", "judge_marks"), ("repeat_favourite_latin", "judge_marks"), ("showdance", "unscored")]
    assert one(t2["couple_weeks"], "couple_week_key", "S02W08-jill-halfpenny")["d_week_total"] == 74
    assert one(t2["performances"], "performance_key", "S02W08-P-julian-clary-showdance")["scoring_mode"] == "unscored"


def test_no_dance_off_and_volumes(t2):
    assert not t2["dance_off_votes"]
    assert one(t2["couple_weeks"], "couple_week_key", "S02W01-carol-vorderman")["result_status"] == "bottom_two"
    assert one(t2["couples"], "couple_key", "S02-quentin-willson")["exit_week_key"] == "S02W01"
    assert len(t2["couples"]) == 10 and len(t2["weeks"]) == 8 and len(t2["couple_weeks"]) == 80
