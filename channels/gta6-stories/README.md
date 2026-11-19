# GTA 6 Stories: channel blueprint

A Shorts channel that takes **gameplay-only** GTA 6 footage (no streamer on screen or on the audio)
and narrates each clip as a story or a fact, so the clip is the evidence and the narration is the product.
Footage comes from no-commentary playthroughs; see [`clips-shirrako-no-commentary.md`](clips-shirrako-no-commentary.md).
(The earlier Live Insaan stream list is kept for reference but is superseded: it needed the streamer cropped and muted.) It runs in Hindi
first, with English versions of whatever performs.

GTA 6 launched on 19 November 2026 (PS5 and Xbox Series X|S). The window that matters is launch
week: the streams are huge right now and the Shorts feed has not yet filled with copies.

## Name and positioning

Pick one and check the handle is free on YouTube before you create the channel:

| Name | Why |
|---|---|
| **Leonida Files** | Sounds like a case file, which suits "story" and "fact" framing, and Leonida is the game's own state name, not a trademark of a streamer. |
| **Vice City Raaz** | A Hindi-first name ("raaz" = secret); good if Hindi stays the main language. |
| **GTA 6 Unseen** | Plain and searchable, but crowded; weakest of the three. |

One line for the channel description: *"Har din GTA 6 ki ek kahani ya ek fact, jo aapne stream mein miss kar diya."*
English: *"One GTA 6 story or fact a day, from the moments you missed on stream."*

## The format (every Short follows this)

1. **0-2s, the hook line on screen and in the voiceover.** It must confirm the title and open a
   question. Never open with the channel name.
2. **2-20s, the clip itself**, cut tight, with the **game's own audio** (police radio, NPC lines) audible
   where it is the proof. The narration sits on top of the quiet parts, never over the payoff.
3. **20-35s, the turn:** the fact, the twist or the "here is why it happened".
4. **Last 2s, a loop line** that sends the viewer back to the start, or one question for the comments.

Length 20-40s. Vertical 9:16, gameplay only. Hindi captions burned in. Credit the footage source on
screen ("Gameplay: Shirrako") and in the description, with a link.

## What travels in launch week

From the breakout GTA 6 Shorts this month (vidIQ outliers, Nov 2026), the formats overperforming
their channels by 10-39x are "details you missed", "weird things to know before you play" and
"is this feature real?". All three are fact framings. Pure gameplay with no angle does not travel.

So every Short is one of two types:

- **Story:** a streamer expected X and got Y (lost save, police chaos, a fail).
- **Fact:** a real game system the clip proves (cop radio, games inside the game, gym and coffee
  stats), told as "you can do this, here is the proof".

## Posting plan

- **Launch week:** 2 Shorts a day, Hindi. The first batch is in
  [`clips-live-insaan-launch.md`](clips-live-insaan-launch.md) with timestamps, and three full
  scripts are in [`scripts/`](scripts/).
- **Week 2:** keep the 2 Hindi Shorts that beat the channel average, and post English versions of them.
- **Sources to mine next** (all launch-day streams, sorted by views as of 19 Nov 2026):
  CarryMinati (16.2M views), Mythpat (15.1M), Kai Cenat (6.2M), GamerFleet (4.0M), Windah Basudara (3.3M).
  Mythpat and CarryMinati run past 8 hours, so cut them in ranges.

## Legal position: read this before you upload

You chose to clip big streams without permission, with heavy narration on top. That is your call
to make, but you should make it with the exposure stated plainly:

1. **The streamer owns the stream recording** (their commentary, facecam and edit). Re-uploading any
   part of it without a licence is *prima facie* infringement. The defence is fair dealing in India
   (Copyright Act 1957, s.52(1)(a): criticism or review) or fair use in the US (17 U.S.C. §107),
   where YouTube actually adjudicates claims. Both turn on how much you took and whether you added
   something new. **Short excerpts + your own narration + a fact or angle the stream did not give
   = your best case. A raw re-upload with captions = no case.**
2. **YouTube's mechanics matter more than the law.** A Content ID claim only diverts the money from
   that video. A manual **copyright strike** is different: three strikes inside 90 days terminate the channel.
   One strike can cost you the whole channel in launch week. Keep every Short under 40 seconds, use
   under 20 seconds of any single stream per Short, and never post two clips from the same streamer back to back.
3. **Rockstar/Take-Two's video policy** allows gameplay videos only for **non-commercial** use and
   reserves the right to remove anything. It specifically removes **isolated cutscenes, story spoilers
   and in-game TV or performances**. So: no clips built around a cutscene, no mission endings, and no
   character arrests or deaths in titles or thumbnails. The scripts here already avoid all of these.
   Monetisation (YPP) therefore sits outside Rockstar's policy, even though it is widely tolerated.
4. **YouTube ad rules** (updated Sept 2026): graphic gaming violence in the first 7 seconds makes a video
   ineligible for ads, and from 8-15 seconds it is allowed. Open on the reaction or the setup, not the gunfire.
5. **Safer upgrade path.** Several streamers now run open clipper programs (Windah Basudara's GTA 6 stream
   advertises one). Message the streamers you clip most and ask for permission; one written "yes"
   turns a strike risk into a licence.

A counter-notification against a strike is a sworn statement, so file one only where the Short is genuinely
transformative. Do not use it as a reflex.

## Why this repo cannot cut the video

The Everygen clipping service needs a paid plan, and this container's network blocks YouTube. The clip list gives exact
source timestamps, so the cut can be done in any editor (or by Everygen's `clipping` workflow once a
plan is active) in a few minutes per Short.

Sources: [Rockstar video policy](https://support.rockstargames.com/articles/200153756/rockstar-games-video-policy),
[GTA 6 release date](https://www.pcgamesn.com/gta-6-release-date),
[YouTube gaming-violence monetisation update](https://www.dexerto.com/gta/youtube-updates-gaming-violence-monetization-rules-ahead-of-gta-6-launch-3405945/).
