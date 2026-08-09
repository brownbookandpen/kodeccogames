#!/usr/bin/env python3
"""
sync_gallery.py — drop a photo into a gallery folder, get it wired onto the site.

USAGE
    python3 scripts/sync_gallery.py
    (or double-click scripts/sync_gallery.bat)

WHAT IT DOES
    Scans every folder listed in FOLDER_CONFIG below for new, not-yet-wired
    photos. For each new .png/.jpg/.jpeg it finds sitting directly in a
    folder (i.e. not already turned into a .webp), it will:
      1. Center-crop it to a square and save an optimized .webp copy.
      2. Turn the filename itself into the caption. Name your file like a
         caption before dropping it in, e.g.:
             "New box render with the matte finish and foil logo.png"
         becomes the caption/title shown on the site.
      3. Insert a new tile into the matching spot on index.html — found via
         an <!-- GALLERY: <folder name> --> comment marker that sits right
         before that section's grid on the page.
      4. Remember it in a per-folder manifest (.gallery-manifest.json) so
         re-running the scan never wires the same photo in twice.

    It does NOT touch the 4 curated "Gallery" hero tiles at the top of the
    page, or the hand-picked lightbox reels — those are curated highlights,
    not simple lists, so they stay a manual edit.

SETUP (once)
    pip install pillow

ADDING A NEW FOLDER
    Add a folder under images/, add an entry to FOLDER_CONFIG below with
    a matching "dir" name, and put a
        <!-- GALLERY: <that same dir name> -->
        <div class="concept-grid"></div>     (or class="brief-gallery")
    marker + empty container in index.html wherever you want photos from
    that folder to appear. That's the only wiring needed — the script
    finds everything else from there.
"""

import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Missing dependency. Run:  pip install pillow")

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"
INDEX_HTML = REPO_ROOT / "index.html"

# dir: folder name under images/ (must exactly match the <!-- GALLERY: ... --> marker)
# slug: short, clean prefix used when naming generated .webp files
# kind: "concept-grid" (140px tiles, used on Roadmap) or "brief-gallery" (52px thumbs, Mission Brief)
FOLDER_CONFIG = [
    {"dir": "[ROADMAP] 1. CONCEPT AND CORE LOOP", "slug": "concept", "kind": "concept-grid"},
    {"dir": "[ROADMAP] 2. PAPER PROTOTYPE", "slug": "paper-prototype", "kind": "concept-grid"},
    {"dir": "[ROADMAP] 3. BALANCING AND PLAYTESTING", "slug": "balancing", "kind": "concept-grid"},
    {"dir": "[ROADMAP] 4. ART AND COMPONENT DESIGN", "slug": "art-component", "kind": "concept-grid"},
    {"dir": "[ROADMAP] 5. PUBLISHING & CROWDFUNDING", "slug": "publishing", "kind": "concept-grid"},
    {"dir": "[GALLERY] 1. LATEST DESIGNS", "slug": "latest-design", "kind": None},
    {"dir": "[GALLERY] 3. CUTTING ROOM", "slug": "cutting-room", "kind": None},
    {"dir": "[GALLERY] 4. PLAY TEST SESSIONS", "slug": "playtest", "kind": None},
    {"dir": "[MISSION BRIEF] 1. SURVIVORS", "slug": "mb-survivors", "kind": "brief-gallery"},
    {"dir": "[MISSION BRIEF] 2. ENCOUNTERS & SUPPLIES", "slug": "mb-encounters", "kind": "brief-gallery"},
    {"dir": "[MISSION BRIEF] 3. ZOMBIES", "slug": "mb-zombies", "kind": "brief-gallery"},
    {"dir": "[MISSION BRIEF] 4. ESCALATION", "slug": "mb-escalation", "kind": "brief-gallery"},
    {"dir": "[INSTAGRAM] POSTS", "slug": "ig", "kind": "ig-grid"},
]
# NOTE: [GALLERY] 1/3/4 have kind=None — they only feed a single curated hero
# thumbnail each, with no repeatable grid on the page yet, so this script
# converts+optimizes photos dropped there but does not auto-insert tiles.
# Set the hero thumbnail (images/latest-designs/executioner.webp etc. — now
# renamed) by hand if you want to swap which photo is featured.

RAW_EXTS = {".png", ".jpg", ".jpeg"}
TILE_SIZE = {"concept-grid": 640, "brief-gallery": 300, "ig-grid": 480}
MANIFEST_NAME = ".gallery-manifest.json"


def load_manifest(folder: Path) -> dict:
    mpath = folder / MANIFEST_NAME
    if mpath.exists():
        return json.loads(mpath.read_text(encoding="utf-8"))
    return {}


def save_manifest(folder: Path, manifest: dict):
    (folder / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def filename_to_caption(stem: str) -> str:
    text = re.sub(r"[_\-]+", " ", stem)
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        text = text[0].upper() + text[1:]
    if text and text[-1] not in ".!?":
        text += "."
    return text


def filename_to_title(caption: str) -> str:
    base = caption.strip(".")
    for sep in (",", " — ", " - "):
        if sep in base:
            head = base.split(sep, 1)[0].strip()
            if 3 <= len(head) <= 32:
                return head
    words = re.split(r"\s+", base)
    title = ""
    for w in words:
        candidate = (title + " " + w).strip()
        if len(candidate) > 28:
            break
        title = candidate
    return title or base[:28]


def next_slug(folder: Path, slug_prefix: str) -> str:
    existing = list(folder.glob("*.webp"))
    n = len(existing) + 1
    while (folder / f"{slug_prefix}-{n}.webp").exists():
        n += 1
    return f"{slug_prefix}-{n}.webp"


def make_square_webp(src: Path, dst: Path, size: int):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    side = min(w, h)
    x0 = (w - side) // 2
    y0 = (h - side) // 2
    im = im.crop((x0, y0, x0 + side, y0 + side))
    if side > size:
        im = im.resize((size, size), Image.LANCZOS)
    im.save(dst, "WEBP", quality=82)


def url_escape(path: str) -> str:
    # Only need to worry about characters that are unsafe *inside an HTML
    # attribute*, since these are relative paths, not full URLs, and browsers
    # tolerate literal spaces/brackets in relative hrefs just fine.
    return path.replace("&", "&amp;")


def find_grid_for_folder(text: str, folder_dir: str):
    """Return (open_tag_end, close_idx) for the container right after this folder's marker comment."""
    marker = f"<!-- GALLERY: {folder_dir} -->"
    idx = text.find(marker)
    if idx == -1:
        return None

    open_re = re.compile(r'<div class="(?:concept-grid|brief-gallery|ig-grid)">')
    m = open_re.search(text, idx)
    if not m:
        return None
    open_tag_end = m.end()

    close_re = re.compile(r"\n\s*</div>")
    m2 = close_re.search(text, open_tag_end)
    if not m2:
        return None
    return open_tag_end, m2.start()


def insert_item(text: str, folder_dir: str, kind: str, slug: str, alt: str, caption: str, title: str) -> str:
    found = find_grid_for_folder(text, folder_dir)
    if found is None:
        print(f"  ! No <!-- GALLERY: {folder_dir} --> marker (with an empty grid after it) found. Skipping HTML wiring.")
        return text
    open_tag_end, close_idx = found

    src = url_escape(f"images/{folder_dir}/{slug}")
    caption_html = caption.replace('"', "&quot;")
    alt_html = alt.replace('"', "&quot;")
    title_html = title.replace("&", "&amp;")

    # Match indentation of the container's own line.
    line_start = text.rfind("\n", 0, open_tag_end) + 1
    base_indent = re.match(r"[ \t]*", text[line_start:open_tag_end]).group(0)
    child_indent = base_indent + "  "

    if kind == "brief-gallery":
        new_item = f'\n{child_indent}<div class="bg-item"><img src="{src}" alt="{alt_html}" title="{caption_html}"></div>'
    elif kind == "ig-grid":
        new_item = (
            f'\n{child_indent}<a class="ig-item" href="https://www.instagram.com/kodecco.games/" '
            f'target="_blank" rel="noopener"><img src="{src}" alt="{alt_html}" loading="lazy"></a>'
        )
    else:
        new_item = (
            f'\n{child_indent}<div class="cg-item"><img src="{src}" '
            f'alt="{alt_html}" data-caption="{caption_html}"><span class="cg-title">{title_html}</span></div>'
        )

    return text[:close_idx] + new_item + text[close_idx:]


def process_folder(cfg: dict) -> int:
    folder = IMAGES_DIR / cfg["dir"]
    if not folder.exists():
        print(f"Skipping {cfg['dir']}/ (folder doesn't exist)")
        return 0

    manifest = load_manifest(folder)
    raw_files = sorted(
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in RAW_EXTS and f.name not in manifest
    )
    if not raw_files:
        return 0

    tile_size = TILE_SIZE.get(cfg["kind"], 640)
    index_text = INDEX_HTML.read_text(encoding="utf-8") if cfg["kind"] else None
    added = 0

    for raw in raw_files:
        caption = filename_to_caption(raw.stem)
        title = filename_to_title(caption)
        slug = next_slug(folder, cfg["slug"])

        make_square_webp(raw, folder / slug, tile_size)

        if cfg["kind"]:
            index_text = insert_item(index_text, cfg["dir"], cfg["kind"], slug, title, caption, title)

        manifest[raw.name] = {"slug": slug, "title": title, "caption": caption}
        print(f"  + {raw.name}\n      -> images/{cfg['dir']}/{slug}  \"{title}\"")
        added += 1

    if cfg["kind"]:
        INDEX_HTML.write_text(index_text, encoding="utf-8")
    save_manifest(folder, manifest)
    return added


def main():
    total = 0
    for cfg in FOLDER_CONFIG:
        print(f"Scanning images/{cfg['dir']}/ ...")
        total += process_folder(cfg)

    if total == 0:
        print("\nNo new photos found. Everything's already wired in.")
    else:
        print(f"\n{total} new photo(s) processed.")


if __name__ == "__main__":
    main()
