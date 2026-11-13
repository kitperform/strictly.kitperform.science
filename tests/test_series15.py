"""Acceptance tests for series 15 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t15():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(15, REPO, REPO / "data/wikipedia/parsoid/series_15.parsoid.html", manifest["Strictly_Come_Dancing_series_15"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t15):
    assert not [c for c in t15["_report"]["checks"] if not c[1]]
    assert not t15["_report"]["unresolved"] and not t15["discrepancies"] and not t15["_report"]["warnings"]


def test_three_judge_week_inside_a_four_judge_series_a166(t15):
    seats = [s for s in t15["panel_seats"] if s["episode_key"] == "S15W05-P"]
    assert len(seats) == 4 and one(seats, "judge_slug", "bruno-tonioli")["panel_role"] == "absent"
    assert not [s for s in seats if s["panel_role"] == "guest_replacement"]
    p = one(t15["performances"], "performance_key", "S15W05-P-davood-ghadami-jive")
    assert p["n_marks_stated"] == 3 and p["d_scale_max"] == 30 and p["stated_total"] == 22
    assert [m["judge_slug"] for m in t15["judge_marks"] if m["performance_key"] == p["performance_key"]] == ["craig-revel-horwood", "darcey-bussell", "shirley-ballas"]
    assert one(t15["performances"], "performance_key", "S15W10-P-joe-mcfadden-quickstep")["d_scale_max"] == 40
    r = one(t15["results_rounds"], "round_key", "S15R05")
    assert r["d_n_scoring_seats"] == 3 and len([v for v in t15["dance_off_votes"] if v["results_round_key"] == "S15R05"]) == 3


def test_casting_votes_a165_a167(t15):
    assert one(t15["results_rounds"], "round_key", "S15R01-02")["casting_vote_used"] == "false"  # week 2 decides the 1+2 round; 1-2 then Ballas: 3-1, not pivotal
    r7 = one(t15["results_rounds"], "round_key", "S15R07")
    assert r7["casting_vote_used"] == "true" and r7["casting_vote_inferred"] == "false"
    assert one([v for v in t15["dance_off_votes"] if v["results_round_key"] == "S15R07"], "judge_slug", "shirley-ballas")["is_casting_vote_stated"] == "true"


def test_paso_marathon_and_merged_semi_a161_a163(t15):
    mar = [p for p in t15["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 7 and all(p["dance_key"] == "paso-doble" for p in mar)
    assert one(t15["couple_weeks"], "couple_week_key", "S15W10-joe-mcfadden")["d_week_total"] == 44
    joe12 = [p for p in t15["performances"] if p["couple_key"] == "S15-joe-mcfadden" and p["week_key"] == "S15W12"]
    assert [p["stated_total"] for p in joe12] == [35, 35]


def test_final_roles_follow_table_order_a164(t15):
    joe = [p for p in t15["performances"] if p["couple_key"] == "S15-joe-mcfadden" and p["week_key"] == "S15W13"]
    assert [p["selection_role"] for p in joe] == ["repeat_judges_choice", "showdance", "repeat_favourite"]
    assert len([c for c in t15["couples"] if c["final_placement"] == 2]) == 3
    assert one(t15["couple_weeks"], "couple_week_key", "S15W13-gemma-atkinson")["d_is_lowest_of_week"] == "true"


def test_labels_and_aliases(t15):
    assert one(t15["couples"], "chart_label", "Rev. Richard & Dianne")["celebrity_display_name"] == "Rev. Richard Coles"
    assert one(t15["couple_partnerships"], "couple_key", "S15-simon-rimmer")["pro_person_key"] == "karen-hauer"
    assert one(t15["results_rounds"], "round_key", "S15R01-02")["votes_carried_over"] == "true"
    assert len(t15["performances"]) == 149 and len(t15["judge_marks"]) == 556


def test_week_one_launch_subsection_ignored_a168(t15):
    assert len(t15["weeks"]) == 13 and one(t15["weeks"], "week_key", "S15W01")["heading_raw"] == "Week 1"


def test_bruno_absent_week5_a180(t15):
    seat = one(t15["panel_seats"], "panel_seat_key", "S15W05-P-jx1")
    assert seat["judge_slug"] == "bruno-tonioli" and seat["panel_role"] == "absent" and seat["absence_reason"] == "scheduling_conflict" and seat["source_kind"] == "stated"
    assert one(t15["episodes"], "episode_key", "S15W05-P")["scale_max_stated"] == 30
