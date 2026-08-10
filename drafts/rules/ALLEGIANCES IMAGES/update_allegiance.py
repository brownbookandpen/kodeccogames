#!/usr/bin/env python3
"""
update_allegiance.py

Scans this folder for PSD files named "[N] NAME.psd", flattens each to a
transparent PNG, saves them into rules/allegiance/images/0N.png, and
rewrites the stack section of rules/allegiance/allegiance.html to match,
ordered by N (low to high).

Rename/renumber the PSDs (e.g. swap [1] and [2]) and re-run to reorder
the page.

Run via UPDATE_ALLEGIANCE.bat (double-click) or:
    python update_allegiance.py
"""
import re
import sys
from pathlib import Path

try:
    from psd_tools import PSDImage
except ImportError:
    print("Missing dependency 'psd-tools'. Install with:")
    print("    pip install psd-tools pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
# ALLEGIANCES IMAGES -> rules -> drafts -> kodeccogames (repo root)
REPO_ROOT = SCRIPT_DIR.parents[2]
IMAGES_OUT = REPO_ROOT / "rules" / "allegiance" / "images"
HTML_PATH = REPO_ROOT / "rules" / "allegiance" / "allegiance.html"

NAME_RE = re.compile(r"^\[(\d+)\]\s*(.+?)\s*\.psd$", re.IGNORECASE)


def find_psds():
    items = []
    for f in SCRIPT_DIR.glob("*.psd"):
        m = NAME_RE.match(f.name)
        if not m:
            print(f"  skip (no [N] prefix): {f.name}")
            continue
        num = int(m.group(1))
        label = m.group(2).strip().upper()
        items.append((num, label, f))
    items.sort(key=lambda t: t[0])
    return items


def flatten_to_png(psd_path: Path, out_path: Path):
    psd = PSDImage.open(psd_path)
    img = psd.composite()  # RGBA, transparent background preserved
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def rewrite_html(items):
    if not HTML_PATH.exists():
        print(f"  WARNING: html not found at {HTML_PATH}, skipping HTML update.")
        return
    html = HTML_PATH.read_text(encoding="utf-8")

    lines = []
    for num, label, _ in items:
        fname = f"{num:02d}.png"
        lines.append(
            f'  <div class="stack-item"><img src="images/{fname}" alt="{label}" loading="lazy"></div>'
        )
    block = "\n".join(lines)

    pattern = re.compile(
        r"(<!-- STACK_ITEMS_START -->)(.*?)(<!-- STACK_ITEMS_END -->)",
        re.DOTALL,
    )
    if not pattern.search(html):
        print("  WARNING: STACK_ITEMS markers not found in allegiance.html; HTML not updated.")
        return

    new_html = pattern.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", html)
    HTML_PATH.write_text(new_html, encoding="utf-8")


def main():
    print(f"Scanning: {SCRIPT_DIR}")
    items = find_psds()
    if not items:
        print("No PSD files found matching '[N] NAME.psd'.")
        return

    for num, label, psd_path in items:
        out_path = IMAGES_OUT / f"{num:02d}.png"
        print(f"  [{num}] {label}: {psd_path.name} -> {out_path.relative_to(REPO_ROOT)}")
        flatten_to_png(psd_path, out_path)

    rewrite_html(items)
    print("Done. Refresh allegiance.html to see the changes.")


if __name__ == "__main__":
    main()
