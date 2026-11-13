"""Acceptance tests for series 7 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t7():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(7, REPO, REPO / "data/wikipedia/parsoid/series_7.parsoid.html", manifest["Strictly_Come_Dancing_series_7"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t7):
    assert not [c for c in t7["_report"]["checks"] if not c[1]]
    assert not t7["_report"]["unresolved"] and not t7["discrepancies"] and not t7["_report"]["warnings"]


def test_half_field_opening_weeks_a055_a056(t7):
    eps = {e["episode_key"]: e for e in t7["episodes"]}
    assert eps["S07W01-N1"]["episode_kind"] == "performance" and eps["S07W01-N2"]["episode_kind"] == "performance_and_results" and "S07W01-R" not in eps
    r1 = one(t7["results_rounds"], "round_key", "S07R01")
    assert r1["decided_at_episode_key"] == "S07W01-N2" and r1["exit_count"] == 1 and r1["dance_off_status"] == "held"
    assert one(t7["couples"], "couple_key", "S07-martina-hingis")["exit_week_key"] == "S07W01"
    ricky = one(t7["couple_weeks"], "couple_week_key", "S07W01-ricky-whittle")
    assert ricky["participation_status"] == "group_only" and ricky["result_status"] == "exempt" and ricky["results_round_key"] == ""
    assert not [p for p in t7["performances"] if p["couple_key"] == "S07-ricky-whittle" and p["week_key"] == "S07W01"]
    assert len([p for p in t7["performances"] if p["couple_key"] == "S07-rav-wilding" and p["week_key"] == "S07W01"]) == 2
    assert one(t7["format_rules"], "format_rule_key", "S07W01-FR")["field_subset"] == "half_a"
    assert one(t7["format_rules"], "format_rule_key", "S07W02-FR")["field_subset"] == "half_b"
    assert one(t7["results_rounds"], "round_key", "S07R01")["casting_vote_used"] == "true"  # 2-2 decided by Len, stated


def test_results_inside_the_saturday_show_a069(t7):
    eps = {e["episode_key"]: e for e in t7["episodes"]}
    assert eps["S07W05-P"]["episode_kind"] == "performance_and_results" and eps["S07W05-P"]["source_kind"] == "inferred" and "S07W05-R" not in eps
    assert one(t7["couples"], "couple_key", "S07-joe-calzaghe")["exit_date_kind"] == "combined_episode"
    assert eps["S07W13-R"]["episode_kind"] == "results"


def test_group_viennese_waltz_for_points_a058(t7):
    grp = [p for p in t7["performances"] if p["week_key"] == "S07W11" and p["performance_kind"] == "group_points"]
    assert len(grp) == 5 and all(p["dance_key"] == "viennese-waltz" and p["scoring_mode"] == "awarded_points" and p["group_key"] == "S07W11-P-G1" and p["running_order"] == "" for p in grp)
    assert sorted(p["points_value"] for p in grp) == [7, 7, 8, 9, 10]
    assert one(t7["couple_weeks"], "couple_week_key", "S07W11-ali-bastian")["d_week_total"] == 47
    assert not [d for d in t7["dances"] if d["dance_key"].startswith("group")]


def test_five_judges_and_no_dance_off_semi_a061_a062_a059(t7):
    seats = sorted((s for s in t7["panel_seats"] if s["episode_key"] == "S07W12-P"), key=lambda s: s["seat_position"])
    assert [(s["judge_slug"], s["panel_role"]) for s in seats] == [("craig-revel-horwood", "regular"), ("darcey-bussell", "guest_additional"), ("len-goodman", "head"), ("alesha-dixon", "regular"), ("bruno-tonioli", "regular")]
    assert one(t7["performances"], "performance_key", "S07W13-P-ali-bastian-american-smooth")["stated_total"] == 50
    assert one(t7["performances"], "performance_key", "S07W13-P-ali-bastian-american-smooth")["d_scale_max"] == 50
    assert one(t7["performances"], "performance_key", "S07W11-P-ali-bastian-charleston")["d_scale_max"] == 40
    r13 = one(t7["results_rounds"], "round_key", "S07R13")
    assert r13["elimination_mechanism_actual"] == "ranking_points_no_dance_off" and r13["dance_off_status"] == "not_held_by_format" and r13["exit_count"] == 1
    assert one(t7["couple_weeks"], "couple_week_key", "S07W13-ali-bastian")["danced_off"] == "false"
    votes = [v for v in t7["dance_off_votes"] if v["results_round_key"] == "S07R12"]
    assert len(votes) == 5 and sorted(v["judge_slug"] for v in votes if v["vote_kind"] == "hypothetical_not_cast") == ["bruno-tonioli", "len-goodman"]
    assert one(votes, "judge_slug", "darcey-bussell")["vote_kind"] == "cast"


def test_final_with_scored_group_lindy_hop_a063(t7):
    chris = [p for p in t7["performances"] if p["couple_key"] == "S07-chris-hollins" and p["week_key"] == "S07W14"]
    assert [(p["episode_key"][-2:], p["performance_kind"], p["selection_role"], p["stated_total"]) for p in chris] == [
        ("S1", "individual", "repeat_highest_ballroom", 46), ("S1", "group_scored", "group", 44), ("S2", "individual", "repeat_highest_latin", 50), ("S2", "showdance", "showdance", 46)]
    assert one(t7["couple_weeks"], "couple_week_key", "S07W14-chris-hollins")["d_week_total"] == 186
    assert one(t7["couple_weeks"], "couple_week_key", "S07W14-ricky-whittle")["d_is_highest_of_week"] == "true"
    assert one(t7["results_rounds"], "round_key", "S07R14")["round_kind"] == "final_placing"


def test_jade_and_laila_a066_a057(t7):
    assert one(t7["couple_weeks"], "couple_week_key", "S07W09-jade-johnson")["participation_status"] == "bye"
    jade = one(t7["couples"], "couple_key", "S07-jade-johnson")
    assert jade["exit_kind"] == "withdrew" and jade["exit_week_key"] == "S07W10" and jade["exit_reason"] == "injury" and jade["final_placement"] == 7
    assert one(t7["results_rounds"], "round_key", "S07R10")["exit_count"] == 1
    laila = one(t7["performances"], "performance_key", "S07W09-P-laila-rouass-rumba")
    assert laila["performance_status"] == "performed_partial" and laila["stated_total"] == 22


def test_labels_and_volumes_a070(t7):
    assert one(t7["couples"], "chart_label", "Ricky W. & Natalie")["couple_key"] == "S07-ricky-whittle"
    assert one(t7["couples"], "chart_label", "Ricky G. & Erin")["couple_key"] == "S07-ricky-groves"
    assert one(t7["couples"], "chart_label", "Natalie & Vincent")["couple_key"] == "S07-natalie-cassidy"
    assert one(t7["couples"], "chart_label", "Zöe & James")["celebrity_display_name"] == "Zöe Lucker"
    assert len(t7["couples"]) == 16 and len(t7["weeks"]) == 14 and len(t7["couple_weeks"]) == 16 * 14
    assert len(t7["performances"]) == 146 and len(t7["judge_marks"]) == 586
