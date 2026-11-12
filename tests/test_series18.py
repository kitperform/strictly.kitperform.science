"""Acceptance tests for series 18, the three-judge Covid series (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t18():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(18, REPO, REPO / "data/wikipedia/parsoid/series_18.parsoid.html", manifest["Strictly_Come_Dancing_series_18"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t18):
    assert not [c for c in t18["_report"]["checks"] if not c[1]]
    assert not t18["_report"]["unresolved"] and not t18["discrepancies"] and not t18["_report"]["warnings"]


def test_three_judges_thirty_points_a198(t18):
    seats = sorted((s for s in t18["panel_seats"] if s["episode_key"] == "S18W01-P"), key=lambda s: s["seat_position"])
    assert [(s["judge_slug"], s["panel_role"]) for s in seats] == [("craig-revel-horwood", "regular"), ("shirley-ballas", "head"), ("motsi-mabuse", "regular")]
    assert one(seats, "judge_slug", "shirley-ballas")["is_head_judge"] == "true" and one(seats, "judge_slug", "shirley-ballas")["seat_position"] == 2
    p = one(t18["performances"], "performance_key", "S18W01-P-jamie-laing-cha-cha-cha")
    assert p["stated_total"] == 14 and p["n_marks_stated"] == 3 and p["d_scale_max"] == 30 and abs(p["d_total_40"] - 18.67) < 0.01
    assert len(t18["judge_marks"]) == 87 * 3
    assert one(t18["format_rules"], "format_rule_key", "S18-FR")["default_scale_max"] == "30"
    bruno = [s for s in t18["panel_seats"] if s["judge_slug"] == "bruno-tonioli"]
    assert bruno and all(s["panel_role"] == "remote_non_scoring" and s["is_scoring"] == "false" and s["episode_key"].endswith("-R") for s in bruno)
    assert len(bruno) == 7  # results shows weeks 2 to 8


def test_du_beke_substitutes_for_mabuse_a191(t18):
    for ekey in ("S18W04-P", "S18W05-P"):
        seats = {s["judge_slug"]: s for s in t18["panel_seats"] if s["episode_key"] == ekey}
        assert seats["anton-du-beke"]["panel_role"] == "guest_replacement" and seats["anton-du-beke"]["seat_position"] == 3 and seats["anton-du-beke"]["replaces_slug"] == "motsi-mabuse"
        assert seats["motsi-mabuse"]["panel_role"] == "absent" and seats["motsi-mabuse"]["absence_reason"] == "covid_contact_or_travel"
    w5 = one(t18["panel_seats"], "panel_seat_key", "S18W05-P-jx1")
    assert w5["source_kind"] == "stated" and "carried forward" in w5["note"]  # 'again substituted' states the absence; the reason comes from week 4
    assert one([m for m in t18["judge_marks"] if m["performance_key"] == "S18W04-P-hrvy-salsa"], "seat_position", 3)["panel_role"] == "guest_replacement"
    roster = {r["series_person_key"]: r for r in t18["series_people"]}
    assert roster["S18-anton-du-beke-judge"]["roster_status"] == "substitute" and roster["S18-anton-du-beke-professional"]["roster_status"] == "competed"
    marks = [m for m in t18["judge_marks"] if m["performance_key"] == "S18W04-P-hrvy-salsa"]
    assert [(m["judge_slug"], m["mark"]) for m in marks] == [("craig-revel-horwood", 8), ("shirley-ballas", 10), ("anton-du-beke", 9)]
    assert one([v for v in t18["dance_off_votes"] if v["results_round_key"] == "S18R04"], "judge_slug", "anton-du-beke")["couple_key"] == "S18-maisie-smith"


def test_head_judge_votes_on_a_split_a193_a194(t18):
    rounds = {r["round_key"]: r for r in t18["results_rounds"]}
    assert rounds["S18R04"]["casting_vote_used"] == "false"  # hypothetical vote, for the eliminated couple
    hyp = one([v for v in t18["dance_off_votes"] if v["results_round_key"] == "S18R04"], "vote_kind", "hypothetical_not_cast")
    assert hyp["judge_slug"] == "shirley-ballas" and hyp["couple_key"] == "S18-max-george"
    for k in ("S18R06", "S18R07", "S18R08"):
        assert rounds[k]["casting_vote_used"] == "true" and rounds[k]["casting_vote_inferred"] == "true" and rounds[k]["d_n_scoring_seats"] == 3
        assert all(v["vote_kind"] == "cast" for v in t18["dance_off_votes"] if v["results_round_key"] == k)


def test_nicola_and_katya_a192(t18):
    c = one(t18["couples"], "couple_key", "S18-nicola-adams")
    assert c["couple_kind"] == "same_sex" and c["exit_kind"] == "withdrew" and c["exit_week_key"] == "S18W04" and c["final_placement"] == 10
    assert c["exit_reason"] == "covid_positive" and c["exit_affected_party"] == "professional" and c["exit_timing"] == "before_live_show"
    assert one(t18["couple_weeks"], "couple_week_key", "S18W03-nicola-adams")["result_status"] == "bottom_two"
    cw = one(t18["couple_weeks"], "couple_week_key", "S18W04-nicola-adams")
    assert cw["participation_status"] == "absent_withdrawn" and cw["affected_party"] == "professional" and cw["absence_reason"] == "covid_positive"
    assert one(t18["results_rounds"], "round_key", "S18R04")["exit_count"] == 1


def test_short_series_and_final_a196_a197(t18):
    assert len(t18["weeks"]) == 9 and len(t18["couples"]) == 12 and len(t18["couple_weeks"]) == 108
    assert t18["series"][0]["launch_date"] == "2020-10-17" and t18["series"][0]["first_live_date"] == "2020-10-24"
    top = sorted(cw["couple_key"] for cw in t18["couple_weeks"] if cw["week_key"] == "S18W09" and cw["d_is_highest_of_week"] == "true")
    assert top == ["S18-bill-bailey", "S18-hrvy", "S18-maisie-smith"]
    assert one(t18["couple_weeks"], "couple_week_key", "S18W09-jamie-laing")["d_is_lowest_of_week"] == "true"
    assert len([c for c in t18["couples"] if c["final_placement"] == 2]) == 3
    jamie8 = [p for p in t18["performances"] if p["couple_key"] == "S18-jamie-laing" and p["week_key"] == "S18W08"]
    assert [p["stated_total"] for p in jamie8] == [24, 24]
    assert one(t18["dances"], "dance_key", "street-commercial")["dance_family"] == "couples_choice"
