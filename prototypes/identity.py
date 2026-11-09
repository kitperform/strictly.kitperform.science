"""Identity resolution across all 24 series (from wikitext).

1. Parse the Couples table: celebrity (link target + display), pro (link +
   display, plus mid-series replacements), status.
2. Parse the Scoring chart row headers "X & Y" labels.
3. Resolve labels -> couples by first-token matching; report failures.
4. Report first-name collisions (celeb/celeb, pro/pro, celeb/pro) per series.
5. Report pro and celebrity link targets whose display name varies across
   series (name changes), and display names whose link target varies.
Usage: python -I prototypes/identity.py
Reads data/wikipedia/wikitext/series_{1..24}.wikitext (override with SDC_WIKITEXT_DIR);
writes prototypes/out/couples_all_series.csv.
"""
import os, sys, re, json
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mwparserfromhell as mw
from sdc_common import wikitext_path

LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


def strip(code):
    """strip_code() drops templates entirely, so {{nowrap|X & Y}} -> ''. Unwrap first."""
    c = mw.parse(str(code))
    for tpl in c.filter_templates(recursive=True):
        n = tpl.name.strip().lower()
        if n in ("nowrap", "small") and tpl.has(1):
            try:
                c.replace(tpl, str(tpl.get(1).value))
            except ValueError:
                pass
    return re.sub(r"\s+", " ", c.strip_code()).strip()


def first_link(code):
    m = LINK_RE.search(str(code))
    if not m:
        return None, strip(code)
    return m.group(1).strip(), (m.group(2) or m.group(1)).strip()


def section(code, title_re, level):
    for s in code.get_sections(levels=[level], include_headings=True):
        if re.match(title_re, s.filter_headings()[0].title.strip()):
            return s
    return None


def rows(table):
    for tr in table.contents.filter_tags(matches=lambda t: t.tag == "tr", recursive=False):
        yield [c for c in tr.contents.filter_tags(matches=lambda t: t.tag in ("td", "th"), recursive=False)]


def parse_couples(code, n):
    sec = section(code, r"Couples", 2)
    tbl = sec.filter_tags(matches=lambda t: t.tag == "table")[0]
    out = []
    last_status = None
    for cells in rows(tbl):
        if len(cells) < 3 or cells[0].tag != "th" or all(c.tag == "th" for c in cells):
            continue
        # PITFALL: joint placings (Runners-up rowspan=2/3, co-runners-up) leave the
        # second/third couple's row with only 3 cells; inherit the Status.
        if len(cells) == 3:
            cells = list(cells) + [None]
        celeb_link, celeb_disp = first_link(cells[0].contents)
        pro_cell = str(cells[3 - 1].contents) if len(cells) == 4 else str(cells[2].contents)
        # pro column is index 2 (Celebrity, Notability, Professional partner, Status)
        pro_cell = str(cells[2].contents)
        pro_links = LINK_RE.findall(pro_cell)
        pro_link, pro_disp = first_link(pro_cell)
        repl = None
        if "<br" in pro_cell or len(pro_links) > 1 or "Week" in pro_cell:
            repl = strip(pro_cell)
        status = strip(cells[3].contents) if cells[3] is not None else f"(rowspan) {last_status}"
        last_status = status if cells[3] is not None else last_status
        out.append({"series": n, "celeb_link": celeb_link, "celeb": celeb_disp, "pro_link": pro_link, "pro": pro_disp,
                    "pro_cell_text": repl, "status": status})
    return out


def parse_chart_labels(code, n):
    sec = section(code, r"Scoring chart", 2)
    tbl = sec.filter_tags(matches=lambda t: t.tag == "table")[0]
    labels = []
    for cells in rows(tbl):
        if cells and cells[0].tag == "th" and len(cells) > 3 and "&" in str(cells[0].contents):
            labels.append(strip(cells[0].contents))
    return labels


def tokens(name):
    return name.replace(" ", " ").split()


def main():
    all_couples, problems = [], []
    collisions = []
    pro_by_link, pro_by_disp = defaultdict(set), defaultdict(set)
    celeb_by_link = defaultdict(set)
    for n in range(1, 25):
        code = mw.parse(wikitext_path(n).read_text(encoding="utf-8"))
        couples = parse_couples(code, n)
        labels = parse_chart_labels(code, n)
        all_couples += couples
        for c in couples:
            pro_by_link[c["pro_link"]].add(c["pro"])
            pro_by_disp[c["pro"]].add(c["pro_link"])
            celeb_by_link[c["celeb_link"]].add(c["celeb"])
        # collisions within series
        cf = Counter(tokens(c["celeb"])[0] for c in couples)
        pf = Counter(tokens(c["pro"])[0] for c in couples)
        for name, k in cf.items():
            if k > 1:
                collisions.append((n, "celebrity/celebrity", name, [c["celeb"] for c in couples if tokens(c["celeb"])[0] == name]))
        for name, k in pf.items():
            if k > 1:
                collisions.append((n, "pro/pro", name, [c["pro"] for c in couples if tokens(c["pro"])[0] == name]))
        for name in set(cf) & set(pf):
            collisions.append((n, "celebrity/pro", name, [c["celeb"] for c in couples if tokens(c["celeb"])[0] == name] + [c["pro"] for c in couples if tokens(c["pro"])[0] == name]))
        # resolve labels
        for lab in labels:
            parts = [p.strip() for p in re.split(r"\s*&\s*", lab)]
            if len(parts) != 2:
                problems.append((n, lab, "label is not 'X & Y'"))
                continue
            cel, pro = parts
            cands = [c for c in couples if c["celeb"].startswith(cel.rstrip(".").split(" ")[0]) and tokens(c["pro"])[0] == pro]
            if len(cands) == 1:
                if not cands[0]["celeb"].startswith(cel):
                    problems.append((n, lab, f"nickname/initial: couples table says {cands[0]['celeb']!r}"))
                continue
            # second pass: celebrity label may be a nickname or carry an initial ("Ricky G.")
            cands2 = [c for c in couples if tokens(c["pro"])[0] == pro]
            if len(cands2) == 1:
                problems.append((n, lab, f"resolved only via pro first name -> {cands2[0]['celeb']} & {cands2[0]['pro']}"))
            else:
                problems.append((n, lab, f"UNRESOLVED ({len(cands)} direct, {len(cands2)} by pro)"))
    print("=== Label resolution problems (series, label, reason) ===")
    for p in problems:
        print("  ", p)
    print("\n=== Same-first-name collisions within a series ===")
    for c in collisions:
        print("  ", c)
    print("\n=== Pro link targets with >1 display name across series (name changes) ===")
    for k, v in sorted(pro_by_link.items(), key=lambda kv: str(kv[0])):
        if len(v) > 1:
            print("  ", k, "->", sorted(v))
    print("\n=== Pro display names with >1 link target (redirects / disambiguation) ===")
    for k, v in sorted(pro_by_disp.items()):
        if len(v) > 1:
            print("  ", k, "->", sorted(map(str, v)))
    print("\n=== Celebrity link != display (disambiguated titles) sample ===")
    for c in all_couples:
        if c["celeb_link"] and c["celeb_link"] != c["celeb"]:
            print("  ", c["series"], c["celeb_link"], "|", c["celeb"])
    print("\n=== Mid-series professional replacements (from the Couples table) ===")
    for c in all_couples:
        if c["pro_cell_text"]:
            print("  ", c["series"], c["celeb"], "|", c["pro_cell_text"])
    print("\n=== Couples without a wiki link (red links / unlinked) ===")
    for c in all_couples:
        if not c["celeb_link"] or not c["pro_link"]:
            print("  ", c)
    print(f"\nTotal couples parsed: {len(all_couples)}; distinct pros by link: {len(pro_by_link)}; distinct celebs by link: {len(celeb_by_link)}")
    import pandas as pd
    from sdc_common import out_dir
    pd.DataFrame(all_couples).to_csv(out_dir() / "couples_all_series.csv", index=False)


if __name__ == "__main__":
    main()
