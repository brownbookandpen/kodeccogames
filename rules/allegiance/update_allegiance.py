#!/usr/bin/env python3
"""
update_allegiance.py

Exports allegiance.html's artwork straight from the source PSDs in this
folder (and its "[B4][ALLEGIANCES]" subfolder) — no re-typing filenames,
no rebuilding the page.

allegiance.html shows 5 secret roles, and each one's images are named
images/NN.png (desktop card thumbnail + click/tap popup modal) and
images/NN-card.png (mobile swipe-carousel poster). Because the page only
shows a curated subset of the available artwork (e.g. Apprentice & Patient
Zero share one combined card, and there's only one Revivalist card even
though 3 portrait variations exist), the PSD -> PNG mapping below is
spelled out explicitly rather than guessed from filenames.

HOW TO USE
----------
1. Edit a PSD in this folder (or [B4][ALLEGIANCES]/) in Photoshop, save
   it, close it.
2. Double-click UPDATE_ALLEGIANCE.bat (in this same folder).
3. Refresh allegiance.html in your browser.

CHANGING WHICH ART IS USED
---------------------------
- Renamed a PSD?  Update the matching entry in MAPPING below (left side
  is the PNG file allegiance.html already points at — don't change that
  side; right side is the PSD file to export from — point it at the new
  filename).
- Want a different Revivalist portrait (there are 3 variations in
  [B4][ALLEGIANCES])?  Change the "images/05.png" entry to the variation
  you want.
- Adding a brand new secret role?  You'll need to add a new
  <section class="role" ...> block to allegiance.html by hand (copy an
  existing one and swap in new text/colors), then add its image(s) to
  MAPPING here.
- Want a different homepage thumbnail?  Make a square (827x827) PSD with
  the rules-text layers hidden (art only) and point the "images/homepage.png"
  entry at it.

Run via UPDATE_ALLEGIANCE.bat (double-click) or:
    python update_allegiance.py
"""
import re
import sys
from pathlib import Path
from typing import Optional

try:
    from psd_tools import PSDImage
except ImportError:
    print("Missing dependency 'psd-tools'. Install with:")
    print("    pip install psd-tools pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent  # rules/allegiance
IMAGES_OUT = SCRIPT_DIR / "images"
B4_DIR = SCRIPT_DIR / "[B4][ALLEGIANCES]"

# destination (relative to rules/allegiance/) : source PSD filename
# Sources with no folder prefix live directly in rules/allegiance/;
# sources under "[B4][ALLEGIANCES]/" are looked up in that subfolder.
MAPPING = {
    # Revivalist — card art is 1 of 3 available portrait variations, mobile
    # poster is the shared "REVIVALISTS" 2x3 poster.
    "images/05.png":      "[B4][ALLEGIANCES]/SURVIVOR - REVIVALIST VARIATION 1.psd",
    "images/05-card.png": "[SECRET ROLE] [2x3] REVIVALISTS Copy.psd",

    # Curefinder
    "images/02.png":      "[B4][ALLEGIANCES]/SURVIVOR - CUREFINDER.psd",
    "images/02-card.png": "[SECRET ROLE] [2x3] CUREFINDER.psd",

    # Executioner
    "images/03.png":      "[B4][ALLEGIANCES]/CARRIER - EXECUTIONER.psd",
    "images/03-card.png": "[SECRET ROLE] [2x3] EXECUTIONER.psd",

    # Saboteur
    "images/08.png":      "[B4][ALLEGIANCES]/CARRIER - SABOTEUR.psd",
    "images/08-card.png": "[SECRET ROLE] [2x3] SABOTEUR.psd",

    # Apprentice & Patient Zero — merged into 1 card. Both the desktop
    # card/modal art AND the mobile poster use the same combined 2x3
    # artwork (it already has both portraits + the shared rules text).
    "images/01-card.png": "[SECRET ROLE] [2x3] APPRENTICE.psd",

    # Homepage (index.html) Mission Brief thumbnail — a square (827x827)
    # crop with the rules text hidden, art-only. Point this at whichever
    # square PSD you want representing Allegiance on the homepage.
    "images/homepage.png": "[SECRET ROLE] [2x3] CUREFINDER [SQUARE].psd",
}


def normalize(name: str) -> str:
    # Compares filenames ignoring stray whitespace (Photoshop's Save As dialog
    # makes it easy to pick up a trailing space before ".psd" by accident, e.g.
    # "EXECUTIONER .psd" vs "EXECUTIONER.psd" — these should still match).
    p = Path(name)
    stem = re.sub(r"\s+", " ", p.stem).strip()
    return (stem + p.suffix).upper()


def resolve_source(rel: str) -> Optional[Path]:
    """Find a source PSD, tolerant of stray trailing spaces / double spaces
    in the filename (Photoshop's Save As dialog makes those easy to pick up
    by accident)."""
    if "/" in rel:
        folder_name, fname = rel.split("/", 1)
        folder = B4_DIR if folder_name == "[B4][ALLEGIANCES]" else SCRIPT_DIR / folder_name
    else:
        folder, fname = SCRIPT_DIR, rel

    direct = folder / fname
    if direct.exists():
        return direct

    if not folder.is_dir():
        return None
    target = normalize(fname)
    for f in folder.glob("*.psd"):
        if normalize(f.name) == target:
            return f
    return None


def flatten_to_png(psd_path: Path, out_path: Path):
    psd = PSDImage.open(psd_path)
    img = psd.composite()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def main():
    print(f"Scanning: {SCRIPT_DIR}")
    exported = 0
    for dest_rel, source_rel in MAPPING.items():
        src = resolve_source(source_rel)
        dest = SCRIPT_DIR / dest_rel
        if src is None:
            print(f"  MISSING: {source_rel}  (expected for {dest_rel}) — skipped.")
            continue
        flatten_to_png(src, dest)
        print(f"  {src.relative_to(SCRIPT_DIR)}  ->  {dest_rel}")
        exported += 1

    print(f"\nDone. {exported}/{len(MAPPING)} image(s) exported.")
    print("Refresh allegiance.html to see the changes.")


if __name__ == "__main__":
    main()
