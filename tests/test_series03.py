"""Acceptance tests for series 3 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t3():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(3, REPO, REPO / "data/wikipedia/parsoid/series_3.parsoid.html", manifest["Strictly_Come_Dancing_series_3"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t3):
    assert not [c for c in t3["_report"]["checks"] if not c[1]]
    assert not t3["_report"]["unresolved"] and not t3["discrepancies"] and not t3["_report"]["warnings"]


def test_names_a025(t3):
    assert one(t3["couples"], "chart_label", "Darren & Lilia")["couple_key"] == "S03-darren-gough"
    assert one(t3["couples"], "chart_label", "Gloria & Darren")["professional_display_name"] == "Darren Bennett"
    andrew = one(t3["people"], "person_key", "unlinked-andrew-cuerden")
    assert andrew["identity_basis"] == "unlinked_name" and andrew["wiki_title"] == ""
    assert one(t3["couple_partnerships"], "couple_key", "S03-jaye-jacobs")["pro_person_key"] == "unlinked-andrew-cuerden"
    assert one(t3["couples"], "chart_label", "Will & Hanna")["professional_display_name"] == "Hanna Haarala"


def test_tie_and_format_a021(t3):
    w1 = {p["couple_key"]: p for p in t3["performances"] if p["week_key"] == "S03W01"}
    assert w1["S03-darren-gough"]["stated_total"] == 19 and w1["S03-patsy-palmer"]["stated_total"] == 19
    assert [m["mark"] for m in t3["judge_marks"] if m["performance_key"] == w1["S03-patsy-palmer"]["performance_key"]] == [3, 4, 6, 6]
    assert not t3["dance_off_votes"]
    assert all(r["dance_off_status"] == "not_in_format" for r in t3["results_rounds"] if r["round_kind"] == "standard")
    eps = {e["episode_key"]: e for e in t3["episodes"]}
    assert eps["S03W01-P"]["episode_kind"] == "performance_and_results" and "S03W01-R" not in eps  # results inside the show
    assert eps["S03W05-P"]["episode_kind"] == "performance_and_results"
    assert eps["S03W02-R"]["episode_kind"] == "results"


def test_quarter_final_and_final_a023_a022(t3):
    q = [p for p in t3["performances"] if p["couple_key"] == "S03-colin-jackson" and p["week_key"] == "S03W08"]
    assert len(q) == 2 and "american-smooth" in {p["dance_key"] for p in q}
    assert one(t3["couple_weeks"], "couple_week_key", "S03W08-colin-jackson")["d_week_total"] == 73
    final = [p for p in t3["performances"] if p["couple_key"] == "S03-darren-gough" and p["week_key"] == "S03W10"]
    assert [p["selection_role"] for p in final] == ["repeat_favourite_ballroom", "repeat_favourite_latin", "showdance"]
    assert final[2]["scoring_mode"] == "unscored"
    assert one(t3["couple_weeks"], "couple_week_key", "S03W10-darren-gough")["d_week_total"] == 72  # the live chart cell is empty (A022); the weekly table still has the scores
    r = one(t3["results_rounds"], "round_key", "S03R10")
    assert r["round_kind"] == "final_placing" and r["exit_count"] == 1  # Zoe & Ian third
    zoe = one(t3["couples"], "couple_key", "S03-zoe-ball")
    assert zoe["final_placement"] == 3 and zoe["exit_round_key"] == "S03R10"
    assert one(t3["couple_weeks"], "couple_week_key", "S03W10-zoe-ball")["result_status"] == "third"
    assert len(t3["couples"]) == 12 and len(t3["weeks"]) == 10 and len(t3["couple_weeks"]) == 120
