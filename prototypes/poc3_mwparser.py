"""POC 3: mwparserfromhell on the raw wikitext: Week sections -> table rows.

Extracts couple, total, per-judge scores, dance, song (+ link target), artist,
result (+ bgcolor), plus template-level facts (efn, dagger) that HTML loses.
Usage: python -I prototypes/poc3_mwparser.py 6 24
Reads data/wikipedia/wikitext/series_N.wikitext (override with SDC_WIKITEXT_DIR).
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mwparserfromhell as mw
import pandas as pd
from sdc_common import wikitext_path, parse_score, out_dir

WEEK_RE = re.compile(r"^\s*Week\s+(\d+)")


def clean(code) -> str:
    """Wikicode -> plain text, dropping <ref>, efn, and keeping dagger symbols."""
    code = mw.parse(str(code))
    for t in code.filter_tags(matches=lambda t: t.tag.lower() == "ref"):
        try:
            code.remove(t)
        except ValueError:
            pass
    for tpl in code.filter_templates(recursive=False):
        name = tpl.name.strip().lower()
        if name in ("efn", "notelist"):
            code.remove(tpl)
        elif name == "dagger":
            code.replace(tpl, "†")
        elif name == "double-dagger":
            code.replace(tpl, "‡")
        elif name in ("fontcolor", "nowrap", "small", "sort", "abbr"):
            # keep display text (last positional param for fontcolor; first for nowrap/small)
            if name == "fontcolor" and tpl.has(2):
                code.replace(tpl, str(tpl.get(2).value))
            elif name == "sort":
                code.replace(tpl, "")
            elif tpl.has(1):
                code.replace(tpl, str(tpl.get(1).value))
            else:
                code.remove(tpl)
        elif name in ("na", "n/a"):
            code.replace(tpl, "N/A")
    txt = code.strip_code(normalize=True, collapse=True)
    txt = re.sub(r"<br\s*/?>", " | ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def cell_meta(cell):
    """Template-level facts in a cell: efn names/text, dagger alt, bgcolor."""
    meta = {}
    attrs = {a.name.strip(): str(a.value).strip().strip('"') for a in cell.attributes}
    if "bgcolor" in attrs:
        meta["bg"] = attrs["bgcolor"]
    if "style" in attrs:
        m = re.search(r"background:\s*([^;]+)", attrs["style"])
        if m:
            meta["bg"] = m.group(1)
    if "rowspan" in attrs:
        meta["rowspan"] = attrs["rowspan"]
    for tpl in cell.contents.filter_templates():
        n = tpl.name.strip().lower()
        if n == "efn":
            meta.setdefault("efn", []).append(str(tpl.get("name").value) if tpl.has("name") else tpl.get(1).value.strip_code()[:40])
        elif n in ("dagger", "double-dagger"):
            meta["marker"] = n
    links = cell.contents.filter_wikilinks()
    if links:
        meta["links"] = [str(l.title) for l in links]
    return meta


def table_rows(table):
    """Yield list-of-cells per <tr>, cells as mwparserfromhell Tag objects.

    PITFALL: when the wikitext table has no "|-" before its first row (the
    series 22-24 style), mwparserfromhell leaves those th/td Tags directly in
    table.contents with no enclosing tr. Collect them as an implicit first row."""
    lead = [c for c in table.contents.filter_tags(matches=lambda t: t.tag in ("td", "th"), recursive=False)]
    if lead:
        yield lead
    for tr in table.contents.filter_tags(matches=lambda t: t.tag == "tr", recursive=False):
        yield [c for c in tr.contents.filter_tags(matches=lambda t: t.tag in ("td", "th"), recursive=False)]


def main(n):
    raw = wikitext_path(n).read_text(encoding="utf-8")
    # PITFALL: mwparserfromhell 0.6 fails to parse a table whose caption line is an
    # empty "|+" (series 24 weeks 3-8); the whole table degrades to Text nodes.
    raw = re.sub(r"\n\|\+[ \t]*\n", "\n", raw)
    code = mw.parse(raw)
    rows, anomalies = [], []
    for sec in code.get_sections(levels=[3], include_headings=True):
        heading = sec.filter_headings()[0]
        m = WEEK_RE.match(heading.title.strip_code())
        if not m:
            continue
        week = int(m.group(1))
        tables = sec.filter_tags(matches=lambda t: t.tag == "table")
        if not tables:
            anomalies.append(f"wk{week}: no table")
        # sub-labels: ;Show 1 / ;Night 1 / ====Show 1====
        for table in tables:
            header = None
            pending_couple = None
            for cells in table_rows(table):
                texts = [clean(c.contents) for c in cells]
                if header is None and all(c.tag == "th" for c in cells):
                    header = [re.sub(r"\s+", " ", t).strip() for t in texts]
                    continue
                if header is None:
                    continue
                rec = {"week": week}
                # Row-header couple cell may be absent on 2nd/3rd dance rows (rowspan)
                if cells and cells[0].tag == "th":
                    rec["couple"] = texts[0]
                    meta = cell_meta(cells[0])
                    if "rowspan" in meta:
                        pending_couple = (texts[0], int(meta["rowspan"]) - 1)
                    cols = list(zip(header[1:], cells[1:], texts[1:]))
                else:
                    if pending_couple and pending_couple[1] > 0:
                        rec["couple"] = pending_couple[0]
                        pending_couple = (pending_couple[0], pending_couple[1] - 1)
                    else:
                        anomalies.append(f"wk{week}: row without couple header: {texts[:3]}")
                    # header-less continuation rows have fewer cells: align from column 1 (Scores)
                    cols = list(zip(header[1:], cells, texts))
                for h, c, t in cols:
                    k = h.lower()
                    meta = cell_meta(c)
                    if k.startswith("score"):
                        ps = parse_score(t)
                        rec["score_raw"] = t
                        if ps:
                            rec["total"], rec["judges"] = ps
                        elif t:
                            anomalies.append(f"wk{week} {rec.get('couple')}: unparsed score {t!r}")
                    elif k.startswith("dance"):
                        rec["dance"] = t
                        rec["dance_link"] = (meta.get("links") or [None])[0]
                    elif k.startswith("music"):
                        parts = re.split(r"\s+[—–]\s+", t, 1)
                        rec["song"] = parts[0].strip('" ')
                        rec["artist"] = parts[1] if len(parts) > 1 else None
                        rec["music_links"] = json.dumps(meta.get("links", []), ensure_ascii=False)
                    elif k.startswith("result"):
                        rec["result"] = t
                        rec["result_bg"] = meta.get("bg")
                    elif k.startswith("couple"):
                        pass
                    else:
                        rec.setdefault("extra", {})[h] = t
                if "extra" in rec:
                    rec["extra"] = json.dumps(rec["extra"], ensure_ascii=False)
                rows.append(rec)
    df = pd.DataFrame(rows)
    out = out_dir() / f"mw_weeks_series_{n}.csv"
    df.to_csv(out, index=False)
    print(f"\n===== Series {n} (wikitext): {len(df)} rows -> {out}")
    print(df[[c for c in ["week", "couple", "total", "judges", "dance", "song", "artist", "result", "result_bg"] if c in df]].head(6).to_string())
    print("rows with no score:", int(df["total"].isna().sum()) if "total" in df else "n/a")
    print("distinct dance link targets (sample):", sorted({str(x) for x in df["dance_link"].dropna().unique()})[:8] if "dance_link" in df else None)
    print("ANOMALIES:")
    for a in anomalies[:20]:
        print("  -", a)

    # Scoring chart: show what templates carry
    sc = [s for s in code.get_sections(levels=[2], include_headings=True) if s.filter_headings()[0].title.strip() == "Scoring chart"]
    if sc:
        tbl = sc[0].filter_tags(matches=lambda t: t.tag == "table")[0]
        names = {}
        for tpl in tbl.contents.filter_templates():
            nm = tpl.name.strip().lower()
            names[nm] = names.get(nm, 0) + 1
        print("\nScoring chart templates used:", names)
        # First data row cells with meta
        for cells in list(table_rows(tbl))[2:4]:
            print("  row:", [(clean(c.contents), {k: v for k, v in cell_meta(c).items() if k != 'links'}) for c in cells][:8])


if __name__ == "__main__":
    for a in sys.argv[1:] or ["6", "24"]:
        main(int(a))
