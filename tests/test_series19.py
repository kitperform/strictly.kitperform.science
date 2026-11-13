"""Acceptance tests for series 19 (complete series; revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t19():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(19, REPO, REPO / "data/wikipedia/parsoid/series_19.parsoid.html", manifest["Strictly_Come_Dancing_series_19"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t19):
    assert not [c for c in t19["_report"]["checks"] if not c[1]]
    assert not t19["_report"]["unresolved"] and not t19["discrepancies"] and not t19["_report"]["warnings"]


def test_guest_judge_replaces_horwood_a211(t19):
    seats = sorted((s for s in t19["panel_seats"] if s["episode_key"] == "S19W09-P"), key=lambda s: s["panel_seat_key"])
    assert [(s["panel_seat_key"][-3:], s["judge_slug"], s["panel_role"], s["is_scoring"]) for s in seats] == [
        ("-j1", "cynthia-erivo", "guest_replacement", "true"), ("-j2", "motsi-mabuse", "regular", "true"),
        ("-j3", "shirley-ballas", "head", "true"), ("-j4", "anton-du-beke", "regular", "true"), ("jx1", "craig-revel-horwood", "absent", "false")]
    assert one(seats, "judge_slug", "cynthia-erivo")["replaces_slug"] == "craig-revel-horwood"
    assert one(seats, "judge_slug", "craig-revel-horwood")["absence_reason"] == "covid_positive"
    marks = [m for m in t19["judge_marks"] if m["performance_key"] == "S19W09-P-aj-odudu-waltz"]
    assert [(m["judge_slug"], m["mark"]) for m in marks] == [("cynthia-erivo", 9), ("motsi-mabuse", 10), ("shirley-ballas", 10), ("anton-du-beke", 9)]
    assert not [m for m in t19["judge_marks"] if m["week_key"] == "S19W09" and m["judge_slug"] == "craig-revel-horwood"]
    votes = [v for v in t19["dance_off_votes"] if v["results_round_key"] == "S19R09"]
    assert one(votes, "judge_slug", "cynthia-erivo")["judge_label_raw"] == "Erivo"


def test_guest_judge_replaces_mabuse_a203(t19):
    seats = {s["judge_slug"]: s for s in t19["panel_seats"] if s["episode_key"] == "S19W10-P"}
    assert seats["cynthia-erivo"]["seat_position"] == 2 and seats["cynthia-erivo"]["replaces_slug"] == "motsi-mabuse"
    assert seats["motsi-mabuse"]["panel_role"] == "absent" and seats["motsi-mabuse"]["absence_reason"] == "covid_contact_or_travel"
    assert seats["craig-revel-horwood"]["seat_position"] == 1
    roster = one(t19["series_people"], "series_person_key", "S19-cynthia-erivo-judge")
    assert roster["roster_status"] == "guest" and roster["first_week_key"] == "S19W09" and roster["last_week_key"] == "S19W10"
    # the constant panel elsewhere still has exactly one row per regular judge
    assert len([s for s in t19["panel_seats"] if s["episode_key"] == "S19W08-P"]) == 4


def test_withdrawals_a208_a205(t19):
    robert = one(t19["couples"], "couple_key", "S19-robert-webb")
    assert robert["exit_kind"] == "withdrew" and robert["exit_week_key"] == "S19W04" and robert["exit_timing"] == "before_live_show" and robert["exit_reason"] == "medical_advice" and robert["final_placement"] == 13
    assert one(t19["couple_weeks"], "couple_week_key", "S19W04-robert-webb")["absence_reason"] == "illness"
    assert one(t19["couple_weeks"], "couple_week_key", "S19W04-robert-webb")["bye_granted"] == "false"  # the bye that week was Ugo Monye's
    assert one(t19["results_rounds"], "round_key", "S19R04")["exit_count"] == 1  # Greg & Karen still eliminated
    aj = one(t19["couples"], "couple_key", "S19-aj-odudu")
    assert aj["exit_week_key"] == "S19W13" and aj["exit_timing"] == "before_final" and aj["exit_reason"] == "injury" and aj["final_placement"] == 3 and aj["exit_round_key"] == ""
    cw = one(t19["couple_weeks"], "couple_week_key", "S19W13-aj-odudu")
    assert cw["participation_status"] == "absent_withdrawn" and cw["result_status"] == "withdrew" and cw["results_round_key"] == ""
    assert not [p for p in t19["performances"] if p["couple_key"] == "S19-aj-odudu" and p["week_key"] == "S19W13"]
    assert len([c for c in t19["couples"] if c["exit_kind"] == "finalist"]) == 2


def test_byes_a207_a209_a210(t19):
    cws = {cw["couple_week_key"]: cw for cw in t19["couple_weeks"]}
    assert cws["S19W02-tom-fletcher"]["participation_status"] == "bye" and cws["S19W02-tom-fletcher"]["absence_reason"] == "covid_positive"
    assert cws["S19W04-ugo-monye"]["participation_status"] == "bye" and cws["S19W04-ugo-monye"]["absence_reason"] == "injury"
    assert cws["S19W05-judi-love"]["participation_status"] == "bye" and cws["S19W05-judi-love"]["absence_reason"] == "covid_positive"
    assert cws["S19W06-judi-love"]["result_status"] == "eliminated"
    r = one(t19["results_rounds"], "round_key", "S19R01-02")
    assert r["votes_carried_over"] == "true"  # 'all scores and votes carried over' (A202)


def test_final_and_misc(t19):
    rose = [p for p in t19["performances"] if p["couple_key"] == "S19-rose-ayling-ellis" and p["week_key"] == "S19W13"]
    assert [p["selection_role"] for p in rose] == ["repeat_judges_choice", "repeat_favourite", "showdance"]  # S19 order (A206)
    john = [p for p in t19["performances"] if p["couple_key"] == "S19-john-whaite" and p["week_key"] == "S19W12"]
    assert [p["stated_total"] for p in john] == [39, 39]  # merged rowspan score cell (A204)
    assert one(t19["couples"], "couple_key", "S19-john-whaite")["couple_kind"] == "same_sex"
    r2 = one(t19["results_rounds"], "round_key", "S19R03")
    assert r2["casting_vote_used"] == "false"  # Ballas voted in a 3-1, not pivotal (A221)
    assert len(t19["performances"]) == 123 and len(t19["judge_marks"]) == 492 and len(t19["panel_seats"]) == 54
