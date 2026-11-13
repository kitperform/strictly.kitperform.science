"""Acceptance tests for series 6 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t6():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(6, REPO, REPO / "data/wikipedia/parsoid/series_6.parsoid.html", manifest["Strictly_Come_Dancing_series_6"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t6):
    assert not [c for c in t6["_report"]["checks"] if not c[1]]
    assert not t6["_report"]["unresolved"] and not t6["_report"]["warnings"]


def test_disputed_showdance_scores_a048(t6):
    for ck, total in (("S06-tom-chambers", 37), ("S06-rachel-stevens", 39), ("S06-lisa-snowdon", 39)):
        p = one(t6["performances"], "performance_key", f"S06W14-P-{ck[4:]}-showdance")
        assert p["scoring_mode"] == "judge_total_only" and p["stated_total"] == total and p["source_kind"] == "disputed" and p["n_marks_stated"] == ""
        assert not [m for m in t6["judge_marks"] if m["performance_key"] == p["performance_key"]]
        d = one(t6["discrepancies"], "natural_key", p["performance_key"])
        assert d["value_a"] == total and d["value_b"] == "" and d["resolution"] == "prefer_a"
    assert one(t6["couple_weeks"], "couple_week_key", "S06W14-tom-chambers")["d_week_total"] == 110
    assert one(t6["couple_weeks"], "couple_week_key", "S06W14-lisa-snowdon")["d_is_highest_of_week"] == "true"
    assert one(t6["format_rules"], "format_rule_key", "S06-FR")["showdance_scored"] == "disputed"


def test_scoring_error_semi_final_and_rollover_a046(t6):
    r13 = one(t6["results_rounds"], "round_key", "S06R13")
    assert r13["round_kind"] == "no_decision" and r13["elimination_mechanism_actual"] == "none" and r13["dance_off_status"] == "cancelled_scoring_error" and r13["exit_count"] == 0
    assert all(cw["result_status"] == "no_elimination" and cw["results_round_key"] == "S06R13" for cw in t6["couple_weeks"] if cw["week_key"] == "S06W13" and cw["participation_status"] == "competed")
    final = one(t6["results_rounds"], "round_key", "S06R13-14")
    assert final["round_kind"] == "final_placing" and final["label"] == "13+14" and final["week_keys"] == "S06W13|S06W14"
    assert final["combined_reason"] == "vote_rollover_final" and final["votes_carried_over"] == "true"
    assert final["exit_count"] == 1  # a single-show final that placed a third couple
    assert one(t6["couples"], "couple_key", "S06-lisa-snowdon")["exit_round_key"] == "S06R13-14"


def test_mislabelled_result_cell_a049(t6):
    cw = one(t6["couple_weeks"], "couple_week_key", "S06W14-lisa-snowdon")
    assert cw["result_status"] == "third" and cw["source_kind"] == "disputed"
    d = one(t6["discrepancies"], "natural_key", "S06W14-lisa-snowdon")
    assert d["value_a"] == "third" and d["value_b"] == "runner_up"
    assert one(t6["couples"], "couple_key", "S06-lisa-snowdon")["final_placement"] == 3
    lisa = [p for p in t6["performances"] if p["couple_key"] == "S06-lisa-snowdon" and p["week_key"] == "S06W14"]
    assert [p["selection_role"] for p in lisa] == ["repeat_favourite_ballroom", "repeat_favourite_latin", "showdance"]


def test_john_sergeant_a045(t6):
    cw = one(t6["couple_weeks"], "couple_week_key", "S06W10-john-sergeant")
    assert cw["participation_status"] == "competed_unscored" and cw["result_status"] == "withdrew" and cw["results_round_key"] == "S06R10" and cw["at_risk"] == "false"
    p = one(t6["performances"], "performance_key", "S06W10-P-john-sergeant-waltz")
    assert p["scoring_mode"] == "unscored" and p["performance_status"] == "performed" and p["score_cell_raw"] == "No scores received"
    c = one(t6["couples"], "couple_key", "S06-john-sergeant")
    assert c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S06W10" and c["exit_timing"] == "before_live_show" and c["final_placement"] == 7
    assert one(t6["results_rounds"], "round_key", "S06R10")["exit_count"] == 1


def test_split_opening_weeks_a043(t6):
    fr = {r["format_rule_key"]: r for r in t6["format_rules"]}
    assert [fr[f"S06W0{n}-FR"]["field_subset"] for n in (1, 2, 3, 4)] == ["male_celebrities", "female_celebrities", "half_a", "half_b"]
    rachel1 = one(t6["couple_weeks"], "couple_week_key", "S06W01-rachel-stevens")
    assert rachel1["participation_status"] == "group_only" and rachel1["result_status"] == "exempt" and rachel1["results_round_key"] == ""
    assert one(t6["couple_weeks"], "couple_week_key", "S06W02-tom-chambers")["participation_status"] == "group_only"  # bare dash cell
    assert one(t6["results_rounds"], "round_key", "S06R01")["casting_vote_used"] == "true"  # first 2-2 (A044)
    hyp = one([v for v in t6["dance_off_votes"] if v["results_round_key"] == "S06R04"], "vote_kind", "hypothetical_not_cast")
    assert hyp["couple_key"] == "S06-jessie-wallace"  # Len's hypothetical for the eliminated couple (A050)


def test_people_and_volumes_a032_a053(t6):
    assert one(t6["couples"], "chart_label", "Christine & Matthew")["couple_key"] == "S06-christine-lampard"
    assert one(t6["person_aliases"], "alias", "Christine Bleakley")["person_key"] == "christine-lampard"
    assert one(t6["couples"], "chart_label", "Tom & Camilla")["professional_display_name"] == "Camilla Sacre-Dallerup"
    seats = sorted((s for s in t6["panel_seats"] if s["episode_key"] == "S06W01-P"), key=lambda s: s["seat_position"])
    assert [s["judge_slug"] for s in seats] == ["craig-revel-horwood", "arlene-phillips", "len-goodman", "bruno-tonioli"]
    assert len(t6["couples"]) == 16 and len(t6["weeks"]) == 14 and len(t6["performances"]) == 120 and len(t6["judge_marks"]) == 464
