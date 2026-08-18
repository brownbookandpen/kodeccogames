#!/usr/bin/env python3
"""
update_encounters.py

Exports encounters.html's artwork straight from the source PSDs — no
re-typing filenames, no rebuilding the page.

The Encounters page is a single merged deck: the 4 Supply items
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
  - The 4 Supply "card" PSDs (non-explainer) live in rules/supplies/
    (e.g. "1. [SUPPLIES] ARMAMENTS.psd").
  - Every "explainer" PSD (both Supplies and Zombies) plus the 10
    zombie "card" PSDs live under rules/Encounters/PSD SOURCE/.

FILES ARE MATCHED BY KEYWORD, NOT BY THEIR NUMBER PREFIX.
-----------------------------------------------------------
Feel free to rename/renumber files in Explorer for your own sorting
(e.g. "2. [EXPLAINER] Z1.psd" -> "4. [EXPLAINER] Z1.psd") — this script
finds each PSD by searching for a keyword (like "Z1" or "ARMAMENTS")
inside the filename, so it doesn't care what number happens to be in
front. It only cares that exactly one match exists per slot in the
right folder.

encounters.html already points at rules/Encounters/images/0N.webp and
0N-explainer.webp, so re-exporting just overwrites those files in place
— the page picks up new artwork the next time it's loaded. No HTML is
touched.

Also exports the square Mission Brief thumbnail used on the homepage:
  PSD SOURCE/[SQUARE] THUMBNAIL.psd -> rules/Encounters/images/homepage.png

HOW TO USE
----------
1. Edit/rename a PSD (in rules/supplies/ or rules/Encounters/PSD SOURCE/),
   save it, close it.
2. Double-click UPDATE_ENCOUNTERS.bat (in this same folder).
3. Refresh encounters.html / index.html in your browser.

ADDING / REORDERING SLOTS
--------------------------
Edit the SLOTS list below — each entry is
    (slot_number, folder, keyword_pattern, is_explainer, label)
If you add a slot you'll also need to add a matching
<section class="role"> block to encounters.html by hand (copy an
existing one).

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

SCRIPT_DIR = Path(__file__).resolve().parent          # rules/Encounters
REPO_ROOT = SCRIPT_DIR.parents[1]                      # kodeccogames
IMAGES_OUT = SCRIPT_DIR / "images"

SUPPLIES_DIR = REPO_ROOT / "rules" / "supplies"
CARDS_DIR = SCRIPT_DIR / "PSD SOURCE" / "CARDS"
PORTRAITS_DIR = SCRIPT_DIR / "PSD SOURCE" / "PORTRAITS"
SQUARE_PSD = SCRIPT_DIR / "PSD SOURCE" / "[SQUARE] THUMBNAIL.psd"


def zpat(n):
    """Matches 'Z<n>' but not 'Z<n><more digits>' (so Z1 doesn't match Z10)."""
    return re.compile(rf"Z{n}(?!\d)", re.IGNORECASE)


# (slot, folder, keyword pattern(s) that must ALL be found in the filename,
#  card/explainer distinguished by whether "EXPLAINER" is required, label)
# keyword can be a compiled regex or a plain substring (case-insensitive).
SLOTS = [
    (1,  "Armaments",         SUPPLIES_DIR, PORTRAITS_DIR, ["ARMAMENTS"]),
    (2,  "Z1",                CARDS_DIR,    PORTRAITS_DIR, [zpat(1)]),
    (3,  "Z2",                CARDS_DIR,    PORTRAITS_DIR, [zpat(2)]),
    (4,  "Medical Supplies",  SUPPLIES_DIR, PORTRAITS_DIR, ["MEDICAL"]),
    (5,  "Z3",                CARDS_DIR,    PORTRAITS_DIR, [zpat(3)]),
    (6,  "High Explosives",   SUPPLIES_DIR, PORTRAITS_DIR, ["EXPLOSIVES"]),
    (7,  "Z4 — Stonewall",    CARDS_DIR,    PORTRAITS_DIR, [zpat(4)]),
    (8,  "Vile Samples",      SUPPLIES_DIR, PORTRAITS_DIR, ["VILE"]),
    (9,  "Z5 — Bloodhound",   CARDS_DIR,    PORTRAITS_DIR, [zpat(5)]),
    (10, "Z6 — Hardshell",    CARDS_DIR,    PORTRAITS_DIR, [zpat(6)]),
    (11, "Z7 — Thornback",    CARDS_DIR,    PORTRAITS_DIR, [zpat(7)]),
    (12, "Z8 — Shrieker",     CARDS_DIR,    PORTRAITS_DIR, [zpat(8)]),
    (13, "Z9 — Behemoth",     CARDS_DIR,    PORTRAITS_DIR, [zpat(9)]),
    (14, "Z10 — Matriarch",   CARDS_DIR,    PORTRAITS_DIR, [zpat(10)]),
]


def _matches(name: str, patterns) -> bool:
    for p in patterns:
        if hasattr(p, "search"):
            if not p.search(name):
                return False
        else:
            if p.upper() not in name.upper():
                return False
    return True


def find_psd(folder: Path, patterns, want_explainer: bool, label: str):
    if not folder.exists():
        print(f"  MISSING FOLDER: {folder.relative_to(REPO_ROOT)}")
        return None

    matches = []
    for f in sorted(folder.glob("*.psd")):
        if not _matches(f.name, patterns):
            continue
        has_explainer_tag = "EXPLAINER" in f.name.upper()
        if has_explainer_tag != want_explainer:
            continue
        matches.append(f)

    kind = "explainer" if want_explainer else "card"
    if not matches:
        print(f"  NOT FOUND ({kind}) for {label} in {folder.relative_to(REPO_ROOT)}")
        return None
    if len(matches) > 1:
        print(f"  AMBIGUOUS ({kind}) for {label} — found {len(matches)} matches in "
              f"{folder.relative_to(REPO_ROOT)}, using \"{matches[-1].name}\":")
        for m in matches:
            print(f"    - {m.name}")
    return matches[-1]


def flatten(psd_path: Path, out_path: Path) -> bool:
    if psd_path is None:
        return False
    psd = PSDImage.open(psd_path)
    img = psd.composite()  # RGBA, transparent background preserved
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"  {psd_path.name}  ->  {out_path.relative_to(REPO_ROOT)}")
    return True


def main():
    card_count = 0
    explainer_count = 0

    for num, label, card_folder, explainer_folder, patterns in SLOTS:
        print(f"Slot {num:02d} — {label}")
        card_psd = find_psd(card_folder, patterns, want_explainer=False, label=label)
        explainer_psd = find_psd(explainer_folder, patterns, want_explainer=True, label=label)

        if flatten(card_psd, IMAGES_OUT / f"{num:02d}.webp"):
            card_count += 1
        if flatten(explainer_psd, IMAGES_OUT / f"{num:02d}-explainer.webp"):
            explainer_count += 1

    homepage_exported = False
    if SQUARE_PSD.exists():
        homepage_exported = flatten(SQUARE_PSD, IMAGES_OUT / "homepage.png")
    else:
        print(f"  MISSING: {SQUARE_PSD.relative_to(REPO_ROOT)}")

    print(f"\nDone. {card_count}/{len(SLOTS)} card(s), "
          f"{explainer_count}/{len(SLOTS)} explainer(s), "
          f"{'1' if homepage_exported else '0'} homepage thumbnail exported.")
    print("Refresh encounters.html / index.html to see the changes.")


if __name__ == "__main__":
    main()
