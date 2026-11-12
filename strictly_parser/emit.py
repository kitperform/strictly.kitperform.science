"""Write the tidy tables as CSV with a fixed column order."""
import csv
from pathlib import Path

PROV = ["source_capture_key", "source_locator", "source_kind", "note"]
COLUMNS = {
    "series": ["series_key", "series_kind", "series_number", "parent_series_key", "label", "wiki_title", "year_start", "launch_date", "first_live_date", "final_date",
               "infobox_first_aired", "infobox_last_aired", "infobox_num_episodes", "home_venue_key", "status", "couples_count_stated", "weeks_count_stated"] + PROV,
    "format_rules": ["format_rule_key", "series_key", "week_key", "episode_key", "elimination_mechanism", "dance_off_used", "at_risk_group_size", "vote_direction",
                     "casting_vote_mode", "rank_tie_policy", "combined_tie_break", "showdance_scored", "default_scoring_judges", "default_scale_max",
                     "week_has_elimination", "field_subset"] + PROV,
    "weeks": ["week_key", "series_key", "week_number", "round_stage", "theme_key", "heading_raw", "dance_brief_raw", "lifecycle_status"] + PROV,
    "episodes": ["episode_key", "series_key", "week_key", "episode_kind", "sub_label", "sequence_in_week", "label_raw", "listed_in_ratings", "air_date", "air_date_source",
                 "original_air_date", "reschedule_reason_text", "status", "venue_key", "charity_beneficiary", "scale_max_stated", "rating_millions", "rank_bbc_one",
                 "rank_all_uk", "share_pct"] + PROV,
    "panel_seats": ["panel_seat_key", "episode_key", "week_key", "series_key", "judge_slug", "seat_position", "panel_role", "is_head_judge", "is_scoring", "replaces_slug",
                    "absence_reason", "vote_label"] + PROV,
    "results_rounds": ["round_key", "series_key", "round_kind", "label", "deciding_week_key", "decided_at_episode_key", "week_keys", "elimination_mechanism_actual",
                       "exit_count", "at_risk_group_size_actual", "dance_off_status", "vote_direction", "casting_vote_slug", "casting_vote_source_kind", "casting_vote_used",
                       "casting_vote_inferred", "votes_recorded", "votes_carried_over", "combined_reason", "d_n_scoring_seats"] + PROV,
    "results_round_weeks": ["results_round_week_key", "round_key", "week_key", "seq"],
    "people": ["person_key", "slug", "person_kind", "identity_basis", "wiki_title", "canonical_name", "given_name", "family_name", "gender"] + PROV,
    "person_aliases": ["person_alias_key", "person_key", "alias", "alias_kind", "context", "series_key"] + PROV,
    "series_people": ["series_person_key", "series_key", "person_key", "role", "roster_status", "display_name_in_series", "is_head_judge", "replaces_person_key",
                      "replaced_by_person_key", "paired_with_person_key", "reason", "reason_text", "event_date", "first_week_key", "last_week_key"] + PROV,
    "couples": ["couple_key", "series_key", "celebrity_person_key", "chart_label", "celebrity_display_name", "professional_display_name", "couple_kind", "notability_text",
                "final_placement", "place_is_shared", "place_label_raw", "exit_kind", "exit_ordinal", "exit_ordinal_is_shared", "exit_ordinal_text", "exit_week_key",
                "exit_round_key", "exit_episode_key", "exit_date", "exit_date_kind", "exit_timing", "exit_reason", "exit_affected_party", "status_raw", "couples_table_order",
                "d_pro_slugs", "d_reached_final"] + PROV,
    "couple_partnerships": ["couple_partnership_key", "couple_key", "pro_person_key", "week_from", "week_to", "partnership_kind", "reason", "reason_text"] + PROV,
    "couple_labels": ["couple_label_key", "couple_key", "label", "context", "week_from", "week_to", "is_typo"] + PROV,
    "couple_weeks": ["couple_week_key", "couple_key", "week_key", "series_key", "series_number", "week_number", "round_stage", "participation_status", "result_status",
                     "results_round_key", "at_risk", "danced_off", "bye_granted", "absence_reason", "affected_party", "absence_scope", "status_raw", "d_pro_slug",
                     "d_partnership_kind", "d_week_total", "d_is_highest_of_week", "d_is_lowest_of_week"] + PROV,
    "performances": ["performance_key", "episode_key", "week_key", "series_key", "series_number", "week_number", "round_stage", "air_date", "sequence_in_week", "performer_group",
                     "couple_key", "chart_label", "performing_pro_slug", "couple_label_raw", "sequence_in_episode", "running_order", "d_perf_seq", "group_key", "performance_kind",
                     "selection_role", "performance_status", "scoring_mode", "stated_total", "n_marks_stated", "score_cell_raw", "points_value", "dance_key", "dance_secondary_key",
                     "dance_raw", "theme_column_label", "theme_reference_text", "theme_reference_wiki_title", "music_raw", "d_total", "d_n_marks", "d_total_mismatch", "d_scale_max",
                     "d_total_40", "d_is_highest_of_week", "d_is_lowest_of_week", "d_results_round_key", "d_partnership_kind"] + PROV,
    "performance_music": ["performance_music_key", "performance_key", "seq", "song_key", "artist_key", "source_work_text", "source_work_wiki_title", "raw_text"] + PROV,
    "songs": ["song_key", "title", "wiki_title"] + PROV,
    "artists": ["artist_key", "name", "wiki_title"] + PROV,
    "judge_marks": ["judge_mark_key", "performance_key", "panel_seat_key", "judge_slug", "judge_name", "seat_position", "panel_role", "is_head_judge", "mark", "episode_key",
                    "week_key", "series_key", "series_number", "week_number", "round_stage", "air_date", "sequence_in_week", "running_order", "sequence_in_episode", "d_perf_seq",
                    "couple_key", "chart_label", "performing_pro_slug", "dance_key", "performance_kind", "scoring_mode", "d_scale_max"] + PROV,
    "dance_off_votes": ["dance_off_vote_key", "results_round_key", "series_key", "week_key", "judge_slug", "judge_label_raw", "couple_key", "vote_kind", "is_casting_vote_stated",
                        "list_position", "raw_text", "vote_direction", "casting_vote_slug", "d_is_casting_judge"] + PROV,
    "dances": ["dance_key", "name", "dance_family", "wiki_title"] + PROV,
    "themes": ["theme_key", "name", "theme_reference_kind", "is_location_theme", "wiki_title"] + PROV,
    "venues": ["venue_key", "name", "city", "wiki_title"] + PROV,
    "source_captures": ["source_capture_key", "wiki_title", "page_id", "revid", "parent_revid", "rev_timestamp", "captured_at", "sha1", "format", "file_path", "parser_version",
                        "is_current", "licence_note"],
    "discrepancies": ["discrepancy_key", "table_name", "natural_key", "field_name", "value_a", "source_capture_a_key", "locator_a", "value_b", "value_b_origin",
                      "source_capture_b_key", "locator_b", "resolution", "note"],
    "crosscheck/chart_cells": ["chart_cell_key", "source_capture_key", "chart_kind", "row_index", "col_index", "row_label_raw", "couple_key", "col_label_raw", "cell_text_raw",
                               "bgcolor_norm", "flags"],
    "crosscheck/chart_legends": ["source_capture_key", "colour_norm", "meaning_text", "scope"],
}
ALIASES = {"chart_cells": "crosscheck/chart_cells", "chart_legends": "crosscheck/chart_legends"}


def write_tables(tables, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, cols in COLUMNS.items():
        src = next((k for k, v in ALIASES.items() if v == name), name)
        rows = tables.get(src, [])
        path = out_dir / f"{name}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({c: ("" if r.get(c) is None else r.get(c, "")) for c in cols})
        written[name] = len(rows)
    return written


def write_report(report, written, out_dir: Path, series_key: str):
    lines = [f"# Build report for {series_key}", ""]
    lines += ["## Tables", "", "| table | rows |", "|---|---|"] + [f"| `{n}.csv` | {c} |" for n, c in written.items()]
    lines += ["", "## Checks", ""]
    for name, ok, detail in report["checks"]:
        lines.append(f"- {'PASS' if ok else 'FAIL'}: {name}" + (f" ({detail})" if detail else ""))
    lines += ["", "## Warnings", ""] + ([f"- {w}" for w in report["warnings"]] or ["- none"])
    lines += ["", "## Unresolved labels", ""] + ([f"- {u}" for u in report["unresolved"]] or ["- none"])
    (out_dir / "build_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines
