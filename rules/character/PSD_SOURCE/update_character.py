#!/usr/bin/env python3
"""
update_character.py

Exports character.html's artwork straight from the source PSDs in this
folder — no re-typing filenames, no rebuilding the page.

  CARDS/[N] NAME.psd                 -> rules/character/images/0N.png
      (the big "full card" art — used for the desktop thumbnail AND the
      click/tap popup modal)

  PORTRAITS/[COLOR] [2x3] NAME EXPLAINER.psd -> rules/character/images/0N-card.png
      (the flattened poster used for the mobile swipe carousel)

  PORTRAITS/[SQUARE] ... NAME EXPLAINER.psd  -> rules/character/images/homepage.png
      (a square, art-only crop — used for the Mission Brief thumbnail on
      the homepage, index.html. Whichever PORTRAITS file has "[SQUARE]"
      in its name is the one used; there should only be one at a time.)

character.html already points at rules/character/images/0N.png and
0N-card.png, so re-exporting just overwrites those files in place — the
page picks up the new artwork the next time it's loaded. No HTML is
touched. (homepage.png is referenced by index.html, not character.html.)

The "N" for a PORTRAITS file is looked up by matching its character NAME
against the CARDS files, so the two folders stay in sync automatically as
long as the name in both filenames matches (e.g. "BRAWLER").

HOW TO USE
----------
1. Edit a PSD in CARDS/ or PORTRAITS/ in Photoshop, save it, close it.
2. Double-click UPDATE_CHARACTER.bat (in this same folder).
3. Refresh character.html in your browser.

ADDING A NEW CHARACTER
-----------------------
1. Drop the full-card PSD in CARDS/ named "[N] NAME.psd" (N = a free
   number, 1-18 are taken).
2. Drop the matching mobile-poster PSD in PORTRAITS/ named
   "[ANYCOLOR] [2x3] NAME EXPLAINER.psd" (NAME must match the CARDS file).
3. Run the bat. It will export both images, but you'll still need to add
   a new <section class="role" ...> block to character.html by hand (copy
   an existing one and swap in the new number/name/text) — this script
   only re-exports artwork for roles that already exist on the page.

Run via UPDATE_CHARACTER.bat (double-click) or:
    python update_character.py
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
CARDS_DIR = SCRIPT_DIR / "CARDS"
PORTRAITS_DIR = SCRIPT_DIR / "PORTRAITS"

# PSD_SOURCE -> character -> rules -> kodeccogames (repo root)
REPO_ROOT = SCRIPT_DIR.parents[2]
IMAGES_OUT = REPO_ROOT / "rules" / "character" / "images"

CARD_RE = re.compile(r"^\[(\d+)\]\s*(.+?)\s*\.psd$", re.IGNORECASE)
PORTRAIT_NAME_RE = re.compile(r"\[2x3\]\s*(.+?)\s*EXPLAINER", re.IGNORECASE)


def normalize(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().upper()


def flatten_to_png(psd_path: Path, out_path: Path, isolate_card_layer: bool = False):
    psd = PSDImage.open(psd_path)

    img = None
    if isolate_card_layer:
        # The CARDS/*.psd canvases are wider than the finished card — they carry a
        # reference callout (the ability text, laid out as editable type, sitting off
        # to the side) alongside the actual card. The finished card itself always
        # lives in exactly one visible top-level smart-object layer, so compositing
        # the whole canvas would grab the callout text too. Isolate that one layer
        # instead of using psd.composite() on the full document.
        smart_layers = [l for l in psd if l.kind == "smartobject" and l.visible]
        if len(smart_layers) == 1:
            img = smart_layers[0].composite()
        else:
            print(f"  WARNING: expected exactly 1 visible smart-object layer in "
                  f"{psd_path.name}, found {len(smart_layers)} — exporting the full "
                  f"canvas instead. Check {out_path.name} looks right.")

    if img is None:
        img = psd.composite()  # RGBA, transparent background preserved

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  {psd_path.relative_to(SCRIPT_DIR)}  ->  {out_path.relative_to(REPO_ROOT)}")


def main():
    if not CARDS_DIR.is_dir():
        print(f"Missing folder: {CARDS_DIR}")
        sys.exit(1)

    # 1. Build NAME -> N from the CARDS folder, and export each full card.
    name_to_num = {}
    card_count = 0
    for f in sorted(CARDS_DIR.glob("*.psd")):
        m = CARD_RE.match(f.name)
        if not m:
            print(f"  skip (expected '[N] NAME.psd'): CARDS/{f.name}")
            continue
        num = int(m.group(1))
        name_to_num[normalize(m.group(2))] = num
        flatten_to_png(f, IMAGES_OUT / f"{num:02d}.png", isolate_card_layer=True)
        card_count += 1

    # 2. Match each PORTRAITS file to its number by name, export the poster.
    #    Files with "[SQUARE]" in the name are the homepage thumbnail instead
    #    (handled separately in step 3), not a mobile poster.
    portrait_count = 0
    square_files = []
    if PORTRAITS_DIR.is_dir():
        for f in sorted(PORTRAITS_DIR.glob("*.psd")):
            if "SQUARE" in normalize(f.name):
                square_files.append(f)
                continue
            m = PORTRAIT_NAME_RE.search(f.name)
            if not m:
                print(f"  skip (expected '... [2x3] NAME EXPLAINER.psd'): PORTRAITS/{f.name}")
                continue
            key = normalize(m.group(1))
            num = name_to_num.get(key)
            if num is None:
                print(f"  WARNING: no CARDS/[N] {key}.psd found for PORTRAITS/{f.name} — skipped.")
                continue
            flatten_to_png(f, IMAGES_OUT / f"{num:02d}-card.png")
            portrait_count += 1
    else:
        print(f"  (no PORTRAITS folder found at {PORTRAITS_DIR}, skipping mobile posters)")

    # 3. Homepage thumbnail — whichever PORTRAITS file is tagged [SQUARE].
    homepage_exported = False
    if len(square_files) == 1:
        flatten_to_png(square_files[0], IMAGES_OUT / "homepage.png")
        homepage_exported = True
    elif len(square_files) > 1:
        print(f"  WARNING: found {len(square_files)} [SQUARE] files in PORTRAITS/, "
              f"expected 1 — using {square_files[-1].name} for images/homepage.png.")
        flatten_to_png(square_files[-1], IMAGES_OUT / "homepage.png")
        homepage_exported = True

    print(f"\nDone. {card_count} card(s), {portrait_count} poster(s), "
          f"{'1' if homepage_exported else '0'} homepage thumbnail exported.")
    print("Refresh character.html to see the changes.")


if __name__ == "__main__":
    main()
