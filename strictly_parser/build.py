"""Build the tidy tables for one series from its captured page.

Everything the page states is emitted with source_kind=stated; everything a
rule in docs/data-model-v2.md section 3.22 derives is 'inferred' and names
the rule in its note; facts from curated/ are 'editorial' or 'stated' as the
curated row says.
"""
import csv
import datetime as dt
import re
from collections import defaultdict, Counter
from pathlib import Path

from .keys import slugify, person_slug, week_key, series_key as mk_series_key
from .htmlgrid import table_grid, header_text, links
from .series_page import SeriesPage

MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                      "August", "September", "October", "November", "December"], 1)}
SCORE_RE = re.compile(r"^(\d+)\s*\(\s*((?:\d+\s*,\s*)*\d+)\s*\)$")
RATINGS_LABEL_RE = re.compile(r"^(?:(Launch show)|Week (\d+))(?:\s*\((Night|Show)\s*(\d)\))?(\s+results)?$")
STATUS_RE = re.compile(r"^(Eliminated (\d+)(?:st|nd|rd|th)(?:\s*&\s*(\d+)(?:st|nd|rd|th))?|Withdrew|Winners?|Runners?-up|Co-runners-up|Third place|Fourth place|Participating)(?:\s*\|?\s*on (\d{1,2} \w+ \d{4}))?", re.I)
ORDINAL_RE = re.compile(r"^(\d+)(?:st|nd|rd|th)$")
DATE_RE = re.compile(r"(\d{1,2}) (\w+)(?: (\d{4}))?")
CASTING_RE = re.compile(r"([A-Z][\w'’\-]+(?: [A-Z][\w'’\-]+){0,3}) had the casting vote")
BYE_RE = re.compile(r"granted a bye", re.I)

RESULT_MAP = {"safe": "safe", "bottom two": "bottom_two", "bottom three": "bottom_three", "eliminated": "eliminated",
              "withdrew": "withdrew", "winners": "winner", "winner": "winner", "runners-up": "runner_up", "runner-up": "runner_up",
              "third place": "third", "fourth place": "fourth"}
SUB_LABEL_CODE = {("Night", "1"): ("N1", "night1"), ("Night", "2"): ("N2", "night2"), ("Show", "1"): ("S1", "show1"), ("Show", "2"): ("S2", "show2")}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_date(text, year_hint, start_month=9):
    m = DATE_RE.search(text or "")
    if not m:
        return None
    day, month, year = int(m.group(1)), MONTHS.get(m.group(2)), m.group(3)
    if not month:
        return None
    if year:
        return dt.date(int(year), month, day)
    y = year_hint if month >= start_month else year_hint + 1
    return dt.date(y, month, day)


def first_token(name):
    return (name or "").split(" ")[0].strip()


class Build:
    def __init__(self, n, repo: Path, html_path: Path, manifest_row, curated_dir: Path):
        self.n = n
        self.repo = repo
        self.skey = mk_series_key(n)
        self.page = SeriesPage(html_path.read_text(encoding="utf-8"))
        self.manifest = manifest_row
        self.curated = curated_dir
        self.T = defaultdict(list)       # table name -> rows
        self.report = {"checks": [], "warnings": [], "unresolved": []}
        self.people = {}
        self.capture_key = f"enwiki:{manifest_row['title']}:r{manifest_row['revid']}:parsoid_html"
        self.rev_date = dt.datetime.strptime(manifest_row["timestamp"], "%Y-%m-%dT%H:%M:%SZ").date()

    # ------------------------------------------------------------ helpers
    def prov(self, locator, kind="stated", note=None):
        return {"source_capture_key": self.capture_key, "source_locator": locator, "source_kind": kind, "note": note or ""}

    def warn(self, msg):
        self.report["warnings"].append(msg)

    def check(self, name, ok, detail=""):
        self.report["checks"].append((name, bool(ok), detail))

    def add_person(self, title, display, locator, kind="person"):
        if title:
            slug, basis = person_slug(title), "wikipedia_title"
        else:
            slug, basis = "unlinked-" + slugify(display), "unlinked_name"
        if slug not in self.people:
            name = display or title
            toks = (title or display or "").replace("(", " (").split(" (")[0].split(" ")
            row = {"person_key": slug, "slug": slug, "person_kind": kind, "identity_basis": basis, "wiki_title": title or "",
                   "canonical_name": title.split(" (")[0] if title else display, "given_name": toks[0] if toks else "",
                   "family_name": " ".join(toks[1:]) if len(toks) > 1 else "", "gender": "", **self.prov(locator)}
            self.people[slug] = row
            self.T["people"].append(row)
        return slug

    # ------------------------------------------------------------ run
    def run(self):
        self.load_curated()
        self.source_capture()
        self.series_and_episodes()
        self.panel()
        self.couples()
        self.weekly()
        self.scoring_chart()
        self.couple_weeks()
        self.finish_couples()
        self.derived()
        self.integrity_checks()
        return self.T, self.report

    # ------------------------------------------------------------ curated
    def load_curated(self):
        c = self.curated
        self.meta = next((r for r in read_csv(c / "series_meta.csv") if r["series_key"] == self.skey), {})
        self.panel_curated = {r["person_slug"]: r for r in read_csv(c / "series_panels.csv") if r["series_key"] == self.skey}
        self.format_curated = [r for r in read_csv(c / "format_rules.csv") if r["series_key"] == self.skey]
        self.label_overrides = {(r["label"], r["context"]): r for r in read_csv(c / "couple_labels.csv") if r["series_key"] == self.skey}
        self.dance_lookup = {}
        for r in read_csv(c / "dances.csv"):
            self.dance_lookup[r["name"].lower()] = r
            for a in filter(None, r["aliases"].split("|")):
                self.dance_lookup[a.lower()] = r
        self.venues = {r["venue_key"]: r for r in read_csv(c / "venues.csv")}

    def source_capture(self):
        m = self.manifest
        self.T["source_captures"].append({
            "source_capture_key": self.capture_key, "wiki_title": m["title"].replace("_", " "), "page_id": m["pageid"], "revid": m["revid"],
            "parent_revid": "", "rev_timestamp": m["timestamp"], "captured_at": m["captured_at"], "sha1": m["sha1"],
            "format": "parsoid_html", "file_path": f"data/wikipedia/parsoid/series_{self.n}.parsoid.html",
            "parser_version": "strictly_parser 0.1.0", "is_current": "true", "licence_note": "CC BY-SA 4.0"})
        self.T["source_captures"].append({
            "source_capture_key": f"enwiki:{m['title']}:r{m['revid']}:wikitext", "wiki_title": m["title"].replace("_", " "), "page_id": m["pageid"],
            "revid": m["revid"], "parent_revid": "", "rev_timestamp": m["timestamp"], "captured_at": m["captured_at"], "sha1": m["sha1"],
            "format": "wikitext", "file_path": m["path"], "parser_version": "strictly_parser 0.1.0", "is_current": "true", "licence_note": "CC BY-SA 4.0"})

    # ------------------------------------------------------------ series, weeks, episodes
    def series_and_episodes(self):
        ib = self.page.infobox()
        release = ib.get("Original release", "")
        years = re.findall(r"\b(20\d\d|19\d\d)\b", release)
        self.year = int(years[0]) if years else self.rev_date.year
        self.weeks = {}          # number -> week dict
        self.episodes = {}       # episode_key -> row
        self.week_eps = defaultdict(dict)  # week -> {code: episode_key}
        headings = {w["number"]: w for w in self.page.weeks()}
        self.headings = headings
        launch_date = first_live = final_date = None
        ratings_rows = self.page.ratings_rows()
        for seq, r in enumerate(ratings_rows, 1):
            m = RATINGS_LABEL_RE.match(r["label"])
            if not m:
                self.warn(f"Ratings row label not understood: {r['label']!r}")
                continue
            date = parse_date(r["date_text"], self.year)
            if m.group(1):
                key, kind, wk, code, sub = f"{self.skey}-L", "launch", None, "L", "none"
                launch_date = date
            else:
                wk = int(m.group(2))
                if m.group(5):
                    code, kind, sub = "R", "results", "none"
                elif m.group(3):
                    code, sub = SUB_LABEL_CODE[(m.group(3), m.group(4))]
                    kind = "performance"
                else:
                    code, kind, sub = "P", "performance", "none"
                key = f"{week_key(self.skey, wk)}-{code}"
                if wk == 1 and code == "P":
                    first_live = date
                final_date = date if date and (final_date is None or date > final_date) else final_date
            status = "aired" if date and date <= self.rev_date else "scheduled"
            row = {"episode_key": key, "series_key": self.skey, "week_key": week_key(self.skey, wk) if wk else "", "episode_kind": kind,
                   "sub_label": sub, "sequence_in_week": "", "label_raw": r["label"], "listed_in_ratings": "true",
                   "air_date": date.isoformat() if date else "", "air_date_source": "ratings_table", "original_air_date": "",
                   "reschedule_reason_text": "", "status": status, "venue_key": "", "charity_beneficiary": "", "scale_max_stated": "",
                   "rating_millions": r["rating"], "rank_bbc_one": r["rank_bbc_one"], "rank_all_uk": r["rank_all_uk"], "share_pct": r["share_pct"],
                   **self.prov(f"section=Ratings; row={r['label']}")}
            self.episodes[key] = row
            if wk:
                self.week_eps[wk][code] = key
        for wk, codes in self.week_eps.items():
            for i, code in enumerate(sorted(codes, key=lambda c: ["L", "PV", "N1", "P", "S1", "N2", "S2", "R"].index(c) if c in ["L", "PV", "N1", "P", "S1", "N2", "S2", "R"] else 9), 1):
                self.episodes[codes[code]]["sequence_in_week"] = i
        # weeks: union of ratings weeks and headings
        for wk in sorted(set(self.week_eps) | set(headings)):
            h = headings.get(wk)
            stage = "regular"
            if h and h["stage_text"]:
                stage = re.sub(r"[\s-]+", "_", h["stage_text"].strip().lower())
                stage = {"quarterfinal": "quarter_final", "semifinal": "semi_final"}.get(stage, stage)
            theme_key = slugify(h["theme"]) if h and h["theme"] else ""
            if theme_key and not any(t["theme_key"] == theme_key for t in self.T["themes"]):
                kind = "film" if "movie" in theme_key or "film" in theme_key else "icon" if "icon" in theme_key else "musical" if "musical" in theme_key else "none"
                self.T["themes"].append({"theme_key": theme_key, "name": h["theme"], "theme_reference_kind": kind, "is_location_theme": "false", "wiki_title": "",
                                         **self.prov(f"section={h['heading']}")})
            self.weeks[wk] = {"week_key": week_key(self.skey, wk), "series_key": self.skey, "week_number": wk, "round_stage": stage,
                              "theme_key": theme_key, "heading_raw": h["heading"] if h else "", "dance_brief_raw": "",
                              "lifecycle_status": "scheduled",
                              **(self.prov(f"section={h['heading']}") if h else self.prov(f"section=Ratings; row=Week {wk}", "inferred", "rule S1: week evidenced only by a Ratings date"))}
        for b in self.page.dance_chart_bullets():
            m = re.match(r"^Weeks? (\d+)(?:[–-](\d+))?:\s*(.*)$", b)
            if m:
                for wk in range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1):
                    if wk in self.weeks:
                        self.weeks[wk]["dance_brief_raw"] = m.group(3)
        couples_n = len(self.page.couples_rows())
        self.T["series"].append({
            "series_key": self.skey, "series_kind": "numbered", "series_number": self.n, "parent_series_key": "", "label": f"Series {self.n}",
            "wiki_title": self.manifest["title"].replace("_", " "), "year_start": self.year,
            "launch_date": launch_date.isoformat() if launch_date else "", "first_live_date": first_live.isoformat() if first_live else "",
            "final_date": final_date.isoformat() if final_date else "", "infobox_first_aired": "", "infobox_last_aired": "",
            "infobox_num_episodes": re.sub(r"\D", "", ib.get("No. of episodes", "")), "home_venue_key": self.meta.get("home_venue_key", ""),
            "status": "in_progress" if any(e["status"] == "scheduled" for e in self.episodes.values()) else "complete",
            "couples_count_stated": couples_n, "weeks_count_stated": max(self.weeks) if self.weeks else "",
            **self.prov("infobox; section=Ratings")})
        iso = re.findall(r"\d{4}-\d{2}-\d{2}", release)
        if iso:
            self.T["series"][0]["infobox_first_aired"] = iso[0]
            self.T["series"][0]["infobox_last_aired"] = iso[-1] if len(iso) > 1 else ""
        for vk, v in self.venues.items():
            if vk == self.meta.get("home_venue_key"):
                self.T["venues"].append({"venue_key": vk, "name": v["name"], "city": v["city"], "wiki_title": v["wiki_title"], **self.prov("curated/venues.csv", "editorial", "venue lookup")})
        # format rules
        for r in self.format_curated:
            wk = int(r["week_number"]) if r["week_number"] else None
            if wk and r["episode_code"]:
                key, wkk, epk = f"{week_key(self.skey, wk)}-{r['episode_code']}-FR", week_key(self.skey, wk), f"{week_key(self.skey, wk)}-{r['episode_code']}"
            elif wk:
                key, wkk, epk = f"{week_key(self.skey, wk)}-FR", week_key(self.skey, wk), ""
            else:
                key, wkk, epk = f"{self.skey}-FR", "", ""
            row = {"format_rule_key": key, "series_key": self.skey, "week_key": wkk, "episode_key": epk}
            for col in ["elimination_mechanism", "dance_off_used", "at_risk_group_size", "vote_direction", "casting_vote_mode", "rank_tie_policy",
                        "combined_tie_break", "showdance_scored", "default_scoring_judges", "default_scale_max", "week_has_elimination", "field_subset"]:
                row[col] = r[col]
            row.update(self.prov(r["source_locator"], r["source_kind"], r["note"]))
            self.T["format_rules"].append(row)

    def effective_rule(self, wk, col):
        rows = self.T["format_rules"]
        for r in rows:
            if r["week_key"] == week_key(self.skey, wk) and not r["episode_key"] and r[col] != "":
                return r[col]
        for r in rows:
            if not r["week_key"] and r[col] != "":
                return r[col]
        return ""

    # ------------------------------------------------------------ judges
    def panel(self):
        order = self.page.judge_order_links()
        self.seat_order = []
        for text, title in order:
            slug = self.add_person(title, text, "section=Weekly scores; order sentence")
            self.seat_order.append(slug)
        self.check("judge order sentence found", bool(self.seat_order), f"{len(self.seat_order)} judges")
        for slug in self.panel_curated:
            if slug not in self.seat_order:
                self.warn(f"curated judge {slug} not in the page's seat order")
        self.head_judge = self.meta.get("head_judge_slug", "")
        for slug in self.seat_order:
            cur = self.panel_curated.get(slug, {})
            self.T["series_people"].append({
                "series_person_key": f"{self.skey}-{slug}-judge", "series_key": self.skey, "person_key": slug, "role": "judge",
                "roster_status": "regular", "display_name_in_series": self.people[slug]["canonical_name"],
                "is_head_judge": "true" if slug == self.head_judge else "false", "replaces_person_key": "", "replaced_by_person_key": "",
                "paired_with_person_key": "", "reason": "", "reason_text": "", "event_date": "", "first_week_key": "", "last_week_key": "",
                **self.prov("section=Weekly scores; order sentence")})
        self.vote_labels = {}  # slug -> label seen in votes lists

    def seat_rows_for(self, episode_key, week, locator_week):
        if any(s["episode_key"] == episode_key for s in self.T["panel_seats"]):
            return
        for i, slug in enumerate(self.seat_order, 1):
            role = self.panel_curated.get(slug, {}).get("panel_role", "regular")
            self.T["panel_seats"].append({
                "panel_seat_key": f"{episode_key}-j{i}", "episode_key": episode_key, "week_key": week_key(self.skey, week), "series_key": self.skey,
                "judge_slug": slug, "seat_position": i, "panel_role": role, "is_head_judge": "true" if slug == self.head_judge else "false",
                "is_scoring": "true", "replaces_slug": "", "absence_reason": "", "vote_label": "",
                **self.prov(f"section={locator_week}; scores column order", "inherited", "constant panel generated from the series order sentence (section 3.6)")})

    def resolve_judge_label(self, label):
        lab = label.strip().lower()
        for slug in self.seat_order:
            name = self.people[slug]["canonical_name"].lower()
            if name == lab or name.endswith(" " + lab) or slugify(name).endswith(slugify(lab)):
                return slug
        return None

    # ------------------------------------------------------------ couples
    def couples(self):
        self.couples_by_key = {}
        self.label_map = {}
        rows = self.page.couples_rows()
        for i, r in enumerate(rows, 1):
            celeb = self.add_person(r["celeb_title"], r["celeb_name"], "section=Couples")
            pro = self.add_person(r["pro_title"], r["pro_name"], "section=Couples")
            ckey = f"{self.skey}-{celeb}"
            m = STATUS_RE.match(r["status_text"].replace(" | ", " "))
            exit_kind, ordinal, ordinal2, exit_date, place_label, placement = "in_competition", None, None, None, "", ""
            if m:
                head = m.group(1).lower()
                if head.startswith("eliminated"):
                    exit_kind, ordinal = "eliminated", int(m.group(2))
                    ordinal2 = int(m.group(3)) if m.group(3) else None
                elif head.startswith("withdrew"):
                    exit_kind = "withdrew"
                elif head.startswith("participating"):
                    exit_kind = "in_competition"
                else:
                    exit_kind, place_label = "finalist", m.group(1)
                    placement = {"winner": 1, "winners": 1, "runners-up": 2, "runner-up": 2, "co-runners-up": 2, "third place": 3, "fourth place": 4}.get(head, "")
                exit_date = parse_date(m.group(4), self.year) if m.group(4) else None
            else:
                self.warn(f"Couples status not understood: {r['status_text']!r}")
            couple = {
                "couple_key": ckey, "series_key": self.skey, "celebrity_person_key": celeb, "chart_label": "",
                "celebrity_display_name": r["celeb_name"], "professional_display_name": r["pro_name"], "couple_kind": "mixed",
                "notability_text": r["notability"] or "", "final_placement": placement, "place_is_shared": "true" if head_is_shared(m) else "false",
                "place_label_raw": place_label, "exit_kind": exit_kind, "exit_ordinal": ordinal if ordinal is not None else "",
                "exit_ordinal_is_shared": "true" if ordinal2 else "false",
                "exit_ordinal_text": re.sub(r"\s*on \d.*$", "", m.group(1)) if m and ordinal else "",
                "exit_week_key": "", "exit_round_key": "", "exit_episode_key": "", "exit_date": exit_date.isoformat() if exit_date else "",
                "exit_date_kind": "", "exit_timing": "", "exit_reason": "", "exit_affected_party": "", "status_raw": r["status_text"],
                "couples_table_order": i, "_exit_date": exit_date,
                **self.prov(f"section=Couples; row={r['celeb_name']}")}
            self.couples_by_key[ckey] = couple
            self.T["couples"].append(couple)
            self.T["series_people"].append({
                "series_person_key": f"{self.skey}-{celeb}-celebrity", "series_key": self.skey, "person_key": celeb, "role": "celebrity", "roster_status": "competed",
                "display_name_in_series": r["celeb_name"], "is_head_judge": "false", "replaces_person_key": "", "replaced_by_person_key": "", "paired_with_person_key": "",
                "reason": "", "reason_text": "", "event_date": "", "first_week_key": week_key(self.skey, 1), "last_week_key": "", **self.prov("section=Couples")})
            self.T["series_people"].append({
                "series_person_key": f"{self.skey}-{pro}-professional", "series_key": self.skey, "person_key": pro, "role": "professional", "roster_status": "competed",
                "display_name_in_series": r["pro_name"], "is_head_judge": "false", "replaces_person_key": "", "replaced_by_person_key": "", "paired_with_person_key": "",
                "reason": "", "reason_text": "", "event_date": "", "first_week_key": week_key(self.skey, 1), "last_week_key": "", **self.prov("section=Couples")})
            self.T["couple_partnerships"].append({
                "couple_partnership_key": f"{ckey}-P1", "couple_key": ckey, "pro_person_key": pro, "week_from": 1, "week_to": "",
                "partnership_kind": "original", "reason": "", "reason_text": "", **self.prov(f"section=Couples; row={r['celeb_name']}")})
            self.label_map[f"{first_token(r['celeb_name'])} & {first_token(r['pro_name'])}"] = ckey
            self.T["couple_labels"].append({"couple_label_key": f"{ckey}|couples_table|{r['celeb_name']}", "couple_key": ckey, "label": r["celeb_name"],
                                            "context": "couples_table", "week_from": "", "week_to": "", "is_typo": "false", **self.prov("section=Couples")})
        # unpartnered professionals named in the Production prose
        pro_paras = self.page.professional_dancers_text()
        all_links = [(t, w) for _, lk in pro_paras for t, w, h in lk if w]
        for text, lk in pro_paras:
            m = re.search(r"^(.*?) did not receive a celebrity partner", text)
            if m:
                names = [n.strip() for n in re.split(r",| and ", m.group(1).replace("During the launch show,", "")) if n.strip()]
                for name in names:
                    title = next((w for t, w in all_links if t == name), None)
                    if not title:
                        title = next((p["wiki_title"] for p in self.people.values() if p["canonical_name"] == name and p["wiki_title"]), None)
                    slug = self.add_person(title, name, "section=Professional dancers; prose")
                    self.T["series_people"].append({
                        "series_person_key": f"{self.skey}-{slug}-professional", "series_key": self.skey, "person_key": slug, "role": "professional",
                        "roster_status": "unpartnered", "display_name_in_series": name, "is_head_judge": "false", "replaces_person_key": "", "replaced_by_person_key": "",
                        "paired_with_person_key": "", "reason": "", "reason_text": "", "event_date": "", "first_week_key": week_key(self.skey, 1), "last_week_key": "",
                        **self.prov("section=Professional dancers; prose", "stated", "did not receive a celebrity partner at the launch show")})
        self.check("couples parsed", len(self.T["couples"]) > 0, f"{len(self.T['couples'])} couples")

    def resolve_couple(self, label, context, week=None):
        lab = re.sub(r"\s+", " ", label).strip()
        ov = self.label_overrides.get((lab, context)) or self.label_overrides.get((lab, "any"))
        if ov:
            return ov["couple_key"]
        if lab in self.label_map:
            return self.label_map[lab]
        first = lab.split(" & ")[0]
        cands = [k for l, k in self.label_map.items() if l.split(" & ")[0] == first]
        if len(cands) == 1:
            self.warn(f"label {lab!r} ({context}, week {week}) resolved by celebrity first name only -> {cands[0]}")
            return cands[0]
        self.report["unresolved"].append((lab, context, week))
        return None

    def record_label(self, ckey, label, context, week):
        key = f"{ckey}|{context}|{label}"
        for r in self.T["couple_labels"]:
            if r["couple_label_key"] == key:
                r["week_to"] = week
                return
        self.T["couple_labels"].append({"couple_label_key": key, "couple_key": ckey, "label": label, "context": context, "week_from": week, "week_to": week,
                                        "is_typo": "false", **self.prov(f"section=Week {week}; table row header")})

    # ------------------------------------------------------------ weekly tables
    def weekly(self):
        self.week_rounds = {}        # week -> round_key announced in that week
        self.perf_rounds = {}        # week -> round_key whose vote the week's scores counted towards
        self.week_results = defaultdict(dict)  # week -> couple_key -> (result_status, raw)
        self.week_rows = defaultdict(set)      # week -> couple keys with a row
        self.week_has_scores = {}
        self.no_elimination_weeks = set()
        self.carry_weeks = set()
        self.casting = {}
        self.bye_notes = {}
        self.dances_seen = {}
        for wk, h in sorted(self.headings.items()):
            wkk = week_key(self.skey, wk)
            prose = " ".join(p for p, _ in h["paragraphs"])
            if re.search(r"no elimination", prose, re.I):
                self.no_elimination_weeks.add(wk)
                if re.search(r"carried over", prose, re.I):
                    self.carry_weeks.add(wk)
            cm = CASTING_RE.search(prose)
            if cm:
                slug = self.resolve_judge_label(cm.group(1))
                if slug:
                    self.casting[wk] = slug
                else:
                    self.warn(f"week {wk}: casting-vote holder {cm.group(1)!r} not resolved")
            for p, _ in h["paragraphs"]:
                if BYE_RE.search(p):
                    self.bye_notes[wk] = p
            if not h["tables"]:
                self.warn(f"week {wk}: no wikitable in section")
                continue
            for label, table in h["tables"]:
                code = "P"
                if label:
                    m = re.match(r"^(Show|Night) (\d)", label)
                    if m:
                        code = SUB_LABEL_CODE[(m.group(1), m.group(2))][0]
                ekey = self.week_eps[wk].get(code) or (self.week_eps[wk].get("P") if code == "P" else None)
                if not ekey:
                    ekey = f"{wkk}-{code}"
                    self.episodes[ekey] = {"episode_key": ekey, "series_key": self.skey, "week_key": wkk, "episode_kind": "performance", "sub_label": "none",
                                           "sequence_in_week": 1, "label_raw": "", "listed_in_ratings": "false", "air_date": "", "air_date_source": "", "original_air_date": "",
                                           "reschedule_reason_text": "", "status": "aired", "venue_key": "", "charity_beneficiary": "", "scale_max_stated": "",
                                           "rating_millions": "", "rank_bbc_one": "", "rank_all_uk": "", "share_pct": "",
                                           **self.prov(f"section={h['heading']}", "inferred", "rule E1: performance table with no Ratings row")}
                    self.week_eps[wk][code] = ekey
                self.parse_week_table(wk, h, ekey, table)
            self.parse_votes(wk, h)
        self.check("weeks with tables", len(self.week_has_scores) > 0, f"{sorted(self.week_has_scores)}")

    def parse_week_table(self, wk, h, ekey, table):
        wkk = week_key(self.skey, wk)
        grid = table_grid(table)
        header = [header_text(c["el"]) for c in grid[0]]
        roles = []
        theme_col = None
        for name in header:
            l = name.lower()
            role = "couple" if l.startswith("couple") else "scores" if l.startswith("score") else "dance" if l.startswith("dance") else \
                   "music" if l.startswith("music") else "result" if l.startswith("result") else "theme"
            if role == "theme":
                theme_col = name
            roles.append(role)
        self.week_has_scores.setdefault(wk, False)
        has_result_col = "result" in roles
        running = 0
        seq_by_couple = Counter()
        ep_aired = self.episodes[ekey]["status"] == "aired"
        for ri, row in enumerate(grid[1:], 1):
            if all(c["is_header"] for c in row):
                continue
            cells = dict(zip(roles, row))
            cc = cells.get("couple")
            if cc is None:
                continue
            label = cc["text"]
            ckey = self.resolve_couple(label, "weekly", wk)
            if not ckey:
                continue
            if not cc["spanned"]:
                running += 1
                self.record_label(ckey, label, "weekly", wk)
            seq_by_couple[ckey] += 1
            self.week_rows[wk].add(ckey)
            score_txt = cells["scores"]["text"] if "scores" in cells else ""
            dance_txt = cells["dance"]["text"] if "dance" in cells else ""
            music_txt = cells["music"]["text"] if "music" in cells else ""
            result_txt = cells["result"]["text"] if has_result_col and not cells["result"].get("colspanned") else ""
            if has_result_col and not cells["result"].get("colspanned") and not (ckey in self.week_results[wk] and self.week_results[wk][ckey][0] and not result_txt):
                self.week_results[wk][ckey] = (result_txt, cells["result"]["bg"])
            if not dance_txt and not music_txt:
                continue  # rule L1
            # dance
            dance_key, dance2_key, kind = "", "", "individual"
            if dance_txt:
                parts = re.split(r"\s*(?:&|/| and )\s*", dance_txt) if re.search(r"\s(&|and)\s|/", dance_txt) else [dance_txt]
                dance_key = self.dance_key(parts[0], wk)
                if len(parts) > 1:
                    dance2_key, kind = self.dance_key(parts[1], wk), "fusion"
                if dance_key == "showdance":
                    kind = "showdance"
                if re.search(r"-?a-?thon|marathon", dance_txt, re.I):
                    kind = "marathon"
            else:
                self.warn(f"week {wk} {label}: music but no dance stated; keyed -tbd (expected re-key)")
            suffix = dance_key or f"tbd{seq_by_couple[ckey]}"
            pkey = f"{ekey}-{ckey.split('-', 1)[1]}-{suffix}"
            if any(p["performance_key"] == pkey for p in self.T["performances"]):
                pkey += f"-{seq_by_couple[ckey]}"
                self.warn(f"duplicate performance key disambiguated: {pkey}")
            # score
            marks, total, nmarks, mode, status, points = [], "", "", "pending", "scheduled", ""
            sm = SCORE_RE.match(score_txt)
            if sm:
                total = int(sm.group(1))
                marks = [int(x) for x in re.split(r"\s*,\s*", sm.group(2))]
                nmarks, mode, status = len(marks), "judge_marks", "performed"
                self.week_has_scores[wk] = True
            elif score_txt.lower().startswith("no scores"):
                mode, status = "unscored", "performed"
            elif re.fullmatch(r"\d+", score_txt):
                points, mode, status = int(score_txt), "rank_points" if kind == "marathon" else "awarded_points", "performed"
            elif score_txt == "" and ep_aired and self.week_has_scores.get(wk):
                mode, status = "unscored", "performed"
            if ep_aired:
                self.seat_rows_for(ekey, wk, h["heading"])
            pro = next((p["pro_person_key"] for p in self.T["couple_partnerships"] if p["couple_key"] == ckey), "")
            theme_text = cells[roles[roles.index("theme")]]["text"] if theme_col and "theme" in roles else ""
            theme_links = links(row[roles.index("theme")]["el"]) if theme_col and "theme" in roles else []
            perf = {
                "performance_key": pkey, "episode_key": ekey, "week_key": wkk, "series_key": self.skey, "performer_group": "couple", "couple_key": ckey,
                "performing_pro_slug": pro, "couple_label_raw": label, "sequence_in_episode": seq_by_couple[ckey], "running_order": running if kind != "marathon" else "",
                "group_key": "", "performance_kind": kind, "selection_role": "showdance" if kind == "showdance" else "marathon" if kind == "marathon" else "unlearned",
                "performance_status": status, "scoring_mode": mode, "stated_total": total, "n_marks_stated": nmarks, "score_cell_raw": score_txt,
                "points_value": points, "dance_key": dance_key, "dance_secondary_key": dance2_key, "dance_raw": dance_txt,
                "theme_reference_text": theme_text, "theme_reference_wiki_title": next((w for t, w, hh in theme_links if w), ""), "theme_column_label": theme_col or "",
                "music_raw": music_txt, "_marks": marks,
                **self.prov(f"section={h['heading']}; table row={label}" + (f" ({dance_txt})" if dance_txt else ""))}
            self.T["performances"].append(perf)
            for i, mk in enumerate(marks, 1):
                self.T["judge_marks"].append({
                    "judge_mark_key": f"{pkey}-j{i}", "performance_key": pkey, "panel_seat_key": f"{ekey}-j{i}",
                    "judge_slug": self.seat_order[i - 1] if i - 1 < len(self.seat_order) else "", "seat_position": i, "mark": mk,
                    **self.prov(f"section={h['heading']}; table row={label}; col=Scores; mark {i}")})
            if len(marks) and len(marks) != len(self.seat_order):
                self.warn(f"week {wk} {label}: {len(marks)} marks but {len(self.seat_order)} seats")
            if music_txt and "music" in cells:
                self.parse_music(perf, cells["music"]["el"], music_txt, h["heading"], label)

    def dance_key(self, text, wk):
        t = text.strip()
        row = self.dance_lookup.get(t.lower())
        key = row["dance_key"] if row else slugify(t)
        if key not in self.dances_seen:
            self.dances_seen[key] = {"dance_key": key, "name": row["name"] if row else t, "dance_family": row["dance_family"] if row else "",
                                     "wiki_title": row["wiki_title"] if row else "", **self.prov(f"section=Week {wk}; Dance column", "stated" if not row else "editorial",
                                                                                                   "" if not row else "family from curated/dances.csv")}
            self.T["dances"].append(self.dances_seen[key])
            if not row:
                self.warn(f"dance {t!r} not in curated/dances.csv (family unknown)")
        return key

    def parse_music(self, perf, el, text, heading, label):
        lk = [(t.strip('"“” '), w) for t, w, h in links(el)]
        segments = [s for s in re.split(r"\s\|\s|\s/\s", text) if s.strip()]
        for seq, seg in enumerate(segments, 1):
            seg = seg.strip()
            src = None
            sm = re.search(r"\((?:from|theme from) (.+?)\)\s*$", seg)
            if sm:
                src, seg = sm.group(1), seg[:sm.start()].strip()
            parts = re.split(r"\s+[—–]\s+", seg, maxsplit=1)
            title = parts[0].strip().strip('"“”').strip()
            artist = parts[1].strip() if len(parts) > 1 else ""
            fm = re.match(r"^(?:theme )?from (.+?)\.?$", artist, re.I)
            if fm:
                src, artist = fm.group(1).strip(), ""
            song_wiki = next((w for t, w in lk if w and t.lower() == title.lower()), "")
            artist_wiki = next((w for t, w in lk if w and artist and t.lower() == artist.lower()), "")
            skey = f"song:{slugify(title)}:{slugify(song_wiki) if song_wiki else 'none'}"
            if not any(s["song_key"] == skey for s in self.T["songs"]):
                self.T["songs"].append({"song_key": skey, "title": title, "wiki_title": song_wiki, **self.prov(f"section={heading}; table row={label}; col=Music")})
            akey = ""
            if artist:
                akey = slugify(artist_wiki or artist)
                if not any(a["artist_key"] == akey for a in self.T["artists"]):
                    self.T["artists"].append({"artist_key": akey, "name": artist, "wiki_title": artist_wiki, **self.prov(f"section={heading}; table row={label}; col=Music")})
            self.T["performance_music"].append({
                "performance_music_key": f"{perf['performance_key']}-{slugify(title)}" + (f"-{seq}" if seq > 1 and slugify(title) == slugify(segments[0].split('—')[0].strip().strip('\"')) else ""),
                "performance_key": perf["performance_key"], "seq": seq, "song_key": skey, "artist_key": akey,
                "source_work_text": src or "", "source_work_wiki_title": next((w for t, w in lk if w and src and t.lower() == src.lower()), ""),
                "raw_text": seg, **self.prov(f"section={heading}; table row={label}; col=Music")})

    # ------------------------------------------------------------ votes and rounds
    def parse_votes(self, wk, h):
        wkk = week_key(self.skey, wk)
        votes = h["votes"] or []
        results = self.week_results.get(wk, {})
        eliminated = [c for c, (t, bg) in results.items() if RESULT_MAP.get(t.lower()) == "eliminated"]
        at_risk = [c for c, (t, bg) in results.items() if RESULT_MAP.get(t.lower()) in ("bottom_two", "bottom_three", "eliminated")]
        if not votes and not eliminated and not any(t for t, _ in results.values()):
            return  # no decision evidenced yet (pending week, or carry-over week)
        if not votes and not eliminated and wk in self.no_elimination_weeks:
            return
        combined_from = None
        for lab in self.chart_combined_labels():
            a, b = lab
            if b == wk:
                combined_from = a
        if combined_from:
            rkey, label, weeks = f"{self.skey}R{combined_from:02d}-{wk:02d}", f"{combined_from}+{wk}", list(range(combined_from, wk + 1))
            reason = "opening_weeks_format" if combined_from == 1 else "withdrawal_carry_over"
        else:
            rkey, label, weeks, reason = f"{self.skey}R{wk:02d}", str(wk), [wk], "single_week"
        direction = h["votes_direction"] or self.effective_rule(wk, "vote_direction")
        holder = self.casting.get(wk)
        holder_kind = "stated"
        if not holder and self.effective_rule(wk, "casting_vote_mode") == "head_judge":
            holder, holder_kind = self.head_judge, "inherited"
        vote_rows = []
        for pos, line in enumerate(votes, 1):
            m = re.match(r"^([^:]+):\s*(.*)$", line)
            if not m:
                self.warn(f"week {wk}: vote line not understood: {line!r}")
                continue
            jlabel, rest = m.group(1).strip(), m.group(2).strip()
            jslug = self.resolve_judge_label(jlabel)
            if not jslug:
                self.warn(f"week {wk}: judge label {jlabel!r} not resolved")
                continue
            self.vote_labels[jslug] = jlabel
            hypothetical = rest.lower().startswith("did not vote")
            cm = re.search(r"voted to (?:save|eliminate) (.+?)\.?$", rest) if hypothetical else None
            named = cm.group(1) if cm else re.sub(r"\s*\(.*\)\s*$", "", rest).rstrip(".")
            ckey = self.resolve_couple(named, "vote_list", wk)
            vote_rows.append({
                "dance_off_vote_key": f"{rkey}-{jslug}", "results_round_key": rkey, "series_key": self.skey, "week_key": wkk, "judge_slug": jslug,
                "judge_label_raw": jlabel, "couple_key": ckey or "", "vote_kind": "hypothetical_not_cast" if hypothetical else "cast",
                "is_casting_vote_stated": "true" if re.search(r"casting vote|head judge", rest, re.I) else "false", "list_position": pos,
                "raw_text": line, "vote_direction": direction, "casting_vote_slug": holder or "",
                **self.prov(f"section={h['heading']}; votes list; item {pos}")})
        # pivotal rule (check 7)
        used, inferred, holder_vote = "", "false", None
        if vote_rows and holder:
            cast = [v for v in vote_rows if v["vote_kind"] == "cast" and v["couple_key"]]
            tally = Counter(v["couple_key"] for v in cast)
            if direction == "eliminate":
                target = eliminated[0] if eliminated else (tally.most_common(1)[0][0] if tally else None)
            else:
                saved = [c for c in at_risk if c not in eliminated]
                target = saved[0] if len(saved) == 1 else (tally.most_common(1)[0][0] if tally else None)
            holder_vote = next((v for v in cast if v["judge_slug"] == holder), None)
            pivotal_ran = False
            if holder_vote is None:
                used = "false"
            elif target:
                pivotal_ran = True
                t2 = Counter(tally)
                if holder_vote["couple_key"] == target:
                    t2[target] -= 1
                others = max([n for c, n in t2.items() if c != target], default=0)
                used = "false" if t2[target] > others else "true"
            inferred = "true" if pivotal_ran and not any(v["is_casting_vote_stated"] == "true" for v in vote_rows) else "false"
        decided_at = self.week_eps[wk].get("R") or self.week_eps[wk].get("S2") or self.week_eps[wk].get("N2") or self.week_eps[wk].get("P")
        dance_off = "held" if votes else ("not_in_format" if self.effective_rule(wk, "dance_off_used") != "true" else "held")
        self.T["results_rounds"].append({
            "round_key": rkey, "series_key": self.skey, "round_kind": "final_placing" if self.weeks[wk]["round_stage"] == "final" else "standard", "label": label,
            "deciding_week_key": wkk, "decided_at_episode_key": decided_at or "", "week_keys": "|".join(week_key(self.skey, w) for w in weeks),
            "elimination_mechanism_actual": self.effective_rule(wk, "elimination_mechanism"), "exit_count": len(eliminated),
            "at_risk_group_size_actual": len(at_risk) if at_risk else "", "dance_off_status": dance_off, "vote_direction": direction,
            "casting_vote_slug": holder or "", "casting_vote_used": used, "casting_vote_inferred": inferred, "votes_recorded": "true" if votes else "false",
            "votes_carried_over": "false" if (combined_from and combined_from in self.carry_weeks) else "", "combined_reason": reason,
            "casting_vote_source_kind": holder_kind if holder else "",
            **self.prov(f"section={h['heading']}; Result column and votes list" + ("; Scoring chart column " + label if combined_from else ""),
                        "stated", "casting_vote_used=true by the pivotal rule (check 7)" if used == "true" else ("casting vote holder did not cast a vote" if used == "false" and holder and vote_rows and holder_vote is None else ""))})
        for seq, w in enumerate(weeks, 1):
            self.T["results_round_weeks"].append({"results_round_week_key": f"{rkey}|{week_key(self.skey, w)}", "round_key": rkey, "week_key": week_key(self.skey, w), "seq": seq})
            self.perf_rounds[w] = rkey
        self.week_rounds[wk] = rkey
        self.T["dance_off_votes"].extend(vote_rows)
        # vote labels onto the seats of this week's performance episode(s)
        for s in self.T["panel_seats"]:
            if s["week_key"] == wkk and s["judge_slug"] in self.vote_labels:
                s["vote_label"] = self.vote_labels[s["judge_slug"]]
        if direction == "save" and votes and eliminated:
            tally = Counter(v["couple_key"] for v in vote_rows if v["vote_kind"] == "cast")
            others = [tally[c] for c in at_risk if c != eliminated[0]]
            if others:
                self.check(f"round {rkey}: eliminated couple has fewest save votes", tally[eliminated[0]] <= min(others), str(dict(tally)))
        if direction == "eliminate" and votes and eliminated:
            tally = Counter(v["couple_key"] for v in vote_rows if v["vote_kind"] == "cast")
            self.check(f"round {rkey}: eliminated couple most named to eliminate", tally.most_common(1)[0][0] == eliminated[0], str(dict(tally)))

    def chart_combined_labels(self):
        if not hasattr(self, "_combined"):
            self._combined = []
            for lab in self.page.scoring_chart()["col_labels"]:
                m = re.fullmatch(r"(\d+)\+(\d+)", lab)
                if m:
                    self._combined.append((int(m.group(1)), int(m.group(2))))
        return self._combined

    # ------------------------------------------------------------ scoring chart (cross-check store)
    def scoring_chart(self):
        sc = self.page.scoring_chart()
        self.chart_rows = {}
        for ri, row in enumerate(sc["rows"]):
            ckey = self.resolve_couple(row["label"], "scoring_chart")
            if ckey:
                self.couples_by_key[ckey]["chart_label"] = row["label"]
                self.record_label(ckey, row["label"], "scoring_chart", "")
                pm = ORDINAL_RE.match(row["place"] or "")
                if pm and self.couples_by_key[ckey]["final_placement"] == "":
                    self.couples_by_key[ckey]["final_placement"] = int(pm.group(1))
                    self.couples_by_key[ckey]["place_label_raw"] = row["place"]
                self.chart_rows[ckey] = row
            for ci, cell in enumerate(row["cells"]):
                col = sc["col_labels"][ci] if ci < len(sc["col_labels"]) else str(ci)
                self.T["chart_cells"].append({
                    "chart_cell_key": f"{self.skey}|scoring|{ri}|{ci}", "source_capture_key": self.capture_key, "chart_kind": "scoring", "row_index": ri, "col_index": ci,
                    "row_label_raw": row["label"], "couple_key": ckey or "", "col_label_raw": col, "cell_text_raw": cell["text"], "bgcolor_norm": cell["bg"] or "",
                    "flags": "|".join(cell["flags"] + [f"efn:{n}" for n in cell["efn"]])})
        for style, text in sc["legend"]:
            self.T["chart_legends"].append({"source_capture_key": self.capture_key, "colour_norm": style or "", "meaning_text": text, "scope": "scoring"})
        for name, text in sc["notes"].items():
            self.T["chart_legends"].append({"source_capture_key": self.capture_key, "colour_norm": f"efn:{name}", "meaning_text": text, "scope": "scoring"})
        self.chart_cols = sc["col_labels"]
        self.chart_notes = sc["notes"]
        # cross-check: chart totals vs weekly totals
        for ckey, row in self.chart_rows.items():
            for ci, cell in enumerate(row["cells"]):
                col = self.chart_cols[ci] if ci < len(self.chart_cols) else ""
                txt = cell["text"].replace("†", "").replace("‡", "").strip()
                if not re.fullmatch(r"\d+(?:\+\d+)*(?:=\d+)?", txt) or not re.fullmatch(r"\d+(?:\+\d+)?", col):
                    continue
                weeks = [int(x) for x in col.split("+")]
                expected = sum(int(p["stated_total"] or 0) for p in self.T["performances"] if p["couple_key"] == ckey and int(p["week_key"][-2:]) in weeks and p["stated_total"] != "")
                stated = int(txt.split("=")[-1])
                if stated != expected:
                    self.T["discrepancies"].append({
                        "discrepancy_key": f"CoupleWeek|{week_key(self.skey, weeks[-1])}-{ckey.split('-', 1)[1]}|week_total|1", "table_name": "CoupleWeek",
                        "natural_key": f"{week_key(self.skey, weeks[-1])}-{ckey.split('-', 1)[1]}", "field_name": "d_week_total", "value_a": stated,
                        "source_capture_a_key": self.capture_key, "locator_a": f"section=Scoring chart; row={row['label']}; col={col}", "value_b": expected,
                        "value_b_origin": "derived", "source_capture_b_key": "", "locator_b": "sum of Performance.stated_total in the weekly tables",
                        "resolution": "both_kept_unresolved", "note": ""})
        self.check("scoring chart totals equal weekly totals", not self.T["discrepancies"], f"{len(self.T['discrepancies'])} discrepancies")

    # ------------------------------------------------------------ couple weeks
    def couple_weeks(self):
        max_week = max(self.weeks)
        active_week = max(self.week_has_scores or {0: 0}) if any(self.week_has_scores.values()) else 0
        self.active_week = max([w for w, v in self.week_has_scores.items() if v], default=0)
        for ckey, couple in self.couples_by_key.items():
            exit_week = self.exit_week_for(couple)
            couple["_exit_week"] = exit_week
            for wk in sorted(self.weeks):
                wkk = week_key(self.skey, wk)
                part, res, rk, raw, at_risk, danced, bye, reason, party, scope, kind, note = "pending", "pending", "", "", False, False, False, "", "", "", "stated", ""
                locator = f"section=Week {wk}"
                if exit_week and wk > exit_week:
                    part, res, kind, note = "exited", "not_applicable", "inferred", "week after the couple's exit"
                elif wk in self.headings and self.week_has_scores.get(wk):
                    heading = self.headings[wk]["heading"]
                    locator = f"section={heading}"
                    if ckey in self.week_rows[wk]:
                        part = "competed"
                        if ckey in self.week_results[wk]:
                            raw, bg = self.week_results[wk][ckey]
                            res = RESULT_MAP.get(raw.lower(), "pending" if raw == "" else raw.lower())
                            locator += f"; table row; col=Result"
                        elif wk in self.carry_weeks:
                            res, kind, note = "carried_forward", "inferred", "no Result column; prose says scores carried over"
                        elif wk in self.no_elimination_weeks:
                            res, kind, note = "no_elimination", "inferred", "no Result column; prose says no elimination"
                        if res == "pending" and self.week_rounds.get(wk):
                            res, kind, note = "safe", "inferred", "blank Result cell in a week with a decided round"
                        rk = self.week_rounds.get(wk, "")
                        if wk in self.carry_weeks:
                            rk = ""
                        at_risk = res in ("bottom_two", "bottom_three", "eliminated")
                        rnd = next((r for r in self.T["results_rounds"] if r["round_key"] == rk), None)
                        danced = at_risk and rnd is not None and rnd["dance_off_status"] == "held"
                    else:
                        cell = self.chart_cell(ckey, wk)
                        efn = cell["efn"] if cell else []
                        if any(n.lower() in ("outsick", "bye", "excused") for n in efn) or "excused" in " ".join(self.chart_notes.get(n, "") for n in efn).lower():
                            part, res, bye, scope, party = "bye", "exempt", True, "whole_week", "celebrity"
                            note_text = self.bye_notes.get(wk, "")
                            reason = "injury" if re.search(r"injur|torn|fractur|rib|broke", note_text, re.I) else "illness" if re.search(r"\bill|sick|unwell|virus|infection", note_text, re.I) else "unspecified"
                            note = f"bye stated by Scoring chart footnote {efn}; reason from week prose" if note_text else f"bye stated by Scoring chart footnote {efn}"
                            locator = f"section=Scoring chart; row={couple['chart_label']}; col={wk}"
                            rk = self.week_rounds.get(wk, "") if False else ""
                        elif couple["exit_kind"] == "withdrew" and exit_week == wk:
                            part, res, kind = "absent_withdrawn", "withdrew", "stated"
                        else:
                            part, res, kind, note = "not_scheduled", "exempt", "inferred", "active couple with no weekly row and no bye footnote"
                            self.warn(f"week {wk} {ckey}: no weekly row and no bye footnote")
                else:
                    kind, note = "inferred", "week not yet scored on the captured page"
                pro = next((p["pro_person_key"] for p in self.T["couple_partnerships"] if p["couple_key"] == ckey), "")
                self.T["couple_weeks"].append({
                    "couple_week_key": f"{wkk}-{ckey.split('-', 1)[1]}", "couple_key": ckey, "week_key": wkk, "series_key": self.skey, "week_number": wk,
                    "participation_status": part, "result_status": res, "results_round_key": rk, "at_risk": str(at_risk).lower(), "danced_off": str(danced).lower(),
                    "bye_granted": str(bye).lower(), "absence_reason": reason, "affected_party": party, "absence_scope": scope, "status_raw": raw,
                    "d_pro_slug": pro, "d_partnership_kind": "original",
                    **self.prov(locator, kind, note)})
        # week lifecycle
        for wk, w in self.weeks.items():
            if self.week_has_scores.get(wk):
                w["lifecycle_status"] = "results_in" if (self.week_rounds.get(wk) or wk in self.carry_weeks or wk in self.no_elimination_weeks) else "scores_in"
            elif wk in self.headings:
                w["lifecycle_status"] = "scheduled"
        for p in self.T["couple_partnerships"]:
            c = self.couples_by_key[p["couple_key"]]
            p["week_to"] = c["_exit_week"] or self.active_week
        self.T["weeks"] = [self.weeks[w] for w in sorted(self.weeks)]
        self.T["episodes"] = [self.episodes[k] for k in sorted(self.episodes, key=lambda k: (self.episodes[k]["air_date"] or "9999", k))]

    def chart_cell(self, ckey, wk):
        row = self.chart_rows.get(ckey)
        if not row:
            return None
        for ci, cell in enumerate(row["cells"]):
            if ci < len(self.chart_cols) and self.chart_cols[ci] == str(wk):
                return cell
        return None

    def exit_week_for(self, couple):
        d = couple.get("_exit_date")
        if not d:
            return None
        for ekey, e in self.episodes.items():
            if e["air_date"] == d.isoformat() and e["week_key"]:
                return int(e["week_key"][-2:])
        # rule E1: exit date with no Ratings row -> the week whose performance date precedes it by at most a day
        for ekey, e in self.episodes.items():
            if e["week_key"] and e["air_date"] and 0 <= (d - dt.date.fromisoformat(e["air_date"])).days <= 1:
                return int(e["week_key"][-2:])
        self.warn(f"{couple['couple_key']}: exit date {d} matches no episode")
        return None

    def finish_couples(self):
        for ckey, c in self.couples_by_key.items():
            wk = c["_exit_week"]
            if wk:
                c["exit_week_key"] = week_key(self.skey, wk)
                if c["exit_kind"] in ("eliminated", "finalist"):
                    c["exit_round_key"] = self.week_rounds.get(wk, "")
                    rnd = next((r for r in self.T["results_rounds"] if r["round_key"] == c["exit_round_key"]), None)
                    ep = rnd["decided_at_episode_key"] if rnd else ""
                    c["exit_episode_key"] = ep
                    ekind = self.episodes.get(ep, {}).get("episode_kind", "")
                    c["exit_date_kind"] = {"results": "results_episode", "performance": "performance_episode", "performance_and_results": "combined_episode"}.get(ekind, "announcement" if c["exit_date"] else "unknown")
                elif c["exit_kind"] == "withdrew":
                    c["exit_date_kind"] = "announcement" if c["exit_date"] else "unknown"
            # a couple's one weekly label becomes its partnership-era label; chart label already set
        for c in self.T["couples"]:
            for k in [k for k in c if k.startswith("_")]:
                c.pop(k)

    # ------------------------------------------------------------ derived columns
    def derived(self):
        ep_date = {e["episode_key"]: (e["air_date"] or "9999-12-31", e["sequence_in_week"] or 0) for e in self.episodes.values()}
        perfs = sorted(self.T["performances"], key=lambda p: (ep_date[p["episode_key"]], p["running_order"] or 999, p["sequence_in_episode"]))
        for i, p in enumerate(perfs, 1):
            p["d_perf_seq"] = i
            p["d_total"] = sum(p["_marks"]) if p["_marks"] else ""
            p["d_n_marks"] = len(p["_marks"]) if p["_marks"] else ""
            p["d_total_mismatch"] = "true" if p["_marks"] and sum(p["_marks"]) != p["stated_total"] else "false"
            p["d_scale_max"] = 10 * len(self.seat_order)
            p["d_total_40"] = round(p["stated_total"] * 40 / p["d_scale_max"], 2) if p["stated_total"] != "" and p["d_scale_max"] else ""
            p["d_results_round_key"] = self.perf_rounds.get(int(p["week_key"][-2:]), "")
            p["d_partnership_kind"] = "original"
            p["air_date"] = self.episodes[p["episode_key"]]["air_date"]
            p["series_number"], p["week_number"] = self.n, int(p["week_key"][-2:])
            p["round_stage"] = self.weeks[p["week_number"]]["round_stage"]
        # highest/lowest of week by stated total
        by_week = defaultdict(list)
        for p in perfs:
            if p["stated_total"] != "":
                by_week[p["week_key"]].append(p["stated_total"])
        for p in perfs:
            tots = by_week.get(p["week_key"])
            p["d_is_highest_of_week"] = "true" if tots and p["stated_total"] == max(tots) else "false"
            p["d_is_lowest_of_week"] = "true" if tots and p["stated_total"] == min(tots) else "false"
        wk_tot = defaultdict(int)
        for p in perfs:
            if p["stated_total"] != "":
                wk_tot[(p["couple_key"], p["week_key"])] += p["stated_total"]
        for cw in self.T["couple_weeks"]:
            cw["d_week_total"] = wk_tot.get((cw["couple_key"], cw["week_key"]), "")
            cw["round_stage"] = self.weeks[cw["week_number"]]["round_stage"]
            cw["series_number"] = self.n
        pmap = {p["performance_key"]: p for p in perfs}
        for jm in self.T["judge_marks"]:
            p = pmap[jm["performance_key"]]
            jm.update({"judge_name": self.people[jm["judge_slug"]]["canonical_name"] if jm["judge_slug"] in self.people else "",
                       "panel_role": self.panel_curated.get(jm["judge_slug"], {}).get("panel_role", "regular"),
                       "is_head_judge": "true" if jm["judge_slug"] == self.head_judge else "false", "episode_key": p["episode_key"], "week_key": p["week_key"],
                       "series_key": self.skey, "series_number": self.n, "week_number": p["week_number"], "round_stage": p["round_stage"], "air_date": p["air_date"],
                       "sequence_in_week": self.episodes[p["episode_key"]]["sequence_in_week"], "running_order": p["running_order"],
                       "sequence_in_episode": p["sequence_in_episode"], "d_perf_seq": p["d_perf_seq"], "couple_key": p["couple_key"], "chart_label": self.couples_by_key[p["couple_key"]]["chart_label"],
                       "performing_pro_slug": p["performing_pro_slug"], "dance_key": p["dance_key"], "performance_kind": p["performance_kind"], "scoring_mode": p["scoring_mode"],
                       "d_scale_max": p["d_scale_max"]})
        for p in perfs:
            p["chart_label"] = self.couples_by_key[p["couple_key"]]["chart_label"]
            p["sequence_in_week"] = self.episodes[p["episode_key"]]["sequence_in_week"]
            p.pop("_marks", None)
        for v in self.T["dance_off_votes"]:
            v["d_is_casting_judge"] = "true" if v["judge_slug"] == v["casting_vote_slug"] else "false"
        for r in self.T["results_rounds"]:
            r["d_n_scoring_seats"] = len(self.seat_order)
        # person aliases: vote-list surnames
        for slug, label in self.vote_labels.items():
            if label != self.people[slug]["family_name"] or True:
                self.T["person_aliases"].append({"person_alias_key": f"{slug}|vote_list|{label}|{self.skey}", "person_key": slug, "alias": label, "alias_kind": "vote_list_surname",
                                                 "context": "vote_list", "series_key": self.skey, **self.prov("Judges' votes lists", "stated", "")})
        for (label, ctx), ov in self.label_overrides.items():
            self.T["couple_labels"].append({"couple_label_key": f"{ov['couple_key']}|{ctx}|{label}", "couple_key": ov["couple_key"], "label": label, "context": ctx,
                                            "week_from": "", "week_to": "", "is_typo": ov["is_typo"], **self.prov("curated/couple_labels.csv", "editorial", ov["note"])})
        for c in self.T["couples"]:
            c["d_pro_slugs"] = "|".join(p["pro_person_key"] for p in self.T["couple_partnerships"] if p["couple_key"] == c["couple_key"])
            c["d_reached_final"] = "true" if c["exit_kind"] == "finalist" else "false"

    # ------------------------------------------------------------ checks
    def integrity_checks(self):
        T = self.T
        bad = [p["performance_key"] for p in T["performances"] if p["d_total_mismatch"] == "true"]
        self.check("check 1: marks sum to stated total", not bad, f"{len(bad)} mismatches {bad[:3]}")
        seats = {s["panel_seat_key"] for s in T["panel_seats"]}
        bad = [j["judge_mark_key"] for j in T["judge_marks"] if j["panel_seat_key"] not in seats]
        self.check("check 2: every mark has a seat", not bad, f"{len(bad)}")
        for r in T["results_rounds"]:
            n = sum(1 for cw in T["couple_weeks"] if cw["results_round_key"] == r["round_key"] and cw["result_status"] in ("eliminated", "third", "fourth"))
            self.check(f"check 5: exit_count {r['round_key']}", n == r["exit_count"], f"{n} vs {r['exit_count']}")
        keys = Counter(p["performance_key"] for p in T["performances"])
        self.check("check 12: performance keys unique", max(keys.values(), default=0) == 1, "")
        for ckey in self.couples_by_key:
            rows = sorted((p for p in T["couple_partnerships"] if p["couple_key"] == ckey), key=lambda p: p["week_from"])
            ok = rows and rows[0]["week_from"] == 1 and all(rows[i]["week_to"] + 1 == rows[i + 1]["week_from"] for i in range(len(rows) - 1))
            if not ok:
                self.check(f"check 11: partnerships contiguous {ckey}", False, str(rows))
        self.check("check 11: partnerships contiguous", all(c[1] for c in self.report["checks"] if c[0].startswith("check 11")), "")
        cw_keys = Counter(cw["couple_week_key"] for cw in T["couple_weeks"])
        self.check("couple_weeks: one row per couple per week", max(cw_keys.values()) == 1 and len(cw_keys) == len(self.couples_by_key) * len(self.weeks), f"{len(cw_keys)} rows")
        self.check("no unresolved couple labels", not self.report["unresolved"], str(self.report["unresolved"][:5]))
        # daggers: highest/lowest of week in the chart agree with the derived flags
        dag_bad = []
        for cell in T["chart_cells"]:
            if cell["couple_key"] and re.fullmatch(r"\d+", cell["col_label_raw"]) and ("dagger" in cell["flags"].split("|") or "double_dagger" in cell["flags"].split("|")):
                wkk = week_key(self.skey, int(cell["col_label_raw"]))
                ps = [p for p in T["performances"] if p["couple_key"] == cell["couple_key"] and p["week_key"] == wkk]
                flag = "d_is_highest_of_week" if "dagger" in cell["flags"].split("|") and "double_dagger" not in cell["flags"].split("|") else "d_is_lowest_of_week"
                if not ps or not any(p[flag] == "true" for p in ps):
                    dag_bad.append((cell["row_label_raw"], cell["col_label_raw"]))
        self.check("daggers agree with derived highest/lowest", not dag_bad, str(dag_bad[:5]))


def head_is_shared(m):
    return bool(m and m.group(1) and m.group(1).lower().startswith("co-"))
