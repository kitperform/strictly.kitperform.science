"""The generated Drupal recipe: every config file parses, names fit Drupal's limits, and every reference points at something that exists."""
import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from generate_drupal_recipe import Recipe  # noqa: E402


@pytest.fixture(scope="module")
def recipe(tmp_path_factory):
    out = tmp_path_factory.mktemp("recipe") / "strictly"
    r = Recipe("/srv/data", "/srv/recipe", REPO / "data" / "package", out)
    r.build()
    cfg = {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in (out / "config").glob("*.yml")}
    return {"out": out, "cfg": cfg, "r": r}


def test_recipe_yml_and_composer(recipe):
    rec = yaml.safe_load((recipe["out"] / "recipe.yml").read_text())
    assert rec["type"] == "Site" and {"node", "taxonomy", "jsonapi", "migrate_plus", "migrate_tools", "migrate_source_csv"} <= set(rec["install"])
    assert rec["config"]["actions"]["user.role.anonymous"]["grantPermissions"] == ["access content"]
    comp = json.loads((recipe["out"] / "composer.json").read_text())
    assert comp["type"] == "drupal-recipe" and comp["name"] == "kitperform/strictly_recipe"


def test_field_names_fit_and_storages_match_instances(recipe):
    cfg = recipe["cfg"]
    storages = {k: v for k, v in cfg.items() if k.startswith("field.storage.")}
    instances = {k: v for k, v in cfg.items() if k.startswith("field.field.")}
    for name, st in storages.items():
        assert len(st["field_name"]) <= 32, name
    for name, inst in instances.items():
        storage = f"field.storage.{inst['entity_type']}.{inst['field_name']}"
        assert storage in storages and storages[storage]["type"] == inst["field_type"], name
        for dep in inst["dependencies"]["config"]:
            assert dep in cfg, (name, dep)
    bundles = {v["type"] for k, v in cfg.items() if k.startswith("node.type.")}
    assert len(bundles) == 20 and all(f"field.field.node.{b}.field_key" in cfg for b in bundles)


def test_every_lookup_targets_an_existing_migration(recipe):
    cfg = recipe["cfg"]
    migs = {v["id"]: v for k, v in cfg.items() if k.startswith("migrate_plus.migration.")}
    assert len(migs) == 34
    for mid, m in migs.items():
        assert m["migration_group"] == "strictly" and m["source"]["plugin"] == "csv" and m["source"]["track_changes"] is True
        for dep in m["migration_dependencies"]["required"]:
            assert dep in migs, (mid, dep)
        for field, proc in m["process"].items():
            if isinstance(proc, list):
                for step in proc:
                    if step.get("plugin") == "migration_lookup":
                        assert step["migration"] in migs, (mid, field)
            if field.startswith("field_") and m["destination"]["plugin"] == "entity:node":
                assert f"field.field.node.{m['destination']['default_bundle']}.{field}" in cfg, (mid, field)


def test_enum_terms_cover_the_data(recipe):
    r = recipe["r"]
    lookups = {p.stem: {row.split(",")[0] for row in p.read_text().splitlines()[1:]} for p in (recipe["out"] / "lookups").glob("*.csv")}
    assert {"result_status", "selection_role", "absence_reason", "roster_status"} <= set(lookups)
    assert set(r.observed[("couple_weeks", "result_status")]) <= lookups["result_status"]
    assert set(r.observed[("couples", "exit_reason")]) <= lookups["absence_reason"]
    assert "same_song" in lookups["selection_role"] and "paired_withdrew_pre_week1" in lookups["roster_status"]


def test_every_bundle_has_displays_showing_every_field(recipe):
    """Node and term bundles get a view display and a form display that place every field (Drupal hides fields with no display config)."""
    cfg = recipe["cfg"]
    bundles = [(k.split(".")[3], k.split(".")[2]) for k in cfg if k.startswith("field.field.")]
    for bundle, et in sorted(set(bundles)):
        fields = {k.split(".")[-1] for k in cfg if k.startswith(f"field.field.{et}.{bundle}.")}
        view, form = cfg[f"core.entity_view_display.{et}.{bundle}.default"], cfg[f"core.entity_form_display.{et}.{bundle}.default"]
        assert fields <= set(view["content"]) and fields <= set(form["content"]), (et, bundle)
        assert all(c["region"] == "content" for c in view["content"].values())
        assert set(view["dependencies"]["config"]) >= {f"field.field.{et}.{bundle}.{f}" for f in fields}


def test_every_table_has_a_filterable_view_with_csv_export(recipe):
    cfg = recipe["cfg"]
    bundles = [k.split(".")[2] for k in cfg if k.startswith("node.type.")]
    for bundle in bundles:
        view = cfg[f"views.view.strictly_{bundle}"]
        d = view["display"]["default"]["display_options"]
        assert view["display"]["page_1"]["display_options"]["path"] == f"data/{bundle}"
        assert view["display"]["data_export_1"]["display_options"]["path"] == f"data/{bundle}/csv"
        assert d["filters"]["type"]["value"] == {bundle: bundle} and d["filters"]["title"]["expose"]["identifier"] == "search"
        fields = {k.split(".")[-1] for k in cfg if k.startswith(f"field.field.node.{bundle}.")}
        # every handler refers to a field that exists on the bundle, and the export covers every field under the package's column names
        for h in list(d["fields"].values()) + [f for f in d["filters"].values() if f["table"] != "node_field_data"]:
            assert h["table"][6:] in fields, (bundle, h["table"])
        export = view["display"]["data_export_1"]["display_options"]["fields"]
        assert set(export) == fields, bundle
        assert "field_key" in d["fields"] and d["fields"]["field_key"]["settings"] == {"link_to_entity": True}
        assert set(view["dependencies"]["config"]) >= {f"field.storage.node.{f}" for f in fields} | {f"node.type.{bundle}"}
    tables = cfg["views.view.strictly_tables"]
    assert tables["display"]["page_1"]["display_options"]["path"] == "data"
    assert set(tables["display"]["default"]["display_options"]["filters"]["type"]["value"]) == set(bundles)


def test_recipe_sets_up_the_site(recipe):
    rec = yaml.safe_load((recipe["out"] / "recipe.yml").read_text())
    assert rec["recipes"] == ["core/recipes/core_recommended_admin_theme", "core/recipes/core_recommended_front_end_theme", "core/recipes/administrator_role"]
    assert {"toolbar", "field_ui", "views_ui", "config", "views_data_export"} <= set(rec["install"])
    assert rec["config"]["actions"]["system.site"]["simpleConfigUpdate"]["page.front"] == "/data"
    assert "views.view.content" in rec["config"]["import"]["node"]
