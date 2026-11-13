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
    assert rec["type"] == "Content type" and {"node", "taxonomy", "jsonapi", "migrate_plus", "migrate_tools", "migrate_source_csv"} <= set(rec["install"])
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
