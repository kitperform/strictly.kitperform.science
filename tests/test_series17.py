"""Acceptance tests for series 17 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t17():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(17, REPO, REPO / "data/wikipedia/parsoid/series_17.parsoid.html", manifest["Strictly_Come_Dancing_series_17"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t17):
    assert not [c for c in t17["_report"]["checks"] if not c[1]]
    assert not t17["_report"]["unresolved"] and not t17["discrepancies"] and not t17["_report"]["warnings"]
    assert not [p for p in t17["people"] if p["person_key"].startswith("unlinked-")]


def test_two_week_substitution_a182(t17):
    ps = sorted((p for p in t17["couple_partnerships"] if p["couple_key"] == "S17-alex-scott"), key=lambda p: p["week_from"])
    assert [(p["pro_person_key"], p["week_from"], p["week_to"], p["partnership_kind"], p["source_kind"]) for p in ps] == [
        ("neil-jones", 1, 5, "original", "stated"), ("kevin-clifton", 6, 7, "substitute_temporary", "stated"), ("neil-jones", 8, 11, "original", "inferred")]
    assert ps[1]["reason"] == "injury"
    for wk, pro, label in ((5, "neil-jones", "Alex & Neil"), (6, "kevin-clifton", "Alex & Kevin"), (7, "kevin-clifton", "Alex & Kevin"), (8, "neil-jones", "Alex & Neil")):
        p = [x for x in t17["performances"] if x["couple_key"] == "S17-alex-scott" and x["week_key"] == f"S17W{wk:02d}"][0]
        assert p["performing_pro_slug"] == pro and p["couple_label_raw"] == label
    cw6 = one(t17["couple_weeks"], "couple_week_key", "S17W06-alex-scott")
    assert cw6["d_pro_slug"] == "kevin-clifton" and cw6["d_partnership_kind"] == "substitute_temporary" and cw6["affected_party"] == "professional" and cw6["absence_reason"] == "injury"
    roster = {r["series_person_key"]: r for r in t17["series_people"]}
    assert roster["S17-kevin-clifton-professional"]["roster_status"] == "competed"  # partnered Anneka Rice
    assert roster["S17-kevin-clifton-professional-2"]["roster_status"] == "partnered_mid_series" and roster["S17-kevin-clifton-professional-2"]["replaces_person_key"] == "neil-jones"
    assert "S17-neil-jones-professional-2" not in roster  # Neil came back; he did not leave


def test_ribeiro_for_tonioli_a180(t17):
    seats = {s["judge_slug"]: s for s in t17["panel_seats"] if s["episode_key"] == "S17W05-P"}
    assert seats["alfonso-ribeiro"]["panel_role"] == "guest_replacement" and seats["alfonso-ribeiro"]["seat_position"] == 4 and seats["alfonso-ribeiro"]["replaces_slug"] == "bruno-tonioli"
    assert seats["bruno-tonioli"]["panel_role"] == "absent" and seats["bruno-tonioli"]["absence_reason"] == "scheduling_conflict"
    assert one([v for v in t17["dance_off_votes"] if v["results_round_key"] == "S17R05"], "judge_slug", "alfonso-ribeiro")["judge_label_raw"] == "Ribeiro"
    assert one(t17["series_people"], "series_person_key", "S17-alfonso-ribeiro-judge")["roster_status"] == "guest"


def test_stated_casting_votes_a183_a178(t17):
    for k, saved in (("S17R06", "S17-mike-bushell"), ("S17R11", "S17-chris-ramsey")):
        r = one(t17["results_rounds"], "round_key", k)
        assert r["casting_vote_used"] == "true" and r["casting_vote_inferred"] == "false"
        v = one([x for x in t17["dance_off_votes"] if x["results_round_key"] == k], "judge_slug", "shirley-ballas")
        assert v["is_casting_vote_stated"] == "true" and v["couple_key"] == saved and v["vote_kind"] == "cast"
    assert one(t17["results_rounds"], "round_key", "S17R05")["casting_vote_used"] == "false"


def test_will_bayley_a181_a184(t17):
    assert one(t17["couple_weeks"], "couple_week_key", "S17W06-will-bayley")["absence_reason"] == "injury"
    c = one(t17["couples"], "couple_key", "S17-will-bayley")
    assert c["exit_week_key"] == "S17W07" and c["exit_timing"] == "before_live_show" and c["exit_reason"] == "unspecified" and c["final_placement"] == 10
    assert one(t17["results_rounds"], "round_key", "S17R07")["exit_count"] == 1


def test_labels_and_final_a188_a179(t17):
    assert one(t17["couples"], "couple_key", "S17-emma-barton")["chart_label"] == "Emma B. & Anton"
    assert one(t17["couples"], "chart_label", "Emma W. & Aljaž")["celebrity_display_name"] == "Emma Weymouth"
    assert one(t17["couple_weeks"], "couple_week_key", "S17W13-karim-zeroual")["d_is_highest_of_week"] == "true"
    assert one(t17["couples"], "couple_key", "S17-kelvin-fletcher")["final_placement"] == 1
    assert len(t17["performances"]) == 131 and len(t17["judge_marks"]) == 524
