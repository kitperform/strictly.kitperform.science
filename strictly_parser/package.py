"""Package the per-series tidy tables into one dataset.

    python -m strictly_parser.package [--tidy data/tidy] [--out data/package] [--dist dist] [--no-dist]

Writes, from every ``data/tidy/S*/`` folder:

- ``data/package/<table>.csv`` — one CSV per table across all series (reference tables such as
  people, songs and dances deduplicated on their primary key, first series wins);
- ``data/package/datapackage.json`` — a Frictionless Data Package describing field types, primary
  and foreign keys and the documented vocabularies (``docs/data-model-v2.md`` section 11);
- ``data/package/package_report.md`` — row counts and the results of the package-level checks;
- ``dist/strictly.sqlite`` — every table as a typed SQLite table with primary keys and indexes;
- ``dist/parquet/<table>.parquet`` — one Parquet file per table (needs pyarrow);
- ``dist/strictly-csv.zip`` — the CSVs and datapackage.json zipped.

The checks (primary keys unique, every foreign key resolves, every enum value documented, every
typed column parses) are also exposed as ``check_package`` for the tests.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sqlite3
import sys
import zipfile
from collections import Counter, OrderedDict
from pathlib import Path

from .emit import COLUMNS

PACKAGE_NAME = "strictly-come-dancing-results"
TABLES = OrderedDict((name.replace("crosscheck/", ""), name) for name in COLUMNS)  # package name -> tidy path stem

# reference tables repeat across series: keep the first row per primary key
DEDUPE = {"people", "person_aliases", "songs", "artists", "dances", "themes", "venues", "source_captures", "chart_legends"}

PRIMARY_KEYS = {
    "results_round_weeks": "results_round_week_key", "performance_music": "performance_music_key", "people": "person_key", "person_aliases": "person_alias_key",
    "results_rounds": "round_key", "chart_legends": None, "source_captures": "source_capture_key", "discrepancies": "discrepancy_key", "chart_cells": "chart_cell_key",
}

BOOLEAN_COLS = {"at_risk", "danced_off", "bye_granted", "place_is_shared", "exit_ordinal_is_shared", "d_reached_final", "listed_in_ratings", "dance_off_used",
                "week_has_elimination", "casting_vote_used", "casting_vote_inferred", "votes_recorded", "votes_carried_over", "is_typo",
                "is_location_theme", "is_current", "d_total_mismatch", "is_casting_vote_stated", "d_is_casting_judge", "is_head_judge", "is_scoring"}
INTEGER_COLS = {"series_number", "week_number", "seat_position", "sequence_in_week", "sequence_in_episode", "running_order", "d_perf_seq", "stated_total", "n_marks_stated",
                "points_value", "d_total", "d_n_marks", "d_scale_max", "mark", "exit_ordinal", "final_placement", "couples_table_order", "week_from", "week_to", "exit_count",
                "at_risk_group_size", "at_risk_group_size_actual", "default_scoring_judges", "default_scale_max", "d_n_scoring_seats", "seq", "row_index", "col_index",
                "list_position", "page_id", "revid", "parent_revid", "infobox_num_episodes", "couples_count_stated", "weeks_count_stated", "year_start", "d_week_total",
                "scale_max_stated", "rank_bbc_one", "rank_all_uk"}
NUMBER_COLS = {"rating_millions", "share_pct", "d_total_40"}
DATE_COLS = {"launch_date", "first_live_date", "final_date", "infobox_first_aired", "infobox_last_aired", "air_date", "original_air_date", "exit_date", "event_date"}
DATETIME_COLS = {"rev_timestamp", "captured_at"}

# documented vocabularies (docs/data-model-v2.md section 11); observed values are unioned in and any undocumented value is reported
ENUMS = {
    "source_kind": ["stated", "inferred", "inherited", "editorial", "disputed"],
    "performance_kind": ["individual", "fusion", "showdance", "group_scored", "group_points", "group_unscored", "marathon", "instant"],
    "scoring_mode": ["judge_marks", "judge_total_only", "rank_points", "awarded_points", "unscored", "not_performed", "pending"],
    "performance_status": ["performed", "performed_partial", "not_performed", "scheduled"],
    "selection_role": ["unlearned", "prescribed", "repeat_favourite", "repeat_favourite_ballroom", "repeat_favourite_latin", "repeat_highest_ballroom", "repeat_highest_latin",
                       "repeat_highest", "repeat_judges_choice", "repeat_rechoreographed", "same_song", "showdance", "marathon", "instant", "group", "unknown"],
    "performer_group": ["couple", "pro_group", "troupe"],
    "result_status": ["safe", "bottom_two", "bottom_three", "eliminated", "withdrew", "carried_forward", "no_elimination", "exempt", "winner", "runner_up", "third", "fourth",
                      "pending", "not_applicable"],
    "participation_status": ["competed", "competed_unscored", "group_only", "not_scheduled", "bye", "absent_withdrawn", "exited", "pending"],
    "exit_kind": ["eliminated", "withdrew", "finalist", "in_competition"],
    "exit_date_kind": ["results_episode", "performance_episode", "combined_episode", "announcement", "unknown"],
    "exit_timing": ["before_live_show", "during_live_show_before_dancing", "after_dancing_before_results", "during_results_show", "between_final_shows", "before_final"],
    "exit_affected_party": ["celebrity", "professional", "both"],
    "affected_party": ["celebrity", "professional", "both"],
    "absence_scope": ["whole_week", "performance_only", "results_show_only"],
    "partnership_kind": ["original", "substitute_temporary", "replacement_permanent", "replacement_pre_week1", "pre_series_only"],
    "d_partnership_kind": ["original", "substitute_temporary", "replacement_permanent", "replacement_pre_week1", "pre_series_only"],
    "person_kind": ["person", "act"],
    "roster_status": ["competed", "unpartnered", "troupe_only", "partnered_mid_series", "left_mid_series", "withdrew_pre_launch", "paired_withdrew_pre_week1",
                      "departed_pre_series", "moved_to_other_role", "regular", "guest", "substitute"],
    "elimination_mechanism": ["ranking_points_no_dance_off", "ranking_points_dance_off", "lowest_public_vote", "lowest_combined_points_stated", "public_vote_final_placing",
                              "none", "special_single_show"],
    "elimination_mechanism_actual": ["ranking_points_no_dance_off", "ranking_points_dance_off", "lowest_public_vote", "lowest_combined_points_stated",
                                     "public_vote_final_placing", "none", "special_single_show"],
    "dance_off_status": ["held", "not_in_format", "not_held_by_format", "cancelled_injury", "cancelled_withdrawal", "cancelled_scoring_error", "not_applicable"],
    "vote_direction": ["save", "eliminate"],
    "casting_vote_mode": ["none", "head_judge", "rotating"],
    "resolution": ["prefer_a", "prefer_b", "both_kept_unresolved"],
    "showdance_scored": ["yes", "no", "disputed"],
}
# columns whose vocabulary is documented only by the data (constraint = observed values)
OBSERVED_ENUM_COLS = {"episode_kind", "panel_role", "round_kind", "round_stage", "lifecycle_status", "status", "couple_kind", "theme_reference_kind", "alias_kind",
                      "vote_kind", "role", "series_kind", "air_date_source", "value_b_origin", "chart_kind", "scope", "casting_vote_source_kind", "field_subset",
                      "rank_tie_policy", "combined_tie_break", "identity_basis", "context", "exit_affected_party"}

# foreign keys: column -> (table, column); applied wherever the column occurs, except where noted
FOREIGN_KEYS = {
    "series_key": ("series", "series_key"), "parent_series_key": ("series", "series_key"),
    "week_key": ("weeks", "week_key"), "deciding_week_key": ("weeks", "week_key"), "exit_week_key": ("weeks", "week_key"), "first_week_key": ("weeks", "week_key"),
    "last_week_key": ("weeks", "week_key"),
    "episode_key": ("episodes", "episode_key"), "decided_at_episode_key": ("episodes", "episode_key"), "exit_episode_key": ("episodes", "episode_key"),
    "couple_key": ("couples", "couple_key"), "performance_key": ("performances", "performance_key"), "panel_seat_key": ("panel_seats", "panel_seat_key"),
    "results_round_key": ("results_rounds", "round_key"), "round_key": ("results_rounds", "round_key"), "exit_round_key": ("results_rounds", "round_key"),
    "d_results_round_key": ("results_rounds", "round_key"),
    "judge_slug": ("people", "person_key"), "person_key": ("people", "person_key"), "celebrity_person_key": ("people", "person_key"), "pro_person_key": ("people", "person_key"),
    "performing_pro_slug": ("people", "person_key"), "d_pro_slug": ("people", "person_key"), "replaces_slug": ("people", "person_key"), "casting_vote_slug": ("people", "person_key"),
    "replaces_person_key": ("people", "person_key"), "replaced_by_person_key": ("people", "person_key"), "paired_with_person_key": ("people", "person_key"),
    "dance_key": ("dances", "dance_key"), "dance_secondary_key": ("dances", "dance_key"), "song_key": ("songs", "song_key"), "artist_key": ("artists", "artist_key"),
    "theme_key": ("themes", "theme_key"), "venue_key": ("venues", "venue_key"), "home_venue_key": ("venues", "venue_key"),
    "source_capture_key": ("source_captures", "source_capture_key"), "source_capture_a_key": ("source_captures", "source_capture_key"),
    "source_capture_b_key": ("source_captures", "source_capture_key"),
}
NO_SELF_FK = {("results_rounds", "round_key"), ("performances", "performance_key"), ("panel_seats", "panel_seat_key"), ("couples", "couple_key"), ("weeks", "week_key"),
              ("episodes", "episode_key"), ("series", "series_key"), ("people", "person_key"), ("dances", "dance_key"), ("songs", "song_key"), ("artists", "artist_key"),
              ("themes", "theme_key"), ("venues", "venue_key"), ("source_captures", "source_capture_key")}


def primary_key(table):
    if table in PRIMARY_KEYS:
        return PRIMARY_KEYS[table]
    return COLUMNS[TABLES[table]][0]


def field_type(col):
    if col in BOOLEAN_COLS or col.startswith("is_") or col.startswith("d_is_"):
        return "boolean"
    if col in INTEGER_COLS:
        return "integer"
    if col in NUMBER_COLS:
        return "number"
    if col in DATE_COLS:
        return "date"
    if col in DATETIME_COLS:
        return "datetime"
    return "string"


def parses(value, ftype):
    try:
        if ftype == "boolean":
            return value in ("true", "false")
        if ftype == "integer":
            int(value)
        elif ftype == "number":
            float(value)
        elif ftype == "date":
            dt.date.fromisoformat(value)
        elif ftype == "datetime":
            dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def read_tidy(tidy_dir: Path):
    """{table: [rows]} across every series folder, in series order, reference tables deduplicated."""
    series_dirs = sorted(p for p in tidy_dir.iterdir() if p.is_dir() and re.fullmatch(r"S\d+", p.name))
    tables, dupes = {}, Counter()
    for table, stem in TABLES.items():
        rows, seen = [], set()
        pk = primary_key(table)
        for sd in series_dirs:
            path = sd / f"{stem}.csv"
            if not path.exists():
                continue
            with path.open(newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    if table in DEDUPE:
                        key = r[pk] if pk else tuple(r.values())
                        if key in seen:
                            dupes[table] += 1
                            continue
                        seen.add(key)
                    rows.append(r)
        tables[table] = rows
    return tables, dupes, series_dirs


def check_package(tables):
    """Primary keys unique, foreign keys resolve, enum values documented, typed columns parse. Returns a list of problem strings."""
    problems = []
    for table, rows in tables.items():
        pk = primary_key(table)
        if pk:
            c = Counter(r[pk] for r in rows)
            d = [k for k, v in c.items() if v > 1]
            if d:
                problems.append(f"{table}: {len(d)} duplicate primary keys, e.g. {d[:3]}")
        cols = COLUMNS[TABLES[table]]
        for col in cols:
            ftype = field_type(col)
            if ftype != "string":
                bad = [r[col] for r in rows if r[col] != "" and not parses(r[col], ftype)]
                if bad:
                    problems.append(f"{table}.{col}: {len(bad)} values are not {ftype}, e.g. {bad[:3]}")
            if col in ENUMS:
                extra = sorted({r[col] for r in rows if r[col] != ""} - set(ENUMS[col]))
                if extra:
                    problems.append(f"{table}.{col}: undocumented values {extra}")
    index = {}
    for col, (ref_table, ref_col) in FOREIGN_KEYS.items():
        if ref_table not in index:
            index[ref_table] = {r[ref_col] for r in tables.get(ref_table, [])}
    for table, rows in tables.items():
        for col in COLUMNS[TABLES[table]]:
            if col in FOREIGN_KEYS:
                ref_table, ref_col = FOREIGN_KEYS[col]
                if (table, col) in NO_SELF_FK and table == ref_table:
                    continue
                missing = sorted({r[col] for r in rows if r[col] != "" and r[col] not in index[ref_table]})
                if missing:
                    problems.append(f"{table}.{col} -> {ref_table}.{ref_col}: {len(missing)} unresolved, e.g. {missing[:3]}")
    return problems


def resource_schema(table, rows):
    cols = COLUMNS[TABLES[table]]
    fields = []
    for col in cols:
        f = {"name": col, "type": field_type(col)}
        if f["type"] == "boolean":
            f["trueValues"], f["falseValues"] = ["true"], ["false"]
        if f["type"] == "datetime":
            f["format"] = "any"
        observed = sorted({r[col] for r in rows if r[col] != ""})
        if col in ENUMS:
            f["constraints"] = {"enum": sorted(set(ENUMS[col]) | set(observed))}
        elif col in OBSERVED_ENUM_COLS and 0 < len(observed) <= 40:
            f["constraints"] = {"enum": observed}
        if col == primary_key(table):
            f.setdefault("constraints", {})["required"] = True
            f["constraints"]["unique"] = True
        fields.append(f)
    schema = {"fields": fields, "missingValues": [""]}
    pk = primary_key(table)
    if pk:
        schema["primaryKey"] = pk
    fks = []
    for col in cols:
        if col in FOREIGN_KEYS:
            ref_table, ref_col = FOREIGN_KEYS[col]
            if (table, col) in NO_SELF_FK and table == ref_table:
                continue
            fks.append({"fields": col, "reference": {"resource": ref_table, "fields": ref_col}})
    if fks:
        schema["foreignKeys"] = fks
    return schema


def datapackage(tables, series_dirs, version):
    captures = tables.get("source_captures", [])
    sources = [{"title": c["wiki_title"], "path": f"https://en.wikipedia.org/w/index.php?title={c['wiki_title'].replace(' ', '_')}&oldid={c['revid']}",
                "revid": c["revid"], "captured_at": c["captured_at"]} for c in captures]
    resources = []
    for table, rows in tables.items():
        resources.append({
            "name": table, "path": f"{table}.csv", "profile": "tabular-data-resource", "format": "csv", "mediatype": "text/csv", "encoding": "utf-8",
            "dialect": {"delimiter": ",", "header": True, "quoteChar": '"'}, "rowCount": len(rows), "schema": resource_schema(table, rows)})
    return {
        "profile": "tabular-data-package", "name": PACKAGE_NAME, "title": "Strictly Come Dancing results, series 1 to 24",
        "description": "Every scored routine, judge mark, results round, couple-week and roster row from the Wikipedia series pages of Strictly Come Dancing, "
                       "as flat tables with provenance (source capture, locator and source kind) on every row. Data model: docs/data-model-v2.md.",
        "version": version, "created": max((c["captured_at"] for c in captures), default=""),  # latest capture, so a rebuild without new data is a no-op in git
        "homepage": "https://strictly.kitperform.science", "keywords": ["strictly come dancing", "bbc", "dance", "television", "scores", "judges"],
        "licenses": [{"name": "CC-BY-SA-4.0", "title": "Creative Commons Attribution-ShareAlike 4.0", "path": "https://creativecommons.org/licenses/by-sa/4.0/"}],
        "contributors": [{"title": "Kit Perform", "role": "author", "path": "https://kitperform.science"}],
        "series": [d.name for d in series_dirs], "sources": sources, "resources": resources,
    }


def write_csvs(tables, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for table, rows in tables.items():
        cols = COLUMNS[TABLES[table]]
        with (out_dir / f"{table}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)


SQL_TYPES = {"boolean": "INTEGER", "integer": "INTEGER", "number": "REAL", "date": "TEXT", "datetime": "TEXT", "string": "TEXT"}


def to_sql(value, ftype):
    if value == "":
        return None
    if ftype == "boolean":
        return 1 if value == "true" else 0
    if ftype == "integer":
        return int(value)
    if ftype == "number":
        return float(value)
    return value


def write_sqlite(tables, path: Path):
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    for table, rows in tables.items():
        cols = COLUMNS[TABLES[table]]
        pk = primary_key(table)
        defs = [f'"{c}" {SQL_TYPES[field_type(c)]}' + (" PRIMARY KEY" if c == pk else "") for c in cols]
        con.execute(f'CREATE TABLE "{table}" ({", ".join(defs)})')
        types = [field_type(c) for c in cols]
        con.executemany(f'INSERT INTO "{table}" VALUES ({", ".join("?" * len(cols))})', ([to_sql(r[c], t) for c, t in zip(cols, types)] for r in rows))
        for c in cols:
            if c in FOREIGN_KEYS and c != pk:
                con.execute(f'CREATE INDEX "ix_{table}_{c}" ON "{table}" ("{c}")')
    con.execute("CREATE TABLE package_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO package_meta VALUES (?, ?)", [("name", PACKAGE_NAME), ("built_at", dt.datetime.now(dt.timezone.utc).isoformat())])
    con.commit()
    con.close()


def write_parquet(tables, out_dir: Path):
    try:
        import pandas as pd
        import pyarrow  # noqa: F401
    except ImportError:
        return False
    out_dir.mkdir(parents=True, exist_ok=True)
    for table, rows in tables.items():
        cols = COLUMNS[TABLES[table]]
        df = pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)
        for c in cols:
            t = field_type(c)
            s = df[c].replace("", None) if len(df) else df[c]
            if t == "boolean":
                df[c] = s.map({"true": True, "false": False}).astype("boolean")
            elif t == "integer":
                df[c] = pd.to_numeric(s).astype("Int64")
            elif t == "number":
                df[c] = pd.to_numeric(s).astype("float64")
            elif t in ("date", "datetime"):
                df[c] = pd.to_datetime(s, utc=(t == "datetime"))
            else:
                df[c] = s.astype("string")
        df.to_parquet(out_dir / f"{table}.parquet", index=False)
    return True


def write_report(tables, dupes, problems, out_dir: Path, dist_dir, parquet_ok, version):
    lines = [f"# Package report ({version})", "", "| table | rows | deduplicated |", "|---|---|---|"]
    lines += [f"| `{t}.csv` | {len(r)} | {dupes.get(t, '')} |" for t, r in tables.items()]
    lines += ["", "## Checks", ""] + ([f"- FAIL: {p}" for p in problems] or ["- PASS: primary keys unique, foreign keys resolve, enum values documented, typed columns parse"])
    lines += ["", "## Distribution files", ""]
    if dist_dir:
        lines += [f"- `{dist_dir}/strictly.sqlite`", f"- `{dist_dir}/strictly-csv.zip`", f"- `{dist_dir}/parquet/*.parquet`" if parquet_ok else "- Parquet skipped (pyarrow not installed)"]
    else:
        lines += ["- not built (--no-dist)"]
    (out_dir / "package_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


def build(tidy_dir: Path, out_dir: Path, dist_dir, version=None):
    tables, dupes, series_dirs = read_tidy(tidy_dir)
    version = version or dt.date.today().strftime("%Y.%m.%d")
    problems = check_package(tables)
    write_csvs(tables, out_dir)
    dp = datapackage(tables, series_dirs, version)
    (out_dir / "datapackage.json").write_text(json.dumps(dp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    parquet_ok = False
    if dist_dir:
        dist_dir.mkdir(parents=True, exist_ok=True)
        write_sqlite(tables, dist_dir / "strictly.sqlite")
        parquet_ok = write_parquet(tables, dist_dir / "parquet")
        with zipfile.ZipFile(dist_dir / "strictly-csv.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(out_dir.glob("*.csv")) + [out_dir / "datapackage.json"]:
                z.write(p, p.name)
    lines = write_report(tables, dupes, problems, out_dir, dist_dir, parquet_ok, version)
    return tables, problems, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    repo = Path(__file__).resolve().parent.parent
    ap.add_argument("--tidy", default=str(repo / "data" / "tidy"))
    ap.add_argument("--out", default=str(repo / "data" / "package"))
    ap.add_argument("--dist", default=str(repo / "dist"))
    ap.add_argument("--no-dist", action="store_true", help="write only the CSVs, datapackage.json and report")
    ap.add_argument("--version", default=None, help="package version (default: today's date as YYYY.MM.DD)")
    a = ap.parse_args(argv)
    tables, problems, lines = build(Path(a.tidy), Path(a.out), None if a.no_dist else Path(a.dist), a.version)
    print("\n".join(lines))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
