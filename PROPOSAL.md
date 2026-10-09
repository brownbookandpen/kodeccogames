# Kodecco Games: Dual-Use Site Proposal

## What I found

**Site (this repo):** static HTML on GitHub Pages. The homepage is one 141 KB `index.html` (Mission Brief, Journal, Album, Roadmap, Signal). There are rules pages, 10 hand-authored posts, and a custom `post-editor.html`. The whole site is themed around the card game: hazard tape, CRT scanlines, Roadmap Phases 1 to 5 ending in crowdfunding. Design tokens already live in `styles.css`.

**Unity game (`CarriersTheGame`):** a 3D zombie survival game. It has a loot system, horseback riding, melee and firearms, a character creator, build mode, Gaia worlds and zombie AI. `Devjournal/*.md` holds about 20 dev notes (Gameplan, Inventory, MeleeCombat, FloodedCity, and so on). Those are ready-made blog material.

**The gap:** the two products share a title and a mood but no content. Today the site can only describe the card game.

## Proposal: one studio hub, two product lines

Rename the site's role from "the Carrier card game site" to **Kodecco Games**, the studio. Carrier then has two editions that share one world.

### Information architecture

| Route | Purpose |
|---|---|
| `/` | Studio landing page. A hero carousel with one slide per product (the carousel you already have), and a latest-posts strip from both. |
| `/tabletop/` | The card game: Mission Brief, rules (existing `/rules/*` moved or redirected), Album, Roadmap Phases 1 to 5. |
| `/game/` | The Unity game: pitch, screenshots and video, feature list (zombies, horses, loot, build mode), Roadmap, wishlist and Signal. |
| `/devlog/` | One blog with a filter: All / Tabletop / Game / Studio. Replaces the Developer Logs section. |
| `/lore/` (optional) | Shared setting. Only if both products really share a world (see questions). |
| `/signal/` | A single mailing list with a checkbox per product. |

Keep every existing URL working with redirects. `sitemap.xml` and the posts' SEO value must survive.

### Technical plan

1. **Don't change hosting.** Stay static on GitHub Pages and keep the CNAME. No framework migration at first.
2. **Add a tiny build step** (Node, or Python like your existing `update_encounters.py`) that renders posts from Markdown front-matter (`product: game|tabletop`, `date`, `tags`). That does three jobs:
   - It removes the 141 KB hand-edited homepage and the duplicated per-post CSS.
   - It makes the post editor optional.
   - It lets **Unity `Devjournal/*.md` be imported as blog posts** (a script that copies chosen files, strips internal notes like "AI assistant instructions", and adds front-matter).
3. **Unify the shared shell:** one header, footer, and `styles.css`. Add `--accent-game` beside the existing red/yellow tokens, so the Unity side looks related but distinct (for example a cold green/teal against the card game's hazard yellow).
4. **Game page content:** screenshots and clips captured from Unity (scripted capture of the existing scenes: `Build 1.0`, `World_0x_Gaia`, `CharacterCreation`). Compressed to webp/mp4 so the repo stays small. Don't copy the 1.8 GB project into this repo.
5. **Keep it private-safe:** the Unity repo is private and contains paid asset packs (Malbers, Synty, Gaia, etc.). Only publish your own screenshots and prose, never asset files.

### Phases (and rough credit use)

| Phase | Work | Est. spend |
|---|---|---|
| 0. Research | Mine Unity Devjournal and scenes, inventory features, decide the shared lore | ~$15 |
| 1. Foundation | Shared shell and tokens, new routes, redirects, build script, mobile and a11y pass | ~$50 |
| 2. Game section | `/game/` page, feature sections, media gallery, roadmap | ~$40 |
| 3. Devlog | Markdown pipeline, filter UI, import of 6 to 8 Unity dev notes as polished posts, migrate the 10 existing posts | ~$60 |
| 4. Polish | Hero carousel, SEO and OG tags, sitemap, Lighthouse, newsletter hookup | ~$30 |
| Buffer | | ~$55 |

That is roughly $250. These are estimates; Phase 0 is the real check, and I'll report spend after each phase.

## Questions that change the plan

1. **Same universe?** Is the Unity game the video-game version of the Carrier card game (same Carriers/Survivors, Daybreak/Nightfall), or a separate zombie game under the same studio? This decides whether `/lore/` exists and whether "Carrier" stays the studio name.
2. **Game's public status:** announce it publicly now, or keep it as "in development" with no dates?
3. **Unity access:** can I keep reading `CarriersTheGame` (private) and also write screenshot scripts, or is it read-only for me? (The `Carriers` repo is empty. Is it intended for something?)
4. **Branding:** keep "CARRIER" as the site title, or move to "KODECCO GAMES" with Carrier as a product?
5. **Newsletter backend:** what handles "Send Signal" today?

## Recommended next step

Approve Phase 0 and answer questions 1 and 4. I'll then build Phases 1 and 2 on a branch with a preview, so nothing live changes until you merge.
