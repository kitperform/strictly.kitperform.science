"""Acceptance tests for series 20 (complete series; revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t20():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(20, REPO, REPO / "data/wikipedia/parsoid/series_20.parsoid.html", manifest["Strictly_Come_Dancing_series_20"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t20):
    assert not [c for c in t20["_report"]["checks"] if not c[1]]
    assert not t20["_report"]["unresolved"] and not t20["_report"]["warnings"]
    assert {d["discrepancy_key"] for d in t20["discrepancies"]} == {"Couple|S20-kym-marsh|exit_date|1", "Couple|S20-will-mellor|exit_date|1"}  # Couples-table date vs results broadcast (A004)


def test_tony_adams_cancelled_dance_off_a226(t20):
    r = one(t20["results_rounds"], "round_key", "S20R08")
    assert r["elimination_mechanism_actual"] == "none" and r["dance_off_status"] == "cancelled_withdrawal" and r["exit_count"] == 0
    assert r["at_risk_group_size_actual"] == 2 and r["votes_recorded"] == "false" and not [v for v in t20["dance_off_votes"] if v["results_round_key"] == "S20R08"]
    tony = one(t20["couple_weeks"], "couple_week_key", "S20W08-tony-adams")
    assert tony["participation_status"] == "competed" and tony["result_status"] == "withdrew" and tony["at_risk"] == "true" and tony["danced_off"] == "false" and tony["results_round_key"] == "S20R08"
    tyler = one(t20["couple_weeks"], "couple_week_key", "S20W08-tyler-west")
    assert tyler["result_status"] == "bottom_two" and tyler["at_risk"] == "true" and tyler["danced_off"] == "false"
    assert one(t20["performances"], "performance_key", "S20W08-P-tony-adams-jive")["stated_total"] == 24
    c = one(t20["couples"], "couple_key", "S20-tony-adams")
    assert c["exit_kind"] == "withdrew" and c["exit_timing"] == "during_results_show" and c["exit_episode_key"] == "S20W08-R"
    assert c["exit_date_kind"] == "results_episode" and c["exit_reason"] == "injury" and c["final_placement"] == 9 and c["exit_round_key"] == ""


def test_covid_bye_a223(t20):
    cw = one(t20["couple_weeks"], "couple_week_key", "S20W10-kym-marsh")
    assert cw["participation_status"] == "bye" and cw["absence_reason"] == "covid_positive" and cw["bye_granted"] == "true"
    assert one(t20["couples"], "couple_key", "S20-kym-marsh")["exit_week_key"] == "S20W11"


def test_postponed_launch_a227(t20):
    e = one(t20["episodes"], "episode_key", "S20-L")
    assert e["air_date"] == "2022-09-23" and e["original_air_date"] == "2022-09-17" and "postponed" in e["reschedule_reason_text"]
    assert one(t20["episodes"], "episode_key", "S20W01-P")["air_date"] == "2022-09-24"
    assert one(t20["episodes"], "episode_key", "S20W11-P")["air_date"] == "2022-12-02"  # a Friday
    assert one(t20["episodes"], "episode_key", "S20W12-R")["air_date"] == "2022-12-12"  # a Monday


def test_bbc_theme_week_a225(t20):
    assert one(t20["themes"], "theme_key", "celebrating-bbc-100-week")["theme_reference_kind"] == "bbc_programme"
    p = one(t20["performances"], "performance_key", "S20W05-P-hamza-yassin-quickstep")
    assert p["theme_column_label"] == "Celebrating BBC" and p["theme_reference_text"]


def test_final_and_ties_a224_a222(t20):
    assert len([c for c in t20["couples"] if c["final_placement"] == 2]) == 3
    hamza = one(t20["couple_weeks"], "couple_week_key", "S20W13-hamza-yassin")
    assert hamza["result_status"] == "winner" and hamza["d_week_total"] == 113 and hamza["d_is_lowest_of_week"] == "true"
    w1_top = [cw for cw in t20["couple_weeks"] if cw["week_key"] == "S20W01" and cw["d_is_highest_of_week"] == "true"]
    assert {cw["couple_key"] for cw in w1_top} == {"S20-hamza-yassin", "S20-will-mellor"}
    assert one(t20["couples"], "couple_key", "S20-ellie-taylor")["chart_label"] == "Ellie T. & Johannes"


def test_volumes(t20):
    assert len(t20["performances"]) == 141 and len(t20["judge_marks"]) == 564 and len(t20["couple_weeks"]) == 195
    assert all(r["casting_vote_slug"] == "shirley-ballas" for r in t20["results_rounds"] if r["votes_recorded"] == "true")
