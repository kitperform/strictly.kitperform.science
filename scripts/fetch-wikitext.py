#!/usr/bin/env python3
"""Fetch the raw wikitext of the Strictly Come Dancing Wikipedia pages with provenance.

Uses the MediaWiki Action API (action=query&prop=revisions) so that every
capture records the revision id, revision timestamp and sha1 that Wikipedia
itself reports. Writes one .wikitext file per page under data/wikipedia/wikitext/
and a MANIFEST.csv alongside. Standard library only.

Usage:
  scripts/fetch-wikitext.py            # main page, specials list, series 1..LATEST
  scripts/fetch-wikitext.py 22 23 24   # just these series
  scripts/fetch-wikitext.py --parsoid 24   # also fetch Parsoid HTML for that series at the captured revid
"""
import csv
import datetime as dt
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

LATEST = 24
UA = "strictly.kitperform.science/0.1 (https://github.com/kitperform/strictly.kitperform.science)"
API = "https://en.wikipedia.org/w/api.php"
REST = "https://en.wikipedia.org/api/rest_v1/page/html/"
ROOT = pathlib.Path(__file__).resolve().parent.parent / "data" / "wikipedia"
OUT = ROOT / "wikitext"
MANIFEST = OUT / "MANIFEST.csv"
FIELDS = ["title", "pageid", "revid", "timestamp", "sha1", "captured_at", "path"]


def get(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def filename(title):
    if title.startswith("Strictly_Come_Dancing_series_"):
        return f"series_{title.rsplit('_', 1)[1]}.wikitext"
    return title + ".wikitext"


def fetch_batch(titles, manifest):
    data = json.loads(get(API, {
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "revisions", "rvslots": "main",
        "rvprop": "ids|timestamp|sha1|content", "maxlag": "5",
        "titles": "|".join(titles),
    }))
    captured_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for page in data["query"]["pages"]:
        if "missing" in page:
            print(f"MISSING  {page['title']}", file=sys.stderr)
            continue
        rev = page["revisions"][0]
        title = page["title"].replace(" ", "_")
        path = OUT / filename(title)
        path.write_text(rev["slots"]["main"]["content"], encoding="utf-8")
        manifest[title] = {
            "title": title, "pageid": page["pageid"], "revid": rev["revid"],
            "timestamp": rev["timestamp"], "sha1": rev["sha1"],
            "captured_at": captured_at, "path": str(path.relative_to(ROOT.parent.parent)),
        }
        print(f"{path.stat().st_size:8d} bytes  rev {rev['revid']}  {path.relative_to(ROOT.parent.parent)}")


def fetch_parsoid(n, manifest):
    title = f"Strictly_Come_Dancing_series_{n}"
    revid = manifest[title]["revid"]
    out = ROOT / "parsoid" / f"series_{n}.parsoid.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(get(REST + urllib.parse.quote(title) + "/" + str(revid)))
    print(f"{out.stat().st_size:8d} bytes  rev {revid}  {out.relative_to(ROOT.parent.parent)}")


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    if MANIFEST.exists():
        with MANIFEST.open(newline="", encoding="utf-8") as f:
            manifest = {row["title"]: row for row in csv.DictReader(f)}
    parsoid = []
    args = []
    it = iter(argv)
    for a in it:
        if a == "--parsoid":
            parsoid.append(next(it))
        else:
            args.append(a)
    if args:
        titles = [f"Strictly_Come_Dancing_series_{n}" for n in args]
    else:
        titles = ["Strictly_Come_Dancing", "List_of_Strictly_Come_Dancing_specials"] + [
            f"Strictly_Come_Dancing_series_{n}" for n in range(1, LATEST + 1)]
    for i in range(0, len(titles), 5):
        fetch_batch(titles[i:i + 5], manifest)
        time.sleep(1)
    for n in parsoid:
        fetch_parsoid(n, manifest)
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for title in sorted(manifest, key=lambda t: (not t.startswith("Strictly_Come_Dancing_series_"), len(t), t)):
            w.writerow({k: manifest[title][k] for k in FIELDS})


if __name__ == "__main__":
    main(sys.argv[1:])
