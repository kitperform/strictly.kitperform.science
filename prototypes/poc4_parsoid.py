"""POC 4: what Parsoid HTML (data-mw) adds over plain/legacy HTML.

Compares the Parsoid REST capture of series 24 with the legacy-parser capture
of series 6: template names, efn names/bodies, dagger alt text, section ids.
Usage: python -I prototypes/poc4_parsoid.py
Uses data/wikipedia/parsoid/series_24.parsoid.html if present (SDC_PARSOID_HTML to
override), otherwise the repo's series 24 read-view capture, which is also Parsoid HTML.
"""
import os, sys, re, json
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bs4 import BeautifulSoup
from sdc_common import parsoid_path, html_path

PARSOID_PATH = parsoid_path()
print("Parsoid HTML:", PARSOID_PATH)
soup = BeautifulSoup(PARSOID_PATH.read_text(encoding="utf-8"), "lxml")

# 1. Which templates are present, by name, from data-mw
tpl = Counter()
examples = {}
for el in soup.find_all(attrs={"data-mw": True}):
    try:
        dm = json.loads(el["data-mw"])
    except json.JSONDecodeError:
        continue
    for part in dm.get("parts", []):
        if isinstance(part, dict) and "template" in part:
            name = part["template"]["target"].get("wt", "").strip().lower()
            tpl[name] += 1
            examples.setdefault(name, (el.name, str(el)[:160].replace("\n", " ")))
print("Template usage in Parsoid HTML (series 24):")
for k, v in tpl.most_common(25):
    print(f"  {v:4d}  {k}")

# 2. efn footnotes: name + body text are recoverable per cell
print("\nefn examples (cell -> note name, body):")
for sup in soup.select('sup[typeof*="mw:Extension/ref"]')[:200]:
    dm = json.loads(sup.get("data-mw", "{}"))
    if dm.get("attrs", {}).get("group") == "lower-alpha":
        name = dm["attrs"].get("name")
        body = ""
        for part in dm.get("parts", []):
            if isinstance(part, dict) and "template" in part:
                p = part["template"].get("params", {})
                body = (p.get("1") or {}).get("wt", "")
        td = sup.find_parent(["td", "th"])
        if td is None:
            continue
        print(f"  cell text={td.get_text(strip=True)[:20]!r} bg={td.get('bgcolor')} -> efn name={name} body={body[:70]!r}")
        break

# 3. dagger alt text survives in data-mw
d = soup.find(string=re.compile("†"))
el = d.parent if d else None
while el is not None and not el.has_attr("data-mw"):
    el = el.parent
if el is not None:
    print("\ndagger element data-mw:", el["data-mw"][:200])

# 4. Sections are explicit
secs = soup.select("section[data-mw-section-id]")
print(f"\n{len(secs)} <section data-mw-section-id> elements; headings:",
      [s.find(["h2", "h3", "h4"]).get("id") for s in secs if s.find(["h2", "h3", "h4"])][:12])

# 5. Links carry rel=mw:WikiLink and canonical hrefs
a = soup.select_one('a[rel="mw:WikiLink"][href*="Will_Best"]')
print("\nwiki link example:", a)

# 6. Legacy HTML comparison (series 6): no data-mw; dagger alt lost? efn body only via #cite_note
leg = BeautifulSoup(html_path(6).read_text(encoding="utf-8"), "lxml")
print("\nLegacy S6: data-mw attrs:", len(leg.find_all(attrs={"data-mw": True})), "| mw:Transclusion:", len(leg.select('[typeof*="mw:Transclusion"]')))
dag = leg.find(string=re.compile("†"))
print("Legacy dagger context:", str(dag.parent)[:200].replace("\n", " "))
ref = leg.select_one('sup.reference a[href^="#cite_note-Bottom2"]')
note = leg.select_one("#cite_note-Bottom2-6 .reference-text") or leg.select_one('li[id^="cite_note-Bottom2"]')
print("Legacy efn marker:", ref.get_text(), "| note body:", note.get_text(" ", strip=True)[:90] if note else None)
na = leg.select_one("td.table-na")
print("Legacy {{NA}} cell:", str(na)[:160])
