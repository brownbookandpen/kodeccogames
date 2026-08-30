# CARRIER 4.1 Design Notes

Working record of decisions made while reworking the 4.1 character set. Not the blog post, just what we settled and why.

---

## 1. The core principle of 4.1

Old cards had three lines: phase, usage limit, effect. New cards have two: phase, effect.

We stopped limiting abilities with a **counter** and started limiting them with **cost** and **timing**:

- a typed supply card to spend (MEDICAL, ARMAMENT, SAMPLE)
- a phase lock
- a drawback written into the ability itself
- a condition outside your control

All of those are decisions made during play. A usage counter is just a number that runs out.

---

## 2. Faction = mechanical identity

Went through all 18 abilities by what they mechanically do. Five factions already mapped cleanly onto one job each. **Outlaw was the only incoherent one**, holding three unrelated cards.

Three moves fixed it:

| Move                                  | Reason                                              |
| ------------------------------------- | --------------------------------------------------- |
| Sheriff → Outlaw (renamed **Warden**) | Joins Stranger and Trickster as player interference |
| Prospector → Ranger                   | Gold Rush is a draw engine, pure supply economy     |
| **Survivalist → Hunter**              | The real outlier. Only Ranger with a combat trigger |

The Survivalist move was the key insight. The original plan was to move Disruptor into Hunter, and every ability invented for her afterwards fought that placement. She was never the problem. Survivalist was.

### Final roster

| Faction   | Members                         | Job                      |
| --------- | ------------------------------- | ------------------------ |
| Detective | Enforcer, Informant, Inspector  | Indirect intel           |
| Scientist | Geneticist, Virologist          | Direct intel             |
| Amnesiac  | Outlander                       | Direct intel, self-blind |
| Hunter    | Sentry, Duelist, Survivalist    | Encounter combat         |
| Ranger    | Blacksmith, Forager, Prospector | Discard economy          |
| Scrapper  | Pathfinder, Surveyor, Disruptor | Encounter deck control   |
| Outlaw    | Stranger, Trickster, Warden     | Player interference      |

Counts: 3 / 3 / 3 / 3 / 3 / 2 / 1. Phase spread: 6 Daybreak, 5 Nightfall, 7 All Phase.

---

## 3. The intel colour rule

A design law worth keeping.

**Yellow and orange get roles on demand.** Geneticist asks, Virologist pays, Outlander just looks. Different prices, same payload, always immediate, always their choice.

**Red never controls the access.** Something has to happen first, or they read an object instead of a person, or they send someone else to look. Enforcer waits for a trigger, Informant infers from a hand, Inspector delegates.

Red can end up learning a role. It can never simply decide to.

---

## 4. MARK

Four cards now place their character card onto another player's character card.

> **MARK**: Place your character card onto another player's character card. It stays there until, on your turn, you move it to another player or take it back.

Same gesture, four different consequences, one per faction:

| Card     | Faction   | Ability     | Effect                                                                      |
| -------- | --------- | ----------- | --------------------------------------------------------------------------- |
| Warden   | Outlaw    | ARREST      | Their ability is blocked                                                    |
| Enforcer | Detective | INVESTIGATE | Whenever they join an encounter, look at their hand before they contribute  |
| Surveyor | Scrapper  | OVERWATCH   | Whenever they draw a card, look at the top 2 and choose which one they draw |
| Sentry   | Hunter    | CROSSFIRE   | Whenever you and that player both take part in an encounter, [-1] danger    |

All four persist. None resolve and return on their own.

**Why "mark" and not "choose":** choose is already used generically on Informant and Duelist, so it can't be a keyword. Mark also gives an adjective for the ongoing state ("a marked player"), which rules text needs.

**Self-balancing:** you only have one mark. Leaving it on someone means watching nobody else, and moving it costs your turn.

---

## 5. Renames

| Was                | Now           | Note                     |
| ------------------ | ------------- | ------------------------ |
| Brawler → Sheriff  | **WARDEN**    | Ability kept as Arrest   |
| Deadeye → Captain  | **SENTRY**    | Longshot → **Crossfire** |
| Outrunner          | **DISRUPTOR** | Evade → **Decoy**        |
| Tracer             | **INFORMANT** | Intercept kept           |
| Surveyor's Lookout | **OVERWATCH** | Character name unchanged |

Warden was chosen over Sheriff because a lawman in the Outlaw faction is a word collision. A warden isn't the law, he's the one holding the keys. Alternative considered: keep Sheriff and lean on the flavour that he took the badge off a body.

Sentry was chosen over Marksman (gendered) and Longshot (the only nickname in a cast of role nouns).

---

## 6. Ability rewrites decided here

**WARDEN / ARREST**

> Mark another player. Their ability is blocked.

**ENFORCER / INVESTIGATE**

> Mark another player. Whenever they join an encounter, look at their hand before they contribute.

**SURVEYOR / OVERWATCH**

> Mark another player. Whenever they draw a card, look at the top 2 cards and choose which one they draw.

**SENTRY / CROSSFIRE**

> Mark another player. Whenever you and that player both take part in an encounter, [-1] danger.

**DISRUPTOR / DECOY**

> Look at the top 3 encounter cards. Place 1 on the bottom of the deck and return the rest in any order.

Disruptor's job is now removal. Pathfinder can only move the problem around, she is the only one who can make an encounter go away.

---

## 7. Rules learned along the way

- **Scale is not identity.** A card that does the same thing as another card with a smaller number is a discount, not a character. This killed old Surveyor (small Pathfinder) and one Disruptor draft (small Pathfinder again).
- **What behaviour does the card change** is a better family test than what the effect is. Survivalist's refund makes you volunteer for fights, so it's combat. Blacksmith's makes you mine the discard pile, so it's economy.
- **Passive plus phase lock is the worst combination.** No agency, and switched off half the game.
- **Visible physical placement generates table drama.** Arrest is the strongest card in the set because everyone can see it and has to argue about it.

### Ideas rejected and why

| Idea                                    | Why it failed                                                             |
| --------------------------------------- | ------------------------------------------------------------------------- |
| Disruptor → Hunter                      | Wrong character moved. Every ability written for her fought the placement |
| Flat [-1] passive on Disruptor          | No decision, and it was Captain with a smaller number                     |
| Ceasefire, reclaim 2 cards on failure   | Duplicates Survivalist, and it's economy wearing a combat trigger         |
| Free discard-pile grab each Nightfall   | Makes Blacksmith strictly worse at his own job                            |
| Push an encounter into the Fallback Row | Players can already run for free, so it does nothing                      |

---

## 8. Open questions

1. **What does falling back actually cost?** Nothing in the set touches the Fallback Row anymore, so either it needs teeth or it needs a card that uses it.

2. **Trickster and MARK.** If Trickster swaps character cards with a marked player, does the mark follow the card or stay with the person? And if Warden's own card is sitting on someone else, what does Trickster take when he targets Warden?

3. **Once per turn.** Dropping the usage line means nothing on the cards stops someone spending three Medicals for three Virologist checks in one turn. Suggested global rule: *an ability can only be used once on your turn, unless the card says otherwise.*

4. **Encounter rules confirmed.** Contributions are made face down and revealed at resolution. Card count is public throughout. The leader chooses how many participants and who they are. Duelist is the exception who chooses 1 or 2 cards himself.
   
   - This makes **Enforcer stronger, not weaker**. Everyone sees a weak contribution at reveal, but only Enforcer can contradict "that's all I had," because he saw the hand beforehand. Leave his card as written.
   - It creates a **problem for Sentry**. Crossfire needs both her and the marked player in the same encounter, but the leader decides that, so her card fires only when a third party allows it. Proposed fix: drop the "and you" so it reads *"whenever that player takes part in an encounter, [-1] danger."* One condition instead of two, and a sniper covering someone should not have to be standing next to them.
   - **Systemic:** Sentry, Enforcer, Survivalist and Duelist all trigger on "take part in an encounter" and none of them can opt in. The leader is now the most powerful seat at the table, deciding who gets to use their character at all. Worth watching in playtest.

5. **Is MARK highlighted?** Trickster highlights TRICKSTERS and AMNESIACS in orange. MARK is plain white on all four cards.

6. **Sentry's phase.** Daybreak only, while the other three marks are All Phase. Deliberate or drift?

7. **Sentry's number.** [-1] may be too quiet next to old Deadeye's [-2] flat discount, given the condition needs two specific people in one fight.

---

## 9. Card errata found in NEW CARDS v3

- **Outlander:** badge says NIGHTFALL, text says "on your turn during DAYBREAK"
- **Duelist:** Nightfall only, but ability says "any encounter"
- **Blacksmith:** "discard 2 [ARMAMENT] supply **card**" should be "cards"
- **Geneticist:** only card using his / he / him, everything else is gender neutral

---

## 10. Housekeeping

**Comparison images needing regeneration (9):** Brawler→Warden, Captain→Sentry, Outrunner→Disruptor, Surveyor, Enforcer, Survivalist (faction), Prospector (faction), Duelist (phase), Blacksmith (phase).

**Filenames drifted from contents:**
`[BLUE] BRAWLER` → `[BROWN] WARDEN`, `[BLUE] CAPTAIN` → `[BLUE] SENTRY`, `[OLIVE] OUTRUNNER` → `[OLIVE] DISRUPTOR`, `[GREEN] SURVIVALIST` → `[BLUE]`, `[BROWN] PROSPECTOR` → `[GREEN]`, and `[B] OUTLANDER` should be `[A]`.

**Character Changes.md:** Warden section missing entirely, Sentry / Disruptor / Surveyor / Enforcer sections still describe old abilities, six image links broken by absolute Windows paths, Prospector still called an Outlaw, heading class tags on only four of seventeen sections.
