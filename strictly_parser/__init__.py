"""strictly_parser: turns a captured Wikipedia series page into the tidy CSV
dataset described in docs/data-model-v2.md (section 10).

Phase 0 covers one series at a time from its Parsoid HTML capture, driven by
the small curated tables in curated/ for facts the page does not state.
"""
__version__ = "0.1.0"
