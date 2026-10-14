#!/usr/bin/env python3
"""Scans the site for screenshot placeholders (data-file="NN-slug") and rewrites SHOTLIST.md,
so the shot list always matches what the pages actually use.
Run: python3 tools/list_shots.py"""
import os, re, glob, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# What each capture should show. Keep in step with the alt text on the pages.
SPEC = {
 "01-hero-horde": ("Clean", "Zombies in the middle distance, the player as a silhouette in front. Zombies are OFF in Build 1.0: turn them on in the F9 panel (or the main menu World Switches), spawn a group, F9 to set golden hour or fog. Use F9 fly for the angle. Leave the upper-right third fairly empty, the title sits bottom-left."),
 "02-hero-rider": ("Clean", "Player on horseback on a painted track with the island behind, side or three-quarter view, long shadows (F9 time near sunset). The white wolf-dog in frame is a bonus."),
 "03-hero-flooded-city": ("Clean", "The flooded capital from inside the wall: knee-deep water, reeds, lily pads, apartment blocks behind. Overcast or fog. F9 fly for a slightly raised angle."),
 "05-combat-melee": ("HUD", "Melee combo mid-swing at a zombie (zombies on via F9). Machete or axe. Zombie clearly readable, blood from the RVFX system is fine."),
 "09-loot-drop": ("HUD", "Loot on the ground beside a fresh corpse with the E pickup prompt showing, or a searched container with its contents out. Rarity colours visible."),
 "10-inventory": ("UI", "The backpack window open and filled with items. No empty grid. An old render exists at Screenshots/Inventory/SyntyBackpack.png; a fresh in-game capture is better."),
 "11-weapon-wheel": ("HUD", "Hold Q with several weapons carried so few slots are greyed out. On horseback if possible (the wheel works there)."),
 "13-build-mode": ("Build UI", "Build Mode (B) open with the palette visible and a prop half-placed, placement ring showing, in a town street."),
 "14-character-creator": ("Creator UI", "The character creator with a styled survivor on the pedestal, layered clothing and colours chosen. Main menu > Create Characters."),
 "15-world-grassland": ("Clean", "Wildflower and wheat fields with the stylised grass, a track, forest and horizon behind. No player. Clear weather, mid-morning."),
 "16-world-forest": ("Clean", "The northern spruce band with snow (F10 cycles snow; the highlands are always snowy). Light shafts or blizzard fog. No player."),
 "17-world-night": ("Clean", "A town street at night (F9 time) with the fog ring and a lit window or two. No player, or a tiny one."),
 "18-wildlife": ("Clean", "Animals grazing or herding in a field with the Quibli look. Very wide: this slot is a letterbox strip, keep the subject in the middle band."),
 "20-cutaway-view": ("Gameplay camera", "The player inside a Builder house or an R apartment block with the dollhouse view open (upper floors and camera-facing walls hidden) and the player outline visible."),
}
OPTIONAL = {
 "04-hero-survivor-closeup": "Player character, upper body, cloak and backpack, shallow depth of field.",
 "06-combat-firearm": "Aiming a rifle from prone with the reticle visible.",
 "07-combat-bow": "Bow drawn on a target from the hunting zoom.",
 "08-zombie-lunge": "An aged zombie mid-lunge toward the camera.",
 "12-horseback-hud": "Riding with gait, stamina and minimap visible.",
 "19-main-menu": "The Dark UI main menu with the hero slideshow (hide Developer Mode / World Switches first).",
 "21-weather-storm": "A storm rolling in over a town: lightning, wet roofs and roads (F9 weather).",
 "22-apartments": "A street of the R01 to R20 apartment blocks, boarded windows, wood gables, from the gameplay camera.",
 "23-climbing": "The player hanging from a window ledge or mid-ladder on an apartment block.",
 "24-northmarch": "Northmarch (walled base) from above: barracks, homes, lumber yard. NPCs are OFF; empty is fine.",
 "25-quest-journal": "The quest journal (J) open with Running Dry and High Ground listed.",
 "26-stealth-focus": "Stealth Focus mode active in tall grass, the greyscale look and the player outline.",
}

uses = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
    rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
    if rel.startswith(("_unpublished", "tabletop", "rules", "posts/")): continue
    page = "/" + rel.replace("index.html", "")
    text = open(f).read()
    for m in re.finditer(r'<figure class="([^"]*)" data-file="([^"]+)"', text):
        cls, name = m.group(1), m.group(2)
        before = text[max(0, m.start()-120):m.start()]
        if "door-art" in before: where = "homepage door (tall, crops to the centre)"
        elif "hero-shot" in cls and "/posts/" in page: where = "post header banner (21:9)"
        elif "hero-shot" in cls: where = "full-screen hero"
        elif 'class="dive"' in before: where = "deep-dive card"
        elif "thumb" in cls: where = "latest-posts card"
        elif "wide" in cls: where = "letterbox strip"
        elif "<figcaption>" in text[m.start():m.start()+400]: where = "photo mosaic"
        else: where = "feature section"
        uses[name].append(f"`{page}` {where}")

have = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(ROOT, "images", "game", "*.webp"))}
# Slots filled with an older or smaller picture as a stand-in. The real capture is still wanted.
STANDIN = {
 "01-hero-horde": "main-menu painting (the horde at the wall); a real in-game capture is still wanted",
 "17-world-night": "main-menu painting (farm at night); a real night capture is still wanted",
}
out = ["# Screenshot manifest",
"",
"Generated by `tools/list_shots.py` from the placeholders on the site. Every row is one image the site is waiting for.",
"",
"**How to deliver**",
"- Capture at **3840x2160 (16:9) PNG**, post-processing on, no editor gizmos, no debug text.",
"- Name the file **exactly** as in the File column (e.g. `05-combat-melee.png`).",
"- Put them in one folder and hand them over. Claude converts them to `images/game/<file>.webp` and they appear on the site automatically; nothing else needs linking.",
"- Take 2 or 3 variations of each; add `-a`, `-b` to the name (e.g. `05-combat-melee-b.png`) and we pick the best.",
"- Clean = HUD hidden. HUD = HUD visible. ⚠ stand-in = the site shows an older picture there for now; the real capture is still on the list.",
"",
"## On the site now (%d)" % len(uses), "",
"| Done | File | HUD | What to capture | Where it appears |", "|---|---|---|---|---|"]
for name in sorted(uses):
    hud, what = SPEC.get(name, ("?", "(no description yet)"))
    done = ("⚠ stand-in: " + STANDIN[name]) if name in STANDIN else ("✅" if name in have else "⬜")
    out.append(f"| {done} | `{name}` | {hud} | {what} | {'<br>'.join(dict.fromkeys(uses[name]))} |")
out += ["", "## Optional extras (not placed on the site yet)", "", "| File | What to capture |", "|---|---|"]
for name, what in OPTIONAL.items():
    out.append(f"| `{name}` | {what} |")
out += ["", "## Already on disk (grab these first, they cost nothing)", "",
"These were saved by tools during development. Copy them into the hand-over folder under their original names; they may do for the report even if not for the site.",
"- `Screenshots/WaterloggedCity/` (production previews of the flooded capital)",
"- `Screenshots/FloodPrototype/FloodedCity_Prototype.png`",
"- `Screenshots/ConcreteReview/*.png` (the concrete city pass: downtown, commercial, suburban, before/after)",
"- `Screenshots/Inventory/SyntyBackpack.png`",
"- `GrassStreamingBackups/Review/` (grass streaming captures: close, zoomed, rotated, walking)",
"- The main menu hero slideshow images (wherever the Day 22 menu work saved them)",
"- Any capture-plan output from the earlier `capture-plan.md`",
"", "## Capture setup that now exists", "",
"- **F9 Hacks panel**: god mode, fly camera, time of day, weather, teleport, zombies on/off, weapons. This replaces the free camera the first list asked for.",
"- **F10** cycles regional snow. **F7** NPC panel. **B** Build Mode (has God and Invisible). **J** quest journal. **Q** weapon wheel. **I / Tab** backpack. **G** recalls the dog.",
"- Main menu **World Switches** turn zombies and NPCs on or off per session.",
"- Capture at 3840x2160 with the built-in 2x screenshot in Play; restart the editor between Play sessions (memory).",
"- Zombies and NPCs are OFF by default: switch zombies on only for 01, 05, 08, 09.",
"", "## Priority if short on time", "",
"`01-hero-horde` (used on both the homepage door and the game hero), `03-hero-flooded-city`, `15-world-grassland`, `05-combat-melee`, `02-hero-rider`, `09-loot-drop`, `14-character-creator`.",
"",
"## Before the shoot",
"- Colour grading is in; the hero shots can go ahead.",
"- Avoid the Developer Mode / World Switches text on the main menu, and any F9 panel left open.",
"- Towns run at 60-90 fps now; the flooded capital and D1-D8 districts are the showpieces.",
"- Never commit raw captures to the Unity repo."]
open(os.path.join(ROOT, "SHOTLIST.md"), "w").write("\n".join(out) + "\n")
print(len(uses), "placeholders;", sum(n in have for n in uses), "delivered")
missing = [n for n in uses if n not in SPEC]
if missing: print("no description for:", missing)
