"""Acceptance tests for series 23 (complete series; revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t23():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(23, REPO, REPO / "data/wikipedia/parsoid/series_23.parsoid.html", manifest["Strictly_Come_Dancing_series_23"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t23):
    assert not [c for c in t23["_report"]["checks"] if not c[1]]
    assert not t23["_report"]["unresolved"] and not t23["discrepancies"]
    assert t23["series"][0]["status"] == "complete"


def test_withdrawal_before_show_a245(t23):
    c = one(t23["couples"], "couple_key", "S23-stefan-dennis")
    assert c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S23W05" and c["exit_round_key"] == "" and c["exit_episode_key"] == ""
    assert c["exit_timing"] == "before_live_show" and c["exit_reason"] == "injury" and c["final_placement"] == 12
    cw = one(t23["couple_weeks"], "couple_week_key", "S23W05-stefan-dennis")
    assert cw["participation_status"] == "absent_withdrawn" and cw["result_status"] == "withdrew" and cw["results_round_key"] == ""
    bye = one(t23["couple_weeks"], "couple_week_key", "S23W03-stefan-dennis")
    assert bye["participation_status"] == "bye" and bye["bye_granted"] == "true" and bye["absence_reason"] == "illness"
    # a normal elimination still happened in week 5
    assert one(t23["results_rounds"], "round_key", "S23R05")["exit_count"] == 1


def test_bye_then_withdrawal_and_carry_over_a246(t23):
    c = one(t23["couples"], "couple_key", "S23-la-voix")
    assert c["exit_timing"] == "during_live_show_before_dancing" and c["exit_episode_key"] == "S23W09-P" and c["exit_date_kind"] == "performance_episode"
    cw = one(t23["couple_weeks"], "couple_week_key", "S23W09-la-voix")
    assert cw["bye_granted"] == "true" and cw["participation_status"] == "absent_withdrawn" and cw["result_status"] == "withdrew"
    r = one(t23["results_rounds"], "round_key", "S23R09-10")
    assert r["label"] == "9+10" and r["combined_reason"] == "withdrawal_carry_over" and r["votes_carried_over"] == "true" and r["exit_count"] == 1
    assert all(cw["result_status"] == "carried_forward" for cw in t23["couple_weeks"] if cw["week_key"] == "S23W09" and cw["participation_status"] == "competed")
    assert one(t23["couples"], "couple_key", "S23-alex-kingston")["exit_round_key"] == "S23R09-10"


def test_instant_dance_a241(t23):
    inst = [p for p in t23["performances"] if p["performance_kind"] == "instant"]
    assert len(inst) == 6 and all(p["scoring_mode"] == "rank_points" and p["selection_role"] == "instant" and p["group_key"] == "S23W10-P-G1" for p in inst)
    assert sorted(p["points_value"] for p in inst) == [1, 2, 3, 4, 5, 6]
    assert one(t23["performances"], "performance_key", "S23W10-P-karen-carney-cha-cha-cha")["points_value"] == 1
    assert one(t23["couple_weeks"], "couple_week_key", "S23W10-karen-carney")["d_week_total"] == 41
    assert not [m for m in t23["judge_marks"] if m["performance_key"] in {p["performance_key"] for p in inst}]


def test_rotating_casting_vote_a248(t23):
    holders = {r["round_key"]: r["casting_vote_slug"] for r in t23["results_rounds"]}
    assert holders["S23R01-02"] == "motsi-mabuse" and holders["S23R04"] == "craig-revel-horwood" and holders["S23R05"] == "anton-du-beke"
    r4 = one(t23["results_rounds"], "round_key", "S23R04")
    assert r4["casting_vote_used"] == "true" and r4["casting_vote_inferred"] == "true"  # 2-2 recorded as four plain votes
    assert one(t23["results_rounds"], "round_key", "S23R03")["casting_vote_used"] == "false"


def test_non_scoring_guest_a243(t23):
    seats = [s for s in t23["panel_seats"] if s["episode_key"] == "S23W03-P"]
    assert len(seats) == 5
    guest = one(seats, "panel_role", "non_scoring_guest")
    assert guest["judge_slug"] == "cynthia-erivo" and guest["is_scoring"] == "false" and guest["panel_seat_key"] == "S23W03-P-jx1"
    assert len([m for m in t23["judge_marks"] if m["episode_key"] == "S23W03-P"]) == 13 * 4


def test_final_a242(t23):
    r = one(t23["results_rounds"], "round_key", "S23R13")
    assert r["round_kind"] == "final_placing" and r["elimination_mechanism_actual"] == "public_vote_final_placing" and r["exit_count"] == 0 and r["dance_off_status"] == "not_applicable"
    winner = one(t23["couples"], "couple_key", "S23-karen-carney")
    assert winner["final_placement"] == 1 and winner["exit_kind"] == "finalist" and winner["exit_date_kind"] == "combined_episode"
    runners = [c for c in t23["couples"] if c["final_placement"] == 2]
    assert len(runners) == 2 and all(c["place_is_shared"] == "true" for c in runners)
    george = [p for p in t23["performances"] if p["couple_key"] == "S23-george-clarke" and p["week_key"] == "S23W13"]
    assert [p["stated_total"] for p in george] == [39, 39, 39] and [p["selection_role"] for p in george] == ["repeat_judges_choice", "showdance", "repeat_favourite"]
    assert one(t23["couple_weeks"], "couple_week_key", "S23W13-karen-carney")["d_is_lowest_of_week"] == "true"  # 117 tied lowest, daggered on the page
    assert one(t23["episodes"], "episode_key", "S23W13-P")["episode_kind"] == "performance_and_results"


def test_musicals_week_is_a_theme_column(t23):
    w11 = [p for p in t23["performances"] if p["week_key"] == "S23W11"]
    assert w11 and all(p["theme_column_label"] == "Musical" and p["theme_reference_text"] and p["music_raw"].startswith(('"', "“")) for p in w11)


def test_volumes(t23):
    assert len(t23["couples"]) == 15 and len(t23["couple_weeks"]) == 15 * 13
    assert len(t23["judge_marks"]) == 128 * 4 and len(t23["performances"]) == 137  # 134 danced + 3 planned routines never performed
    assert len([r for r in t23["series_people"] if r["roster_status"] == "unpartnered"]) == 5


def test_pre_series_replacements_a247(t23):
    nairn = one(t23["series_people"], "series_person_key", "S23-kristian-nairn-celebrity")
    assert nairn["roster_status"] == "withdrew_pre_launch" and nairn["replaced_by_person_key"] == "lewis-cope" and nairn["reason"] == "medical_advice" and nairn["event_date"] == "2025-08-21"
    dyer = one(t23["series_people"], "series_person_key", "S23-dani-dyer-celebrity")
    assert dyer["roster_status"] == "paired_withdrew_pre_week1" and dyer["paired_with_person_key"] == "nikita-kuzmin" and dyer["replaced_by_person_key"] == "amber-davies" and dyer["reason"] == "injury"
    assert one(t23["series_people"], "series_person_key", "S23-amber-davies-celebrity")["replaces_person_key"] == "dani-dyer"


def test_planned_dances_never_performed_a244_a252(t23):
    planned = {p["performance_key"]: p for p in t23["performances"] if p["performance_status"] == "not_performed"}
    assert set(planned) == {"S23W03-P-stefan-dennis-waltz", "S23W05-P-stefan-dennis-planned", "S23W09-P-la-voix-samba"}
    assert planned["S23W05-P-stefan-dennis-planned"]["dance_key"] == "" and planned["S23W05-P-stefan-dennis-planned"]["theme_reference_text"] == "Jon Bon Jovi"
    assert planned["S23W09-P-la-voix-samba"]["music_raw"] == '"Love Is in the Air" — John Paul Young' and planned["S23W09-P-la-voix-samba"]["scoring_mode"] == "not_performed"
    assert all(p["stated_total"] == "" for p in planned.values())
