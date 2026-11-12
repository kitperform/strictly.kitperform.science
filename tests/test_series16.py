"""Acceptance tests for series 16 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t16():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(16, REPO, REPO / "data/wikipedia/parsoid/series_16.parsoid.html", manifest["Strictly_Come_Dancing_series_16"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t16):
    assert not [c for c in t16["_report"]["checks"] if not c[1]]
    assert not t16["_report"]["unresolved"] and not t16["discrepancies"] and not t16["_report"]["warnings"]


def test_karen_clifton_is_karen_hauer_a053(t16):
    assert one(t16["couple_partnerships"], "couple_key", "S16-charles-venn")["pro_person_key"] == "karen-hauer"
    assert not [p for p in t16["people"] if "clifton" in p["person_key"] and p["person_key"] != "kevin-clifton"]
    alias = one(t16["person_aliases"], "alias", "Karen Clifton")
    assert alias["person_key"] == "karen-hauer" and alias["alias_kind"] == "former_name"
    assert one(t16["couples"], "couple_key", "S16-charles-venn")["professional_display_name"] == "Karen Clifton"


def test_silent_week_one_carry_over_a170(t16):
    r = one(t16["results_rounds"], "round_key", "S16R01-02")
    assert r["week_keys"] == "S16W01|S16W02" and r["votes_carried_over"] == "" and r["combined_reason"] == "opening_weeks_format"
    w1 = [cw for cw in t16["couple_weeks"] if cw["week_key"] == "S16W01"]
    assert all(cw["result_status"] == "carried_forward" and cw["source_kind"] == "inferred" for cw in w1)
    assert one(t16["format_rules"], "format_rule_key", "S16W01-FR")["source_kind"] == "inferred"


def test_lindy_hop_marathon_a171(t16):
    mar = [p for p in t16["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 7 and all(p["dance_key"] == "lindy-hop" and p["group_key"] == "S16W10-P-G1" for p in mar)
    assert one(t16["couple_weeks"], "couple_week_key", "S16W10-faye-tozer")["d_week_total"] == 45
    assert one(t16["couple_weeks"], "couple_week_key", "S16W10-faye-tozer")["d_is_highest_of_week"] == "true"


def test_ribeiro_and_split_votes_a174_a175_a173(t16):
    seats = {s["judge_slug"]: s for s in t16["panel_seats"] if s["episode_key"] == "S16W05-P"}
    assert seats["alfonso-ribeiro"]["replaces_slug"] == "bruno-tonioli" and seats["bruno-tonioli"]["absence_reason"] == "scheduling_conflict"
    assert seats["darcey-bussell"]["seat_position"] == 2
    for k in ("S16R05", "S16R07", "S16R08"):  # 1-3 splits with Ballas voting: not pivotal
        assert one(t16["results_rounds"], "round_key", k)["casting_vote_used"] == "false"
    hyp = one([v for v in t16["dance_off_votes"] if v["results_round_key"] == "S16R03"], "vote_kind", "hypothetical_not_cast")
    assert hyp["couple_key"] == "S16-lee-ryan"  # head judge's hypothetical vote was for the eliminated couple


def test_final_and_couples_choice_a172_a176(t16):
    for ck in ("S16-ashley-roberts", "S16-faye-tozer"):
        ps = [p for p in t16["performances"] if p["couple_key"] == ck and p["week_key"] == "S16W13"]
        assert [p["stated_total"] for p in ps] == [40, 40, 40]
    stacey = one(t16["couple_weeks"], "couple_week_key", "S16W13-stacey-dooley")
    assert stacey["result_status"] == "winner" and stacey["d_week_total"] == 114 and stacey["d_is_lowest_of_week"] == "true"
    assert len([c for c in t16["couples"] if c["final_placement"] == 2]) == 3
    assert {d["dance_key"] for d in t16["dances"]} >= {"contemporary", "theatre-jazz", "street-commercial"}
    assert one(t16["couples"], "chart_label", "Dr. Ranj & Janette")["celebrity_display_name"] == "Dr. Ranj Singh"
    assert len(t16["performances"]) == 149 and len(t16["judge_marks"]) == 568
