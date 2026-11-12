"""python -m strictly_parser 24 [--out data/tidy]"""
import argparse
import csv
import sys
from pathlib import Path

from .build import Build
from .emit import write_tables, write_report


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the tidy Strictly dataset for one series from its captured Wikipedia page.")
    ap.add_argument("series", type=int)
    ap.add_argument("--out", default="data/tidy", help="output root; the series goes in <out>/S<nn>/")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    html = repo / "data" / "wikipedia" / "parsoid" / f"series_{a.series}.parsoid.html"
    if not html.exists():
        html = repo / "data" / "wikipedia" / "series" / f"{a.series:03d}" / f"Strictly_Come_Dancing_series_{a.series}.html"
    with (repo / "data" / "wikipedia" / "wikitext" / "MANIFEST.csv").open(newline="", encoding="utf-8") as f:
        manifest = {r["title"]: r for r in csv.DictReader(f)}
    row = manifest[f"Strictly_Come_Dancing_series_{a.series}"]
    b = Build(a.series, repo, html, row, repo / "curated")
    tables, report = b.run()
    out = Path(a.out) if Path(a.out).is_absolute() else repo / a.out
    out = out / b.skey
    written = write_tables(tables, out)
    lines = write_report(report, written, out, b.skey)
    print("\n".join(lines))
    failed = [c for c in report["checks"] if not c[1]]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
