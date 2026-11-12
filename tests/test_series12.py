"""Acceptance tests for series 12 (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t12():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(12, REPO, REPO / "data/wikipedia/parsoid/series_12.parsoid.html", manifest["Strictly_Come_Dancing_series_12"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t12):
    assert not [c for c in t12["_report"]["checks"] if not c[1]]
    assert not t12["_report"]["unresolved"] and not t12["discrepancies"] and not t12["_report"]["warnings"]


def test_five_judge_week_a122(t12):
    seats = sorted((s for s in t12["panel_seats"] if s["episode_key"] == "S12W03-P"), key=lambda s: s["seat_position"])
    assert [(s["judge_slug"], s["panel_role"]) for s in seats] == [("craig-revel-horwood", "regular"), ("darcey-bussell", "regular"), ("donny-osmond", "guest_additional"),
                                                                  ("len-goodman", "head"), ("bruno-tonioli", "regular")]
    assert not [s for s in seats if s["panel_role"] == "absent"]
    p = one(t12["performances"], "performance_key", "S12W03-P-frankie-bridge-paso-doble")
    assert p["stated_total"] == 45 and p["n_marks_stated"] == 5 and p["d_scale_max"] == 50 and p["d_total_40"] == 36.0
    marks = [m for m in t12["judge_marks"] if m["performance_key"] == p["performance_key"]]
    assert [(m["judge_slug"], m["mark"], m["panel_role"]) for m in marks][2] == ("donny-osmond", 10, "guest_additional")
    # the 'first 10 of the series' trap: the only 10 of week 3 came from the guest judge on a 50-point scale
    tens = [m for m in t12["judge_marks"] if m["week_key"] == "S12W03" and m["mark"] == 10]
    assert [(m["judge_slug"], m["d_scale_max"]) for m in tens] == [("donny-osmond", 50)]
    assert one(t12["performances"], "performance_key", "S12W04-P-frankie-bridge-cha-cha-cha")["d_scale_max"] == 40
    votes = [v for v in t12["dance_off_votes"] if v["results_round_key"] == "S12R03"]
    assert len(votes) == 5 and one(votes, "judge_slug", "donny-osmond")["vote_kind"] == "cast"
    assert sorted(v["judge_slug"] for v in votes if v["vote_kind"] == "hypothetical_not_cast") == ["bruno-tonioli", "len-goodman"]
    assert one(t12["results_rounds"], "round_key", "S12R03")["d_n_scoring_seats"] == 5
    assert one(t12["series_people"], "series_person_key", "S12-donny-osmond-judge")["roster_status"] == "guest"


def test_three_casting_votes_a124(t12):
    for k in ("S12R05", "S12R11", "S12R12"):
        r = one(t12["results_rounds"], "round_key", k)
        assert r["casting_vote_slug"] == "len-goodman" and r["casting_vote_used"] == "true" and r["casting_vote_inferred"] == "false"
    assert one(t12["results_rounds"], "round_key", "S12R09")["casting_vote_used"] == "false"  # 3-1 with Len voting


def test_two_show_final_a121(t12):
    a = one(t12["results_rounds"], "round_key", "S12R13a")
    assert a["round_kind"] == "intermediate_final_exit" and a["exit_count"] == 1
    mark = one(t12["couples"], "couple_key", "S12-mark-wright")
    assert mark["final_placement"] == 4 and mark["exit_round_key"] == "S12R13a" and mark["exit_kind"] == "finalist"
    caroline = [p for p in t12["performances"] if p["couple_key"] == "S12-caroline-flack" and p["week_key"] == "S12W13"]
    assert [p["stated_total"] for p in caroline] == [40, 40, 40] and [p["selection_role"] for p in caroline] == ["repeat_judges_choice", "showdance", "repeat_favourite"]
    assert one(t12["couple_weeks"], "couple_week_key", "S12W13-caroline-flack")["d_week_total"] == 120
    assert one(t12["couple_weeks"], "couple_week_key", "S12W07-caroline-flack")["result_status"] == "bottom_two"  # the eventual winner in the bottom two (A125)
    assert len([c for c in t12["couples"] if c["final_placement"] == 2]) == 2


def test_waltz_marathon_and_country_week_a120_a123(t12):
    mar = [p for p in t12["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 6 and all(p["dance_key"] == "waltz" and p["week_key"] == "S12W11" for p in mar)
    assert one(t12["performances"], "performance_key", "S12W11-P-jake-wood-waltz")["points_value"] == 1
    p = one(t12["performances"], "performance_key", "S12W10-P-mark-wright-salsa")
    assert p["theme_column_label"] == "Country" and p["theme_reference_text"]
    assert one(t12["themes"], "theme_key", "around-the-world-week")["theme_reference_kind"] == "country"


def test_volumes(t12):
    assert len(t12["performances"]) == 147 and len(t12["judge_marks"]) == 578 and len(t12["panel_seats"]) == 61
    assert len([p for p in t12["performances"] if p["episode_key"] == "S12W01-N1"]) == 6
