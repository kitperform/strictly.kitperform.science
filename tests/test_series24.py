"""Acceptance tests for the Phase 0 parser on the series 24 capture.

Each test states a fact that the Wikipedia page (revision in
data/wikipedia/wikitext/MANIFEST.csv) records and that the data model expects
to be represented declaratively.
"""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def tables():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(24, REPO, REPO / "data/wikipedia/parsoid/series_24.parsoid.html", manifest["Strictly_Come_Dancing_series_24"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def by_key(rows, col, value):
    return [r for r in rows if r[col] == value]


def test_all_checks_pass(tables):
    failed = [c for c in tables["_report"]["checks"] if not c[1]]
    assert not failed, failed
    assert not tables["_report"]["unresolved"]


def test_couples_and_exits(tables):
    couples = tables["couples"]
    assert len(couples) == 15
    elim = sorted((c for c in couples if c["exit_kind"] == "eliminated"), key=lambda c: c["exit_ordinal"])
    assert [c["exit_ordinal"] for c in elim] == [1, 2, 3, 4, 5, 6]
    assert [c["exit_week_key"] for c in elim] == ["S24W02", "S24W03", "S24W04", "S24W05", "S24W06", "S24W07"]
    assert all(c["exit_date_kind"] == "results_episode" for c in elim)
    chris = by_key(couples, "couple_key", "S24-chris-appleton")[0]
    assert chris["exit_round_key"] == "S24R01-02" and chris["exit_episode_key"] == "S24W02-R" and chris["final_placement"] == 15
    assert by_key(couples, "couple_key", "S24-lawrence-robb")[0]["chart_label"] == "Lawrence & Jowita"


def test_opening_weeks_are_one_round(tables):
    r = by_key(tables["results_rounds"], "round_key", "S24R01-02")[0]
    assert r["label"] == "1+2" and r["week_keys"] == "S24W01|S24W02" and r["combined_reason"] == "opening_weeks_format"
    assert r["votes_carried_over"] == "false"
    w1 = [cw for cw in tables["couple_weeks"] if cw["week_key"] == "S24W01"]
    assert len(w1) == 15 and all(cw["result_status"] == "carried_forward" and cw["results_round_key"] == "" for cw in w1)
    assert all(cw["results_round_key"] == "S24R01-02" for cw in tables["couple_weeks"] if cw["week_key"] == "S24W02" and cw["participation_status"] == "competed")


def test_triple_dance_off_a253(tables):
    r = by_key(tables["results_rounds"], "round_key", "S24R06")[0]
    assert r["at_risk_group_size_actual"] == 3 and r["vote_direction"] == "eliminate" and r["exit_count"] == 1
    assert r["casting_vote_slug"] == "motsi-mabuse" and r["casting_vote_used"] == "false"
    cws = {cw["couple_key"]: cw for cw in tables["couple_weeks"] if cw["week_key"] == "S24W06"}
    assert cws["S24-bethany-antonia"]["result_status"] == "bottom_three" and cws["S24-jaime-winstone"]["result_status"] == "bottom_three"
    assert cws["S24-lawrence-robb"]["result_status"] == "eliminated" and cws["S24-lawrence-robb"]["danced_off"] == "true"
    votes = by_key(tables["dance_off_votes"], "results_round_key", "S24R06")
    assert len(votes) == 4
    hyp = [v for v in votes if v["vote_kind"] == "hypothetical_not_cast"]
    assert len(hyp) == 1 and hyp[0]["judge_slug"] == "motsi-mabuse" and hyp[0]["couple_key"] == "S24-lawrence-robb"


def test_casting_vote_pivotal_week7(tables):
    r = by_key(tables["results_rounds"], "round_key", "S24R07")[0]
    assert r["casting_vote_slug"] == "shirley-ballas" and r["casting_vote_used"] == "true" and r["casting_vote_inferred"] == "true"
    assert by_key(tables["results_rounds"], "round_key", "S24R03")[0]["casting_vote_used"] == "false"


def test_byes(tables):
    cws = {cw["couple_week_key"]: cw for cw in tables["couple_weeks"]}
    for key in ("S24W04-delta-goodrem", "S24W07-jaime-winstone"):
        cw = cws[key]
        assert cw["participation_status"] == "bye" and cw["result_status"] == "exempt" and cw["bye_granted"] == "true"
        assert cw["absence_reason"] == "injury" and cw["absence_scope"] == "whole_week"
    assert not [p for p in tables["performances"] if p["couple_key"] == "S24-jaime-winstone" and p["week_key"] == "S24W07"]


def test_marks_and_panel(tables):
    scored = [p for p in tables["performances"] if p["scoring_mode"] == "judge_marks"]
    assert len(scored) == 88 and len(tables["judge_marks"]) == 88 * 4
    assert all(p["d_total_mismatch"] == "false" for p in scored)
    seats = by_key(tables["panel_seats"], "episode_key", "S24W06-P")
    assert [s["judge_slug"] for s in sorted(seats, key=lambda s: s["seat_position"])] == ["craig-revel-horwood", "motsi-mabuse", "shirley-ballas", "anton-du-beke"]
    assert [s["vote_label"] for s in sorted(seats, key=lambda s: s["seat_position"])] == ["Revel Horwood", "Mabuse", "Ballas", "Du Beke"]
    assert by_key(seats, "judge_slug", "shirley-ballas")[0]["is_head_judge"] == "true"
    tango = by_key(tables["performances"], "performance_key", "S24W06-P-lawrence-robb-tango")[0]
    assert tango["stated_total"] == 26 and [m["mark"] for m in by_key(tables["judge_marks"], "performance_key", tango["performance_key"])] == [6, 7, 6, 7]


def test_live_series_scheduled_rows(tables):
    w8 = [p for p in tables["performances"] if p["week_key"] == "S24W08"]
    assert w8 and all(p["performance_status"] == "scheduled" and p["scoring_mode"] == "pending" for p in w8)
    assert not [m for m in tables["judge_marks"] if m["week_key"] == "S24W08"]
    assert len([cw for cw in tables["couple_weeks"] if cw["week_key"] == "S24W08" and cw["participation_status"] == "pending"]) == 9
    weeks = {w["week_key"]: w for w in tables["weeks"]}
    assert weeks["S24W08"]["lifecycle_status"] == "scheduled" and weeks["S24W07"]["lifecycle_status"] == "results_in"
    assert weeks["S24W13"]["heading_raw"] == "" and weeks["S24W13"]["source_kind"] == "inferred"
    assert by_key(tables["episodes"], "episode_key", "S24W08-P")[0]["status"] == "scheduled"
    assert tables["series"][0]["status"] == "in_progress"


def test_episodes_and_dates(tables):
    eps = {e["episode_key"]: e for e in tables["episodes"]}
    assert eps["S24-L"]["episode_kind"] == "launch" and eps["S24-L"]["air_date"] == "2026-09-19"
    assert eps["S24W02-R"]["episode_kind"] == "results" and eps["S24W02-R"]["air_date"] == "2026-10-04"
    assert "S24W01-R" not in eps
    s = tables["series"][0]
    assert s["infobox_first_aired"] == "2026-09-19" and s["infobox_last_aired"] == "2026-12-19" and s["final_date"] == "2026-12-19"


def test_music_and_people(tables):
    pm = by_key(tables["performance_music"], "performance_key", "S24W01-P-will-best-samba")[0]
    assert pm["song_key"] == "song:rock-dj:rock-dj" and pm["artist_key"] == "robbie-williams"
    people = {p["person_key"]: p for p in tables["people"]}
    assert people["craig-revel-horwood"]["family_name"] == "Revel Horwood"
    assert people["aljaz-skorjanec"]["wiki_title"] == "Aljaž Škorjanec"
    unpartnered = [r for r in tables["series_people"] if r["roster_status"] == "unpartnered"]
    assert {r["person_key"] for r in unpartnered} == {"neil-jones", "aleksandra-isaeva", "cristian-priori", "lethabo-monametsi"}
    assert not tables["discrepancies"]


def test_review_fixes(tables):
    pm = by_key(tables["performance_music"], "performance_key", "S24W01-P-graeme-hall-cha-cha-cha")[0]
    assert pm["artist_key"] == "" and pm["source_work_text"] == "Smokey Joe's Cafe" and pm["source_work_wiki_title"]
    assert not [a for a in tables["artists"] if a["name"].lower().startswith("from ")]
    assert by_key(tables["performances"], "performance_key", "S24W01-P-will-best-samba")[0]["d_results_round_key"] == "S24R01-02"
    assert by_key(tables["people"], "person_key", "jowita-przystal")
    assert all(a["person_alias_key"].endswith("|S24") and a["series_key"] == "S24" for a in tables["person_aliases"])
    r = by_key(tables["results_rounds"], "round_key", "S24R06")[0]
    assert r["casting_vote_inferred"] == "false" and "did not cast" in r["note"]
