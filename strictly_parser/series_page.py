"""Read-only view of one captured Wikipedia series page (Parsoid HTML)."""
import re
from bs4 import BeautifulSoup
from .htmlgrid import cell_text, header_text, links, table_grid, efn_names, style_bg

WEEK_ID_RE = re.compile(r"^Week_(\d+)")
HEADING_RE = re.compile(r"^Week (\d+)(?::\s*(.*?))?\s*(?:\((.*?)\))?\s*$")


class SeriesPage:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "lxml")

    # -- sections ---------------------------------------------------------
    def heading(self, prefix):
        return self.soup.find(lambda t: t.name in ("h2", "h3", "h4") and (t.get("id") or "").startswith(prefix))

    def section(self, prefix):
        h = self.heading(prefix)
        return h.find_parent("section") if h else None

    @staticmethod
    def children(section):
        return [c for c in section.children if getattr(c, "name", None)] if section is not None else []

    def paragraphs(self, section):
        return [(cell_text(p, br=" "), bool(p.find("i"))) for p in section.find_all("p", recursive=False)] if section is not None else []

    def lead_text(self):
        lead = self.soup.find("section", attrs={"data-mw-section-id": "0"})
        return " ".join(cell_text(p, br=" ") for p in lead.find_all("p", recursive=False)) if lead else ""

    # -- infobox ------------------------------------------------------------
    def infobox(self):
        ib = self.soup.find("table", class_=re.compile("infobox"))
        out = {}
        if ib is None:
            return out
        for r in ib.find_all("tr"):
            th, td = r.find("th"), r.find("td")
            if th and td:
                out[header_text(th)] = cell_text(td, br=" ")
        return out

    # -- ratings ------------------------------------------------------------
    def ratings_rows(self):
        sec = self.section("Ratings")
        if sec is None:
            return []
        table = sec.find("table")
        rows = []
        for r in table.find_all("tr")[1:]:
            cells = r.find_all(["th", "td"])
            if not cells:
                continue
            vals = [cell_text(c) for c in cells]
            rows.append({"label": vals[0], "date_text": vals[1] if len(vals) > 1 else "", "rating": vals[2] if len(vals) > 2 else "",
                         "rank_bbc_one": vals[3] if len(vals) > 3 else "", "rank_all_uk": vals[4] if len(vals) > 4 else "",
                         "share_pct": vals[5] if len(vals) > 5 else ""})
        return rows

    # -- couples -------------------------------------------------------------
    def couples_rows(self):
        sec = self.section("Couples")
        table = sec.find("table")
        grid = table_grid(table)
        header = [header_text(c["el"]) for c in grid[0]]
        idx = {h.lower(): i for i, h in enumerate(header)}
        out = []
        for r in grid[1:]:
            if all(c["is_header"] for c in r):
                continue
            def col(name):
                for k, i in idx.items():
                    if k.startswith(name):
                        return r[i] if i < len(r) else None
                return None
            celeb, pro, status, notab = col("celebrity"), col("professional"), col("status"), col("notability")
            if celeb is None or pro is None:
                continue
            cl, pl = links(celeb["el"]), links(pro["el"])
            # 'Amy Dowden (Weeks 1–6) | Lauren Oakley (Weeks 7–13)' -> one entry per professional with the stated range
            pros = []
            for seg in [s.strip() for s in pro["text"].split(" | ") if s.strip()]:
                m = re.match(r"^(.*?)\s*(?:\((?:Weeks?|Wks?\.?)\s*(\d+)(?:\s*[–-]\s*(\d+))?\))?$", seg)
                name = (m.group(1) if m else seg).strip()
                title = next((w for t, w, h in pl if t == name and w), None)
                pros.append({"name": name, "title": title, "week_from": int(m.group(2)) if m and m.group(2) else None,
                             "week_to": int(m.group(3)) if m and m.group(3) else (int(m.group(2)) if m and m.group(2) else None)})
            out.append({
                "celeb_name": celeb["text"], "celeb_title": cl[0][1] if cl else None,
                "pro_name": pros[0]["name"] if pros else pro["text"], "pro_title": pros[0]["title"] if pros else (pl[0][1] if pl else None),
                "pros": pros, "pro_cell_raw": pro["text"], "pro_spanned": pro["spanned"],
                "notability": notab["text"] if notab else None,
                "status_text": status["text"] if status else "", "status_bg": status["bg"] if status else None,
                "status_spanned": status["spanned"] if status else False,
            })
        return out

    # -- weekly scores --------------------------------------------------------
    def judge_order_links(self):
        """Links in the 'listed in this order' sentence under Weekly scores."""
        sec = self.section("Weekly_scores")
        for p in sec.find_all("p", recursive=False):
            if "order" in p.get_text():
                return [(t, w) for t, w, h in links(p) if w]
        return []

    def weeks(self):
        """One dict per 'Week N' heading, in page order."""
        out = []
        for h in self.soup.find_all(["h3", "h4"]):
            m = WEEK_ID_RE.match(h.get("id") or "")
            if not m:
                continue
            sec = h.find_parent("section")
            heading = cell_text(h, br=" ")
            hm = HEADING_RE.match(heading)
            kids = self.children(sec)
            tables = [t for t in sec.find_all("table") if "wikitable" in " ".join(t.get("class", []))]
            theme = (hm.group(2) or "").strip() if hm else ""
            stage = (hm.group(3) or "").strip() if hm else ""
            if re.fullmatch(r"(quarter-?\s*final|semi-?\s*final|final)", theme, re.I):
                theme, stage = "", theme
            order_links = []
            for p in sec.find_all("p", recursive=False):
                if re.search(r"listed in this order|in the following order", p.get_text()):
                    order_links = [(t, w) for t, w, h in links(p)] or [(n.strip(), None) for n in re.split(r",| and ", cell_text(p).split(":")[-1]) if n.strip()]
            week = {
                "number": int(m.group(1)), "heading": heading,
                "theme": theme,
                "stage_text": stage, "order_links": order_links,
                "paragraphs": self.paragraphs(sec),
                "sub_labels": [], "tables": [], "votes": None, "votes_direction": None, "votes_heading": None,
                "guest_lists": [],
            }
            # sub-labels (';Show 1' renders as <dl><dt>) and tables in order
            label = None
            for el in kids:
                if el.name == "dl" and re.match(r"^(Show|Night) \d", cell_text(el)):
                    label = cell_text(el)
                elif el.name == "table" and el in tables:
                    week["tables"].append((label, el))
                elif el.name == "div":
                    for t in el.find_all("table"):
                        if t in tables:
                            week["tables"].append((label, t))
                elif el.name == "section":
                    sub_h = el.find(["h4", "h5"])
                    sub_label = cell_text(sub_h, br=" ") if sub_h else label
                    for t in el.find_all("table"):
                        if t in tables:
                            week["tables"].append((sub_label if re.match(r"^(Show|Night) \d", sub_label or "") else label, t))
                    week["paragraphs"].extend(self.paragraphs(el))
            # judges' votes list: heading in <dl>/<p>, items in the next <ul>
            for i, el in enumerate(kids):
                if el.name in ("dl", "p"):
                    tx = cell_text(el)
                    vm = re.search(r"Judges.? votes to (save|eliminate)", tx)
                    if vm:
                        week["votes_direction"] = vm.group(1)
                        week["votes_heading"] = tx
                        for nxt in kids[i + 1:]:
                            if nxt.name == "ul":
                                week["votes"] = [cell_text(li, br=" ") for li in nxt.find_all("li", recursive=False)]
                                break
                        break
            for el in kids:
                if el.name == "ul" and "Musical guest" in cell_text(el):
                    week["guest_lists"].append(cell_text(el, br=" "))
            out.append(week)
        return out

    # -- scoring chart ------------------------------------------------------------
    def scoring_chart(self):
        """{'col_labels': [...], 'rows': [{'label','place','cells':[{text,flags,bg,efn}]}], 'legend': [...], 'notes': {...}}"""
        sec = self.section("Scoring_chart")
        table = sec.find("table")
        grid = table_grid(table)
        head0 = [c["el"] for c in grid[0]]
        two_header_rows = len(grid) > 1 and all(c["is_header"] for c in grid[1])
        col_labels = [header_text(c["el"]) for c in grid[1][2:]] if two_header_rows else [header_text(c["el"]) for c in grid[0][2:]]
        col_efn = [efn_names(c["el"]) for c in (grid[1][2:] if two_header_rows else grid[0][2:])]
        rows = []
        for grow in grid[2:] if two_header_rows else grid[1:]:
            if not grow or all(c["is_header"] for c in grow):
                continue
            label = grow[0]["text"]
            place = grow[1]["text"] if len(grow) > 1 else ""
            data = []
            for gc in grow[2:]:
                c = gc["el"]
                raw = gc["text"]
                flags = []
                if "†" in raw:
                    flags.append("dagger")
                if "‡" in raw:
                    flags.append("double_dagger")
                if c.find("b"):
                    flags.append("bold")
                if c.find("i"):
                    flags.append("italic")
                if gc["spanned"]:
                    flags.append("rowspan_copy")
                if gc.get("colspanned"):
                    flags.append("colspan_copy")
                data.append({"text": raw, "flags": flags, "bg": gc["bg"], "efn": efn_names(c), "el": c})
            rows.append({"label": label, "place": place, "cells": data})
        legend = []
        for li in sec.find_all("li"):
            sw = li.find("span", class_=re.compile("legend-color"))
            legend.append(((sw.get("style") if sw else None), cell_text(li)))
        notes = {}
        for ol in sec.find_all("ol", class_=re.compile("references")):
            for li in ol.find_all("li"):
                nid = li.get("id") or ""
                m = re.match(r"cite_note-([A-Za-z][A-Za-z0-9_]*)-\d+$", nid)
                txt = cell_text(li.find("span", class_="reference-text") or li)
                if m:
                    notes[m.group(1)] = txt
        head_text = " ".join(cell_text(p, br=" ") for p in sec.find_all("p", recursive=False))
        return {"col_labels": col_labels, "col_efn": col_efn, "rows": rows, "legend": legend, "notes": notes, "intro": head_text, "head0": [header_text(c) for c in head0]}

    def section_links(self, heading_text):
        """All (text, wiki title) links in the paragraphs of the section with this heading."""
        h = self.soup.find(lambda t: t.name in ("h2", "h3", "h4") and cell_text(t, br=" ") == heading_text)
        sec = h.find_parent("section") if h else None
        return [(t, w) for p in (sec.find_all("p", recursive=False) if sec is not None else []) for t, w, hh in links(p) if w]

    def dance_chart_bullets(self):
        sec = self.section("Dance_chart")
        if sec is None:
            return []
        return [cell_text(li, br=" ") for ul in sec.find_all("ul") for li in ul.find_all("li")]

    def couples_prose(self):
        sec = self.section("Couples")
        return [(cell_text(p, br=" "), links(p)) for p in sec.find_all("p", recursive=False)] if sec is not None else []

    def professional_dancers_text(self):
        sec = self.section("Professional_dancers")
        return [(cell_text(p, br=" "), links(p)) for p in sec.find_all("p", recursive=False)] if sec is not None else []
