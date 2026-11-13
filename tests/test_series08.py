"""Acceptance tests for series 8 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t8():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(8, REPO, REPO / "data/wikipedia/parsoid/series_8.parsoid.html", manifest["Strictly_Come_Dancing_series_8"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t8):
    assert not [c for c in t8["_report"]["checks"] if not c[1]]
    assert not t8["_report"]["unresolved"] and not t8["_report"]["warnings"]


def test_two_night_semi_final_with_marathon_a076(t8):
    eps = {e["episode_key"]: e for e in t8["episodes"]}
    assert eps["S08W11-N1"]["air_date"] == "2010-12-10" and eps["S08W11-N2"]["air_date"] == "2010-12-11" and eps["S08W11-R"]["episode_kind"] == "results"
    n1 = [p for p in t8["performances"] if p["episode_key"] == "S08W11-N1"]
    assert len(n1) == 10 and len([p for p in n1 if p["performance_kind"] == "marathon"]) == 5
    assert len([p for p in t8["performances"] if p["episode_key"] == "S08W11-N2"]) == 5
    r = one(t8["results_rounds"], "round_key", "S08R11")
    assert r["exit_count"] == 2 and r["at_risk_group_size_actual"] == "" and r["decided_at_episode_key"] == "S08W11-R"
    assert one(t8["couple_weeks"], "couple_week_key", "S08W11-kara-tointon")["d_week_total"] == 83  # 39 + 5 + 39
    for ck in ("S08-gavin-henson", "S08-scott-maslen"):
        c = one(t8["couples"], "couple_key", ck)
        assert c["exit_ordinal"] == 10 and c["exit_ordinal_is_shared"] == "true" and c["exit_round_key"] == "S08R11"
        assert one(t8["couple_weeks"], "couple_week_key", f"S08W11-{ck[4:]}")["at_risk"] == "false"


def test_disputed_final_mechanism_a077(t8):
    a = one(t8["results_rounds"], "round_key", "S08R12a")
    assert a["elimination_mechanism_actual"] == "lowest_combined_points_stated" and a["source_kind"] == "disputed" and a["exit_count"] == 1
    d = one(t8["discrepancies"], "natural_key", "S08R12a")
    assert d["value_a"] == "lowest_combined_points_stated" and d["value_b"] == "lowest_public_vote" and d["resolution"] == "both_kept_unresolved"
    pamela = one(t8["couples"], "couple_key", "S08-pamela-stephenson")
    assert pamela["final_placement"] == 3 and pamela["exit_round_key"] == "S08R12a"
    assert one(t8["couple_weeks"], "couple_week_key", "S08W12-pamela-stephenson")["result_status"] == "third"
    kara = [p for p in t8["performances"] if p["couple_key"] == "S08-kara-tointon" and p["week_key"] == "S08W12"]
    assert [p["selection_role"] for p in kara] == ["repeat_highest", "showdance", "unlearned", "repeat_favourite"]
    assert one(t8["couple_weeks"], "couple_week_key", "S08W12-kara-tointon")["d_week_total"] == 150


def test_no_dance_off_and_bye_a082_a079(t8):
    assert not t8["dance_off_votes"]
    assert all(r["dance_off_status"] == "not_in_format" for r in t8["results_rounds"] if r["round_kind"] == "standard")
    cw = one(t8["couple_weeks"], "couple_week_key", "S08W03-tina-o-brien")
    assert cw["participation_status"] == "bye" and cw["absence_reason"] == "illness"
    assert one(t8["couple_weeks"], "couple_week_key", "S08W02-peter-shilton")["result_status"] == "bottom_two"


def test_ian_waite_stands_in_a080(t8):
    ps = sorted((p for p in t8["couple_partnerships"] if p["couple_key"] == "S08-michelle-williams"), key=lambda p: p["week_from"])
    assert [(p["pro_person_key"], p["week_from"], p["week_to"], p["partnership_kind"]) for p in ps] == [
        ("brendan-cole", 1, 3, "original"), ("ian-waite", 4, 4, "substitute_temporary"), ("brendan-cole", 5, 7, "original")]
    assert ps[1]["reason"] == "bereavement"
    assert one(t8["performances"], "performance_key", "S08W04-P-michelle-williams-tango")["performing_pro_slug"] == "ian-waite"


def test_names_and_volumes_a078(t8):
    assert one(t8["couples"], "chart_label", "Goldie & Kristina")["celebrity_display_name"] == "Goldie"
    top2 = sorted(cw["couple_key"] for cw in t8["couple_weeks"] if cw["week_key"] == "S08W02" and cw["d_is_highest_of_week"] == "true")
    assert top2 == ["S08-kara-tointon", "S08-pamela-stephenson", "S08-scott-maslen"]
    assert len(t8["performances"]) == 128 and len(t8["judge_marks"]) == 492 and len(t8["couple_weeks"]) == 14 * 12
