"""Shared helpers for the Strictly table-structure proof of concept.

Paths, a rowspan/colspan-aware HTML table grid expander, and cell-text
normalisation that works on both legacy-parser HTML (series 1-21 captures,
2024) and Parsoid HTML (series 22-24 captures, Nov 2026).

Run the prototypes from the repository root, e.g.
    python -I prototypes/poc2_bs4_weeks.py 6 24
"""
import os
import re
from pathlib import Path

# Paths -------------------------------------------------------------------
# Everything is resolved relative to the repository root (the parent of this
# prototypes/ folder) so the scripts run from any working directory. Each
# location can be overridden with an environment variable for experiments.
REPO = Path(os.environ.get("SDC_REPO", Path(__file__).resolve().parent.parent))
HTML_DIR = Path(os.environ.get("SDC_HTML_DIR", REPO / "data/wikipedia/series"))
WIKITEXT_DIR = Path(os.environ.get("SDC_WIKITEXT_DIR", REPO / "data/wikipedia/wikitext"))
OUT_DIR = Path(os.environ.get("SDC_OUT_DIR", REPO / "prototypes/out"))
# A Parsoid REST capture (api/rest_v1/page/html/...) if one has been saved;
# falls back to the repo's series 24 read-view capture, which is also Parsoid output.
PARSOID_PATH = Path(os.environ.get("SDC_PARSOID_HTML", REPO / "data/wikipedia/parsoid/series_24.parsoid.html"))


def html_path(n: int) -> Path:
    """data/wikipedia/series/0NN/Strictly_Come_Dancing_series_N.html (as fetched by scripts/fetch-wikipedia.sh)."""
    return HTML_DIR / f"{n:03d}" / f"Strictly_Come_Dancing_series_{n}.html"


def wikitext_path(n: int) -> Path:
    """data/wikipedia/wikitext/series_N.wikitext (raw wikitext; see prototypes/README.md for how to fetch it)."""
    return WIKITEXT_DIR / f"series_{n}.wikitext"


def parsoid_path() -> Path:
    return PARSOID_PATH if PARSOID_PATH.exists() else html_path(24)


def out_dir() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR


# Regexes ------------------------------------------------------------------
# "18 (4, 5, 4, 5)"  -> total 18, judges [4,5,4,5]; also 3- and 5-judge weeks
SCORE_RE = re.compile(r"^\s*(\d+)\s*\(\s*((?:\d+\s*,\s*)*\d+)\s*\)\s*$")
# scoring-chart multi-dance cells "31+36=67", "+39+40=156", "35+38+37=110"
SUM_RE = re.compile(r"^\s*\+?((?:\d+\+)*\d+)=(\d+)\s*$")
FOOTNOTE_RE = re.compile(r"\[[a-z0-9]+\]")  # [a], [12] rendered ref markers


def cell_text(el, drop_refs=True) -> str:
    """Visible text of a BeautifulSoup cell with footnote/ref markers removed.

    Works for legacy (<sup class="reference">) and Parsoid (<sup class="mw-ref
    reference">) markup, and keeps the dagger characters so the caller can
    detect highest/lowest-of-the-night markers.
    """
    el = el.__copy__() if hasattr(el, "__copy__") else el
    if drop_refs:
        for sup in el.find_all("sup"):
            cls = " ".join(sup.get("class", []))
            if "reference" in cls or "mw-ref" in cls:
                sup.decompose()
    for br in el.find_all("br"):
        br.replace_with(" | ")
    txt = el.get_text("")
    txt = txt.replace("\xa0", " ")
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def table_grid(table, text_fn=cell_text):
    """Expand an HTML <table> into a list of rows of dicts, honouring rowspan
    and colspan so every logical row has every column. Each cell dict has
    text, el (the BeautifulSoup tag), is_header, spanned (True when copied
    from a rowspan/colspan origin)."""
    grid = []  # list of lists
    pending = {}  # col index -> (remaining_rows, cell)
    rows = table.find_all("tr", recursive=False)
    if not rows:
        tbody = table.find("tbody")
        rows = tbody.find_all("tr", recursive=False) if tbody else []
    for tr in rows:
        row = []
        col = 0
        cells = tr.find_all(["th", "td"], recursive=False)
        ci = 0
        while ci < len(cells) or col in pending:
            if col in pending:
                remaining, cell = pending[col]
                row.append({**cell, "spanned": True, "colspanned": False})
                remaining -= 1
                if remaining == 0:
                    del pending[col]
                else:
                    pending[col] = (remaining, cell)
                col += 1
                continue
            if ci >= len(cells):
                break
            c = cells[ci]
            ci += 1
            try:
                rs = int(c.get("rowspan", 1))
            except ValueError:
                rs = 1
            try:
                cs = int(c.get("colspan", 1))
            except ValueError:
                cs = 1
            cell = {
                "text": text_fn(c),
                "el": c,
                "is_header": c.name == "th",
                "bg": (c.get("bgcolor") or _style_bg(c.get("style", ""))),
                "spanned": False,
            }
            for k in range(cs):
                row.append({**cell, "spanned": k > 0, "colspanned": k > 0})
                if rs > 1:
                    pending[col] = (rs - 1, cell)
                col += 1
        grid.append(row)
    return grid


def _style_bg(style: str):
    m = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style or "")
    return m.group(1).strip() if m else None


def parse_score(txt: str):
    """'18 (4, 5, 4, 5)' -> (18, [4,5,4,5]); returns None if not a score."""
    m = SCORE_RE.match(txt)
    if not m:
        return None
    total = int(m.group(1))
    judges = [int(x) for x in re.split(r"\s*,\s*", m.group(2))]
    return total, judges


def split_music(txt: str):
    """'"Song" — Artist' -> (song, artist). Handles em dash, en dash, 'from X'."""
    t = txt.strip()
    parts = re.split(r"\s+[—–]\s+", t, maxsplit=1)
    song = parts[0].strip().strip('"“”')
    artist = parts[1].strip() if len(parts) > 1 else None
    return song, artist
