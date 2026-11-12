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
            out.append({
                "celeb_name": celeb["text"], "celeb_title": cl[0][1] if cl else None,
                "pro_name": pro["text"], "pro_title": pl[0][1] if pl else None, "pro_spanned": pro["spanned"],
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
        trs = table.find_all("tr")
        head0 = trs[0].find_all(["th", "td"])
        head1 = trs[1].find_all(["th", "td"])
        col_labels = [header_text(c) for c in head1] if head1 and all(c.name == "th" for c in head1) else []
        rows = []
        for tr in trs[2:] if col_labels else trs[1:]:
            cells = tr.find_all(["th", "td"])
            if not cells:
                continue
            label = cell_text(cells[0])
            place = cell_text(cells[1]) if len(cells) > 1 else ""
            data = []
            for c in cells[2:]:
                raw = cell_text(c)
                flags = []
                if "†" in raw:
                    flags.append("dagger")
                if "‡" in raw:
                    flags.append("double_dagger")
                if c.find("b"):
                    flags.append("bold")
                if c.find("i"):
                    flags.append("italic")
                if c.get("rowspan"):
                    flags.append("rowspan")
                if c.get("colspan"):
                    flags.append("colspan")
                data.append({"text": raw, "flags": flags, "bg": style_bg(c), "efn": efn_names(c), "el": c})
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
        return {"col_labels": col_labels, "rows": rows, "legend": legend, "notes": notes, "intro": head_text, "head0": [header_text(c) for c in head0]}

    def dance_chart_bullets(self):
        sec = self.section("Dance_chart")
        if sec is None:
            return []
        return [cell_text(li, br=" ") for ul in sec.find_all("ul") for li in ul.find_all("li")]

    def professional_dancers_text(self):
        sec = self.section("Professional_dancers")
        return [(cell_text(p, br=" "), links(p)) for p in sec.find_all("p", recursive=False)] if sec is not None else []
