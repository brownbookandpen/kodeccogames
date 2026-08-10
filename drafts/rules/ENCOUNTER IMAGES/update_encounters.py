#!/usr/bin/env python3
"""
update_encounters.py

Scans this folder for PSD files named "[N] NAME.psd", flattens each to a
transparent PNG, saves them into rules/encounters/images/0N.png, rewrites the
stack section of rules/encounters/encounters.html (creating the page from a
template on first run), and updates the "ENCOUNTERS" card thumbnail on the
homepage Mission Brief section (index.html) to point at the new page.

Rename/renumber the PSDs (e.g. swap [1] and [2]) and re-run to reorder
the page.

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

SLUG = "encounters"
TITLE = "ENCOUNTERS"
SUBTAG = "[THREATS]"

SCRIPT_DIR = Path(__file__).resolve().parent
# ENCOUNTER IMAGES -> rules -> drafts -> kodeccogames (repo root)
REPO_ROOT = SCRIPT_DIR.parents[2]
IMAGES_OUT = REPO_ROOT / "rules" / SLUG / "images"
HTML_PATH = REPO_ROOT / "rules" / SLUG / f"{SLUG}.html"
INDEX_PATH = REPO_ROOT / "index.html"

NAME_RE = re.compile(r"^\[(\d+)\]\s*(.+?)\s*\.psd$", re.IGNORECASE)

PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ENCOUNTERS — CARRIER</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DotGothic16&family=VT323&display=swap" rel="stylesheet">
<style>
  :root{
    --black:#0a0a0a; --panel:#161616; --panel2:#1c1c1c;
    --red:#c81d1d; --brightred:#e8341f; --darkred:#6e1010;
    --yellow:#f2c14e; --grey:#9a9a9a; --white:#eee8dc;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html{scroll-behavior:smooth;}
  body{
    background:var(--black); color:var(--white);
    font-family:'VT323','Courier New',monospace; font-size:1.25rem; line-height:1.7;
    overflow-x:hidden;
  }
  h1,.logo,nav a,.tag{font-family:'DotGothic16',monospace;}
  a{color:inherit;}
  .hazard{height:10px; background:repeating-linear-gradient(45deg, var(--yellow) 0 20px, var(--black) 20px 40px);}
  header{
    position:sticky; top:0; z-index:10001; display:flex; align-items:center; justify-content:space-between;
    padding:12px 6%; border-bottom:2px solid var(--darkred);
    background:rgba(22,22,22,0.92); backdrop-filter:blur(4px);
  }
  .logo-group{display:flex; align-items:center; gap:14px; cursor:pointer; transition:opacity .15s;}
  .logo-group:hover{opacity:0.85;}
  .logo-group img{height:52px; width:auto; display:block; filter:drop-shadow(3px 3px 0 #000) drop-shadow(0 0 10px rgba(0,0,0,0.6));}
  nav a{
    color:var(--grey); text-decoration:none; margin-left:22px; font-size:0.6rem;
    text-transform:uppercase; border-bottom:2px solid transparent; padding-bottom:4px;
  }
  nav a:hover{color:var(--yellow); border-bottom:2px solid var(--yellow);}
  .nav-toggle{
    display:none; background:none; border:2px solid var(--darkred); color:var(--yellow);
    font-size:1.2rem; line-height:1; padding:6px 10px; cursor:pointer;
  }
  .nav-toggle:hover{border-color:var(--yellow);}

  .post-header{
    padding:70px 6% 40px; text-align:center;
    background:linear-gradient(rgba(8,8,8,0.9),rgba(8,8,8,0.94)), repeating-linear-gradient(135deg,#1a1a1a 0 40px,#141414 40px 80px);
    border-bottom:2px solid var(--darkred);
  }
  .post-header .tag{
    display:block; width:fit-content; margin:0 auto 22px; color:var(--yellow); border:2px solid var(--yellow);
    padding:8px 14px; font-size:0.5rem; letter-spacing:1px;
  }
  .post-header h1{font-size:clamp(1.4rem,4vw,2.1rem); color:var(--brightred); text-shadow:3px 3px 0 #000; margin-bottom:14px; line-height:1.5;}
  .post-header .subtag{color:var(--yellow); font-size:0.85rem; letter-spacing:1px; text-transform:uppercase;}

  .stack{max-width:900px; margin:0 auto; padding:50px 6% 40px;}
  .stack-item{margin:0 0 36px; text-align:center;}
  .stack-item img{
    display:block; width:100%; height:auto; margin:0 auto; cursor:zoom-in;
    transition:filter .2s;
  }
  .stack-item img:hover{filter:brightness(1.06);}

  .lightbox{
    position:fixed; inset:0; background:rgba(5,5,5,0.94); display:none;
    align-items:center; justify-content:center; z-index:20000; padding:24px; cursor:zoom-out;
  }
  .lightbox.active{display:flex;}
  .lightbox img{
    max-width:94vw; max-height:90vh; cursor:zoom-in;
    transition:transform .25s ease; transform-origin:center center;
  }
  .lightbox img.zoomed{transform:scale(1.6); cursor:zoom-out;}
  .lightbox-close{
    position:absolute; top:22px; right:34px; color:var(--yellow); font-size:2.4rem;
    font-family:'DotGothic16',monospace; cursor:pointer; line-height:1; z-index:20001;
  }
  .lightbox-close:hover{color:var(--red);}
  .lightbox-hint{
    position:absolute; bottom:18px; left:0; right:0; text-align:center;
    color:var(--grey); font-size:0.65rem; letter-spacing:0.5px; text-transform:uppercase;
    font-family:'DotGothic16',monospace; pointer-events:none;
  }

  .back-link{
    display:block; max-width:900px; margin:0 auto 80px; padding:0 6%;
    color:var(--yellow); text-decoration:none; font-size:0.7rem; letter-spacing:1px;
    font-family:'DotGothic16',monospace;
  }
  .back-link:hover{text-decoration:underline;}

  footer{text-align:center; padding:38px 6%; color:#5a5a5a; font-size:0.85rem; border-top:2px solid var(--darkred);}
  footer .socials a{margin:0 10px; color:var(--grey); text-decoration:none; font-weight:700;}
  footer .socials a:hover{color:var(--red);}

  .crt-overlay{
    position:fixed; inset:0; pointer-events:none; z-index:9999;
    background:repeating-linear-gradient(0deg, rgba(0,0,0,0.18) 0px, rgba(0,0,0,0.18) 1px, transparent 1px, transparent 3px);
    mix-blend-mode:overlay;
    animation:crtflicker 6s infinite;
  }
  @keyframes crtflicker{
    0%,100%{opacity:0.85;} 92%{opacity:0.85;} 93%{opacity:0.55;} 94%{opacity:0.85;} 96%{opacity:0.65;} 97%{opacity:0.85;}
  }
  .post-header .tag::after{
    content:"_"; margin-left:3px; animation:cursorblink 1s steps(1) infinite;
  }
  @keyframes cursorblink{ 50%{ opacity:0; } }

  @media (max-width:560px){
    .stack{padding-top:34px;}
    .stack-item{margin-bottom:26px;}
  }
  @media (max-width:640px){
    .nav-toggle{display:block;}
    nav{
      display:none; position:absolute; top:100%; left:0; right:0;
      flex-direction:column; gap:2px; padding:10px 6% 18px;
      background:rgba(10,10,10,0.98); border-bottom:2px solid var(--darkred);
      z-index:10000;
    }
    nav.open{display:flex;}
    nav a{margin-left:0; padding:12px 0; font-size:0.8rem; border-bottom:1px solid #2b2b2b;}
  }
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
  <h1>ENCOUNTERS</h1>
  <div class="subtag">[THREATS]</div>
</div>

<div class="stack">
<!-- STACK_ITEMS_START -->
<!-- STACK_ITEMS_END -->
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
  (function(){
    var lb = document.getElementById('lightbox');
    var lbImg = document.getElementById('lightboxImg');
    var closeBtn = document.getElementById('lightboxClose');

    document.querySelectorAll('.stack-item img').forEach(function(img){
      img.addEventListener('click', function(){
        lbImg.src = img.getAttribute('src');
        lbImg.alt = img.getAttribute('alt') || '';
        lbImg.classList.remove('zoomed');
        lb.classList.add('active');
      });
    });

    lbImg.addEventListener('click', function(e){
      e.stopPropagation();
      lbImg.classList.toggle('zoomed');
    });

    function closeLightbox(){
      lb.classList.remove('active');
      lbImg.classList.remove('zoomed');
    }
    closeBtn.addEventListener('click', closeLightbox);
    lb.addEventListener('click', function(e){ if(e.target === lb) closeLightbox(); });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeLightbox(); });

    var navToggle = document.getElementById('navToggle');
    var mainNav = document.getElementById('mainNav');
    if (navToggle && mainNav){
      navToggle.addEventListener('click', function(){
        var open = mainNav.classList.toggle('open');
        navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      mainNav.querySelectorAll('a').forEach(function(a){
        a.addEventListener('click', function(){
          mainNav.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
        });
      });
    }
  })();
</script>

</body>
</html>
"""


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


def ensure_page():
    if HTML_PATH.exists():
        return
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = PAGE_TEMPLATE.replace("ENCOUNTERS", TITLE).replace("[THREATS]", SUBTAG)
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"  created page: {HTML_PATH.relative_to(REPO_ROOT)}")


def rewrite_html(items):
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
        print("  WARNING: STACK_ITEMS markers not found; page not updated.")
        return

    new_html = pattern.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", html)
    HTML_PATH.write_text(new_html, encoding="utf-8")


def rewrite_index(items):
    if not items:
        return
    if not INDEX_PATH.exists():
        print(f"  WARNING: index.html not found at {INDEX_PATH}, skipping index update.")
        return

    html = INDEX_PATH.read_text(encoding="utf-8")

    first_num, _, _ = items[0]
    thumb_src = f"rules/{SLUG}/images/{first_num:02d}.png"
    page_href = f"rules/{SLUG}/{SLUG}.html"

    card_re = re.compile(
        r'(<div class="brief-card" data-slug="' + SLUG + r'")([^>]*)(>.*?\n    </div>)',
        re.DOTALL,
    )
    m = card_re.search(html)
    if not m:
        print(f"  WARNING: brief-card for slug '{SLUG}' not found in index.html; not updated.")
        return

    open_attrs = m.group(2)
    body = m.group(3)

    already_linked = "data-page=" in open_attrs
    if not already_linked:
        open_attrs = f' data-page="{page_href}"' + open_attrs

    if already_linked:
        # Card is already wired up to its page from a previous run — leave the
        # homepage thumbnail alone (it may have been swapped for a custom
        # "coming soon" image on purpose) and only keep the link current.
        new_body = body
    else:
        shot_re = re.compile(r'<div class="brief-shot">.*?</div>', re.DOTALL)
        new_shot = f'<div class="brief-shot"><img src="{thumb_src}" alt="{TITLE} art"></div>'
        new_body = shot_re.sub(new_shot, body, count=1)

    new_card = m.group(1) + open_attrs + new_body
    new_html = html[: m.start()] + new_card + html[m.end():]
    INDEX_PATH.write_text(new_html, encoding="utf-8")


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

    ensure_page()
    rewrite_html(items)
    rewrite_index(items)
    print("Done. Refresh index.html / the page to see the changes.")


if __name__ == "__main__":
    main()
