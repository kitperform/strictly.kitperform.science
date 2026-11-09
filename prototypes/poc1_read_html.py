"""POC 1: pandas.read_html on the repo HTML captures (legacy S6, Parsoid S24).

Reports every table that comes out, what it looks like, and the problems.
Usage: python -I prototypes/poc1_read_html.py 6 24
"""
import io, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from sdc_common import html_path

pd.set_option("display.width", 220, "display.max_columns", 30, "display.max_colwidth", 40)


def classify(df, i):
    cols = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in df.columns]
    joined = " ".join(cols)
    if "Notability" in joined:
        return "couples"
    if "Rank by" in joined or "Rank byaverage" in joined.replace(" ", ""):
        return "average"
    if "Official rating" in joined:
        return "ratings"
    if "Pl." in joined and "Week" in joined:
        return "scoring_chart"
    if "Dance" in joined and "Music" in joined:
        return "weekly"
    if "Couple" in joined and "Week" in joined:
        return "dance_chart"
    return "other"


def main(n):
    html = html_path(n).read_text(encoding="utf-8")
    tables = pd.read_html(io.StringIO(html), flavor="lxml")  # default: match any table with text
    print(f"\n===== Series {n}: pandas.read_html found {len(tables)} tables =====")
    kinds = {}
    for i, df in enumerate(tables):
        k = classify(df, i)
        kinds.setdefault(k, []).append(i)
    print({k: len(v) for k, v in kinds.items()})

    # Weekly tables: how clean are they?
    for i in kinds.get("weekly", [])[:3] + kinds.get("weekly", [])[-1:]:
        df = tables[i]
        print(f"\n--- weekly table #{i} shape={df.shape} columns={list(df.columns)}")
        print(df.head(4).to_string())
        sc = [c for c in df.columns if str(c).startswith("Score")]
        if sc:
            bad = df[~df[sc[0]].astype(str).str.match(r"^\d+ \((\d+, )+\d+\)$")]
            if len(bad):
                print("  non-standard Score cells:", bad[sc[0]].astype(str).tolist()[:6])

    for i in kinds.get("scoring_chart", []):
        df = tables[i]
        print(f"\n--- scoring chart #{i} shape={df.shape}")
        print("columns (MultiIndex?):", type(df.columns).__name__, list(df.columns)[:6], "...")
        print(df.head(3).to_string())
        flat = [str(v) for v in df.to_numpy().ravel()]
        odd = sorted({v for v in flat if not re.fullmatch(r"\d+|nan|\d+(st|nd|rd|th)", v)})
        print("  non-numeric cell values (sample):", odd[:12])

    for i in kinds.get("average", []):
        df = tables[i]
        print(f"\n--- average chart #{i} shape={df.shape} cols={list(df.columns)}")
        print(df.head(6).to_string())

    for i in kinds.get("couples", []):
        df = tables[i]
        print(f"\n--- couples #{i} shape={df.shape} cols={list(df.columns)}")
        print(df.head(3).to_string())
        print("  NOTE: wiki links (identity!) are lost by read_html; only display text survives.")

    for i in kinds.get("dance_chart", []):
        df = tables[i]
        print(f"\n--- dance chart #{i} shape={df.shape}")
        print(df.head(3).to_string())

    for i in kinds.get("ratings", []):
        df = tables[i]
        print(f"\n--- ratings #{i} shape={df.shape} cols={list(df.columns)}")
        print(df.tail(3).to_string())

    print("\n--- 'other' tables (infobox, legend, navbox...):", [tables[i].shape for i in kinds.get("other", [])][:10])


if __name__ == "__main__":
    for a in sys.argv[1:] or ["6", "24"]:
        main(int(a))
