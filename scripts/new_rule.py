#!/usr/bin/env python3
"""
new_rule.py — turn a plain text/markdown draft into a Mission Brief rules page.

USAGE
    python3 scripts/new_rule.py drafts/rules/allegiance.md

WHAT IT DOES
    1. Reads a draft file with a small frontmatter block + your writing.
       Same format as new_post.py's Dev Journal drafts.
    2. Crops every photo you reference to a clean rectangle (landscape,
       default 3:2) so nothing looks stretched or squished on the site.
    3. Generates rules/<slug>/<slug>.html, with its own rules/<slug>/images/
       folder — each rule page is fully self-contained in one folder.
    4. Wires the matching Mission Brief card on index.html (matched by
       its data-slug="<slug>" attribute) so clicking it opens the new
       page directly instead of the "Coming Soon" popup.

RUNNING ON EVERYTHING AT ONCE
    python3 scripts/new_rule.py --all
    (or double-click scripts/new_rule.bat with no file dragged onto it)
    Scans every drafts/rules/*.md and rebuilds/updates all of them.

SETUP (once)
    pip install pillow

DRAFT FILE FORMAT  (see drafts/rules/example-rule.md for a working sample)

    ---
    title: Allegiance
    tag: Secret Role
    slug: allegiance      (must match the data-slug on the Mission Brief card)
    aspect: 3:2            (optional, default 3:2. try 16:9 or 4:3)
    ---

    Plain paragraphs just work.

    ## A heading

    More paragraphs. **bold** and *italic* work.

    ![Alt text for accessibility](my-photo.jpg "Optional caption shown under the photo")

    Photos are found relative to the draft file itself, so keep them
    in the same folder (or a subfolder) as the .md file.
"""

import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Missing dependency. Run:  pip install pillow")

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / "rules"
INDEX_HTML = REPO_ROOT / "index.html"

MAX_WIDTH = 1400


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        sys.exit("Draft is missing the --- frontmatter block at the top.")
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, val = line.split(":", 1)
        fm[key.strip()] = val.strip()
    return fm, body


def parse_aspect(aspect_str: str) -> float:
    if ":" in aspect_str:
        w, h = aspect_str.split(":")
        return float(w) / float(h)
    return float(aspect_str)


def crop_to_rect(src: Path, dst: Path, aspect: float):
    """Center-crop an image to the given landscape aspect ratio, resize, save as .avif."""
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    target_ratio = aspect
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        y0 = (h - new_h) // 2
        im = im.crop((0, y0, w, y0 + new_h))

    if im.width > MAX_WIDTH:
        new_h = int(MAX_WIDTH / target_ratio)
        im = im.resize((MAX_WIDTH, new_h), Image.LANCZOS)

    dst.parent.mkdir(parents=True, exist_ok=True)
    avif_dst = dst.with_suffix(".avif")
    try:
        im.save(avif_dst, "AVIF", quality=80)
        return avif_dst
    except Exception:
        jpg_dst = dst.with_suffix(".jpg")
        im.save(jpg_dst, "JPEG", quality=88)
        return jpg_dst


IMG_RE = re.compile(
    r'!\[(?P<alt>[^\]]*)\]\((?P<path>[^\s)"]+)(?:\s+"(?P<cap>[^"]*)")?\)'
    r'(?:\s*\{aspect=(?P<aspect>[^}]+)\})?'
)
HEADING_RE = re.compile(r"^##\s+(.*)$")
CARD_BLOCK_RE = re.compile(r"^::card\s*\n(.*?)\n::\s*$", re.DOTALL | re.MULTILINE)


def resolve_and_save_image(src_path: Path, out_path_no_ext: Path, per_image_aspect: str, fallback_aspect: float):
    """Crop+save an image, honoring a per-image {aspect=...} override (including 'original' = no crop)."""
    aspect_str = (per_image_aspect or "").strip().lower()
    if aspect_str == "original":
        return save_card_image(src_path, out_path_no_ext, max_width=MAX_WIDTH)
    target = parse_aspect(per_image_aspect) if per_image_aspect else fallback_aspect
    return crop_to_rect(src_path, out_path_no_ext, target)


def inline_format(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s


def save_card_image(src: Path, dst: Path, max_width: int = 520):
    """Save a card/asset image as-is (no crop, alpha preserved) for side-by-side layout."""
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGBA", "RGB"):
        im = im.convert("RGBA")
    if im.width > max_width:
        new_h = int(im.height * (max_width / im.width))
        im = im.resize((max_width, new_h), Image.LANCZOS)
    dst = dst.with_suffix(".png")
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "PNG", optimize=True)
    return dst


def build_card_block_html(inner: str, draft_dir: Path, images_dir: Path, img_counter: int):
    """Render a ::card ... :: block as an image-left / text-right row. Returns (html, img_counter)."""
    blocks = re.split(r"\n\s*\n", inner.strip())
    img_html = ""
    title_html = ""
    text_parts = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        img_match = IMG_RE.match(block)
        h_match = HEADING_RE.match(block)
        if img_match and not img_html:
            img_counter += 1
            alt = img_match.group("alt")
            src_path = draft_dir / img_match.group("path")
            if not src_path.exists():
                sys.exit(f"Image not found: {src_path}")
            out_path = images_dir / f"{img_counter:02d}-card"
            card_aspect = img_match.group("aspect")
            if card_aspect and card_aspect.strip().lower() != "original":
                final_path = resolve_and_save_image(src_path, out_path, card_aspect, 1.0)
            else:
                final_path = save_card_image(src_path, out_path)
            img_html = f'<img src="images/{final_path.name}" alt="{alt}">'
        elif h_match and not title_html:
            title_html = inline_format(h_match.group(1))
        else:
            paragraph = " ".join(line.strip() for line in block.splitlines())
            text_parts.append(f"<p>{inline_format(paragraph)}</p>")

    html = (
        '  <div class="card-row">\n'
        f'    <h3 class="card-title">{title_html}</h3>\n'
        f'    <div class="card-img">{img_html}</div>\n'
        f'    <div class="card-text">\n      ' + "\n      ".join(text_parts) + "\n    </div>\n"
        "  </div>"
    )
    return html, img_counter


def build_body_html(body: str, draft_dir: Path, rule_images_dir: Path, aspect: float):
    html_parts = []
    img_counter = 0

    card_html_by_token = {}
    def _stash_card(m):
        nonlocal img_counter
        html, img_counter = build_card_block_html(m.group(1), draft_dir, rule_images_dir, img_counter)
        token = f"@@CARD{len(card_html_by_token)}@@"
        card_html_by_token[token] = html
        return f"\n\n{token}\n\n"
    body = CARD_BLOCK_RE.sub(_stash_card, body)

    blocks = re.split(r"\n\s*\n", body.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        if block in card_html_by_token:
            html_parts.append(card_html_by_token[block])
            continue

        img_match = IMG_RE.match(block)
        h_match = HEADING_RE.match(block)

        if img_match:
            img_counter += 1
            alt = img_match.group("alt")
            src_path = draft_dir / img_match.group("path")
            caption = img_match.group("cap")
            if not src_path.exists():
                sys.exit(f"Image not found: {src_path}")

            out_name = f"{img_counter:02d}{src_path.suffix.lower()}"
            out_path = rule_images_dir / out_name
            final_path = resolve_and_save_image(src_path, out_path, img_match.group("aspect"), aspect)
            web_path = f"images/{final_path.name}"

            html_parts.append("  <figure>")
            html_parts.append(f'    <img src="{web_path}" alt="{alt}">')
            if caption:
                html_parts.append(f"    <figcaption>{caption}</figcaption>")
            html_parts.append("  </figure>")

        elif h_match:
            html_parts.append(f"  <h2>{inline_format(h_match.group(1))}</h2>")

        else:
            paragraph = " ".join(line.strip() for line in block.splitlines())
            html_parts.append(f"  <p>{inline_format(paragraph)}</p>")

    return "\n\n".join(html_parts)


RULE_TEMPLATE = """<!DOCTYPE html>
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
  }}
  h1,h2,.logo,nav a,.tag{{font-family:'DotGothic16',monospace;}}
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

  .post-body{{max-width:720px; margin:0 auto; padding:60px 6% 40px;}}
  .post-body p{{color:var(--white); margin-bottom:24px; font-size:1.15rem;}}
  .post-body h2{{color:var(--red); font-size:1.2rem; margin:36px 0 16px;}}
  .post-body figure{{margin:0 0 32px;}}
  .post-body figure img{{display:block; width:100%; height:auto; border:2px solid var(--darkred); cursor:zoom-in; transition:border-color .2s;}}
  .post-body figure img:hover{{border-color:var(--yellow);}}
  .post-body figcaption{{color:var(--grey); font-size:0.9rem; margin-top:10px; line-height:1.5;}}

  .card-row{{
    display:grid; grid-template-columns:220px 1fr; grid-template-areas:"title title" "img text";
    column-gap:28px; row-gap:16px; margin:0 0 32px;
    background:var(--panel); border:2px solid var(--darkred); padding:22px 26px;
  }}
  .card-row .card-title{{
    grid-area:title; color:var(--red); font-family:'DotGothic16',monospace; font-size:1.05rem;
    letter-spacing:0.5px; text-transform:uppercase;
  }}
  .card-row .card-img{{grid-area:img; width:220px;}}
  .card-row .card-img img{{display:block; width:100%; height:auto; cursor:zoom-in; transition:filter .2s;}}
  .card-row .card-img img:hover{{filter:brightness(1.08);}}
  .card-row .card-text{{grid-area:text; min-width:0;}}
  .card-row .card-text p{{color:var(--white); margin-bottom:16px; font-size:1.05rem; line-height:1.6;}}
  @media (max-width:560px){{
    .card-row{{grid-template-columns:1fr; grid-template-areas:"title" "img" "text"; text-align:center;}}
    .card-row .card-img{{width:100%; max-width:260px; margin:0 auto;}}
  }}

  .lightbox{{
    position:fixed; inset:0; background:rgba(5,5,5,0.94); display:none;
    align-items:center; justify-content:center; z-index:20000; padding:40px; cursor:zoom-out;
  }}
  .lightbox.active{{display:flex;}}
  .lightbox img{{
    max-width:92vw; max-height:88vh; border:2px solid var(--darkred);
    box-shadow:0 0 40px rgba(0,0,0,0.6); cursor:zoom-in;
    transition:transform .25s ease; transform-origin:center center;
  }}
  .lightbox img.zoomed{{transform:scale(1.9); cursor:zoom-out;}}
  .lightbox-close{{
    position:absolute; top:22px; right:34px; color:var(--yellow); font-size:2.4rem;
    font-family:'DotGothic16',monospace; cursor:pointer; line-height:1; z-index:20001;
  }}
  .lightbox-close:hover{{color:var(--red);}}
  .lightbox-hint{{
    position:absolute; bottom:22px; left:0; right:0; text-align:center;
    color:var(--grey); font-size:0.7rem; letter-spacing:0.5px; text-transform:uppercase;
    font-family:'DotGothic16',monospace; pointer-events:none;
  }}

  .back-link{{
    display:block; max-width:720px; margin:0 auto 80px; padding:0 6%;
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
</style>
</head>
<body>

<div class="crt-overlay"></div>
<div class="hazard"></div>
<header>
  <a href="../../index.html" class="logo-group">
    <img src="../../images/kodecco-icon.png" alt="Kodecco Games">
  </a>
  <nav>
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
  <div class="subtag">[{tag}]</div>
</div>

<div class="post-body">

{body_html}

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

    document.querySelectorAll('.post-body figure img, .post-body .card-row img').forEach(function(img){{
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
  }})();
</script>

</body>
</html>
"""


def wire_brief_card(slug: str, page_path: str):
    """Add/refresh data-page="rules/<slug>/<slug>.html" on the matching Mission Brief card."""
    text = INDEX_HTML.read_text(encoding="utf-8")

    card_re = re.compile(
        r'<div class="brief-card"([^>]*)data-slug="' + re.escape(slug) + r'"([^>]*)>'
    )
    m = card_re.search(text)
    if not m:
        print(f'  ! No <div class="brief-card" data-slug="{slug}"> found on index.html — add data-page manually.')
        return

    attrs_before, attrs_after = m.group(1), m.group(2)
    combined = attrs_before + attrs_after
    # strip any existing data-page="..." so re-running never duplicates it
    combined = re.sub(r'\s*data-page="[^"]*"', "", combined)
    new_tag = f'<div class="brief-card" data-slug="{slug}" data-page="{page_path}"{combined}>'
    # normalize potential double spacing
    new_tag = re.sub(r"\s{2,}", " ", new_tag).replace(' >', '>')

    text = text[:m.start()] + new_tag + text[m.end():]
    INDEX_HTML.write_text(text, encoding="utf-8")


def process_draft(draft_path: Path):
    raw = draft_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)

    if str(fm.get("skip", "")).strip().lower() in ("true", "yes", "1"):
        print(f"Skipped (marked skip: true):  {draft_path.relative_to(REPO_ROOT)}")
        return None

    title = fm.get("title", "Untitled")
    tag = fm.get("tag", "").upper()
    aspect = parse_aspect(fm.get("aspect", "3:2"))
    slug = fm.get("slug") or slugify(title)

    rule_dir = RULES_DIR / slug
    rule_images_dir = rule_dir / "images"

    body_html = build_body_html(body, draft_path.parent, rule_images_dir, aspect)

    rule_html = RULE_TEMPLATE.format(title=title, tag=tag, body_html=body_html)
    rule_dir.mkdir(parents=True, exist_ok=True)
    rule_path = rule_dir / f"{slug}.html"
    rule_path.write_text(rule_html, encoding="utf-8")

    wire_brief_card(slug, f"rules/{slug}/{slug}.html")

    try:
        src_label = draft_path.relative_to(REPO_ROOT)
    except ValueError:
        src_label = draft_path
    print(f"Updated:  rules/{slug}/{slug}.html  (from {src_label})")
    return slug


def find_all_drafts():
    drafts_dir = REPO_ROOT / "drafts" / "rules"
    if not drafts_dir.exists():
        return []
    return sorted(drafts_dir.rglob("*.md"))


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--all", "all"):
        drafts = find_all_drafts()
        if not drafts:
            sys.exit("No drafts found in drafts/rules/. Drag a .md file onto new_rule.bat, or pass a path.")
        for d in drafts:
            process_draft(d)
        return

    draft_path = Path(args[0])
    if not draft_path.is_absolute():
        draft_path = REPO_ROOT / draft_path
    if not draft_path.exists():
        sys.exit(f"Draft not found: {draft_path}")
    process_draft(draft_path)


if __name__ == "__main__":
    main()
