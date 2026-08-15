#!/usr/bin/env python3
"""
update_supplies.py

Exports supplies.html's artwork straight from the source PSDs in this same
folder — no re-typing filenames, no rebuilding the page.

  N. [SUPPLIES] NAME.psd             -> rules/supplies/images/0N.png
      (the finished card art — used as the thumbnail on the page AND on the
      mobile swipe carousel.)

  N. [SUPPLIES] NAME {EXPLAINER].psd -> rules/supplies/images/0N-explainer.png
      (the full art + rules-text readout — shown when you click/tap the
      card, same as the "shows the card" popup on the other pages.)

The number "N" at the start of the filename controls which card slot on the
page it fills — it must match the order the cards are already wired up in
supplies.html (1=Armaments, 2=Medical, 3=Explosives, 4=Vile Samples).

supplies.html already points at rules/supplies/images/0N.png and
0N-explainer.png, so re-exporting just overwrites those files in place —
the page picks up the new artwork the next time it's loaded. No HTML is
touched.

HOW TO USE
----------
1. Edit a PSD in this folder in Photoshop, save it, close it.
2. Double-click UPDATE_SUPPLIES.bat (in this same folder).
3. Refresh supplies.html in your browser.

ADDING A NEW SUPPLY TYPE
--------------------------
1. Drop the card PSD named "N. [SUPPLIES] NAME.psd" (N = a free number).
2. Drop the matching "N. [SUPPLIES] NAME {EXPLAINER].psd" explainer PSD.
3. Run the bat — it will export both images, but you'll still need to add a
   new <section class="role" ...> block to supplies.html by hand (copy an
   existing one and swap in the new number/name/text) — this script only
   re-exports artwork for supplies that already exist on the page.

Run via UPDATE_SUPPLIES.bat (double-click) or:
    python update_supplies.py
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

# supplies -> rules -> kodeccogames (repo root)
REPO_ROOT = SCRIPT_DIR.parents[1]
IMAGES_OUT = REPO_ROOT / "rules" / "supplies" / "images"

NUM_RE = re.compile(r"^(\d+)\.\s*")


def flatten_to_png(psd_path: Path, out_path: Path):
    psd = PSDImage.open(psd_path)
    img = psd.composite()  # RGBA, transparent background preserved
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  {psd_path.name}  ->  {out_path.relative_to(REPO_ROOT)}")


def main():
    card_count = 0
    explainer_count = 0

    for f in sorted(SCRIPT_DIR.glob("*.psd")):
        m = NUM_RE.match(f.name)
        if not m:
            print(f"  skip (expected 'N. NAME.psd'): {f.name}")
            continue
        num = int(m.group(1))
        is_explainer = "EXPLAINER" in f.name.upper()

        if is_explainer:
            flatten_to_png(f, IMAGES_OUT / f"{num:02d}-explainer.png")
            explainer_count += 1
        else:
            flatten_to_png(f, IMAGES_OUT / f"{num:02d}.png")
            card_count += 1

    print(f"\nDone. {card_count} card(s), {explainer_count} explainer(s) exported.")
    print("Refresh supplies.html to see the changes.")


if __name__ == "__main__":
    main()
