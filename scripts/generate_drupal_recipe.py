"""Generate the Drupal recipe at recipes/strictly from the dataset schema.

    ./venv/bin/python scripts/generate_drupal_recipe.py [--data-path /var/www/html/data/package] [--recipe-path /var/www/html/recipes/strictly]

The schema is read from the parser (strictly_parser.emit.COLUMNS) and the package module (field types, documented
vocabularies, foreign keys), so the recipe follows the data model (docs/data-model-v2.md section 9) without a
hand-maintained copy of it:

- one node content type per fact table, with ``field_key`` (the natural key) and one field per column;
- vocabularies for dance, theme, venue and artist, and for the open-ended enumerations (participation_status,
  result_status, performance_kind, panel_role, elimination_mechanism, dance_off_status, selection_role,
  absence_reason, roster_status, exit_timing); every other enumeration is a list_string with its allowed values;
- entity references wherever the package declares a foreign key;
- one Migrate migration per table (migrate_source_csv over data/package/*.csv, keyed on the natural key, with
  migration_lookup for every reference) in the group ``strictly``, plus one per vocabulary;
- recipe.yml installing the modules, granting anonymous ``access content`` and making JSON:API read-only.

Paths inside the migrations default to the DDEV layout (repository mounted at /var/www/html).
"""
import argparse
import csv
import shutil
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from strictly_parser.emit import COLUMNS  # noqa: E402
from strictly_parser.package import ENUMS, FOREIGN_KEYS, OBSERVED_ENUM_COLS, TABLES, field_type, primary_key  # noqa: E402

VOCAB_TABLES = {"dances": "dance", "themes": "theme", "venues": "venue", "artists": "artist"}
SKIP_TABLES = {"results_round_weeks", "chart_cells", "chart_legends"}  # join table folded into results_round.field_weeks; cross-check tables stay in the data repo
# column -> vocabulary for the open-ended enumerations (several columns can share one vocabulary)
ENUM_VOCAB_COLS = {"participation_status": "participation_status", "result_status": "result_status", "performance_kind": "performance_kind", "panel_role": "panel_role",
                   "elimination_mechanism": "elimination_mechanism", "elimination_mechanism_actual": "elimination_mechanism", "dance_off_status": "dance_off_status",
                   "selection_role": "selection_role", "absence_reason": "absence_reason", "exit_reason": "absence_reason", "reason": "absence_reason",
                   "roster_status": "roster_status", "exit_timing": "exit_timing"}
# reference columns -> field name (without field_) ; target comes from FOREIGN_KEYS
REF_NAMES = {"series_key": "series", "parent_series_key": "parent_series", "week_key": "week", "deciding_week_key": "deciding_week", "exit_week_key": "exit_week",
             "first_week_key": "first_week", "last_week_key": "last_week", "episode_key": "episode", "decided_at_episode_key": "decided_at_episode",
             "exit_episode_key": "exit_episode", "couple_key": "couple", "performance_key": "performance", "panel_seat_key": "panel_seat",
             "results_round_key": "results_round", "exit_round_key": "exit_round", "d_results_round_key": "d_results_round", "judge_slug": "judge",
             "person_key": "person", "celebrity_person_key": "celebrity", "pro_person_key": "professional", "performing_pro_slug": "performing_pro",
             "d_pro_slug": "d_pro", "replaces_slug": "replaces", "casting_vote_slug": "casting_vote_judge", "replaces_person_key": "replaces",
             "replaced_by_person_key": "replaced_by", "paired_with_person_key": "paired_with", "dance_key": "dance", "dance_secondary_key": "dance_secondary",
             "song_key": "song", "artist_key": "artist", "theme_key": "theme", "venue_key": "venue", "home_venue_key": "home_venue",
             "source_capture_key": "source_capture", "source_capture_a_key": "source_capture_a", "source_capture_b_key": "source_capture_b"}
MULTI_REFS = {"d_pro_slugs": ("d_professionals", "people", "person_key"), "week_keys": ("weeks", "weeks", "week_key")}
SHORT = {"elimination_mechanism_actual": "mechanism_actual", "theme_reference_wiki_title": "theme_ref_wiki_title", "at_risk_group_size_actual": "at_risk_size_actual",
         "professional_display_name": "pro_display_name", "casting_vote_source_kind": "casting_vote_src_kind"}
BUNDLE_SCOPED = {"status", "context"}  # same column name, different vocabularies per bundle
TITLES = {  # columns joined with ' · ' for the node title; default is the natural key
    "series": ["label"], "weeks": ["series_key", "heading_raw"], "episodes": ["series_key", "label_raw"], "people": ["canonical_name"],
    "couples": ["series_key", "chart_label"], "couple_weeks": ["couple_week_key", "participation_status", "result_status"], "performances": ["week_key", "chart_label", "dance_raw"],
    "judge_marks": ["week_key", "chart_label", "dance_key", "judge_name", "mark"], "results_rounds": ["round_key", "label"], "panel_seats": ["episode_key", "judge_slug", "panel_role"],
    "series_people": ["series_key", "role", "display_name_in_series", "roster_status"], "songs": ["title"], "source_captures": ["source_capture_key"],
    "discrepancies": ["table_name", "natural_key", "field_name"], "dance_off_votes": ["results_round_key", "judge_label_raw", "couple_key"],
    "performance_music": ["performance_key", "seq"], "couple_partnerships": ["couple_key", "pro_person_key", "partnership_kind"],
    "person_aliases": ["alias", "person_key"], "format_rules": ["format_rule_key"], "couple_labels": ["couple_key", "label", "context"],
}
LABELS = {"series": "Series", "format_rules": "Format rule", "weeks": "Week", "episodes": "Episode", "panel_seats": "Panel seat", "results_rounds": "Results round",
          "people": "Person", "person_aliases": "Person alias", "series_people": "Series person", "couples": "Couple", "couple_partnerships": "Couple partnership",
          "couple_labels": "Couple label", "couple_weeks": "Couple week", "performances": "Performance", "performance_music": "Performance music", "songs": "Song",
          "judge_marks": "Judge mark", "dance_off_votes": "Dance-off vote", "source_captures": "Source capture", "discrepancies": "Discrepancy"}


def bundle_of(table):
    return {"series": "series", "people": "person", "person_aliases": "person_alias", "series_people": "series_person", "couples": "couple", "couple_weeks": "couple_week",
            "performances": "performance", "performance_music": "performance_music", "songs": "song", "judge_marks": "judge_mark", "dance_off_votes": "dance_off_vote",
            "source_captures": "source_capture", "discrepancies": "discrepancy"}.get(table, table.rstrip("s") if not table.endswith("ss") else table)


def plain(x):
    """OrderedDict -> dict (recursively) so yaml.safe_dump can represent it; dicts keep insertion order."""
    if isinstance(x, dict):
        return {k: plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    return x


def yml(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = plain(data)
    path.write_text(yaml.safe_dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")


class Recipe:
    def __init__(self, data_path, recipe_path, package_dir: Path, out_dir: Path = None):
        self.data_path, self.recipe_path, self.package_dir = data_path.rstrip("/"), recipe_path.rstrip("/"), package_dir
        self.out_dir = out_dir or REPO / "recipes" / "strictly"
        self.storages = OrderedDict()   # (entity_type, field_name) -> storage dict
        self.fields = []                # (entity_type, bundle, field_name, instance dict)
        self.observed = {}              # (table, col) -> sorted values
        self.maxlen = {}                # (table, col) -> max string length
        self.migrations = OrderedDict()
        self.vocab_terms = defaultdict(set)
        self.rows = {}
        self.colname = {}               # (bundle, field name) -> source column

    # -- data -----------------------------------------------------------------
    def load(self):
        for table in TABLES:
            path = self.package_dir / f"{table}.csv"
            with path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.rows[table] = rows
            for col in COLUMNS[TABLES[table]]:
                vals = [r[col] for r in rows if r[col] != ""]
                self.observed[(table, col)] = sorted(set(vals))
                self.maxlen[(table, col)] = max((len(v) for v in vals), default=0)
                if col in ENUM_VOCAB_COLS:
                    self.vocab_terms[ENUM_VOCAB_COLS[col]].update(vals)
        for col, vocab in ENUM_VOCAB_COLS.items():
            if col in ENUMS:
                self.vocab_terms[vocab].update(ENUMS[col])

    # -- fields -----------------------------------------------------------------
    def field_name(self, table, col):
        if col == primary_key(table):
            return "field_key"
        if col in MULTI_REFS:
            return "field_" + MULTI_REFS[col][0]
        if col in REF_NAMES and col in FOREIGN_KEYS:
            return "field_" + REF_NAMES[col]
        if col in BUNDLE_SCOPED:
            return f"field_{bundle_of(table)}_{col}"
        name = "field_" + SHORT.get(col, col)
        assert len(name) <= 32, name
        return name

    def spec(self, table, col):
        """(type, storage settings, instance settings, cardinality, migration kind, migration target)"""
        if col == primary_key(table):
            return "string", {"max_length": 255, "case_sensitive": False, "is_ascii": False}, {}, 1, "string", None
        if col in MULTI_REFS:
            _, ref_table, _ = MULTI_REFS[col]
            b = bundle_of(ref_table)
            return "entity_reference", {"target_type": "node"}, self.ref_settings("node", b), -1, "multi_ref", f"strictly_{ref_table}"
        if col in REF_NAMES and col in FOREIGN_KEYS:
            ref_table = FOREIGN_KEYS[col][0]
            if ref_table in VOCAB_TABLES:
                v = VOCAB_TABLES[ref_table]
                return "entity_reference", {"target_type": "taxonomy_term"}, self.ref_settings("taxonomy_term", v), 1, "ref", f"strictly_term_{v}"
            return "entity_reference", {"target_type": "node"}, self.ref_settings("node", bundle_of(ref_table)), 1, "ref", f"strictly_{ref_table}"
        if col in ENUM_VOCAB_COLS:
            v = ENUM_VOCAB_COLS[col]
            return "entity_reference", {"target_type": "taxonomy_term"}, self.ref_settings("taxonomy_term", v), 1, "ref", f"strictly_term_{v}"
        ft = field_type(col)
        if ft == "boolean":
            return "boolean", {}, {"on_label": "Yes", "off_label": "No"}, 1, "boolean", None
        if ft == "integer":
            return "integer", {"unsigned": False, "size": "normal"}, {"min": None, "max": None, "prefix": "", "suffix": ""}, 1, "scalar", None
        if ft == "number":
            return "float", {}, {"min": None, "max": None, "prefix": "", "suffix": ""}, 1, "scalar", None
        if ft == "date":
            return "datetime", {"datetime_type": "date"}, {}, 1, "scalar", None
        if ft == "datetime":
            return "datetime", {"datetime_type": "datetime"}, {}, 1, "datetime", None
        if col in ENUMS or col in OBSERVED_ENUM_COLS:
            return "list_string", {"allowed_values": [], "allowed_values_function": ""}, {}, 1, "scalar", None
        if self.maxlen[(table, col)] > 200 or col in ("note", "reason_text", "source_locator", "raw_text", "music_raw", "heading_raw", "dance_brief_raw", "value_a", "value_b"):
            return "string_long", {"case_sensitive": False}, {}, 1, "string", None
        return "string", {"max_length": 255, "case_sensitive": False, "is_ascii": False}, {}, 1, "string", None

    @staticmethod
    def ref_settings(target_type, bundle):
        return {"handler": f"default:{target_type}", "handler_settings": {"target_bundles": {bundle: bundle}, "sort": {"field": "_none", "direction": "ASC"}, "auto_create": False}}

    def add_field(self, entity_type, bundle, name, ftype, storage_settings, inst_settings, cardinality, label, allowed=None, required=False):
        module = {"list_string": "options", "datetime": "datetime", "entity_reference": "core"}.get(ftype, "core")
        key = (entity_type, name)
        if key in self.storages:
            st = self.storages[key]
            assert st["type"] == ftype and st["cardinality"] == cardinality, (key, st["type"], ftype)
            if ftype == "entity_reference":
                assert st["settings"] == storage_settings, key
            if ftype == "list_string" and allowed:
                have = {a["value"] for a in st["settings"]["allowed_values"]}
                st["settings"]["allowed_values"] += [{"value": v, "label": v} for v in allowed if v not in have]
        else:
            mods = {entity_type if entity_type == "node" else "taxonomy", *([module] if module != "core" else [])}
            if ftype == "entity_reference":
                mods.add("taxonomy" if storage_settings["target_type"] == "taxonomy_term" else "node")
            deps = {"module": sorted(mods)}
            self.storages[key] = {"langcode": "en", "status": True, "dependencies": deps, "id": f"{entity_type}.{name}", "field_name": name, "entity_type": entity_type,
                                  "type": ftype, "settings": dict(storage_settings, **({"allowed_values": [{"value": v, "label": v} for v in (allowed or [])]} if ftype == "list_string" else {})),
                                  "module": module, "locked": False, "cardinality": cardinality, "translatable": True, "indexes": {}, "persist_with_no_fields": False, "custom_storage": False}
        bundle_cfg = f"node.type.{bundle}" if entity_type == "node" else f"taxonomy.vocabulary.{bundle}"
        cfg_deps = [f"field.storage.{entity_type}.{name}", bundle_cfg]
        if ftype == "entity_reference":
            tb = next(iter(inst_settings["handler_settings"]["target_bundles"]))
            cfg_deps.append(f"node.type.{tb}" if storage_settings["target_type"] == "node" else f"taxonomy.vocabulary.{tb}")
        mod_deps = [module] if module != "core" else []
        self.fields.append((entity_type, bundle, name, {
            "langcode": "en", "status": True, "dependencies": {"config": sorted(set(cfg_deps)), **({"module": mod_deps} if mod_deps else {})},
            "id": f"{entity_type}.{bundle}.{name}", "field_name": name, "entity_type": entity_type, "bundle": bundle, "label": label, "description": "",
            "required": required, "translatable": False, "default_value": [], "default_value_callback": "", "settings": inst_settings, "field_type": ftype}))

    # -- build -----------------------------------------------------------------
    def build(self):
        self.load()
        out = self.out_dir
        if out.exists():
            shutil.rmtree(out)
        cfg = out / "config"
        # vocabularies
        vocabs = list(VOCAB_TABLES.values()) + sorted(set(ENUM_VOCAB_COLS.values()))
        for v in vocabs:
            yml(cfg / f"taxonomy.vocabulary.{v}.yml", {"langcode": "en", "status": True, "dependencies": {}, "name": v.replace("_", " ").capitalize(), "vid": v,
                                                       "description": "Generated from the Strictly dataset (scripts/generate_drupal_recipe.py).", "weight": 0, "new_revision": False})
            self.add_field("taxonomy_term", v, "field_key", "string", {"max_length": 255, "case_sensitive": False, "is_ascii": False}, {}, 1, "Key", required=True)
        term_extra = {"dance": [("dance_family", "string"), ("wiki_title", "string")], "theme": [("theme_reference_kind", "string"), ("is_location_theme", "boolean"), ("wiki_title", "string")],
                      "venue": [("city", "string"), ("wiki_title", "string")], "artist": [("wiki_title", "string")]}
        for v, extras in term_extra.items():
            for col, ft in extras:
                if ft == "boolean":
                    self.add_field("taxonomy_term", v, f"field_{col}", "boolean", {}, {"on_label": "Yes", "off_label": "No"}, 1, col.replace("_", " ").capitalize())
                else:
                    self.add_field("taxonomy_term", v, f"field_{col}", "string", {"max_length": 255, "case_sensitive": False, "is_ascii": False}, {}, 1, col.replace("_", " ").capitalize())
        # term migrations
        lookups = out / "lookups"
        lookups.mkdir(parents=True)
        for v in sorted(set(ENUM_VOCAB_COLS.values())):
            with (lookups / f"{v}.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["key", "name"])
                for code in sorted(self.vocab_terms[v]):
                    w.writerow([code, code.replace("_", " ")])
            self.migrations[f"strictly_term_{v}"] = self.migration(f"strictly_term_{v}", f"Terms: {v}", f"{self.recipe_path}/lookups/{v}.csv", ["key"],
                                                                 {"name": "name", "vid": "constants/vid", "field_key": "key"}, {"plugin": "entity:taxonomy_term", "default_bundle": v}, [], {"vid": v})
        for table, v in VOCAB_TABLES.items():
            pk = primary_key(table)
            process = {"name": "name", "vid": "constants/vid", "field_key": pk}
            for col, ft in term_extra[v]:
                process[f"field_{col}"] = [{"plugin": "skip_on_empty", "method": "process", "source": col}, {"plugin": "static_map", "map": {"true": 1, "false": 0}}] if ft == "boolean" else col
            self.migrations[f"strictly_term_{v}"] = self.migration(f"strictly_term_{v}", f"Terms: {v}", f"{self.data_path}/{table}.csv", [pk], process,
                                                                 {"plugin": "entity:taxonomy_term", "default_bundle": v}, [], {"vid": v})
        # node types, fields, migrations
        for table in TABLES:
            if table in SKIP_TABLES or table in VOCAB_TABLES:
                continue
            bundle, pk = bundle_of(table), primary_key(table)
            yml(cfg / f"node.type.{bundle}.yml", {"langcode": "en", "status": True, "dependencies": {}, "name": LABELS[table], "type": bundle,
                                                  "description": f"One row of {table}.csv in the Strictly dataset (docs/data-model-v2.md).", "help": None, "new_revision": True,
                                                  "preview_mode": 0, "display_submitted": False})
            process, deps = {}, set()
            cols = list(COLUMNS[TABLES[table]])
            if table == "results_rounds":
                cols.append("week_keys") if "week_keys" not in cols else None
            for col in cols:
                if col == "week_keys" and table != "results_rounds":
                    continue
                if col == "week_keys":
                    name, (ftype, st, inst, card, kind, target) = "field_weeks", self.spec(table, "week_keys")
                else:
                    name, (ftype, st, inst, card, kind, target) = self.field_name(table, col), self.spec(table, col)
                allowed = None
                if ftype == "list_string":
                    allowed = sorted(set(ENUMS.get(col, [])) | set(self.observed[(table, col)]))
                self.add_field("node", bundle, name, ftype, st, inst, card, "Key" if name == "field_key" else name[6:].replace("_", " ").capitalize(), allowed, required=(name == "field_key"))
                self.colname[(bundle, name)] = col
                process[name] = self.process_for(kind, col, target)
                if target and target != f"strictly_{table}":
                    deps.add(target)
                if table == "judge_marks" and col == "judge_slug":
                    self.add_field("node", bundle, "field_d_judge_slug", "string", {"max_length": 255, "case_sensitive": False, "is_ascii": False}, {}, 1, "Judge slug (derived)")
                    process["field_d_judge_slug"] = col
                    self.colname[(bundle, "field_d_judge_slug")] = "d_judge_slug"
            title_cols = [c for c in TITLES.get(table, [pk]) if c in COLUMNS[TABLES[table]]] or [pk]
            process = {"title": [{"plugin": "concat", "source": title_cols, "delimiter": " · "}, {"plugin": "substr", "start": 0, "length": 250}],
                       "uid": "constants/uid", "status": "constants/status", **process}
            self.migrations[f"strictly_{table}"] = self.migration(f"strictly_{table}", LABELS[table] + "s", f"{self.data_path}/{table}.csv", [pk], process,
                                                                {"plugin": "entity:node", "default_bundle": bundle}, sorted(deps), {"uid": 1, "status": 1})
        # write config
        for (et, name), st in self.storages.items():
            yml(cfg / f"field.storage.{et}.{name}.yml", st)
        for et, bundle, name, inst in self.fields:
            yml(cfg / f"field.field.{et}.{bundle}.{name}.yml", inst)
        yml(cfg / "migrate_plus.migration_group.strictly.yml", {"langcode": "en", "status": True, "dependencies": {}, "id": "strictly", "label": "Strictly Come Dancing dataset",
                                                                "description": "CSV tables from data/package, keyed on natural keys; re-run with --update after each dataset rebuild.",
                                                                "source_type": "CSV (strictly.kitperform.science dataset)", "module": None, "shared_configuration": None})
        for mid, m in self.migrations.items():
            yml(cfg / f"migrate_plus.migration.{mid}.yml", m)
        yml(cfg / "jsonapi.settings.yml", {"read_only": True, "maintenance_header_retry_seconds": {"min": 5, "max": 10}})
        self.presentation(cfg, [t for t in TABLES if t not in SKIP_TABLES and t not in VOCAB_TABLES])
        yml(out / "recipe.yml", {
            "name": "Strictly Come Dancing results", "description": "Content types, vocabularies and Migrate migrations for the strictly.kitperform.science dataset "
                                                                   "(every judge mark, performance, results round and roster row from series 1 onwards).",
            "type": "Site",
            "recipes": ["core/recipes/core_recommended_admin_theme", "core/recipes/core_recommended_front_end_theme", "core/recipes/administrator_role"],
            "install": ["node", "taxonomy", "field", "text", "options", "datetime", "serialization", "jsonapi", "views", "migrate", "migrate_plus", "migrate_tools", "migrate_source_csv",
                        "block", "toolbar", "field_ui", "views_ui", "config", "rest", "csv_serialization", "views_data_export"],
            "config": {"strict": False,  # re-applying on a site that already has the recipe leaves existing config alone and adds what is new
                       "import": {"node": ["views.view.content"], "taxonomy": ["views.view.taxonomy_term"], "user": ["views.view.user_admin_people"]},
                       "actions": {"user.role.anonymous": {"grantPermissions": ["access content"]}, "user.role.authenticated": {"grantPermissions": ["access content"]},
                                   "node.settings": {"simpleConfigUpdate": {"use_admin_theme": True}},
                                   "system.site": {"simpleConfigUpdate": {"page.front": "/data"}}}}})
        (out / "composer.json").write_text(yaml_to_json({
            "name": "kitperform/strictly_recipe", "description": "Drupal recipe for the Strictly Come Dancing results dataset", "type": "drupal-recipe", "license": "GPL-2.0-or-later",
            "require": {"drupal/core": "^11.2", "drupal/migrate_plus": "^6", "drupal/migrate_tools": "^6", "drupal/migrate_source_csv": "^3", "drupal/views_data_export": "^1.10", "drupal/csv_serialization": "^4"}}), encoding="utf-8")
        (out / "README.md").write_text(readme(self), encoding="utf-8")
        return out

    # -- presentation: displays, table views, landing page ------------------------------
    PROV_COLS = ("source_capture_key", "source_locator", "source_kind", "note")

    def bundle_fields(self, entity_type, bundle):
        """[(name, ftype, storage settings, label, source column)] in column order."""
        out = []
        for et, b, name, inst in self.fields:
            if et == entity_type and b == bundle:
                out.append((name, inst["field_type"], self.storages[(et, name)]["settings"], inst["label"], self.colname.get((b, name), name[6:])))
        return out

    @staticmethod
    def formatter(ftype, storage_settings, link=True):
        """(formatter plugin, settings, providing module or None)"""
        if ftype == "string":
            return "string", {"link_to_entity": False}, None
        if ftype == "string_long":
            return "basic_string", {}, None
        if ftype == "integer":
            return "number_integer", {"thousand_separator": "", "prefix_suffix": True}, None
        if ftype == "float":
            return "number_decimal", {"thousand_separator": "", "decimal_separator": ".", "scale": 2, "prefix_suffix": True}, None
        if ftype == "boolean":
            return "boolean", {"format": "default", "format_custom_false": "", "format_custom_true": ""}, None
        if ftype == "datetime":
            return "datetime_default", {"timezone_override": "", "format_type": "html_date" if storage_settings.get("datetime_type") == "date" else "medium"}, "datetime"
        if ftype == "list_string":
            return "list_default", {}, "options"
        if ftype == "entity_reference":
            return "entity_reference_label", {"link": link}, None
        raise ValueError(ftype)

    @staticmethod
    def widget(ftype):
        return {"string": ("string_textfield", {"size": 60, "placeholder": ""}, None), "string_long": ("string_textarea", {"rows": 5, "placeholder": ""}, None),
                "integer": ("number", {"placeholder": ""}, None), "float": ("number", {"placeholder": ""}, None),
                "boolean": ("boolean_checkbox", {"display_label": True}, None), "datetime": ("datetime_default", {}, "datetime"),
                "list_string": ("options_select", {}, "options"),
                "entity_reference": ("entity_reference_autocomplete", {"match_operator": "CONTAINS", "match_limit": 10, "size": 60, "placeholder": ""}, None)}[ftype]

    def displays(self, cfg, entity_type, bundle):
        """core.entity_view_display + core.entity_form_display for one bundle: every field visible, in column order."""
        fields = self.bundle_fields(entity_type, bundle)
        bundle_cfg = f"node.type.{bundle}" if entity_type == "node" else f"taxonomy.vocabulary.{bundle}"
        deps = sorted([f"field.field.{entity_type}.{bundle}.{n}" for n, *_ in fields] + [bundle_cfg])
        content, mods = {}, set()
        for i, (name, ftype, st, label, col) in enumerate(fields):
            plugin, settings, mod = self.formatter(ftype, st)
            content[name] = {"type": plugin, "label": "inline", "settings": settings, "third_party_settings": {}, "weight": i, "region": "content"}
            mods.add(mod) if mod else None
        hidden = {"links": True} if entity_type == "node" else {}
        if entity_type == "taxonomy_term":
            content["description"] = {"type": "text_default", "label": "hidden", "settings": {}, "third_party_settings": {}, "weight": -1, "region": "content"}
            mods.add("text")
        yml(cfg / f"core.entity_view_display.{entity_type}.{bundle}.default.yml",
            {"langcode": "en", "status": True, "dependencies": {"config": deps, **({"module": sorted(mods)} if mods else {})}, "id": f"{entity_type}.{bundle}.default",
             "targetEntityType": entity_type, "bundle": bundle, "mode": "default", "content": content, "hidden": hidden})
        form, mods = {}, set()
        for i, (name, ftype, st, label, col) in enumerate(fields):
            plugin, settings, mod = self.widget(ftype)
            form[name] = {"type": plugin, "weight": i, "region": "content", "settings": settings, "third_party_settings": {}}
            mods.add(mod) if mod else None
        if entity_type == "node":
            form["title"] = {"type": "string_textfield", "weight": -5, "region": "content", "settings": {"size": 60, "placeholder": ""}, "third_party_settings": {}}
            form["status"] = {"type": "boolean_checkbox", "weight": 200, "region": "content", "settings": {"display_label": True}, "third_party_settings": {}}
            hidden = {"created": True, "promote": True, "sticky": True, "uid": True}
        else:
            form["name"] = {"type": "string_textfield", "weight": -5, "region": "content", "settings": {"size": 60, "placeholder": ""}, "third_party_settings": {}}
            form["description"] = {"type": "text_textarea", "weight": -4, "region": "content", "settings": {"rows": 5, "placeholder": ""}, "third_party_settings": {}}
            form["status"] = {"type": "boolean_checkbox", "weight": 200, "region": "content", "settings": {"display_label": True}, "third_party_settings": {}}
            hidden = {"path": True}
            mods.add("text")
        yml(cfg / f"core.entity_form_display.{entity_type}.{bundle}.default.yml",
            {"langcode": "en", "status": True, "dependencies": {"config": deps, **({"module": sorted(mods)} if mods else {})}, "id": f"{entity_type}.{bundle}.default",
             "targetEntityType": entity_type, "bundle": bundle, "mode": "default", "content": form, "hidden": hidden})

    # views ----------------------------------------------------------------------
    @staticmethod
    def expose(identifier, label, op_id):
        return {"operator_id": op_id, "label": label, "description": "", "use_operator": False, "operator": op_id, "operator_limit_selection": False, "operator_list": {},
                "identifier": identifier, "required": False, "remember": False, "multiple": False, "remember_roles": {"authenticated": "authenticated"}, "reduce": False}

    @staticmethod
    def group_info():
        return {"label": "", "description": "", "identifier": "", "optional": True, "widget": "select", "multiple": False, "remember": False, "default_group": "All", "default_group_multiple": {}, "group_items": {}}

    def view_field(self, name, ftype, st, label, link_key=False, link=True):
        plugin, settings, _ = self.formatter(ftype, st, link=link)
        if name == "field_key":
            settings = {"link_to_entity": link_key}
        column = "target_id" if ftype == "entity_reference" else "value"
        return {"id": name, "table": f"node__{name}", "field": name, "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "field", "label": label, "exclude": False,
                "alter": {"alter_text": False, "make_link": False, "absolute": False, "word_boundary": True, "ellipsis": True, "strip_tags": False, "trim": False, "html": False},
                "element_type": "", "element_class": "", "element_label_type": "", "element_label_class": "", "element_label_colon": True, "element_wrapper_type": "", "element_wrapper_class": "",
                "element_default_classes": True, "empty": "", "hide_empty": False, "empty_zero": False, "hide_alter_empty": True, "click_sort_column": column, "type": plugin, "settings": settings,
                "group_column": column, "group_columns": {}, "group_rows": True, "delta_limit": 0, "delta_offset": 0, "delta_reversed": False, "delta_first_last": False,
                "multi_type": "separator", "separator": ", ", "field_api_classes": False}

    def view_filters(self, table, bundle, fields):
        f = OrderedDict()
        f["status"] = {"id": "status", "table": "node_field_data", "field": "status", "entity_type": "node", "entity_field": "status", "plugin_id": "boolean", "value": "1", "group": 1, "expose": {"operator": ""}}
        f["type"] = {"id": "type", "table": "node_field_data", "field": "type", "entity_type": "node", "entity_field": "type", "plugin_id": "bundle", "operator": "in", "value": {bundle: bundle}, "group": 1}
        f["title"] = {"id": "title", "table": "node_field_data", "field": "title", "entity_type": "node", "entity_field": "title", "plugin_id": "string", "operator": "contains", "value": "",
                      "group": 1, "exposed": True, "expose": self.expose("search", "Search", "title_op"), "is_grouped": False, "group_info": self.group_info()}
        names = {n: (ft, st, label, col) for n, ft, st, label, col in fields}
        if "field_series" in names and bundle != "series":
            f["field_series_target_id"] = {"id": "field_series_target_id", "table": "node__field_series", "field": "field_series_target_id", "relationship": "none", "group_type": "group", "admin_label": "",
                                           "plugin_id": "entity_reference", "operator": "or", "value": {}, "group": 1, "exposed": True, "expose": self.expose("series", "Series", "field_series_target_id_op"),
                                           "is_grouped": False, "group_info": self.group_info(), "reduce_duplicates": False, "sub_handler": "default:node", "widget": "select",
                                           "sub_handler_settings": {"target_bundles": {"series": "series"}, "sort": {"field": "field_series_number", "direction": "ASC"}, "auto_create": False}}
        for n in ("field_series_number", "field_week_number", "field_mark", "field_final_placement"):
            if n in names:
                lbl = names[n][2]
                f[f"{n}_value"] = {"id": f"{n}_value", "table": f"node__{n}", "field": f"{n}_value", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "numeric", "operator": "=",
                                   "value": {"min": "", "max": "", "value": ""}, "group": 1, "exposed": True, "expose": self.expose(n[6:], lbl, f"{n}_value_op"), "is_grouped": False, "group_info": self.group_info()}
        for n, (ft, st, label, col) in names.items():
            if ft == "entity_reference" and st["target_type"] == "taxonomy_term":
                vocab = next(next(iter(inst["settings"]["handler_settings"]["target_bundles"])) for et, b, nm, inst in self.fields if et == "node" and b == bundle and nm == n)
                f[f"{n}_target_id"] = {"id": f"{n}_target_id", "table": f"node__{n}", "field": f"{n}_target_id", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "taxonomy_index_tid",
                                       "operator": "or", "value": {}, "group": 1, "exposed": True, "expose": self.expose(n[6:], label, f"{n}_target_id_op"), "is_grouped": False, "group_info": self.group_info(),
                                       "reduce_duplicates": False, "vid": vocab, "type": "select", "hierarchy": False, "limit": True, "error_message": True}
            elif ft == "list_string":
                f[f"{n}_value"] = {"id": f"{n}_value", "table": f"node__{n}", "field": f"{n}_value", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "list_field",
                                   "operator": "or", "value": {}, "group": 1, "exposed": True, "expose": self.expose(n[6:], label, f"{n}_value_op"), "is_grouped": False, "group_info": self.group_info(), "reduce_duplicates": False}
        return f

    @staticmethod
    def cache_meta():
        return {"max-age": -1, "contexts": ["languages:language_content", "languages:language_interface", "url", "url.query_args", "user.permissions"], "tags": []}

    def table_view(self, table, bundle):
        fields = self.bundle_fields("node", bundle)
        shown = [(n, ft, st, label, col) for n, ft, st, label, col in fields if n == "field_key" or (col not in self.PROV_COLS and ft != "string_long")]
        page_fields = OrderedDict((n, self.view_field(n, ft, st, label, link_key=True)) for n, ft, st, label, col in shown)
        export_fields, relationships = OrderedDict(), OrderedDict()
        for n, ft, st, label, col in fields:   # CSV header = package column names; values as in the package (keys, true/false, ISO dates)
            if ft == "entity_reference" and self.storages[("node", n)]["cardinality"] == 1:
                target = st["target_type"]
                relationships[n] = {"id": n, "table": f"node__{n}", "field": n, "relationship": "none", "group_type": "group", "admin_label": col, "plugin_id": "standard", "required": False}
                export_fields[n] = dict(self.view_field("field_key", "string", {}, col, link_key=False), id=n, relationship=n, table=f"{target}__field_key")
            else:
                fld = self.view_field(n, ft, st, col, link=False)
                if ft == "boolean":
                    fld["settings"] = {"format": "custom", "format_custom_true": "true", "format_custom_false": "false"}
                elif ft == "datetime" and st.get("datetime_type") != "date":
                    fld["settings"] = {"timezone_override": "UTC", "format_type": "html_datetime"}
                export_fields[n] = fld
        columns = {n: n for n in page_fields}
        info = {n: {"sortable": True, "default_sort_order": "asc", "align": "", "separator": "", "empty_column": False, "responsive": "priority-low" if col.startswith("d_") else ""} for n, ft, st, label, col in shown}
        vocabs = sorted({next(iter(inst["settings"]["handler_settings"]["target_bundles"])) for et, b, nm, inst in self.fields
                         if et == "node" and b == bundle and inst["field_type"] == "entity_reference" and self.storages[(et, nm)]["settings"]["target_type"] == "taxonomy_term"})
        label = LABELS[table] + ("s" if not LABELS[table].endswith("s") else "")
        plural = {"Series": "Series", "Person": "People", "Person alias": "Person aliases", "Discrepancy": "Discrepancies", "Performance music": "Performance music"}.get(LABELS[table], label)
        intro = (f"<p>One row per line of <code>{table}.csv</code> in the packaged dataset; the column meanings are in "
                 f"<a href=\"https://github.com/kitperform/strictly.kitperform.science/blob/main/docs/data-model-v2.md\">docs/data-model-v2.md</a>. "
                 f"The same rows are available as JSON:API at <a href=\"/jsonapi/node/{bundle}\">/jsonapi/node/{bundle}</a>; the CSV link below the table downloads the filtered rows.</p>")
        default = {
            "title": plural, "fields": page_fields,
            "pager": {"type": "full", "options": {"offset": 0, "pagination_heading_level": "h4", "items_per_page": 50, "total_pages": None, "id": 0,
                                                  "tags": {"next": "Next ›", "previous": "‹ Previous", "first": "« First", "last": "Last »"},
                                                  "expose": {"items_per_page": True, "items_per_page_label": "Rows per page", "items_per_page_options": "25, 50, 100, 250, 500", "items_per_page_options_all": False,
                                                             "items_per_page_options_all_label": "- All -", "offset": False, "offset_label": "Offset"}, "quantity": 9}},
            "exposed_form": {"type": "basic", "options": {"submit_button": "Filter", "reset_button": True, "reset_button_label": "Reset", "exposed_sorts_label": "Sort by", "expose_sort_order": True, "sort_asc_label": "Asc", "sort_desc_label": "Desc"}},
            "access": {"type": "perm", "options": {"perm": "access content"}}, "cache": {"type": "tag", "options": {}}, "empty": {}, "arguments": {}, "relationships": {},
            "sorts": {"nid": {"id": "nid", "table": "node_field_data", "field": "nid", "relationship": "none", "group_type": "group", "admin_label": "", "entity_type": "node", "entity_field": "nid", "plugin_id": "standard", "order": "ASC", "exposed": False}},
            "filters": self.view_filters(table, bundle, fields),
            "style": {"type": "table", "options": {"grouping": [], "row_class": "", "default_row_class": True, "columns": columns, "default": "-1", "info": info, "override": True, "sticky": True,
                                                   "summary": "", "empty_table": True, "caption": "", "description": ""}},
            "row": {"type": "fields", "options": {"default_field_elements": True, "inline": {}, "separator": "", "hide_empty": False}},
            "query": {"type": "views_query", "options": {"query_comment": "", "disable_sql_rewrite": False, "distinct": False, "replica": False, "query_tags": []}},
            "header": {"area_text_custom": {"id": "area_text_custom", "table": "views", "field": "area_text_custom", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "text_custom", "empty": True, "content": intro, "tokenize": False},
                       "result": {"id": "result", "table": "views", "field": "result", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "result", "empty": False, "content": "Rows @start to @end of @total."}},
            "footer": {}, "display_extenders": {}, "use_ajax": False, "group_by": False, "show_admin_links": False,
        }
        page = {"display_extenders": {}, "path": f"data/{bundle}", "defaults": {}}
        export = {"display_extenders": {}, "path": f"data/{bundle}/csv", "displays": {"page_1": "page_1"}, "filename": f"strictly-{table}.csv", "automatic_download": False,
                  "export_method": "batch", "export_batch_size": 500, "export_limit": 0, "export_filesystem": "public", "custom_redirect_path": False, "redirect_to_display": "page_1", "include_query_params": True,
                  "defaults": {"fields": False, "pager": False, "style": False, "row": False, "header": False, "footer": False, "relationships": False},
                  "fields": export_fields, "relationships": relationships, "header": {}, "footer": {}, "pager": {"type": "none", "options": {"offset": 0}},
                  "style": {"type": "data_export", "options": {"formats": {"csv": "csv"}, "csv_settings": {"delimiter": ",", "enclosure": '"', "escape_char": "\\", "strip_tags": True, "trim": True, "encoding": "utf8",
                                                                                                           "utf8_bom": "0", "use_serializer_encode_only": False, "output_header": True}}},
                  "row": {"type": "data_field", "options": {"field_options": {}}}}
        deps = {"config": sorted({f"field.storage.node.{n}" for n, *_ in fields} | {f"node.type.{bundle}"} | {f"taxonomy.vocabulary.{v}" for v in vocabs}),
                "module": sorted({"node", "user", "views_data_export", "rest", "csv_serialization"} | ({"taxonomy"} if vocabs else set())
                                 | {m for n, ft, st, label, col in fields for m in [self.formatter(ft, st)[2]] if m})}
        return {"langcode": "en", "status": True, "dependencies": deps, "id": f"strictly_{bundle}", "label": plural, "module": "views",
                "description": f"Table of {table}.csv from the Strictly dataset, with filters and CSV export (generated by scripts/generate_drupal_recipe.py).", "tag": "strictly",
                "base_table": "node_field_data", "base_field": "nid",
                "display": {"default": {"id": "default", "display_title": "Default", "display_plugin": "default", "position": 0, "display_options": default, "cache_metadata": self.cache_meta()},
                            "page_1": {"id": "page_1", "display_title": "Page", "display_plugin": "page", "position": 1, "display_options": page, "cache_metadata": self.cache_meta()},
                            "data_export_1": {"id": "data_export_1", "display_title": "CSV", "display_plugin": "data_export", "position": 2, "display_options": export, "cache_metadata": self.cache_meta()}}}

    def tables_view(self, tables):
        """Landing page at /data: one row per content type with its row count, linking to the table view."""
        type_field = {"id": "type", "table": "node_field_data", "field": "type", "relationship": "none", "group_type": "group", "admin_label": "", "entity_type": "node", "entity_field": "type", "plugin_id": "field",
                      "label": "Table", "exclude": False, "alter": {"alter_text": True, "text": '<a href="/data/{{ type__target_id }}">{{ type }}</a>', "make_link": False, "absolute": False, "word_boundary": True, "ellipsis": True, "strip_tags": False, "trim": False, "html": False},
                      "element_type": "", "element_class": "", "element_label_type": "", "element_label_class": "", "element_label_colon": True, "element_wrapper_type": "", "element_wrapper_class": "",
                      "element_default_classes": True, "empty": "", "hide_empty": False, "empty_zero": False, "hide_alter_empty": True, "click_sort_column": "target_id", "type": "entity_reference_label",
                      "settings": {"link": False}, "group_column": "target_id", "group_columns": {}, "group_rows": True, "delta_limit": 0, "delta_offset": 0, "delta_reversed": False, "delta_first_last": False,
                      "multi_type": "separator", "separator": ", ", "field_api_classes": False}
        count_field = {"id": "nid", "table": "node_field_data", "field": "nid", "relationship": "none", "group_type": "count", "admin_label": "", "entity_type": "node", "entity_field": "nid", "plugin_id": "field",
                       "label": "Rows", "exclude": False, "alter": {"alter_text": False}, "element_label_colon": True, "element_default_classes": True, "empty": "", "hide_empty": False, "empty_zero": False, "hide_alter_empty": True,
                       "click_sort_column": "value", "type": "number_integer", "settings": {"thousand_separator": "", "prefix_suffix": False}, "group_column": "value", "group_columns": {}, "group_rows": True,
                       "delta_limit": 0, "delta_offset": 0, "delta_reversed": False, "delta_first_last": False, "multi_type": "separator", "separator": "", "field_api_classes": False}
        bundles = {bundle_of(t): t for t in tables}
        desc = "".join(f"<li><a href=\"/data/{b}\">{LABELS[t]}</a> — one row per line of <code>{t}.csv</code></li>" for b, t in bundles.items())
        intro = ("<p>Every judge mark, performance, results round and roster row of <em>Strictly Come Dancing</em> from series 1 onwards, built from the Wikipedia series pages by an "
                 "<a href=\"https://github.com/kitperform/strictly.kitperform.science\">open-source parser</a>. Each table below is browsable and filterable here, downloadable as CSV from its page, "
                 "and served read-only through <a href=\"/jsonapi\">JSON:API</a> for notebooks and Pandas. The tables, keys and column meanings are documented in "
                 "<a href=\"https://github.com/kitperform/strictly.kitperform.science/blob/main/docs/data-model-v2.md\">docs/data-model-v2.md</a>.</p>")
        default = {"title": "The tables", "fields": {"type": type_field, "nid": count_field}, "group_by": True,
                   "pager": {"type": "none", "options": {"offset": 0}}, "exposed_form": {"type": "basic", "options": {"submit_button": "Apply", "reset_button": False, "reset_button_label": "Reset", "exposed_sorts_label": "Sort by", "expose_sort_order": True, "sort_asc_label": "Asc", "sort_desc_label": "Desc"}},
                   "access": {"type": "perm", "options": {"perm": "access content"}}, "cache": {"type": "tag", "options": {}}, "empty": {}, "arguments": {}, "relationships": {},
                   "sorts": {"type": {"id": "type", "table": "node_field_data", "field": "type", "relationship": "none", "group_type": "group", "admin_label": "", "entity_type": "node", "entity_field": "type", "plugin_id": "standard", "order": "ASC", "exposed": False}},
                   "filters": {"status": {"id": "status", "table": "node_field_data", "field": "status", "entity_type": "node", "entity_field": "status", "plugin_id": "boolean", "value": "1", "group": 1, "expose": {"operator": ""}},
                               "type": {"id": "type", "table": "node_field_data", "field": "type", "entity_type": "node", "entity_field": "type", "plugin_id": "bundle", "operator": "in", "value": {b: b for b in bundles}, "group": 1}},
                   "style": {"type": "table", "options": {"grouping": [], "row_class": "", "default_row_class": True, "columns": {"type": "type", "nid": "nid"}, "default": "-1",
                                                          "info": {"type": {"sortable": True, "default_sort_order": "asc", "align": "", "separator": "", "empty_column": False, "responsive": ""},
                                                                   "nid": {"sortable": True, "default_sort_order": "desc", "align": "", "separator": "", "empty_column": False, "responsive": ""}},
                                                          "override": True, "sticky": False, "summary": "", "empty_table": True, "caption": "", "description": ""}},
                   "row": {"type": "fields", "options": {"default_field_elements": True, "inline": {}, "separator": "", "hide_empty": False}},
                   "query": {"type": "views_query", "options": {"query_comment": "", "disable_sql_rewrite": False, "distinct": False, "replica": False, "query_tags": []}},
                   "header": {"area_text_custom": {"id": "area_text_custom", "table": "views", "field": "area_text_custom", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "text_custom", "empty": True, "content": intro, "tokenize": False}},
                   "footer": {"area_text_custom": {"id": "area_text_custom", "table": "views", "field": "area_text_custom", "relationship": "none", "group_type": "group", "admin_label": "", "plugin_id": "text_custom", "empty": True,
                                                   "content": f"<h3>What each table holds</h3><ul>{desc}</ul>", "tokenize": False}},
                   "display_extenders": {}, "use_ajax": False, "show_admin_links": False}
        page = {"display_extenders": {}, "path": "data", "menu": {"type": "normal", "title": "Tables", "description": "", "weight": 0, "expanded": False, "menu_name": "main", "parent": "", "context": ""}}
        return {"langcode": "en", "status": True, "dependencies": {"config": sorted(f"node.type.{b}" for b in bundles), "module": ["node", "user"]}, "id": "strictly_tables", "label": "Strictly tables",
                "module": "views", "description": "Landing page listing the dataset tables with their row counts (generated by scripts/generate_drupal_recipe.py).", "tag": "strictly",
                "base_table": "node_field_data", "base_field": "nid",
                "display": {"default": {"id": "default", "display_title": "Default", "display_plugin": "default", "position": 0, "display_options": default, "cache_metadata": self.cache_meta()},
                            "page_1": {"id": "page_1", "display_title": "Page", "display_plugin": "page", "position": 1, "display_options": page, "cache_metadata": self.cache_meta()}}}

    def presentation(self, cfg, tables):
        for table in tables:
            self.displays(cfg, "node", bundle_of(table))
            yml(cfg / f"views.view.strictly_{bundle_of(table)}.yml", self.table_view(table, bundle_of(table)))
        for v in list(VOCAB_TABLES.values()) + sorted(set(ENUM_VOCAB_COLS.values())):
            self.displays(cfg, "taxonomy_term", v)
        yml(cfg / "views.view.strictly_tables.yml", self.tables_view(tables))


    def process_for(self, kind, col, target):
        if kind == "string":
            return col
        if kind == "scalar":
            return [{"plugin": "skip_on_empty", "method": "process", "source": col}]
        if kind == "boolean":
            return [{"plugin": "skip_on_empty", "method": "process", "source": col}, {"plugin": "static_map", "map": {"true": 1, "false": 0}}]
        if kind == "datetime":
            return [{"plugin": "skip_on_empty", "method": "process", "source": col}, {"plugin": "format_date", "from_format": "Y-m-d\\TH:i:s\\Z", "to_format": "Y-m-d\\TH:i:s", "from_timezone": "UTC", "to_timezone": "UTC"}]
        if kind == "ref":
            return [{"plugin": "skip_on_empty", "method": "process", "source": col}, {"plugin": "migration_lookup", "migration": target, "no_stub": True}]
        if kind == "multi_ref":
            return [{"plugin": "skip_on_empty", "method": "process", "source": col}, {"plugin": "explode", "delimiter": "|"}, {"plugin": "migration_lookup", "migration": target, "no_stub": True}]
        raise ValueError(kind)

    @staticmethod
    def migration(mid, label, path, ids, process, destination, deps, constants):
        return {"langcode": "en", "status": True, "dependencies": {}, "id": mid, "class": None, "field_plugin_method": None, "cck_plugin_method": None,
                "migration_tags": ["strictly"], "migration_group": "strictly", "label": label,
                "source": {"plugin": "csv", "path": path, "ids": ids, "track_changes": True, "constants": constants},
                "process": process, "destination": destination, "migration_dependencies": {"required": deps, "optional": []}}


def yaml_to_json(d):
    import json
    return json.dumps(d, indent=4) + "\n"


def readme(r: Recipe):
    n_types = sum(1 for et, b, n, i in r.fields if et == "node" and n == "field_key")
    n_vocab = sum(1 for et, b, n, i in r.fields if et == "taxonomy_term" and n == "field_key")
    return f"""# Strictly Come Dancing results — Drupal recipe

Generated by `scripts/generate_drupal_recipe.py` from the dataset schema; do not edit by hand.

- {n_types} node content types (one per table of `data/package/`), each with `field_key` holding the natural key.
- {n_vocab} vocabularies: dance, theme, venue, artist, and the open-ended enumerations.
- {len(r.storages)} field storages, {len(r.fields)} field instances, {len(r.migrations)} migrations in the group `strictly`.
- a view display and a form display per content type and vocabulary (every field visible);
- a table View per content type at `/data/<bundle>` with exposed filters (title search, series, series/week number, marks, every enumeration),
  sortable columns and a batch CSV export at `/data/<bundle>/csv` whose columns and values match the package CSV; the landing page `/data`
  (set as the front page) lists the tables with their row counts;
- Olivero + Claro + toolbar, Field UI, Views UI, the core admin content/people/term listings, read-only JSON:API.

The recipe depends on the core recipes `core_recommended_admin_theme`, `core_recommended_front_end_theme` and `administrator_role`, and on the
contrib modules migrate_plus, migrate_tools, migrate_source_csv, views_data_export (+ csv_serialization). `config.strict` is false, so re-applying
on a site that already has it leaves existing config alone; to push regenerated config use `drush config:import --partial --source=<recipe>/config`.

Apply (Drupal 11.2+, Drush 13, with migrate_plus, migrate_tools and migrate_source_csv in the codebase):

```sh
drush recipe {r.recipe_path}
drush cache:rebuild
drush migrate:import --group=strictly            # first load
drush migrate:import --group=strictly --update   # after a dataset rebuild
```

The migrations read `{r.data_path}/<table>.csv` and `{r.recipe_path}/lookups/<vocabulary>.csv`.
Regenerate with other paths: `scripts/generate_drupal_recipe.py --data-path ... --recipe-path ...`.

Locally: `scripts/drupal-local.sh setup` then `scripts/drupal-local.sh apply` (DDEV, repository root as project root).
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data-path", default="/var/www/html/data/package", help="where the migrations find the package CSVs at run time")
    ap.add_argument("--recipe-path", default="/var/www/html/recipes/strictly", help="where the recipe (and its lookups/) lives at run time")
    ap.add_argument("--package-dir", default=str(REPO / "data" / "package"), help="the package CSVs to read observed values from now")
    ap.add_argument("--out", default=str(REPO / "recipes" / "strictly"))
    a = ap.parse_args(argv)
    r = Recipe(a.data_path, a.recipe_path, Path(a.package_dir), Path(a.out))
    out = r.build()
    print(f"wrote {out}: {len(list((out / 'config').glob('*.yml')))} config files, {len(r.migrations)} migrations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
