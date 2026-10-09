#!/usr/bin/env python3
"""Generates the Unity dev log deep-dive pages under game/posts/<slug>/index.html.
Edit POSTS below, then run: python3 tools/build_game_posts.py
Also refreshes the 'Deep dives' list on game/index.html (between the DIVES markers)."""
import os, html, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

POSTS = [
 ("flooded-city", "The flooded city",
  "A walled capital that is permanently knee-deep in water, and how we made wading feel right.",
  [
   "The capital of the island is flooded, and it stays that way. The water sits about knee to waist height on the player. That is deep enough to slow the mood down and shallow enough that walking and fighting still work. There is no swimming.",
   "The flood covers roughly 1,344 by 832 metres, enough for the whole connected city core. The water is deliberately calm and murky, a flat brown-green surface with a faint reflection of the buildings. It looks heavy and still, which is the point.",
   "Moving through it is where it comes alive. Every step makes a splash and sends ripples out, and running leaves a wider wake that fades after a second or two. Standing still still gives off the occasional tiny ring, as if you were breathing. Footsteps in water are loud, and the stealth system treats them that way.",
   "Reeds, lily pads and floating debris dress the surface. At night the water goes almost fully opaque and the reflections dim, so submerged grass does not turn into black spikes.",
   "To keep it fast, the water is split into 273 small tiles that are only drawn when you can see them, and grass that is fully underwater is switched off entirely.",
  ]),
 ("grass-and-the-hunting-view", "Grass, and the hunting view",
  "Why the island's grass fades in smoothly, and why you can zoom out without being safe.",
  [
   "Grass is one of the most expensive things to draw on a big island, so it is handled in 16 metre cells. The world remembers where every clump goes, and only what the camera can actually see gets drawn.",
   "Close grass uses a detailed model, and further grass swaps to cheaper ones. The swap is a 14 metre crossfade, so you do not see it happen. New grass fades in over about two seconds with a small random delay per clump, which avoids square patches popping in. The outermost band blends into the colour of the ground and the distant meadows.",
   "The camera can zoom out far enough to scan a field for animals. Zooming does not change what the animals can sense. They still react to you through sight lines, sound, scent and how well you are hidden in the grass, so a wide view is not protection if you are already close.",
   "Moving the camera alone makes no noise and does not move the player.",
  ]),
 ("building-the-world", "Building the world",
  "The placement tool we use to dress the island, and the rules built into it.",
  [
   "Hand-placing every prop in the editor does not scale to an island this size, so we built a placement tool. Press B, pick something from the panel, click the ground and it is placed. Layouts save themselves a second after every change.",
   "The palette holds over a thousand items: swamp plants, ivy and vines, vehicles, debris, barriers, props, trees, plants and rocks. There is a paint mode for dragging out a lot at once, a delete mode, colour variants for most items, and undo. Ivy and vines turn to face out of walls, and swamp scum, lily pads and reeds sit on the water surface.",
   "It has a few safety rules. Nothing can be placed below sea level. A God mode and an Invisible mode let us wander and place without being attacked. Combat is switched off while building so that a click places an object instead of swinging a weapon.",
   "Saves keep dated backups, and a broken layout refuses to load instead of silently turning into an empty one.",
  ]),
 ("melee-and-the-weapon-wheel", "Melee and the weapon wheel",
  "Making swings feel solid, and switching weapons without opening a menu.",
  [
   "Melee animation was throwing weapons around, because every animated swing also twisted the weapon in the character's hand. Now the game records how the weapon sits in the hand at the start of a swing and keeps it locked there, so a machete or an axe stays pointed along the swing.",
   "Fists chain too. Click again during a punch to follow with the other hand, and a single click still gives one punch. Blade and fist combos finish after two hits.",
   "Weapons are chosen from a wheel. Hold Q, point at a weapon with the mouse and let go. It runs clockwise from the bow at the top, through blades, sidearm, rifle, shotgun and grenades, to knives and fists. On a controller you use the Menu button and the right stick. You carry one gun and one melee weapon at a time, and swapping drops the old one with its ammo intact.",
   "Rifles and shotguns can be fired lying down, and aiming stops you crawling. Sprinting puts any gun away straight away and cancels a reload.",
  ]),
 ("the-backpack", "The backpack",
  "Picking things up, dropping them again, and what is still missing.",
  [
   "Pick up a backpack with E and press I or Tab to open it. The window uses a rusted, post-apocalypse look. Select a slot to inspect it, then drop one item or the whole stack. Anything you drop can be picked up again.",
   "Your character crouches while you browse, and the world keeps running, so opening your bag in the open is a risk.",
   "The same system powers the weapon wheel's ammo and grenade counts, which also show on the HUD.",
   "What it does not do yet is consumables, so food and medicine have no effect when used, and your inventory is not saved between sessions. Both are on the list.",
  ]),
 ("cutaway-view", "The cutaway view",
  "How the camera sees you inside buildings, trees and ivy.",
  [
   "The game uses a top-down camera, which means buildings and trees constantly block the view of your character. Our answer is a cutaway. A soft, dithered circle opens through any building, tree or ivy between the camera and you, so you can always see where you are.",
   "Walk into a building that has been prepared for it and the upper floors and the camera-facing walls fade away, like looking into a dollhouse. The base of the walls stays, and so do the colliders, so the building still feels solid.",
   "The ivy on the tall buildings was the hard part. It is drawn in huge batches rather than as separate objects, so ordinary tricks for hiding things did not affect it. We rebuilt the shaders so ivy, concrete and the building materials all follow the same cutaway.",
   "The camera can zoom from 9 to 42 metres from the player.",
  ]),
]

# Hero screenshot for each post: (file in images/game/ without extension, alt text)
SHOTS = {
  "flooded-city": ("03-hero-flooded-city", "The flooded capital, water up to the knees"),
  "grass-and-the-hunting-view": ("15-world-grassland", "Grassland stretching to a distant forest"),
  "building-the-world": ("13-build-mode", "Build mode placing props on the ground"),
  "melee-and-the-weapon-wheel": ("11-weapon-wheel", "The weapon wheel open mid-game"),
  "the-backpack": ("10-inventory", "The backpack inventory screen"),
  "cutaway-view": ("20-cutaway-view", "The camera cutting away a building around the player"),
}

def esc(t): return html.escape(t, quote=True)

def shot(file, alt, prefix, cls="shot", lazy=True):
    l = ' loading="lazy"' if lazy else ''
    return (f'<figure class="{cls}" data-file="{file}"><img src="{prefix}images/game/{file}.webp" '
            f'alt="{esc(alt)}"{l} onerror="shotMissing(this)"></figure>')

def page(i):
    slug, title, sub, paras = POSTS[i]
    file, alt = SHOTS[slug]
    words = sum(len(p.split()) for p in paras)
    mins = max(1, round(words / 200))
    body = "\n".join("      <p>%s</p>" % html.escape(p, quote=False) for p in paras)
    prev_ = POSTS[i-1] if i > 0 else None
    next_ = POSTS[i+1] if i < len(POSTS)-1 else None
    def nav(p, label, cls):
        if not p: return '<span></span>'
        return f'<a class="pn {cls}" href="../{p[0]}/"><span class="term">{label}</span><b>{esc(p[1])}</b></a>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#050505">
<title>{esc(title)} — Carriers: Built in Unity</title>
<meta name="description" content="{esc(sub)}">
<link rel="icon" href="../../../favicon.ico" sizes="any">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)} — Carriers dev log">
<meta property="og:description" content="{esc(sub)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=VT323&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../styles.css">
<link rel="stylesheet" href="../../../site.css">
<link rel="stylesheet" href="../../../ios.css">
<script>function shotMissing(i){{var f=i.closest('.shot');if(f)f.classList.add('missing');i.remove();}}</script>
<style>
  .post-hero{{position:relative;}}
  .post-hero .shot{{aspect-ratio:21/9;max-height:62vh;width:100%;}}
  .post-hero .shot.missing::after{{align-items:center;}}
  .post-head{{margin-top:-90px;position:relative;z-index:2;}}
  .post-head .card{{background:var(--ink);padding:36px clamp(20px,4vw,48px) 8px;max-width:820px;}}
  .post-head h1{{font-size:clamp(2.8rem,7vw,5.2rem);}}
  .post-head .sub{{font-size:clamp(1.1rem,1.7vw,1.3rem);color:var(--paper-2);margin-top:14px;max-width:56ch;}}
  .post-head .meta{{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px;}}
  article.prose{{max-width:720px;margin:0 auto;padding:30px var(--gutter) 40px;font-size:1.12rem;line-height:1.85;}}
  article.prose p{{margin-bottom:24px;color:#ddd7ca;}}
  article.prose p:first-child::first-letter{{font-family:var(--f-display);float:left;font-size:4.6rem;line-height:.8;padding:8px 12px 0 0;color:var(--fog);}}
  .pn-row{{max-width:var(--max);margin:30px auto 0;padding:0 var(--gutter);display:grid;grid-template-columns:1fr 1fr;gap:2px;}}
  .pn{{display:block;background:var(--ink-2);border:1px solid var(--line);padding:22px 24px;transition:border-color .2s;}}
  .pn:hover{{border-color:color-mix(in srgb,var(--fog) 50%,transparent);}}
  .pn .term{{display:block;color:var(--fog);font-size:1.05rem;}}
  .pn b{{font-weight:600;font-size:1.05rem;}}
  .pn.next{{text-align:right;}}
  .back-row{{max-width:var(--max);margin:0 auto;padding:40px var(--gutter) 90px;}}
  @media(max-width:640px){{.pn-row{{grid-template-columns:1fr;}} .pn.next{{text-align:left;}} .post-head{{margin-top:-40px;}}}}
</style>
</head>
<body class="theme-unity">
<div class="hazard"></div>
<header class="site-header">
  <a class="mark" href="../../../" aria-label="Kodecco Games home"><img src="../../../images/kodecco-icon.png" alt="Kodecco Games"></a>
  <nav class="site-nav">
    <a href="../../../">Studio</a>
    <a href="../../../tabletop/">Card Game</a>
    <a href="../../">Unity Game</a>
    <a href="../../#log" aria-current="page">Dev Log</a>
    <a class="nav-cta" href="../../#signal">Get Alerts</a>
  </nav>
</header>
<main>
  <div class="post-hero">{shot(file, alt, "../../../", "shot hero-shot", lazy=False)}</div>
  <div class="wrap post-head">
    <div class="card">
      <div class="eyebrow">Dev log · Deep dive</div>
      <h1 class="display">{esc(title)}</h1>
      <p class="sub">{esc(sub)}</p>
      <div class="meta"><span class="chip uni">Carriers · Unity</span><span class="chip">{mins} min read</span><span class="chip">Work in progress</span></div>
    </div>
  </div>
  <article class="prose">
{body}
  </article>
  <nav class="pn-row" aria-label="More deep dives">
    {nav(prev_, "← Previous", "prev")}
    {nav(next_, "Next →", "next")}
  </nav>
  <div class="back-row"><a class="btn" href="../../#log">← Back to the dev log</a></div>
</main>
<footer class="site-footer">
  <div class="inner">
    <div><img src="../../../images/kodecco-icon.png" alt="Kodecco Games"><div>© 2026 Kodecco Games. Carriers is in development; everything shown is work in progress.</div></div>
    <nav><a href="../../../">Studio</a><a href="../../">Unity Game</a><a href="../../../tabletop/">Card Game</a><a href="https://www.instagram.com/kodecco.games/" target="_blank" rel="noopener">Instagram</a></nav>
  </div>
</footer>
<script src="../../../site.js"></script>
<script src="../../../local-preview.js"></script>
</body>
</html>
"""

for i, (slug, *_ ) in enumerate(POSTS):
    d = os.path.join(ROOT, "game", "posts", slug); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page(i))

# refresh the deep-dive cards on the game page (between the DIVES markers)
cards = "\n".join(
  f'          <a class="dive" href="posts/{s}/">{shot(SHOTS[s][0], SHOTS[s][1], "../")}'
  f'<div class="b"><h4>{esc(t)}</h4><p>{esc(sub)}</p></div></a>' for s, t, sub, _ in POSTS)
gp = os.path.join(ROOT, "game", "index.html"); g = open(gp).read()
block = f'<!--DIVES-->\n        <div class="dives">\n{cards}\n        </div>\n        <!--/DIVES-->'
g = re.sub(r"<!--DIVES-->.*?<!--/DIVES-->", lambda m: block, g, flags=re.S)
open(gp, "w").write(g)

# sitemap
sp = os.path.join(ROOT, "sitemap.xml"); sm = open(sp).read()
for s, *_ in POSTS:
    loc = f"https://kodeccogames.com/game/posts/{s}/"
    if loc not in sm:
        sm = sm.replace("</urlset>", f"  <url><loc>{loc}</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>\n</urlset>")
open(sp, "w").write(sm)
print("built", len(POSTS), "posts")
