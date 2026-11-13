"""The packaged dataset: one table per entity across all series, with keys that hold and vocabularies that are documented."""
import csv
import sqlite3
from pathlib import Path

import pytest

from strictly_parser.package import TABLES, build, check_package, primary_key, read_tidy

REPO = Path(__file__).resolve().parent.parent
TIDY = REPO / "data" / "tidy"


@pytest.fixture(scope="module")
def pkg(tmp_path_factory):
    out = tmp_path_factory.mktemp("package")
    dist = tmp_path_factory.mktemp("dist")
    tables, problems, _ = build(TIDY, out, dist, version="test")
    return {"tables": tables, "problems": problems, "out": out, "dist": dist}


def test_package_checks_pass(pkg):
    assert pkg["problems"] == []


def test_every_table_has_a_resource_and_the_right_row_count(pkg):
    import json
    dp = json.loads((pkg["out"] / "datapackage.json").read_text())
    names = [r["name"] for r in dp["resources"]]
    assert names == list(TABLES)
    for r in dp["resources"]:
        with (pkg["out"] / r["path"]).open(newline="", encoding="utf-8") as f:
            assert sum(1 for _ in csv.DictReader(f)) == r["rowCount"] == len(pkg["tables"][r["name"]])
    assert len(dp["sources"]) == len(pkg["tables"]["source_captures"]) and dp["series"] == [f"S{n:02d}" for n in range(1, 25)]


def test_concatenation_keeps_every_series_row(pkg):
    for table in ("performances", "judge_marks", "couple_weeks", "results_rounds", "couples"):
        stem = TABLES[table]
        n = 0
        for sd in sorted(TIDY.glob("S*")):
            with (sd / f"{stem}.csv").open(newline="", encoding="utf-8") as f:
                n += sum(1 for _ in csv.DictReader(f))
        assert len(pkg["tables"][table]) == n


def test_reference_tables_deduplicated_on_key(pkg):
    for table in ("people", "songs", "artists", "dances", "themes", "venues"):
        keys = [r[primary_key(table)] for r in pkg["tables"][table]]
        assert len(keys) == len(set(keys))


def test_sqlite_matches_the_csvs(pkg):
    con = sqlite3.connect(pkg["dist"] / "strictly.sqlite")
    for table, rows in pkg["tables"].items():
        assert con.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0] == len(rows)
    assert con.execute("SELECT typeof(mark), typeof(is_head_judge), typeof(air_date) FROM judge_marks LIMIT 1").fetchone() == ("integer", "integer", "text")
    assert con.execute("SELECT count(*) FROM sqlite_master WHERE type='index' AND name='ix_judge_marks_performance_key'").fetchone()[0] == 1
    con.close()


def test_parquet_round_trips(pkg):
    pd = pytest.importorskip("pandas")
    pytest.importorskip("pyarrow")
    jm = pd.read_parquet(pkg["dist"] / "parquet" / "judge_marks.parquet")
    assert len(jm) == len(pkg["tables"]["judge_marks"]) and str(jm["mark"].dtype) == "Int64" and str(jm["is_head_judge"].dtype) == "boolean"
    assert str(jm["air_date"].dtype).startswith("datetime64")


def test_cross_series_facts(pkg):
    con = sqlite3.connect(pkg["dist"] / "strictly.sqlite")
    q = con.execute
    # Craig's first ever 10
    assert q("SELECT performance_key FROM judge_marks WHERE judge_slug='craig-revel-horwood' AND mark=10 ORDER BY series_number, d_perf_seq LIMIT 1").fetchone()[0] == "S02W08-P-jill-halfpenny-jive"
    # Craig has judged every series
    assert q("SELECT count(DISTINCT series_key) FROM series_people WHERE person_key='craig-revel-horwood' AND role='judge'").fetchone()[0] == 24
    # the only bye that turned into a withdrawal
    assert [r[0] for r in q("SELECT couple_week_key FROM couple_weeks WHERE bye_granted=1 AND result_status='withdrew'")] == ["S23W09-la-voix"]
    # same-sex couples
    assert {r[0] for r in q("SELECT couple_key FROM couples WHERE couple_kind='same_sex'")} == {"S18-nicola-adams", "S19-john-whaite"}
    # Blackpool
    assert q("SELECT count(*) FROM episodes WHERE venue_key='blackpool-tower-ballroom'").fetchone()[0] == 32
    # routines never performed are never scored
    assert q("SELECT count(*) FROM performances WHERE performance_status='not_performed' AND (stated_total IS NOT NULL OR d_total IS NOT NULL)").fetchone()[0] == 0
    con.close()


def test_check_package_catches_a_broken_foreign_key():
    tables, _, _ = read_tidy(TIDY)
    tables["judge_marks"][0]["performance_key"] = "S99W99-P-nobody-waltz"
    problems = check_package(tables)
    assert any(p.startswith("judge_marks.performance_key -> performances") for p in problems)
