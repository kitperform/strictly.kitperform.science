"""Acceptance tests for series 9, a series without dance-offs (revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t9():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(9, REPO, REPO / "data/wikipedia/parsoid/series_9.parsoid.html", manifest["Strictly_Come_Dancing_series_9"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t9):
    assert not [c for c in t9["_report"]["checks"] if not c[1]]
    assert not t9["_report"]["unresolved"]
    assert {d["discrepancy_key"] for d in t9["discrepancies"]} == {"ResultsRound|S09R12a|elimination_mechanism_actual|1"}  # Show 1 mechanism is disputed (A077)


def test_no_dance_off_series_a096(t9):
    assert not t9["dance_off_votes"]
    std = [r for r in t9["results_rounds"] if r["round_kind"] == "standard"]
    assert std and all(r["elimination_mechanism_actual"] == "ranking_points_no_dance_off" and r["dance_off_status"] == "not_in_format" and r["casting_vote_slug"] == "" for r in std)
    cw = one(t9["couple_weeks"], "couple_week_key", "S09W05-audley-harrison")
    assert cw["result_status"] == "bottom_two" and cw["at_risk"] == "true" and cw["danced_off"] == "false"
    assert one(t9["format_rules"], "format_rule_key", "S09-FR")["dance_off_used"] == "false"


def test_double_elimination_without_bottom_two_a089(t9):
    r = one(t9["results_rounds"], "round_key", "S09R11")
    assert r["exit_count"] == 2 and r["at_risk_group_size_actual"] == ""
    for ck in ("S09-alex-jones", "S09-holly-valance"):
        cw = one(t9["couple_weeks"], "couple_week_key", f"S09W11-{ck[4:]}")
        assert cw["result_status"] == "eliminated" and cw["at_risk"] == "false"
        c = one(t9["couples"], "couple_key", ck)
        assert c["exit_ordinal"] == 10 and c["exit_ordinal_is_shared"] == "true" and c["exit_ordinal_text"] == "10th & 11th" and c["exit_round_key"] == "S09R11"
    assert one(t9["couples"], "couple_key", "S09-holly-valance")["final_placement"] == 4
    harry = [p for p in t9["performances"] if p["couple_key"] == "S09-harry-judd" and p["week_key"] == "S09W11"]
    assert [p["stated_total"] for p in harry] == [39, 39]  # merged score cell


def test_brendan_substitutes_twice_a093_a094(t9):
    anita = sorted((p for p in t9["couple_partnerships"] if p["couple_key"] == "S09-anita-dobson"), key=lambda p: p["week_from"])
    assert [(p["pro_person_key"], p["week_from"], p["week_to"], p["partnership_kind"]) for p in anita] == [("robin-windsor", 1, 8, "original"), ("brendan-cole", 9, 9, "substitute_temporary")]
    c = one(t9["couples"], "couple_key", "S09-anita-dobson")
    assert c["chart_label"] == "Anita & Robin" and c["exit_week_key"] == "S09W09" and c["exit_round_key"] == "S09R09"  # exit recorded against the original couple
    assert one(t9["performances"], "performance_key", "S09W09-P-anita-dobson-cha-cha-cha")["performing_pro_slug"] == "brendan-cole"
    assert one(t9["performances"], "performance_key", "S09W07-P-holly-valance-rumba")["performing_pro_slug"] == "brendan-cole"
    roster = {r["series_person_key"]: r for r in t9["series_people"]}
    assert roster["S09-brendan-cole-professional"]["roster_status"] == "competed"
    assert {roster["S09-brendan-cole-professional-2"]["replaces_person_key"], roster["S09-brendan-cole-professional-3"]["replaces_person_key"]} == {"robin-windsor", "artem-chigvintsev"}


def test_jennifer_grey_for_len_a092(t9):
    seats = {s["judge_slug"]: s for s in t9["panel_seats"] if s["episode_key"] == "S09W06-P"}
    assert seats["jennifer-grey"]["panel_role"] == "guest_replacement" and seats["jennifer-grey"]["seat_position"] == 2 and seats["jennifer-grey"]["replaces_slug"] == "len-goodman"
    assert seats["len-goodman"]["panel_role"] == "absent" and seats["len-goodman"]["is_head_judge"] == "true"
    marks = [m for m in t9["judge_marks"] if m["episode_key"] == "S09W06-P"]
    assert marks and all(m["judge_slug"] != "len-goodman" for m in marks) and any(m["judge_slug"] == "jennifer-grey" for m in marks)


def test_final_at_blackpool_a090(t9):
    eps = {e["episode_key"]: e for e in t9["episodes"]}
    assert eps["S09W12-S1"]["venue_key"] == "blackpool-tower-ballroom" and eps["S09W12-S2"]["episode_kind"] == "performance_and_results"
    jason = one(t9["couples"], "couple_key", "S09-jason-donovan")
    assert jason["final_placement"] == 3 and jason["exit_round_key"] == "S09R12a"
    assert one(t9["couple_weeks"], "couple_week_key", "S09W12-jason-donovan")["result_status"] == "third"
    harry = [p for p in t9["performances"] if p["couple_key"] == "S09-harry-judd" and p["week_key"] == "S09W12"]
    assert [p["selection_role"] for p in harry] == ["repeat_judges_choice", "showdance", "unlearned", "repeat_favourite"]
    assert one(t9["couple_weeks"], "couple_week_key", "S09W12-harry-judd")["d_week_total"] == 156
    chelsee = [p for p in t9["performances"] if p["couple_key"] == "S09-chelsee-healey" and p["episode_key"] == "S09W12-S2"]
    assert [p["stated_total"] for p in chelsee] == [39, 39]


def test_marathon_wembley_and_names_a095_a091_a098(t9):
    mar = [p for p in t9["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 7 and all(p["dance_key"] == "swing" for p in mar)
    assert one(t9["performances"], "performance_key", "S09W09-P-robbie-savage-swing")["points_value"] == 1
    assert one(t9["episodes"], "episode_key", "S09W08-P")["venue_key"] == "wembley-arena"
    assert one(t9["couples"], "chart_label", "Lulu & Brendan")["celebrity_display_name"] == "Lulu"
    assert one(t9["couples"], "chart_label", "Nancy & Anton")["couple_key"] == "S09-nancy-dell-olio"
    assert one(t9["performances"], "performance_key", "S09W10-P-jason-donovan-american-smooth")["theme_reference_text"] == "Singin' in the Rain"  # stray cell (A088)
    assert len(t9["performances"]) == 131 and len(t9["judge_marks"]) == 496
