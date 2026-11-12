"""HTML table helpers that work on Parsoid and legacy MediaWiki HTML."""
import re

REF_RE = re.compile(r"\s*\[\s*[a-z0-9]+\s*\]")


def cell_text(el, drop_refs=True, br=" | ") -> str:
    """Visible text with <ref> markers removed and <br> turned into a separator."""
    el = el.__copy__()
    if drop_refs:
        for sup in el.find_all("sup"):
            cls = " ".join(sup.get("class", []))
            if "reference" in cls or "mw-ref" in cls:
                sup.decompose()
    for b in el.find_all("br"):
        b.replace_with(br)
    txt = el.get_text("").replace("\xa0", " ")
    return re.sub(r"\s+", " ", txt).strip()


def header_text(el) -> str:
    return REF_RE.sub("", cell_text(el)).strip()


def links(el):
    """[(link text, wiki title or None, href)] for every anchor in the cell."""
    from .keys import wiki_title_from_href
    out = []
    for a in el.find_all("a"):
        if a.find_parent("sup"):
            continue
        href = a.get("href", "")
        out.append((a.get_text(" ", strip=True), wiki_title_from_href(href), href))
    return out


def style_bg(el):
    bg = el.get("bgcolor")
    if bg:
        return bg.strip().lower()
    m = re.search(r"background(?:-color)?\s*:\s*([^;]+)", el.get("style", "") or "")
    return m.group(1).strip().lower() if m else None


def efn_names(el):
    """Names of explanatory footnotes referenced from the cell (Parsoid: #cite_note-NAME-n)."""
    names = []
    for sup in el.find_all("sup"):
        for a in sup.find_all("a"):
            href = a.get("href", "")
            m = re.search(r"#cite_note-([A-Za-z][A-Za-z0-9_]*)-\d+$", href)
            if m:
                names.append(m.group(1))
    return names


def table_grid(table):
    """Expand a <table> into rows of cell dicts honouring rowspan/colspan.

    Each cell: text, el, is_header, bg, spanned (copied from a rowspan origin),
    colspanned (copied from a colspan origin).
    """
    grid = []
    pending = {}
    rows = table.find_all("tr", recursive=False)
    if not rows:
        tbody = table.find("tbody")
        rows = tbody.find_all("tr", recursive=False) if tbody else []
    for tr in rows:
        row, col, ci = [], 0, 0
        cells = tr.find_all(["th", "td"], recursive=False)
        if not cells and not pending:
            continue
        while ci < len(cells) or col in pending:
            if col in pending:
                remaining, cell = pending[col]
                row.append({**cell, "spanned": True, "colspanned": cell.get("colspanned", False)})
                if remaining - 1 == 0:
                    del pending[col]
                else:
                    pending[col] = (remaining - 1, cell)
                col += 1
                continue
            if ci >= len(cells):
                break
            c = cells[ci]
            ci += 1
            rs = _int(c.get("rowspan"), 1)
            cs = _int(c.get("colspan"), 1)
            cell = {"text": cell_text(c), "el": c, "is_header": c.name == "th", "bg": style_bg(c), "spanned": False}
            for k in range(cs):
                row.append({**cell, "spanned": k > 0, "colspanned": k > 0})
                if rs > 1:
                    pending[col] = (rs - 1, {**cell, "colspanned": k > 0})
                col += 1
        grid.append(row)
    return grid


def _int(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default
