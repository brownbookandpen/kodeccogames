#!/usr/bin/env python3
"""
update_encounters.py

Exports encounters.html's artwork straight from the source PSDs in this
same folder — no re-typing filenames, no rebuilding the page.

  ZN.psd -> rules/Encounters/images/zN.webp
      (the card art shown in the swipeable deck on the page.)

The number "N" controls which card slot the art fills — it must match
the Z-number the card already uses on the page (encounters.html currently
wires up Z1..Z10).

Files that don't match the exact "ZN.psd" pattern (for example a stray
backup copy like "Z4[2].psd") are skipped — rename it to "Z4.psd" first
if that's the version you want exported.

encounters.html already points at rules/Encounters/images/zN.webp, so
re-exporting just overwrites those files in place — the page picks up
the new artwork the next time it's loaded. No HTML is touched.

HOW TO USE
----------
1. Edit a PSD in this folder in Photoshop, save it, close it.
2. Double-click UPDATE_ENCOUNTERS.bat (in this same folder).
3. Refresh encounters.html in your browser.

ADDING A NEW ENCOUNTER CARD
-----------------------------
1. Drop the card PSD named "ZN.psd" (N = a free number) in this folder.
2. Run the bat — it will export the image, but you'll still need to bump
   COUNT in encounters.html's <script> block by hand so the new slide
   shows up.

Run via UPDATE_ENCOUNTERS.bat (double-click) or:
    python update_encounters.py
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
IMAGES_OUT = SCRIPT_DIR / "images"

NUM_RE = re.compile(r"^Z(\d+)\.psd$", re.IGNORECASE)


def flatten_to_webp(psd_path: Path, out_path: Path):
    psd = PSDImage.open(psd_path)
    img = psd.composite()  # RGBA, transparent background preserved
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  {psd_path.name}  ->  {out_path.relative_to(SCRIPT_DIR)}")


def main():
    print(f"Scanning: {SCRIPT_DIR}")
    exported = 0
    skipped = []

    for f in sorted(SCRIPT_DIR.glob("*.psd")):
        m = NUM_RE.match(f.name)
        if not m:
            skipped.append(f.name)
            continue
        num = int(m.group(1))
        flatten_to_webp(f, IMAGES_OUT / f"z{num}.webp")
        exported += 1

    if skipped:
        print("\nSkipped (didn't match 'ZN.psd'):")
        for name in skipped:
            print(f"  {name}")

    print(f"\nDone. {exported} card(s) exported.")
    print("Refresh encounters.html to see the changes.")


if __name__ == "__main__":
    main()
