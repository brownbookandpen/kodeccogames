#!/usr/bin/env python3
"""
sync_rule_stack.py — turn a folder of finished PNGs (e.g. designed in Photoshop)
into a stacked, mobile-friendly Mission Brief rules page.

USAGE
    python3 scripts/sync_rule_stack.py
    (or double-click scripts/[SYNC RULE STACK] sync_rule_stack.bat)

WHAT IT DOES
    Scans every folder under drafts/rules/ whose name ends in " TEXT"
    (e.g. "ALLEGIANCE TEXT", "CHARACTER TEXT"). For each one, it:
      1. Derives the rule's slug from the folder name — "ALLEGIANCE TEXT"
         -> "allegiance" — which must match the data-slug on that card's
         Mission Brief tile on index.html.
      2. Copies every .png/.jpg/.jpeg in the folder into rules/<slug>/images/,
         in order (sorted by the leading "[1]", "[2]", ... in the filename).
         Images are left as full-quality PNG (no cropping, no re-compression)
         since you're designing these yourself.
      3. Builds/overwrites rules/<slug>/<slug>.html — full-width, stacked,
         mobile-responsive, with the same site chrome (header/nav/CRT
         overlay/footer) as the rest of the site, plus click-to-zoom.
      4. Wires the matching Mission Brief card on index.html so clicking it
         opens this page directly instead of the "Coming Soon" popup.

    Re-running is always safe — it fully regenerates that rule's page and
    image folder from what's currently in the drafts/rules/<NAME> TEXT/
    folder, so just add/remove/rename PNGs there and re-run.

NAMING YOUR IMAGES
    Prefix each filename with its stack order, e.g.:
        [1] EXECUTIONER TEXT.png
        [2] WATCHMAN TEXT.png
    They'll be stacked top to bottom in that order. Files without a
    "[N]" prefix are sorted alphabetically after the numbered ones.

SETUP (once)
    pip install pillow
"""

import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Missing dependency. Run:  pip install pillow")

REPO_ROOT = Path(__file__).resolve().parent.parent
DRAFTS_RULES_DIR = REPO_ROOT / "drafts" / "rules"
RULES_DIR = REPO_ROOT / "rules"
INDEX_HTML = REPO_ROOT / "index.html"

RAW_EXTS = {".png", ".jpg", ".jpeg"}
MAX_WIDTH = 1600  # generous — these are meant to be read at full size


def slug_from_folder_name(name: str) -> str:
    base = re.sub(r"\s+text$", "", name.strip(), flags=re.IGNORECASE)
    s = base.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def sort_key(path: Path):
    m = re.match(r"^\s*\[(\d+)\]", path.stem)
    if m:
        return (0, int(m.group(1)), path.name.lower())
    return (1, 0, path.name.lower())


def copy_optimized(src: Path, dst: Path):
    im = Image.open(src)
    if im.mode not in ("RGBA", "RGB"):
        im = im.convert("RGBA")
    if im.width > MAX_WIDTH:
        new_h = int(im.height * (MAX_WIDTH / im.width))
        im = im.resize((MAX_WIDTH, new_h), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "PNG", optimize=True)


def get_title_and_tag(slug: str):
    """Pull the real title + [TAG] straight off the Mission Brief card on index.html,
    so this page always matches whatever's currently on the homepage."""
    text = INDEX_HTML.read_text(encoding="utf-8")
    card_re = re.compile(
        r'<div class="brief-card"[^>]*data-slug="' + re.escape(slug) + r'"[^>]*>.*?<h3>(.*?)</h3>',
        re.DOTALL,
    )
    m = card_re.search(text)
    if not m:
        return slug.replace("-", " ").title(), ""
    h3_inner = m.group(1).strip()
    tag_m = re.search(r'<span class="brief-tag">\[(.*?)\]</span>', h3_inner)
    tag = tag_m.group(1).strip() if tag_m else ""
    title = re.sub(r'<span class="brief-tag">.*?</span>', "", h3_inner).strip()
    title = re.sub(r"\s+", " ", title)
    return title or slug.replace("-", " ").title(), tag


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — CARRIER</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&family=VT323&display=swap" rel="stylesheet">
<style>
  :root{{
    --black:#0a0a0a; --panel:#161616; --panel2:#1c1c1c;
    --red:#c81d1d; --brightred:#e8341f; --darkred:#6e1010;
    --yellow:#f2c14e; --grey:#9a9a9a; --white:#eee8dc;
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  html{{scroll-behavior:smooth;}}
  body{{
    background:var(--black); color:var(--white);
    font-family:'VT323','Courier New',monospace; font-size:1.25rem; line-height:1.7;
    overflow-x:hidden;
  }}
  h1,.logo,nav a,.tag{{font-family:'DotGothic16',monospace;}}
  a{{color:inherit;}}
  .hazard{{height:10px; background:repeating-linear-gradient(45deg, var(--yellow) 0 20px, var(--black) 20px 40px);}}
  header{{
    position:sticky; top:0; z-index:10001; display:flex; align-items:center; justify-content:space-between;
    padding:12px 6%; border-bottom:2px solid var(--darkred);
    background:rgba(22,22,22,0.92); backdrop-filter:blur(4px);
  }}
  .logo-group{{display:flex; align-items:center; gap:14px; cursor:pointer; transition:opacity .15s;}}
  .logo-group:hover{{opacity:0.85;}}
  .logo-group img{{height:52px; width:auto; display:block; filter:drop-shadow(3px 3px 0 #000) drop-shadow(0 0 10px rgba(0,0,0,0.6));}}
  nav a{{
    color:var(--grey); text-decoration:none; margin-left:22px; font-size:0.6rem;
    text-transform:uppercase; border-bottom:2px solid transparent; padding-bottom:4px;
  }}
  nav a:hover{{color:var(--yellow); border-bottom:2px solid var(--yellow);}}
  .nav-toggle{{
    display:none; background:none; border:2px solid var(--darkred); color:var(--yellow);
    font-size:1.2rem; line-height:1; padding:6px 10px; cursor:pointer;
  }}
  .nav-toggle:hover{{border-color:var(--yellow);}}

  .post-header{{
    padding:70px 6% 40px; text-align:center;
    background:linear-gradient(rgba(8,8,8,0.9),rgba(8,8,8,0.94)), repeating-linear-gradient(135deg,#1a1a1a 0 40px,#141414 40px 80px);
    border-bottom:2px solid var(--darkred);
  }}
  .post-header .tag{{
    display:block; width:fit-content; margin:0 auto 22px; color:var(--yellow); border:2px solid var(--yellow);
    padding:8px 14px; font-size:0.5rem; letter-spacing:1px;
  }}
  .post-header h1{{font-size:clamp(1.4rem,4vw,2.1rem); color:var(--brightred); text-shadow:3px 3px 0 #000; margin-bottom:14px; line-height:1.5;}}
  .post-header .subtag{{color:var(--yellow); font-size:0.85rem; letter-spacing:1px; text-transform:uppercase;}}

  .stack{{max-width:900px; margin:0 auto; padding:50px 6% 40px;}}
  .stack-item{{margin:0 0 36px; text-align:center;}}
  .stack-item img{{
    display:block; width:100%; height:auto; margin:0 auto; cursor:zoom-in;
    transition:filter .2s;
  }}
  .stack-item img:hover{{filter:brightness(1.06);}}

  .lightbox{{
    position:fixed; inset:0; background:rgba(5,5,5,0.94); display:none;
    align-items:center; justify-content:center; z-index:20000; padding:24px; cursor:zoom-out;
  }}
  .lightbox.active{{display:flex;}}
  .lightbox img{{
    max-width:94vw; max-height:90vh; cursor:zoom-in;
    transition:transform .25s ease; transform-origin:center center;
  }}
  .lightbox img.zoomed{{transform:scale(1.6); cursor:zoom-out;}}
  .lightbox-close{{
    position:absolute; top:22px; right:34px; color:var(--yellow); font-size:2.4rem;
    font-family:'DotGothic16',monospace; cursor:pointer; line-height:1; z-index:20001;
  }}
  .lightbox-close:hover{{color:var(--red);}}
  .lightbox-hint{{
    position:absolute; bottom:18px; left:0; right:0; text-align:center;
    color:var(--grey); font-size:0.65rem; letter-spacing:0.5px; text-transform:uppercase;
    font-family:'DotGothic16',monospace; pointer-events:none;
  }}

  .back-link{{
    display:block; max-width:900px; margin:0 auto 80px; padding:0 6%;
    color:var(--yellow); text-decoration:none; font-size:0.7rem; letter-spacing:1px;
    font-family:'DotGothic16',monospace;
  }}
  .back-link:hover{{text-decoration:underline;}}

  footer{{text-align:center; padding:38px 6%; color:#5a5a5a; font-size:0.85rem; border-top:2px solid var(--darkred);}}
  footer .socials a{{margin:0 10px; color:var(--grey); text-decoration:none; font-weight:700;}}
  footer .socials a:hover{{color:var(--red);}}

  .crt-overlay{{
    position:fixed; inset:0; pointer-events:none; z-index:9999;
    background:repeating-linear-gradient(0deg, rgba(0,0,0,0.18) 0px, rgba(0,0,0,0.18) 1px, transparent 1px, transparent 3px);
    mix-blend-mode:overlay;
    animation:crtflicker 6s infinite;
  }}
  @keyframes crtflicker{{
    0%,100%{{opacity:0.85;}} 92%{{opacity:0.85;}} 93%{{opacity:0.55;}} 94%{{opacity:0.85;}} 96%{{opacity:0.65;}} 97%{{opacity:0.85;}}
  }}
  .post-header .tag::after{{
    content:"_"; margin-left:3px; animation:cursorblink 1s steps(1) infinite;
  }}
  @keyframes cursorblink{{ 50%{{ opacity:0; }} }}

  @media (max-width:560px){{
    .stack{{padding-top:34px;}}
    .stack-item{{margin-bottom:26px;}}
  }}
  @media (max-width:640px){{
    .nav-toggle{{display:block;}}
    nav{{
      display:none; position:absolute; top:100%; left:0; right:0;
      flex-direction:column; gap:2px; padding:10px 6% 18px;
      background:rgba(10,10,10,0.98); border-bottom:2px solid var(--darkred);
      z-index:10000;
    }}
    nav.open{{display:flex;}}
    nav a{{margin-left:0; padding:12px 0; font-size:0.8rem; border-bottom:1px solid #2b2b2b;}}
  }}
</style>
</head>
<body>

<div class="crt-overlay"></div>
<div class="hazard"></div>
<header>
  <a href="../../index.html" class="logo-group">
    <img src="../../images/kodecco-icon.png" alt="Kodecco Games">
  </a>
  <button class="nav-toggle" id="navToggle" aria-label="Toggle menu" aria-expanded="false">☰</button>
  <nav id="mainNav">
    <a href="../../index.html#brief">Mission Brief</a>
    <a href="../../index.html#gallery">Gallery</a>
    <a href="../../index.html#roadmap">Roadmap</a>
    <a href="../../index.html#journal">Dev Journal</a>
    <a href="../../index.html#signal">Send Signal</a>
  </nav>
</header>

<div class="post-header">
  <span class="tag">// MISSION BRIEF</span>
  <h1>{title}</h1>
  {subtag_html}
</div>

<div class="stack">
{stack_html}
</div>

<a class="back-link" href="../../index.html#brief">← Back to Mission Brief</a>

<footer>
  <div class="socials">
    <a href="#">Instagram</a> · <a href="#">BoardGameGeek</a> · <a href="#">Email</a>
  </div>
  <p style="margin-top:12px;">© 2026 CARRIER — a survival board game in development.</p>
</footer>

<div class="lightbox" id="lightbox">
  <span class="lightbox-close" id="lightboxClose">&times;</span>
  <img id="lightboxImg" src="" alt="">
  <span class="lightbox-hint">Click image to zoom · Click outside or press Esc to close</span>
</div>

<script>
  (function(){{
    var lb = document.getElementById('lightbox');
    var lbImg = document.getElementById('lightboxImg');
    var closeBtn = document.getElementById('lightboxClose');

    document.querySelectorAll('.stack-item img').forEach(function(img){{
      img.addEventListener('click', function(){{
        lbImg.src = img.getAttribute('src');
        lbImg.alt = img.getAttribute('alt') || '';
        lbImg.classList.remove('zoomed');
        lb.classList.add('active');
      }});
    }});

    lbImg.addEventListener('click', function(e){{
      e.stopPropagation();
      lbImg.classList.toggle('zoomed');
    }});

    function closeLightbox(){{
      lb.classList.remove('active');
      lbImg.classList.remove('zoomed');
    }}
    closeBtn.addEventListener('click', closeLightbox);
    lb.addEventListener('click', function(e){{ if(e.target === lb) closeLightbox(); }});
    document.addEventListener('keydown', function(e){{ if(e.key === 'Escape') closeLightbox(); }});

    var navToggle = document.getElementById('navToggle');
    var mainNav = document.getElementById('mainNav');
    if (navToggle && mainNav){{
      navToggle.addEventListener('click', function(){{
        var open = mainNav.classList.toggle('open');
        navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }});
      mainNav.querySelectorAll('a').forEach(function(a){{
        a.addEventListener('click', function(){{
          mainNav.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
        }});
      }});
    }}
  }})();
</script>

</body>
</html>
"""


def wire_brief_card(slug: str, page_path: str):
    text = INDEX_HTML.read_text(encoding="utf-8")
    card_re = re.compile(
        r'<div class="brief-card"([^>]*)data-slug="' + re.escape(slug) + r'"([^>]*)>'
    )
    m = card_re.search(text)
    if not m:
        print(f'  ! No <div class="brief-card" data-slug="{slug}"> found on index.html — add data-page manually.')
        return
    attrs_before, attrs_after = m.group(1), m.group(2)
    combined = re.sub(r'\s*data-page="[^"]*"', "", attrs_before + attrs_after)
    new_tag = f'<div class="brief-card" data-slug="{slug}" data-page="{page_path}"{combined}>'
    new_tag = re.sub(r"\s{2,}", " ", new_tag).replace(' >', '>')
    text = text[:m.start()] + new_tag + text[m.end():]
    INDEX_HTML.write_text(text, encoding="utf-8")


def process_folder(folder: Path):
    slug = slug_from_folder_name(folder.name)
    if not slug:
        print(f"Skipping {folder.name}/ (couldn't derive a slug from the folder name)")
        return

    images = sorted(
        (f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in RAW_EXTS),
        key=sort_key,
    )
    if not images:
        print(f"Skipping {folder.name}/ (no .png/.jpg/.jpeg files found)")
        return

    rule_dir = RULES_DIR / slug
    images_dir = rule_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # wipe old generated images so removed/renamed source files don't linger
    for old in images_dir.glob("*.png"):
        old.unlink()

    stack_html_parts = []
    for i, src in enumerate(images, start=1):
        out_name = f"{i:02d}.png"
        copy_optimized(src, images_dir / out_name)
        alt = re.sub(r"^\s*\[\d+\]\s*", "", src.stem).strip()
        alt = re.sub(r"\s+text$", "", alt, flags=re.IGNORECASE).strip() or slug
        stack_html_parts.append(
            f'  <div class="stack-item"><img src="images/{out_name}" alt="{alt}" loading="lazy"></div>'
        )

    title, tag = get_title_and_tag(slug)
    subtag_html = f'<div class="subtag">[{tag.upper()}]</div>' if tag else ""

    page_html = PAGE_TEMPLATE.format(
        title=title,
        subtag_html=subtag_html,
        stack_html="\n".join(stack_html_parts),
    )
    (rule_dir / f"{slug}.html").write_text(page_html, encoding="utf-8")

    wire_brief_card(slug, f"rules/{slug}/{slug}.html")

    print(f"Updated:  rules/{slug}/{slug}.html  ({len(images)} image(s) from {folder.relative_to(REPO_ROOT)})")


def main():
    if not DRAFTS_RULES_DIR.exists():
        sys.exit(f"No drafts/rules/ folder found at {DRAFTS_RULES_DIR}")

    folders = [f for f in DRAFTS_RULES_DIR.iterdir() if f.is_dir() and f.name.lower().endswith(" text")]
    if not folders:
        sys.exit('No folders ending in " TEXT" found under drafts/rules/ (e.g. "ALLEGIANCE TEXT").')

    for folder in sorted(folders):
        process_folder(folder)


if __name__ == "__main__":
    main()
