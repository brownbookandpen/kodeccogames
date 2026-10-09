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

CSS = """
  :root{ --accent-game:#4fd1b0; }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#000;color:#eee8dc;font-family:'Inter',-apple-system,'Segoe UI',Roboto,Arial,sans-serif;line-height:1.75;font-size:1.05rem;}
  a{color:inherit;text-decoration:none;}
  .hazard{height:14px;background:repeating-linear-gradient(45deg,#f2c14e 0 20px,#000 20px 40px);}
  header{display:flex;align-items:center;justify-content:space-between;padding:14px 6%;background:#0c0c0c;border-bottom:2px solid #0f4a3c;}
  header img{height:64px;display:block;}
  header nav a{color:#9a9a9a;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;margin-left:22px;}
  header nav a:hover{color:var(--accent-game);}
  main{max-width:720px;margin:0 auto;padding:56px 6% 90px;}
  .eyebrow{color:var(--accent-game);font-size:.75rem;letter-spacing:.3em;text-transform:uppercase;margin-bottom:12px;}
  h1{font-size:clamp(1.9rem,5vw,2.8rem);line-height:1.12;margin-bottom:12px;}
  .sub{color:#9fb0ab;margin-bottom:34px;}
  p{margin-bottom:18px;color:#d6d0c2;}
  .back{display:inline-block;margin-top:30px;color:var(--accent-game);font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;}
  .shot{margin:30px 0;border:1px dashed #1f2a27;padding:30px;text-align:center;color:#51615d;font-size:.72rem;letter-spacing:.22em;}
"""

def page(slug, title, sub, paras):
    body = "\n".join("  <p>%s</p>" % html.escape(p, quote=False) for p in paras)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Carriers: Built in Unity</title>
<meta name="description" content="{html.escape(sub)}">
<link rel="icon" href="../../../favicon.ico" sizes="any">
<link rel="stylesheet" href="../../../styles.css">
<style>{CSS}</style>
</head>
<body>
<div class="hazard"></div>
<header>
  <a href="../../../"><img src="../../../images/kodecco-icon.png" alt="Kodecco Games"></a>
  <nav><a href="../../">Dev Log</a><a href="../../../tabletop/">Card Game</a></nav>
</header>
<main>
  <div class="eyebrow">// Dev log · Deep dive</div>
  <h1>{html.escape(title)}</h1>
  <p class="sub">{html.escape(sub)}</p>
{body}
  <div class="shot">SCREENSHOT PENDING</div>
  <a class="back" href="../../">← Back to the dev log</a>
</main>
</body>
</html>
"""

for slug, title, sub, paras in POSTS:
    d = os.path.join(ROOT, "game", "posts", slug); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page(slug, title, sub, paras))

# refresh the deep-dive list on the game page
cards = "\n".join(
  f'    <a class="sys dive" href="posts/{s}/"><b>{html.escape(t)}</b>{html.escape(sub)}</a>' for s, t, sub, _ in POSTS)
gp = os.path.join(ROOT, "game", "index.html"); g = open(gp).read()
block = f"<!--DIVES-->\n  <h2>Deep dives</h2>\n  <div class=\"systems\">\n{cards}\n  </div>\n  <!--/DIVES-->"
if "<!--DIVES-->" in g:
    g = re.sub(r"<!--DIVES-->.*?<!--/DIVES-->", lambda m: block, g, flags=re.S)
else:
    g = g.replace("<h2>Log</h2>", block + "\n\n  <h2>Log</h2>", 1)
open(gp, "w").write(g)

# sitemap
sp = os.path.join(ROOT, "sitemap.xml"); sm = open(sp).read()
for s, *_ in POSTS:
    loc = f"https://kodeccogames.com/game/posts/{s}/"
    if loc not in sm:
        sm = sm.replace("</urlset>", f"  <url><loc>{loc}</loc><changefreq>yearly</changefreq><priority>0.6</priority></url>\n</urlset>")
open(sp, "w").write(sm)
print("built", len(POSTS), "posts")
