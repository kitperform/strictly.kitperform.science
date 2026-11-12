"""Acceptance tests for series 14, Len Goodman's last (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t14():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(14, REPO, REPO / "data/wikipedia/parsoid/series_14.parsoid.html", manifest["Strictly_Come_Dancing_series_14"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t14):
    assert not [c for c in t14["_report"]["checks"] if not c[1]]
    assert not t14["_report"]["unresolved"] and not t14["discrepancies"] and not t14["_report"]["warnings"]


def test_two_night_week_one_a148(t14):
    eps = {e["episode_key"]: e for e in t14["episodes"]}
    assert eps["S14W01-N1"]["sub_label"] == "night1" and eps["S14W01-N1"]["air_date"] == "2016-09-23"
    assert eps["S14W01-N2"]["sub_label"] == "night2" and eps["S14W01-N2"]["air_date"] == "2016-09-24" and "S14W01-P" not in eps
    assert len([p for p in t14["performances"] if p["episode_key"] == "S14W01-N1"]) == 6
    assert len([p for p in t14["performances"] if p["episode_key"] == "S14W01-N2"]) == 9
    assert len([s for s in t14["panel_seats"] if s["episode_key"] == "S14W01-N2"]) == 4
    assert one(t14["results_rounds"], "round_key", "S14R01-02")["votes_carried_over"] == "true"


def test_cancelled_dance_off_public_vote_a152(t14):
    r = one(t14["results_rounds"], "round_key", "S14R01-02")
    assert r["dance_off_status"] == "cancelled_injury" and r["elimination_mechanism_actual"] == "lowest_public_vote"
    assert r["votes_recorded"] == "false" and r["exit_count"] == 1 and r["at_risk_group_size_actual"] == 2
    for ck, res in (("S14-melvin-odoom", "eliminated"), ("S14-anastacia", "bottom_two")):
        cw = one(t14["couple_weeks"], "couple_week_key", f"S14W02-{ck[4:]}")
        assert cw["result_status"] == res and cw["at_risk"] == "true" and cw["danced_off"] == "false"
    assert not [v for v in t14["dance_off_votes"] if v["results_round_key"] == "S14R01-02"]


def test_will_young_a154(t14):
    c = one(t14["couples"], "couple_key", "S14-will-young")
    assert c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S14W04" and c["exit_reason"] == "personal" and c["exit_timing"] == "before_live_show" and c["final_placement"] == 13
    assert one(t14["results_rounds"], "round_key", "S14R04")["exit_count"] == 1


def test_one_week_substitution_and_bye_a155_a156(t14):
    ps = sorted((p for p in t14["couple_partnerships"] if p["couple_key"] == "S14-anastacia"), key=lambda p: p["week_from"])
    assert [(p["pro_person_key"], p["week_from"], p["week_to"], p["partnership_kind"]) for p in ps] == [
        ("brendan-cole", 1, 4, "original"), ("gorka-marquez", 5, 5, "substitute_temporary"), ("brendan-cole", 6, 6, "original")]
    assert ps[1]["reason"] == "illness"
    p = one(t14["performances"], "performance_key", "S14W05-P-anastacia-quickstep")
    assert p["performing_pro_slug"] == "gorka-marquez" and p["couple_label_raw"] == "Anastacia & Gorka"
    assert one(t14["people"], "person_key", "anastacia")["family_name"] == ""
    laura = one(t14["couple_weeks"], "couple_week_key", "S14W05-laura-whitmore")
    assert laura["participation_status"] == "bye" and laura["absence_reason"] == "injury"


def test_len_goodman_head_judge_a153(t14):
    seats = sorted((s for s in t14["panel_seats"] if s["episode_key"] == "S14W03-P"), key=lambda s: s["seat_position"])
    assert [s["judge_slug"] for s in seats] == ["craig-revel-horwood", "darcey-bussell", "len-goodman", "bruno-tonioli"]
    assert one(seats, "judge_slug", "len-goodman")["is_head_judge"] == "true"
    r3 = one(t14["results_rounds"], "round_key", "S14R03")
    assert r3["casting_vote_slug"] == "len-goodman" and r3["casting_vote_used"] == "false"  # 3-1 with Len voting
    assert one([v for v in t14["dance_off_votes"] if v["results_round_key"] == "S14R03"], "judge_slug", "darcey-bussell")["couple_key"] == "S14-tameka-empson"


def test_rinder_marathon_final_a158_a149_a151(t14):
    assert one(t14["couples"], "chart_label", "Judge Rinder & Oksana")["celebrity_display_name"] == "Judge Rinder"
    mar = [p for p in t14["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 6 and all(p["dance_key"] == "cha-cha-cha" for p in mar)
    assert one(t14["couple_weeks"], "couple_week_key", "S14W10-danny-mac")["d_week_total"] == 45
    lows = sorted(cw["couple_key"] for cw in t14["couple_weeks"] if cw["week_key"] == "S14W13" and cw["d_is_lowest_of_week"] == "true")
    assert lows == ["S14-danny-mac", "S14-louise-redknapp"]
    assert one(t14["couples"], "couple_key", "S14-ore-oduba")["final_placement"] == 1
    assert len(t14["performances"]) == 134 and len(t14["judge_marks"]) == 512
