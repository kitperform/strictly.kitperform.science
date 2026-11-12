"""Slugs and natural keys (docs/data-model-v2.md section 3.1)."""
import re
import unicodedata
from urllib.parse import unquote


def slugify(text: str) -> str:
    """NFC -> strip diacritics -> lower -> non-alphanumerics to '-' -> collapse."""
    if text is None:
        return ""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.replace("&", " and ").lower()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def wiki_title_from_href(href):
    """'./Chris_Appleton' -> 'Chris Appleton'; None for refs, anchors and external links."""
    if not href or not href.startswith("./"):
        return None
    t = href[2:]
    if "#" in t:
        t = t.split("#", 1)[0]
    if not t:
        return None
    return unquote(t).replace("_", " ")


def person_slug(wiki_title: str, display: str | None = None) -> str:
    """Curated slug seed: the article title without any disambiguator."""
    base = wiki_title or display or ""
    base = re.sub(r"\s*\(.*?\)\s*$", "", base)
    return slugify(base)


def week_key(series_key: str, week: int) -> str:
    return f"{series_key}W{week:02d}"


def series_key(n: int) -> str:
    return f"S{n:02d}"
