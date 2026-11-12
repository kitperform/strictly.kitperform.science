"""Acceptance tests for series 22 (complete series; revision in MANIFEST.csv)."""
import csv
from pathlib import Path

import pytest

from strictly_parser.build import Build

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def t22():
    with (REPO / "data/wikipedia/wikitext/MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    b = Build(22, REPO, REPO / "data/wikipedia/parsoid/series_22.parsoid.html", manifest["Strictly_Come_Dancing_series_22"], REPO / "curated")
    t, report = b.run()
    t["_report"] = report
    return t


def one(rows, col, value):
    found = [r for r in rows if r[col] == value]
    assert len(found) == 1, (col, value, len(found))
    return found[0]


def test_checks_pass(t22):
    assert not [c for c in t22["_report"]["checks"] if not c[1]]
    assert not t22["_report"]["unresolved"] and not t22["discrepancies"] and not t22["_report"]["warnings"]


def test_professional_change_a237(t22):
    ps = sorted((p for p in t22["couple_partnerships"] if p["couple_key"] == "S22-jb-gill"), key=lambda p: p["week_from"])
    assert [(p["pro_person_key"], p["week_from"], p["week_to"], p["partnership_kind"], p["reason"]) for p in ps] == [
        ("amy-dowden", 1, 6, "original", ""), ("lauren-oakley", 7, 7, "substitute_temporary", "illness"), ("lauren-oakley", 8, 13, "replacement_permanent", "injury")]
    assert one(t22["performances"], "performance_key", "S22W06-P-jb-gill-foxtrot")["performing_pro_slug"] == "amy-dowden"
    w7 = one(t22["performances"], "performance_key", "S22W07-P-jb-gill-couples-choice")
    assert w7["performing_pro_slug"] == "lauren-oakley" and w7["d_partnership_kind"] == "substitute_temporary" and w7["couple_label_raw"] == "JB & Lauren"
    assert one(t22["couple_weeks"], "couple_week_key", "S22W09-jb-gill")["d_partnership_kind"] == "replacement_permanent"
    c = one(t22["couples"], "couple_key", "S22-jb-gill")
    assert c["chart_label"] == "JB & Amy/Lauren" and c["professional_display_name"] == "Amy Dowden" and c["d_pro_slugs"] == "amy-dowden|lauren-oakley|lauren-oakley"
    roster = {r["series_person_key"]: r for r in t22["series_people"]}
    assert roster["S22-lauren-oakley-professional"]["roster_status"] == "unpartnered" and roster["S22-lauren-oakley-professional"]["last_week_key"] == "S22W06"
    assert roster["S22-lauren-oakley-professional-2"]["roster_status"] == "partnered_mid_series" and roster["S22-lauren-oakley-professional-2"]["replaces_person_key"] == "amy-dowden"
    assert roster["S22-amy-dowden-professional-2"]["roster_status"] == "left_mid_series" and roster["S22-amy-dowden-professional-2"]["reason"] == "injury"
    # week 6: Dowden missed only the results show
    cw6 = one(t22["couple_weeks"], "couple_week_key", "S22W06-jb-gill")
    assert cw6["participation_status"] == "competed" and cw6["absence_scope"] == "results_show_only" and cw6["affected_party"] == "professional"


def test_samba_thon_a235(t22):
    mar = [p for p in t22["performances"] if p["performance_kind"] == "marathon"]
    assert len(mar) == 7 and all(p["dance_key"] == "samba" and p["scoring_mode"] == "rank_points" and p["group_key"] == "S22W10-P-G1" and p["running_order"] == "" for p in mar)
    assert one(t22["performances"], "performance_key", "S22W10-P-jb-gill-samba")["points_value"] == 7
    assert one(t22["couple_weeks"], "couple_week_key", "S22W10-jb-gill")["d_week_total"] == 46
    assert one(t22["couple_weeks"], "couple_week_key", "S22W10-jamie-borthwick")["result_status"] == "eliminated"
    assert one(t22["results_rounds"], "round_key", "S22R10")["exit_count"] == 1


def test_head_judge_casting_vote_a238(t22):
    r = one(t22["results_rounds"], "round_key", "S22R08")
    assert r["casting_vote_slug"] == "shirley-ballas" and r["casting_vote_source_kind"] == "inherited"
    assert r["casting_vote_used"] == "true" and r["casting_vote_inferred"] == "true"
    assert one(t22["couples"], "couple_key", "S22-shayne-ward")["exit_round_key"] == "S22R08"
    assert all(x["casting_vote_slug"] == "shirley-ballas" for x in t22["results_rounds"] if x["round_kind"] == "standard")


def test_bye_with_footnote_a236(t22):
    cw = one(t22["couple_weeks"], "couple_week_key", "S22W03-nick-knowles")
    assert cw["participation_status"] == "bye" and cw["bye_granted"] == "true" and cw["absence_reason"] == "injury"
    assert one(t22["couples"], "couple_key", "S22-nick-knowles")["exit_week_key"] == "S22W04"


def test_labels_and_music(t22):
    assert one(t22["couples"], "couple_key", "S22-punam-krishan")["chart_label"] == "Dr. Punam & Gorka"
    songs = [m for m in t22["performance_music"] if m["performance_key"] == "S22W07-P-jb-gill-couples-choice"]
    # Icons Week: the artist sits in the Icon column, so the Music cell credits no artist and the icon is the theme reference
    assert [m["song_key"].split(":")[1] for m in songs] == ["uptown-funk", "treasure", "24k-magic"] and {m["artist_key"] for m in songs} == {""}
    w7 = one(t22["performances"], "performance_key", "S22W07-P-jb-gill-couples-choice")
    assert w7["theme_reference_text"] == "Bruno Mars" and w7["theme_column_label"] == "Icon"


def test_final_and_volumes(t22):
    assert len([c for c in t22["couples"] if c["final_placement"] == 2]) == 3
    assert one(t22["results_rounds"], "round_key", "S22R13")["round_kind"] == "final_placing"
    assert len(t22["performances"]) == 148 and len(t22["judge_marks"]) == 564 and len(t22["couple_weeks"]) == 195
