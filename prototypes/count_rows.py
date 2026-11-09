"""Rough regex census of the wikitext: weeks, couples, performances and judge marks per series.

Usage: python -I prototypes/count_rows.py [WIKITEXT_DIR]
Defaults to data/wikipedia/wikitext/ (or SDC_WIKITEXT_DIR). Counts are approximate.
"""
import os, re, sys, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sdc_common import WIKITEXT_DIR
base = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else WIKITEXT_DIR
tot_perf = tot_scores = tot_couples = 0
for n in range(1, 25):
    t = (base / f"series_{n}.wikitext").read_text(encoding="utf-8", errors="replace")
    # Weekly scores section
    m = re.search(r"==\s*Weekly scores\s*==(.*?)==\s*Dance chart\s*==", t, re.S)
    ws = m.group(1) if m else ""
    # score cells like "7, 8, 8, 8" (3-5 ints, possibly with '–' for absent judge)
    cells = re.findall(r"\|\s*'''?\d{1,2}'''?\s*\|\|?\s*((?:\d{1,2}|–|-)\s*,\s*(?:\d{1,2}|–|-)\s*,\s*(?:\d{1,2}|–|-)(?:\s*,\s*(?:\d{1,2}|–|-))?(?:\s*,\s*(?:\d{1,2}|–|-))?)", ws)
    # fallback: any 3-5 comma separated score lists
    cells2 = re.findall(r"(?<![\d,])((?:\d{1,2}|–)\s*,\s*(?:\d{1,2}|–)\s*,\s*(?:\d{1,2}|–)(?:\s*,\s*(?:\d{1,2}|–)){0,2})(?![\d,])", ws)
    nperf = len(cells2)
    nscores = sum(len([x for x in c.split(",") if x.strip().isdigit()]) for c in cells2)
    cm = re.search(r"==\s*Couples\s*==(.*?)==\s*Scoring chart", t, re.S)
    ncouples = len(re.findall(r"^\|-", cm.group(1), re.M)) if cm else 0
    weeks = len(re.findall(r"^===\s*Week\s+\d+", t, re.M))
    print(f"series {n:2d}: weeks={weeks:2d} couples~{ncouples:2d} perf~{nperf:4d} scores~{nscores:5d}")
    tot_perf += nperf; tot_scores += nscores; tot_couples += ncouples
print("TOTAL perf~", tot_perf, "scores~", tot_scores, "couples~", tot_couples)
