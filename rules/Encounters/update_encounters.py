#!/usr/bin/env python3
"""
update_encounters.py

Exports encounters.html's artwork straight from the source PSDs — no
re-typing filenames, no rebuilding the page.

The Encounters page is now a single merged deck: the 4 Supply items
(Armaments, Medical, Explosives, Vile Samples) are shuffled in among the
10 zombie threat cards (Z1-Z10), in the order the physical deck is meant
to be drawn in:

  01 Armaments   02 Z1          03 Z2          04 Medical
  05 Z3          06 Explosives  07 Z4 Stonewall
  08 Vile Samples 09 Z5 Bloodhound 10 Z6 Hardshell 11 Z7 Thornback
  12 Z8 Shrieker 13 Z9 Behemoth 14 Z10 Matriarch

For each of the 14 slots this script exports two images into
rules/Encounters/images/:

  0N.webp             the plain card art (poster) — shown large in the
                       on-page modal when you click/tap a card.
  0N-explainer.webp    the full art + rules-text readout — shown inline
                       on the page itself (and on the mobile carousel).

Source PSDs live in two places:
  - The 4 Supply "card" PSDs (non-explainer) still live in
    rules/supplies/ (e.g. "1. [SUPPLIES] ARMAMENTS.psd").
  - Every "explainer" PSD (both Supplies and Zombies) plus the 10
    zombie "card" PSDs live under rules/Encounters/PSD SOURCE/.

encounters.html already points at rules/Encounters/images/0N.webp and
0N-explainer.webp, so re-exporting just overwrites those files in place
— the page picks up new artwork the next time it's loaded. No HTML is
touched.

Also exports the square Mission Brief thumbnail used on the homepage:
  PSD SOURCE/[SQUARE] THUMBNAIL.psd -> rules/Encounters/images/homepage.png

HOW TO USE
----------
1. Edit a PSD (in rules/supplies/ or rules/Encounters/PSD SOURCE/),
   save it, close it.
2. Double-click UPDATE_ENCOUNTERS.bat (in this same folder).
3. Refresh encounters.html / index.html in your browser.

ADDING / REORDERING SLOTS
--------------------------
Edit the SLOTS list below — each entry is
    (slot_number, card_psd_path, explainer_psd_path, label)
card_psd_path / explainer_psd_path are relative to REPO_ROOT. If you
add a slot you'll also need to add a matching <section class="role">
block to encounters.html by hand (copy an existing one).

Run via UPDATE_ENCOUNTERS.bat (double-click) or:
    python update_encounters.py
"""
import sys
from pathlib import Path

try:
    from psd_tools import PSDImage
except ImportError:
    print("Missing dependency 'psd-tools'. Install with:")
    print("    pip install psd-tools pillow")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent          # rules/Encounters
REPO_ROOT = SCRIPT_DIR.parents[1]                      # kodeccogames
IMAGES_OUT = SCRIPT_DIR / "images"

SUPPLIES_DIR = REPO_ROOT / "rules" / "supplies"
CARDS_DIR = SCRIPT_DIR / "PSD SOURCE" / "CARDS"
PORTRAITS_DIR = SCRIPT_DIR / "PSD SOURCE" / "PORTRAITS"
SQUARE_PSD = SCRIPT_DIR / "PSD SOURCE" / "[SQUARE] THUMBNAIL.psd"

# (slot, card psd, explainer psd, label — label is just for console output)
SLOTS = [
    (1,  SUPPLIES_DIR / "1. [SUPPLIES] ARMAMENTS.psd",
         PORTRAITS_DIR / "1. [SUPPLIES] ARMAMENTS {EXPLAINER].psd",
         "Armaments"),
    (2,  CARDS_DIR / "Z1.psd",
         PORTRAITS_DIR / "2. [EXPLAINER] Z1.psd",
         "Z1"),
    (3,  CARDS_DIR / "Z2.psd",
         PORTRAITS_DIR / "3. [EXPLAINER] Z2.psd",
         "Z2"),
    (4,  SUPPLIES_DIR / "2. [SUPPLIES] MEDICAL.psd",
         PORTRAITS_DIR / "4. [SUPPLIES] MEDICAL {EXPLAINER].psd",
         "Medical Supplies"),
    (5,  CARDS_DIR / "Z3.psd",
         PORTRAITS_DIR / "5. [EXPLAINER] Z3.psd",
         "Z3"),
    (6,  SUPPLIES_DIR / "3. [SUPPLIES] EXPLOSIVES.psd",
         PORTRAITS_DIR / "6. [SUPPLIES] EXPLOSIVES {EXPLAINER].psd",
         "High Explosives"),
    (7,  CARDS_DIR / "Z4 [STONEWALL].psd",
         PORTRAITS_DIR / "7. [EXPLAINER] Z4[STONEWALL].psd",
         "Z4 — Stonewall"),
    (8,  SUPPLIES_DIR / "4. VILE SAMPLES.psd",
         PORTRAITS_DIR / "8. VILE SAMPLES {EXPLAINER].psd",
         "Vile Samples"),
    (9,  CARDS_DIR / "Z5 [BLOODHOUND].psd",
         PORTRAITS_DIR / "9. [EXPLAINER] Z5 [BLOODHOUND].psd",
         "Z5 — Bloodhound"),
    (10, CARDS_DIR / "Z6 [HARDSHELL].psd",
         PORTRAITS_DIR / "10. [EXPLAINER] Z6 [HARDSHELL].psd",
         "Z6 — Hardshell"),
    (11, CARDS_DIR / "Z7 [THORNBACK].psd",
         PORTRAITS_DIR / "11. [EXPLAINER] Z7 [THORNBACK].psd",
         "Z7 — Thornback"),
    (12, CARDS_DIR / "Z8 [SHRIEKER].psd",
         PORTRAITS_DIR / "12. [EXPLAINER] Z8 [SHRIEKER].psd",
         "Z8 — Shrieker"),
    (13, CARDS_DIR / "Z9 [BEHEMOTH].psd",
         PORTRAITS_DIR / "13. [EXPLAINER] Z9 [BEHEMOTH].psd",
         "Z9 — Behemoth"),
    (14, CARDS_DIR / "Z10 [MATRIACH].psd",
         PORTRAITS_DIR / "14. [EXPLAINER] Z10 [MATRIACH].psd",
         "Z10 — Matriarch"),
]


def flatten_to_webp(psd_path: Path, out_path: Path):
    if not psd_path.exists():
        print(f"  MISSING: {psd_path.relative_to(REPO_ROOT)}")
        return False
    psd = PSDImage.open(psd_path)
    img = psd.composite()  # RGBA, transparent background preserved
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  {psd_path.name}  ->  {out_path.relative_to(REPO_ROOT)}")
    return True


def flatten_to_png(psd_path: Path, out_path: Path):
    if not psd_path.exists():
        print(f"  MISSING: {psd_path.relative_to(REPO_ROOT)}")
        return False
    psd = PSDImage.open(psd_path)
    img = psd.composite()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  {psd_path.name}  ->  {out_path.relative_to(REPO_ROOT)}")
    return True


def main():
    card_count = 0
    explainer_count = 0

    for num, card_psd, explainer_psd, label in SLOTS:
        print(f"Slot {num:02d} — {label}")
        if flatten_to_webp(card_psd, IMAGES_OUT / f"{num:02d}.webp"):
            card_count += 1
        if flatten_to_webp(explainer_psd, IMAGES_OUT / f"{num:02d}-explainer.webp"):
            explainer_count += 1

    homepage_exported = flatten_to_png(SQUARE_PSD, IMAGES_OUT / "homepage.png")

    print(f"\nDone. {card_count}/{len(SLOTS)} card(s), "
          f"{explainer_count}/{len(SLOTS)} explainer(s), "
          f"{'1' if homepage_exported else '0'} homepage thumbnail exported.")
    print("Refresh encounters.html / index.html to see the changes.")


if __name__ == "__main__":
    main()
