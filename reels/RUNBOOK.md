# Reel production runbook (@pundirandassociates)

Each scheduled run makes exactly ONE reel: the first row in `.claude/instagram/plan.md` whose status is TODO.
Read `.claude/instagram/voice.md` first and obey it (Bar Council Rule 36: no solicitation, no results, no invented numbers).

1. **Script** (Hinglish, Roman script, 85-110 words, ~40 s). Hook first sentence (use the plan's hook), one
   provision per beat, close with "Ise save karo, aur us insaan ko bhejo jise kabhi iski zaroorat pad sakti hai."
   Verify every section/article number against the bare act before using it. If unsure of a provision, stop and ask.
   Write `reels/reelNN/script.json` ({"sentences":[{"scene":i,"text":...}]}, 6-9 scenes, numbered 0..n).
2. **Voiceover**: vidiq_voiceover_generate, voiceId `nPczCjzI2devNBz1zQrb` (Brian), script = sentences joined by spaces.
   Poll vidiq_job_poll; `curl -sS -o reels/reelNN/voice.mp3 <audioUrl>`.
3. **Timing**: `python3 -I reels/engine/build_timing.py reels/reelNN`. Check the printed sentence spans make sense
   (first sentence usually ends at the first pause); patch timing.json if a boundary slipped.
4. **Scenes**: write `reels/reelNN/scenes.json` in the same style as reels/reel01/scenes.json (ivory/navy/gold,
   one big numeral or headline, one line-art SVG icon, a navy section pill, `keywords` list for gold subtitle words;
   last scene = recap checklist + SAVE/SHARE pills + "For general awareness only. Not legal advice.").
5. **Render**: `node reels/engine/render.js reels/reelNN` (~70 s). Grab 8 frames into a contact sheet and LOOK at it;
   fix overlaps/cut-off text before continuing.
6. **Caption**: `reels/reelNN/caption.txt` like reel01 (hook line <125 chars, numbered points with sections,
   save/share line, the disclaimer, max 5 hashtags). Lint: `python3 -I .claude/skills/ig-caption/caption.py`.
7. **Upload**: vidiq_video_upload with localFile -> run the returned command -> call again with uploadId for videoUrl.
8. **Approval gate**: send the user the mp4 (SendUserFile) + the caption, and a push notification. Wait for "post".
   Publish only after an explicit yes: vidiq_instagram_publish_reel, platformAccountId `29235951796023926`,
   isAiGenerated true; continue with containerId until PUBLISHED.
9. **Log**: set the plan row to `POSTED <date> <permalink>`, append to `.claude/instagram/log.md`, commit, push to
   branch `claude/beautiful-wright-7yopsj`.

Budget: each reel costs 28 vidIQ credits (voiceover). Check vidiq_balance first; if < 28, notify the user and stop.
