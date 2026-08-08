#!/usr/bin/env python3
"""
new_post.py — turn a plain text/markdown draft into a Dev Journal post page.

USAGE
    python3 scripts/new_post.py drafts/my-post.md

WHAT IT DOES
    1. Reads a draft file with a small frontmatter block + your writing.
    2. Crops every photo you reference to a clean rectangle (landscape,
       default 3:2) so nothing looks stretched or squished on the site.
    3. Generates posts/<slug>/index.html, with its own posts/<slug>/images/
       folder — each post is fully self-contained in one folder.
    4. Adds the new entry to the top of the Dev Journal on index.html
       (re-running on an edited draft updates it in place, no duplicates).

RUNNING ON EVERYTHING AT ONCE
    python3 scripts/new_post.py --all
    (or double-click scripts/new_post.bat with no file dragged onto it)
    Scans every drafts/**/*.md and rebuilds/updates all of them.

SETUP (once)
    pip install pillow

DRAFT FILE FORMAT  (see drafts/example-post.md for a working sample)

    ---
    title: Survivors vs. Carriers
    date: Aug 8, 2026
    read: 2 min read
    desc: One-line summary shown on the homepage card.
    aspect: 3:2        (optional, default 3:2. try 16:9 or 4:3)
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
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Missing dependency. Run:  pip install pillow")

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "posts"
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
        # too wide -> crop sides
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, h))
    else:
        # too tall -> crop top/bottom
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


IMG_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<path>[^\s)"]+)(?:\s+"(?P<cap>[^"]*)")?\)')
HEADING_RE = re.compile(r"^##\s+(.*)$")


def inline_format(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s


def build_body_html(body: str, draft_dir: Path, post_images_dir: Path, aspect: float):
    html_parts = []
    first_image_filename = None
    img_counter = 0

    blocks = re.split(r"\n\s*\n", body.strip())
    for block in blocks:
        block = block.strip()
        if not block:
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
            out_path = post_images_dir / out_name
            final_path = crop_to_rect(src_path, out_path, aspect)
            web_path = f"images/{final_path.name}"
            if first_image_filename is None:
                first_image_filename = final_path.name

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

    return "\n\n".join(html_parts), first_image_filename


POST_TEMPLATE = """<!DOCTYPE html>
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
  .post-header h1{{font-size:clamp(1.4rem,4vw,2.1rem); color:var(--brightred); text-shadow:3px 3px 0 #000; margin-bottom:18px; line-height:1.5;}}
  .post-header .meta{{color:var(--grey); font-size:0.9rem;}}

  .post-body{{max-width:720px; margin:0 auto; padding:60px 6% 40px;}}
  .post-body p{{color:var(--white); margin-bottom:24px; font-size:1.15rem;}}
  .post-body h2{{color:var(--red); font-size:1.2rem; margin:36px 0 16px;}}
  .post-body figure{{margin:0 0 32px;}}
  .post-body figure img{{display:block; width:100%; height:auto; border:2px solid var(--darkred);}}
  .post-body figcaption{{color:var(--grey); font-size:0.9rem; margin-top:10px; line-height:1.5;}}

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
  <span class="tag">// DEV JOURNAL</span>
  <h1>{title}</h1>
  <div class="meta">{date} · {read}</div>
</div>

<div class="post-body">

{body_html}

</div>

<a class="back-link" href="../../index.html#journal">← Back to Dev Journal</a>

<footer>
  <div class="socials">
    <a href="#">Instagram</a> · <a href="#">BoardGameGeek</a> · <a href="#">Email</a>
  </div>
  <p style="margin-top:12px;">© 2026 CARRIER — a survival board game in development.</p>
</footer>

</body>
</html>
"""

CARD_TEMPLATE = """    <a class="post-card" href="posts/{slug}/{slug}.html">
      <div class="post-thumb" style="background-image:url('{thumb}'); background-size:cover; background-position:center;"></div>
      <div class="post-cap">
        <span class="post-meta">{date} · {read}</span>
        <b class="post-cap-title">{title}</b>
        <span class="post-cap-desc">{desc}</span>
        <span class="post-link">Read entry →</span>
      </div>
    </a>
"""


def insert_into_index(card_html: str, slug: str):
    text = INDEX_HTML.read_text(encoding="utf-8")

    # Remove any existing card for this slug first, so re-running the script
    # on an edited draft updates the homepage instead of duplicating it.
    existing_card_re = re.compile(
        r'\s*<a class="post-card" href="posts/' + re.escape(slug) + r'/' + re.escape(slug) + r'\.html">.*?</a>\n',
        re.DOTALL,
    )
    text = existing_card_re.sub("\n", text, count=1)

    marker = '<div class="posts">'
    idx = text.find(marker)
    if idx == -1:
        sys.exit('Could not find <div class="posts"> in index.html — add the card manually.')
    insert_at = idx + len(marker) + 1
    new_text = text[:insert_at] + card_html + text[insert_at:]
    INDEX_HTML.write_text(new_text, encoding="utf-8")


def process_draft(draft_path: Path) -> str:
    """Build/update a single post from a draft .md file. Returns the slug, or None if skipped."""
    raw = draft_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)

    if str(fm.get("skip", "")).strip().lower() in ("true", "yes", "1"):
        print(f"Skipped (marked skip: true):  {draft_path.relative_to(REPO_ROOT)}")
        return None

    title = fm.get("title", "Untitled")
    date = fm.get("date", "")
    read = fm.get("read", "3 min read")
    desc = fm.get("desc", "")
    aspect = parse_aspect(fm.get("aspect", "3:2"))
    slug = fm.get("slug") or slugify(title)

    post_dir = POSTS_DIR / slug
    post_images_dir = post_dir / "images"

    body_html, first_image = build_body_html(body, draft_path.parent, post_images_dir, aspect)

    post_html = POST_TEMPLATE.format(title=title, date=date, read=read, body_html=body_html)
    post_dir.mkdir(parents=True, exist_ok=True)
    post_path = post_dir / f"{slug}.html"
    post_path.write_text(post_html, encoding="utf-8")

    thumb = fm.get("thumb")
    if thumb:
        thumb_web = thumb  # explicit path, relative to site root
    elif first_image:
        thumb_web = f"posts/{slug}/images/{first_image}"
    else:
        thumb_web = "images/kodecco-icon.png"

    card_html = CARD_TEMPLATE.format(slug=slug, thumb=thumb_web, date=date, read=read, title=title, desc=desc)
    insert_into_index(card_html, slug)

    print(f"Updated:  posts/{slug}/{slug}.html  (from {draft_path.relative_to(REPO_ROOT)})")
    return slug


def find_all_drafts():
    drafts_dir = REPO_ROOT / "drafts"
    if not drafts_dir.exists():
        return []
    return sorted(drafts_dir.rglob("*.md"))


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("--all", "all"):
        drafts = find_all_drafts()
        if not drafts:
            sys.exit("No .md drafts found under drafts/")
        print(f"Scanning {len(drafts)} draft(s)...\n")
        done = 0
        for draft_path in drafts:
            try:
                if process_draft(draft_path):
                    done += 1
            except SystemExit as e:
                print(f"  ! Skipped {draft_path.relative_to(REPO_ROOT)}: {e}")
        print(f"\n{done} post(s) built/updated. Dev Journal on index.html is up to date.")
        return

    draft_path = Path(args[0]).resolve()
    if not draft_path.exists():
        sys.exit(f"Draft not found: {draft_path}")
    process_draft(draft_path)
    print("Added to Dev Journal on index.html")


if __name__ == "__main__":
    main()
