---
title: Example Rule
tag: Example Tag
slug: example-rule
aspect: 3:2
skip: true
---

Write your Mission Brief rule text here. Plain paragraphs, just like this one, become <p> tags automatically.

## Use headings like this

**Bold** and *italic* work inline. So do [links](https://example.com).

![Describe the photo for accessibility](images/your-photo.jpg "Optional caption shown under the photo")

Drop photo files in this same drafts/rules/ folder (or a subfolder), reference them by filename above,
and the script will auto-crop them to a clean rectangle and copy them into the site for you.

IMPORTANT: `slug` must exactly match the `data-slug` on the Mission Brief card in index.html
(currently: allegiance, character, supplies, encounters, mission) or the script won't know
which card to wire up.

CARD IMAGES (like a role/character card): use a ::card block to lay the card image on the
left with text beside it on the right, instead of the normal full-width photo. The card
image is kept at its original aspect ratio (no cropping), so transparent PNG card art
renders cleanly. Use "## Title" inside the block for the bold title line (styled like a
heading), then normal paragraphs for the rest:

::card
![Executioner card art](executioner.png)

## Executioner

You are infected, hiding among the survivors. Your goal is to eliminate the Custodians
before they escape.

On your turn, you may reveal yourself to eliminate one player of your choice.
::

SECRET ROLE CARDS (forced 4:3 portrait crop): add {aspect=3:4} right after the image line
inside a ::card block to force-crop the card art to a clean 4:3 portrait shape instead of
leaving it uncropped. This is what the Post Editor's "🃏 Secret Role Card" button generates
automatically — same ::card layout, just with the crop applied:

::card
![Executioner card art](executioner.png) {aspect=3:4}

## Executioner

You are infected, hiding among the survivors.
::

Delete this example file once you're comfortable — it's just a template.
