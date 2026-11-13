"""Slugs and natural keys (docs/data-model-v2.md section 3.1)."""
import re
import unicodedata
from urllib.parse import unquote


# Letters with no NFKD decomposition, so that "Przystał" -> "przystal" rather than "przysta".
TRANSLIT = str.maketrans({"ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "đ": "d", "Đ": "D", "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE", "þ": "th", "Þ": "Th", "ı": "i"})


def slugify(text: str) -> str:
    """NFC -> strip diacritics -> lower -> non-alphanumerics to '-' -> collapse."""
    if text is None:
        return ""
    t = text.translate(TRANSLIT)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("&", " and ").lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def wiki_title_from_href(href):
    """'./Chris_Appleton' -> 'Chris Appleton'; None for refs, anchors and external links."""
    if not href:
        return None
    for prefix in ("./", "/wiki/", "https://en.wikipedia.org/wiki/"):
        if href.startswith(prefix):
            t = href[len(prefix):]
            break
    else:
        return None
    if "#" in t:
        t = t.split("#", 1)[0]
    if not t:
        return None
    return unquote(t).replace("_", " ")


def person_slug(wiki_title: str, display: str | None = None) -> str:
    """Curated slug seed: the article title without any disambiguator."""
    base = wiki_title or display or ""
    stripped = re.sub(r"\s*\(.*?\)\s*$", "", base)
    if " " not in stripped.strip() and stripped != base:
        return slugify(base)  # a mononym keeps its disambiguator: 'Dev (DJ)' -> dev-dj
    return slugify(stripped)


def week_key(series_key: str, week: int) -> str:
    return f"{series_key}W{week:02d}"


def series_key(n: int) -> str:
    return f"S{n:02d}"
