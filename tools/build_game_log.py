#!/usr/bin/env python3
"""Renders the public Carriers development report (from the brownbookandpen/Carriers repo,
public/devlog-report.md) into game/log/index.html.
Usage: python3 tools/build_game_log.py /path/to/Carriers/public/devlog-report.md
Each day shows its hours and summary at once; the detailed lists sit under 'Full detail'."""
import sys, os, re, html, datetime
import markdown
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
md = open(src, encoding='utf-8').read()

# Wrap everything after each day's summary paragraph in a collapsible block.
def wrap_days(text):
    parts = re.split(r'\n(?=### Day \d+ · )', text)
    out = [parts[0]]
    for p in parts[1:]:
        head, rest = p.split('\n', 1)
        rest = rest.lstrip('\n')
        lines = rest.split('\n')
        hours = lines[0] if lines[0].startswith('**Total hours') else ''
        body = '\n'.join(lines[1:]).strip('\n') if hours else rest
        summary, _, detail = body.partition('\n\n')
        photos = ''
        if '**Photos**' in detail:
            detail, _, photos = detail.partition('**Photos**')
            photos = '**Photos**' + photos
        block = f'{head}\n<p class="hours">{markdown.markdown(hours)[3:-4] if hours else ""}</p>\n\n{summary}\n'
        if photos.strip():
            block += f'\n{photos.strip()}\n'
        if detail.strip():
            block += f'\n<details class="day-detail" markdown="1">\n<summary>Full detail</summary>\n\n{detail.strip()}\n\n</details>\n'
        out.append(block)
    return '\n'.join(out)

md = wrap_days(md)

# Photos: copy each referenced media file next to the page and render as a captioned grid.
import shutil
SRC_ROOT = os.path.dirname(os.path.dirname(src))  # the Carriers repo root
def photo_grid(m):
    figs = []
    for cap, rel in re.findall(r'!\[([^\]]*)\]\((media/[^)]+)\)', m.group(0)):
        dst = os.path.join(ROOT, 'game', 'log', rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        srcf = os.path.join(SRC_ROOT, rel)
        if os.path.exists(srcf): shutil.copyfile(srcf, dst)
        figs.append(f'<figure><a href="{rel}" target="_blank" rel="noopener"><img src="{rel}" alt="{html.escape(cap)}" loading="lazy"></a><figcaption>{html.escape(cap)}</figcaption></figure>')
    return '\n<div class="photos">\n' + '\n'.join(figs) + '\n</div>\n'
md = re.sub(r'\*\*Photos\*\*\n(?:!\[[^\]]*\]\(media/[^)]+\)\n?)+', photo_grid, md)
body = markdown.markdown(md, extensions=['tables', 'md_in_html', 'sane_lists'])
title_m = re.search(r'Day 1 to Day (\d+)', md); last = title_m.group(1) if title_m else '?'
hours_m = re.search(r'about (\d+) hours so far', md); total_h = hours_m.group(1) if hours_m else '?'
built = datetime.date.today().strftime('%-d %B %Y')

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<title>Development Report — Carriers: Built in Unity</title>
<meta name="description" content="Day-by-day development report for Carriers, the Unity survival game from Kodecco Games. Day 1 to Day {last}, about {total_h} hours of work, updated daily.">
<link rel="icon" href="../../favicon.ico" sizes="any">
<meta property="og:type" content="article">
<meta property="og:title" content="Carriers development report, Day 1 to Day {last}">
<meta property="og:description" content="What was built, what broke and what was decided, every day since 18 September 2026.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=VT323&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../styles.css">
<link rel="stylesheet" href="../../site.css">
<link rel="stylesheet" href="../../ios.css">
<style>
  .report{{max-width:820px;margin:0 auto;padding:40px var(--gutter) 90px;}}
  .report-head{{padding:56px 0 30px;border-bottom:1px solid var(--line);margin-bottom:10px;}}
  .report-head h1{{font-size:clamp(2.6rem,7vw,5rem);}}
  .report-head .facts{{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;}}
  .report > h1{{display:none;}}
  .report > p:first-of-type{{font-size:.95rem;color:var(--paper-2);border-left:3px solid var(--fog);padding-left:14px;}}
  .report h2{{font-family:var(--f-term);font-weight:400;font-size:1.5rem;letter-spacing:.14em;text-transform:uppercase;color:var(--fog);margin:56px 0 10px;padding-top:26px;border-top:1px solid var(--line);}}
  .report h3{{font-family:var(--f-display);font-weight:400;font-size:clamp(1.7rem,3.4vw,2.4rem);line-height:1;margin:38px 0 4px;letter-spacing:.01em;}}
  .report .hours{{font-family:var(--f-term);font-size:1.1rem;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:0 0 12px;}}
  .report .hours strong{{color:var(--fog);font-weight:400;}}
  .report p{{color:#ddd7ca;margin:0 0 14px;line-height:1.75;}}
  .report ul{{margin:0 0 14px 20px;color:var(--paper-2);}}
  .report li{{margin-bottom:5px;line-height:1.6;}}
  .report strong{{color:var(--paper);font-weight:600;}}
  .report code{{font-family:var(--f-term);font-size:1.05em;color:var(--paper);}}
  .report hr{{border:0;border-top:1px solid var(--line);margin:40px 0;}}
  .report table{{border-collapse:collapse;width:100%;font-size:.92rem;margin:14px 0 24px;}}
  .report th,.report td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;}}
  .report th{{font-family:var(--f-term);font-weight:400;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);font-size:1.05rem;}}
  details.day-detail{{border:1px solid var(--line);background:var(--ink-2);padding:0 18px;margin:6px 0 10px;}}
  details.day-detail summary{{cursor:pointer;list-style:none;font-family:var(--f-term);font-size:1.15rem;letter-spacing:.1em;text-transform:uppercase;color:var(--fog);padding:12px 0;}}
  details.day-detail summary::-webkit-details-marker{{display:none;}}
  details.day-detail summary::before{{content:"+ ";}}
  details.day-detail[open] summary::before{{content:"− ";}}
  details.day-detail[open] summary{{border-bottom:1px solid var(--line);margin-bottom:14px;}}
  details.day-detail > p,details.day-detail > ul{{font-size:.95rem;}}
  .photos{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:18px 0 10px;}}
  .photos figure{{margin:0;background:#070a0a;border:1px solid var(--line);}}
  .photos img{{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;}}
  .photos figcaption{{font-family:var(--f-term);font-size:.98rem;letter-spacing:.04em;color:var(--paper-2);padding:8px 10px 10px;line-height:1.35;}}
  .toolbar{{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0 0;}}
  .toolbar button{{font-family:var(--f-term);font-size:1.1rem;letter-spacing:.08em;text-transform:uppercase;background:none;border:1px solid var(--line);color:var(--paper-2);padding:6px 14px;cursor:pointer;}}
  .toolbar button:hover{{border-color:var(--fog);color:var(--fog);}}
  .updated{{font-family:var(--f-term);font-size:1.05rem;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin-top:40px;}}
</style>
</head>
<body class="theme-unity">
<div class="hazard"></div>
<header class="site-header">
  <a class="mark" href="../../" aria-label="Kodecco Games home"><img src="../../images/kodecco-icon.png" alt="Kodecco Games"></a>
  <nav class="site-nav">
    <a href="../../">Studio</a>
    <a href="../../tabletop/">Card Game</a>
    <a href="../">Unity Game</a>
    <a href="./" aria-current="page">Dev Report</a>
    <a class="nav-cta" href="../#signal">Get Alerts</a>
  </nav>
</header>
<main class="report">
  <div class="report-head">
    <div class="eyebrow">Carriers · Built in Unity</div>
    <h1 class="display">Development report</h1>
    <div class="facts"><span class="chip live">Updated daily</span><span class="chip">Day 1 to Day {last}</span><span class="chip">About {total_h} hours</span><span class="chip">Since 18 Sep 2026</span></div>
    <div class="toolbar"><button type="button" onclick="document.querySelectorAll('details.day-detail').forEach(function(d){{d.open=true}})">Expand all</button><button type="button" onclick="document.querySelectorAll('details.day-detail').forEach(function(d){{d.open=false}})">Collapse all</button><button type="button" onclick="var a=document.querySelectorAll('.report h3');a[0].scrollIntoView({{behavior:'smooth'}})">Latest day ↓</button><button type="button" onclick="var a=document.querySelectorAll('.report h3');a[a.length-1].scrollIntoView({{behavior:'smooth'}})">Day 1 ↓</button></div>
  </div>
{body}
  <p class="updated">Page built {built}. Source: the studio's daily development log.</p>
</main>
<footer class="site-footer">
  <div class="inner">
    <div><img src="../../images/kodecco-icon.png" alt="Kodecco Games"><div>© 2026 Kodecco Games. Carriers is in development; everything shown is work in progress.</div></div>
    <nav><a href="../../">Studio</a><a href="../">Unity Game</a><a href="../../tabletop/">Card Game</a><a href="https://www.instagram.com/kodecco.games/" target="_blank" rel="noopener">Instagram</a></nav>
  </div>
</footer>
<script src="../../site.js"></script>
<script src="../../local-preview.js"></script>
</body>
</html>
"""
os.makedirs(os.path.join(ROOT, 'game', 'log'), exist_ok=True)
open(os.path.join(ROOT, 'game', 'log', 'index.html'), 'w', encoding='utf-8').write(page)
print('built game/log/index.html: Day 1 to', last, ',', total_h, 'h')
