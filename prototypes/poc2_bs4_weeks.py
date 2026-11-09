"""POC 2: BeautifulSoup walk from each "Week N" heading to its table(s).

Extracts couple, total, per-judge scores, dance, song, artist, extra theme
column, result (+ background colour), and the judges' votes list.
Works on legacy HTML (S1-21 captures) and Parsoid HTML (S22-24 captures).
Usage: python -I prototypes/poc2_bs4_weeks.py 6 24   (writes CSV to prototypes/out/)
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bs4 import BeautifulSoup
import pandas as pd
from sdc_common import html_path, table_grid, cell_text, parse_score, split_music, out_dir

WEEK_RE = re.compile(r"^Week_(\d+)")


def heading_level(tag):
    return int(tag.name[1]) if tag.name in ("h2", "h3", "h4", "h5") else None


def iter_week_sections(soup):
    """Yield (week_number, heading_text, [elements until next h2/h3])."""
    for h in soup.find_all(["h3"]):
        hid = h.get("id", "")
        m = WEEK_RE.match(hid)
        if not m:
            continue
        # In MW >= 1.42 the <hN> sits inside <div class="mw-heading">; walk from that div.
        start = h.parent if "mw-heading" in " ".join(h.parent.get("class", [])) else h
        els = []
        for sib in start.next_siblings:
            if getattr(sib, "name", None) is None:
                continue
            if sib.name in ("h2", "h3") or (sib.name == "div" and "mw-heading2" in " ".join(sib.get("class", [])) or sib.name == "div" and "mw-heading3" in " ".join(sib.get("class", []))):
                break
            if sib.name == "section":  # Parsoid REST output wraps sections
                els.extend([c for c in sib.children if getattr(c, "name", None)])
            else:
                els.append(sib)
        yield int(m.group(1)), cell_text(h), els


def parse_week_table(table, week, show_label=None):
    grid = table_grid(table)
    if not grid:
        return [], []
    header = [c["text"] for c in grid[0]]
    header = [re.sub(r"\[\d+\]", "", h).strip() for h in header]  # strip <ref> markers like Scores[6]
    rows = []
    anomalies = []
    for r in grid[1:]:
        if len(r) != len(header):
            anomalies.append(f"wk{week}: row has {len(r)} cells vs {len(header)} header cells: {[c['text'] for c in r][:5]}")
        rec = {"week": week, "show": show_label}
        for h, c in zip(header, r):
            key = h.lower()
            if key.startswith("couple"):
                rec["couple"] = c["text"]
                rec["couple_rowspan"] = c["spanned"]
            elif key.startswith("score"):
                ps = parse_score(c["text"])
                rec["score_raw"] = c["text"]
                if ps:
                    rec["total"], rec["judges"] = ps
                    rec["n_judges"] = len(ps[1])
                    if sum(ps[1]) != ps[0]:
                        anomalies.append(f"wk{week} {rec.get('couple')}: judges {ps[1]} do not sum to {ps[0]}")
                elif c["text"]:
                    anomalies.append(f"wk{week} {rec.get('couple')}: unparsed score cell {c['text']!r}")
            elif key.startswith("dance"):
                rec["dance"] = c["text"]
            elif key.startswith("music"):
                rec["music_raw"] = c["text"]
                rec["song"], rec["artist"] = split_music(c["text"])
            elif key.startswith("result"):
                if c.get("colspanned"):
                    continue  # group-dance rows: Music cell has colspan=2 and swallows the Result column
                rec["result"] = c["text"]
                rec["result_bg"] = c["bg"]
            else:
                rec.setdefault("extra", {})[h] = c["text"]
        if "extra" in rec:
            rec["extra"] = json.dumps(rec["extra"], ensure_ascii=False)
        rows.append(rec)
    return rows, anomalies


def parse_votes(els):
    """Judges' votes list: <dl><dt>Judges' votes to save</dt></dl><ul><li>Surname: X & Y</li>..."""
    out = []
    for i, el in enumerate(els):
        txt = cell_text(el) if el.name in ("dl", "p", "b") else ""
        if re.search(r"Judges.? votes to (save|eliminate)", txt):
            kind = "save" if "save" in txt else "eliminate"
            # the <ul> is the next element
            for nxt in els[i + 1:]:
                if nxt.name == "ul":
                    for li in nxt.find_all("li"):
                        t = cell_text(li)
                        m = re.match(r"^([^:]+):\s*(.*)$", t)
                        if m:
                            out.append({"judge": m.group(1).strip(), "vote": m.group(2).strip(), "kind": kind,
                                        "did_not_vote": t.lower().startswith(m.group(1).lower() + ": did not vote")})
                    break
    return out


def main(n):
    soup = BeautifulSoup(html_path(n).read_text(encoding="utf-8"), "lxml")
    all_rows, all_votes, anomalies = [], [], []
    for week, title, els in iter_week_sections(soup):
        tables = []
        label = None
        for el in els:
            if el.name == "table" and "wikitable" in " ".join(el.get("class", [])):
                tables.append((label, el))
            elif el.name == "dl" and re.match(r"(Show|Night) \d", cell_text(el)):
                label = cell_text(el)
            elif el.name == "div" and "mw-heading4" in " ".join(el.get("class", [])):
                label = cell_text(el)
            if el.name == "div":
                for t in el.find_all("table"):
                    if "wikitable" in " ".join(t.get("class", [])):
                        tables.append((label, t))
        if not tables:
            anomalies.append(f"wk{week} ({title}): NO wikitable found in section")
        for label, t in tables:
            rows, an = parse_week_table(t, week, label)
            all_rows += rows
            anomalies += an
        votes = parse_votes(els)
        for v in votes:
            v["week"] = week
        all_votes += votes
        if not votes:
            anomalies.append(f"wk{week}: no judges' votes list (no elimination / in progress?)")
    df = pd.DataFrame(all_rows)
    out = out_dir() / f"bs4_weeks_series_{n}.csv"
    df.to_csv(out, index=False)
    print(f"\n===== Series {n}: {len(df)} performance rows, {len(all_votes)} judge votes -> {out}")
    print(df[[c for c in ["week", "show", "couple", "total", "judges", "dance", "song", "artist", "result", "result_bg"] if c in df]].head(8).to_string())
    if "n_judges" in df:
        print("judge-count distribution:", df["n_judges"].value_counts(dropna=False).to_dict())
    print("rows with no parsed score (group dances / in-progress / byes):", int(df["total"].isna().sum()) if "total" in df else "n/a")
    print("distinct results:", sorted(df["result"].dropna().unique().tolist()) if "result" in df else None)
    print("distinct result backgrounds:", sorted({str(x) for x in df["result_bg"].dropna().unique()}) if "result_bg" in df else None)
    print("rows with extra theme columns:", int(df["extra"].notna().sum()) if "extra" in df else 0, "| sample:", df["extra"].dropna().head(2).tolist() if "extra" in df else None)
    print("music cells without an artist (no dash):", int(df["artist"].isna().sum()) if "artist" in df else None, df.loc[df["artist"].isna(), "music_raw"].head(3).tolist() if "artist" in df else None)
    print("\nANOMALIES:")
    for a in anomalies[:25]:
        print("  -", a)
    pd.DataFrame(all_votes).to_csv(out_dir() / f"bs4_votes_series_{n}.csv", index=False)
    if all_votes:
        print("\nvotes sample:", all_votes[:3], "... did-not-vote entries:", sum(v["did_not_vote"] for v in all_votes))


if __name__ == "__main__":
    for a in sys.argv[1:] or ["6", "24"]:
        main(int(a))
