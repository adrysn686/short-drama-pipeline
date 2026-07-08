# AI Vertical Short-Drama Factory — Technical Architecture

**Scope locked from clarifying answers:** Western platforms first (TikTok/IG Reels/YT Shorts), prototype/solo-creator budget ($500–3,000/mo), technical builder who can self-host n8n and write glue code. Chinese-platform (Douyin/Xiaohongshu) publishing is designed as a Phase-2+ manual/semi-automated add-on, not the initial target.

## Context

The goal is a pipeline that takes a one-line prompt ("CEO falls in love with his bodyguard") and produces a 13-episode, vertical, AI-generated short drama — story, script, video, voice, subtitles, and a published post — with a human only reviewing at a few checkpoints, not doing the work. This is a real, fast-moving market (ReelShort/DramaBox did $2.8B+ in IAP revenue in 2025; AI production is cutting per-drama cost from $150–300K to roughly $2–5K), but every "AI video pipeline" plan lives or dies on two things: (1) character consistency across 13 episodes and dozens of shots, and (2) which steps platforms actually let you automate vs. which need a workaround. This document is opinionated about both, based on July 2026 tool capabilities.

---

## 1. System Overview (text diagram)

```
[User Prompt]
     │
     ▼
┌─────────────────────┐
│ 1. STORY BIBLE AGENT │  (Claude, structured output)
│  → title, genre, cast,│
│   arcs, 13-ep outline,│
│   cliffhangers, twists│
└─────────┬────────────┘
          │  ⏸ HUMAN GATE 1 (approve bible — cheap to fix here, expensive later)
          ▼
┌─────────────────────┐
│ 2. CHARACTER BIBLE   │  (Seedream / Kling text-to-image)
│  reference sheets:    │
│  face, outfit, hair,  │
│  per main character   │
└─────────┬────────────┘
          │  ⏸ HUMAN GATE 2 (approve character look-lock — this is reused 13× )
          ▼
┌─────────────────────┐
│ 3. SCRIPT AGENT      │  (Claude, per-episode, structured JSON)
│  scenes, dialogue,    │
│  camera directions,   │
│  emotion tags, SFX/BGM│
│  mood, runtime target │
└─────────┬────────────┘
          ▼
┌─────────────────────┐        ┌──────────────────────┐
│ 4. VIDEO GENERATION  │◄──────►│ CHARACTER/PROP ELEMENTS│
│  Kling 3.0 / Seedance │        │  (reused across all    │
│  2.0, shot-by-shot    │        │   13 episodes for      │
│  using locked elements│        │   consistency)         │
└─────────┬────────────┘        └──────────────────────┘
          ▼
┌─────────────────────┐
│ 5. VOICE + LIP SYNC  │  (ElevenLabs TTS → Sync.so)
│  per-character voice, │
│  emotional delivery,  │
│  synced to mouth      │
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│ 6. ASSEMBLY          │  (FFmpeg, self-hosted)
│  merge clips + VO +   │
│  BGM/SFX + Whisper     │
│  subtitles (burned-in)│
└─────────┬────────────┘
          │  ⏸ HUMAN GATE 3 (final QA — artifacts, mistranslation, policy risk)
          ▼
┌─────────────────────┐
│ 7. PUBLISHING        │  (n8n → TikTok/IG/YT native APIs)
│  captions, hashtags,  │
│  thumbnail, schedule  │
└─────────┬────────────┘
          ▼
┌─────────────────────┐
│ 8. ANALYTICS LOOP     │  (platform Insights APIs → DB)
│  retention, completion│
│  rate → feeds back into│
│  Story Bible Agent's  │
│  prompt for next drama│
└──────────────────────┘
```

Orchestration engine for all of this: **n8n, self-hosted** (justification in §6).

---

## 2. Story Planning (Story Bible Agent)

**Tool: Claude (Opus for the bible, Sonnet is fine for episode outlines) via the Anthropic API**, called from an n8n node with a forced JSON schema (tool-use / structured output), not free-text parsing.

Why Claude over GPT/Gemini here: the failure mode in this genre is losing the thread — inconsistent character motivation, forgotten twist setup, cliffhangers that don't pay off. That's a long-context coherence and instruction-following problem across ~15K+ tokens of accumulated story state, which is Claude's strongest relative area versus alternatives, and it has first-class structured-output support so the pipeline never has to regex-parse prose.

**Output schema (single JSON object):**
- `title`, `genre`, `tropes` (the "troader" — e.g. `["revenge", "secret identity", "billionaire CEO", "fake dating"]`, tagged because these drive both video mood-boarding and hashtag generation later)
- `characters[]`: name, role, appearance description (feeds the Character Bible image prompts), personality, arc (start state → end state), voice profile tag (age/gender/register, feeds TTS voice selection)
- `relationships[]`: pair, dynamic, how it evolves
- `setting`: time/place, visual style (feeds a global "look bible" prompt prefix used on every image/video generation call)
- `overall_plot`: 3-act summary
- `episodes[1..13]`: each with `synopsis`, `emotional_beat` (e.g. humiliation → hidden power reveal), `cliffhanger`, `runtime_target_sec` (60–90)
- `major_twists[]`: which episode, what's revealed, foreshadowing already planted in earlier episodes (explicit cross-references so the script agent doesn't contradict itself)
- `final_payoff`

**Pacing pattern to hard-code into the prompt** (this is what separates a working microdrama from generic AI fiction): episode 1 cold-opens on the most dramatic moment (often mid-scene from later, then flashback "3 days earlier"), a reveal or reversal every 20–30 seconds, a cliffhanger in the final 5–8 seconds of *every* episode, and escalating stakes every 3–4 episodes rather than one slow build.

**Human Gate 1:** the story bible is ~2 pages and costs one LLM call (~$0.20–0.50). Reject/regenerate here is nearly free; a bad character arc discovered after 13 episodes are shot is not. This is the single highest-leverage manual checkpoint in the whole system — do not automate past it.

---

## 3. Script Generation

One Claude call per episode (13 total, can run in parallel since each has the full story bible as context), each producing structured JSON per episode:

- `scenes[]`: location, time of day, shot list
- Per shot: `dialogue` (Mandarin, with pinyin optional for QA), `narration` (if any), `camera_direction` (shot type, movement — phrased as a direct prompt fragment for the video model, e.g. "slow push-in, medium close-up, 3/4 angle"), `character_emotion` + `facial_expression` (explicit tags, not left to be inferred — this is what the video-gen prompt and TTS emotion parameter both key off of), `environment_description`, `sfx_suggestion`, `bgm_mood`
- `estimated_runtime_sec` (validated against the 60–90s target; if the script agent overshoots, an n8n IF-node kicks it back for a trim pass rather than letting a human catch it downstream)

Each scene/shot description is written to double as a **video-gen prompt** and a **TTS script line**, so no separate "convert script to prompt" translation step is needed — design the schema once, consume it twice.

---

## 4. AI Video Generation

### Tool comparison (as of mid-2026)

| Tool | Character consistency | Cinematic quality | Speed / batch fit | API access | Best fit here |
|---|---|---|---|---|---|
| **Kling 3.0 (Kuaishou)** | Very strong via "Elements" (train once on a few reference photos, reuse by name in every prompt) | Best-in-class for stylized, story-driven video — closest to Chinese drama house style | Moderate speed | API via aggregators (fal.ai, PiAPI) | **Primary** — Elements feature is exactly the "reuse character across 13 episodes" mechanism this project needs |
| **Seedance 2.0 (ByteDance)** | Excellent, holds identity across cuts so a multi-shot sequence reads as one continuous piece | Very strong motion quality | Fastest + best price/performance of the top tier | API via aggregators | **Secondary / batch workhorse** — use for high-volume B-roll and simpler dialogue shots to control cost |
| **Sora (OpenAI)** | Good | Excellent for photorealism | Slower, pricier at scale | API | Situational — use for a hero shot (episode 1 cold open, finale) where cost is justified |
| **Runway Gen-4** | Good, strong with reference-image conditioning | Strong, very controllable camera work | Moderate | Mature API | Fallback if Kling/Seedance access is constrained; strongest existing ecosystem of n8n/Zapier integrations |

**Recommendation:** Kling 3.0 as primary generator (Elements = character-lock), Seedance 2.0 as the cost/speed workhorse for simpler shots, both accessed through an aggregator (fal.ai or PiAPI) so the pipeline has one unified job-submit/poll API instead of juggling native SDKs — this also gives a drop-in fallback if one vendor rate-limits or degrades.

**Workflow per episode:** for each shot in the script → build prompt (camera direction + emotion + environment + locked Element references for every character/prop/location in frame) → submit to video-gen API → poll job status → download clip → tag with episode/scene/shot ID → store in asset bucket (S3/R2). 6–10 shots per 60–90s episode is a reasonable target; longer single takes are avoided because current models still degrade in fidelity past ~10s.

---

## 5. Voice Generation

**TTS: ElevenLabs (Eleven Multilingual, Mandarin)** — chosen over MiniMax Audio and Azure because it has the most mature API for automation (voice design + cloning + emotion/style controls exposed programmatically, not just in a web UI), which matters more than marginal tonal-accuracy differences at prototype scale. *If the roadmap moves toward Chinese-platform-first (Phase 2+), re-evaluate MiniMax Audio, which is Chinese-native and may have an edge on Mandarin tonal nuance.*

**Voice assignment automation:** the Story Bible Agent's `voice_profile` tag per character (age/gender/register/personality) maps to a curated pool of pre-selected ElevenLabs voice IDs (build this pool once, manually, during setup — picking good voices is a one-time human judgment call, not something to re-automate per drama). Each script line's `character_emotion` tag feeds ElevenLabs' emotion/style parameter so delivery isn't flat.

**Lip sync: Sync.so** — chosen specifically because it's the only major player priced and built for *programmatic, usage-based, in-pipeline* use; HeyGen and Hedra are stronger for polished multilingual avatar content but are built around a manual/UI workflow and are priced accordingly. Sync.so takes the generated video clip + the TTS audio and produces a lip-synced final clip via API call — this is the join point between the video and voice branches of the pipeline.

---

## 6. Asset Management (consistency across 13 episodes)

The single hardest problem in this whole system is *drift* — character 2, or character 1 in episode 9 looking subtly different from episode 1. Solve it with a **Look Bible**, generated once (Human Gate 2) and referenced by ID everywhere downstream, never regenerated per-episode:

- **Character appearance/clothing/hairstyle:** one Seedream/Kling reference-image set per character per "outfit state" (e.g., "poor delivery girl — work uniform" and "revealed heiress — gala dress" are two separate locked Elements, since the story arc changes wardrobe). Store as named Kling Elements + raw reference images in the asset DB, keyed by character name + outfit state.
- **Locations:** same pattern — one locked Element per recurring location (CEO's office, the family mansion, the rundown apartment).
- **Lighting / color grading / camera style:** don't leave these to per-shot prompting — bake a fixed "style prefix" string (e.g., "cinematic Chinese urban drama, warm-cool contrast grade, shallow depth of field, handheld-smooth camera") into every video-gen prompt from a single config value, so a style tweak is a one-line change, not a 13-episode redo.
- **Props:** same Elements mechanism for anything plot-relevant (the contract, the ring, the phone with the incriminating photo).

All of this lives in a lightweight **asset registry** (a Postgres table or even an Airtable base is enough at prototype scale): `asset_id, type (character/location/prop), name, outfit_state, kling_element_id, seedream_reference_urls[], voice_id, style_prefix`. Every downstream prompt-builder step reads from this registry instead of re-describing things in free text — this is what makes 13 episodes look like one drama instead of 13 independent ones.

---

## 7. Automation Pipeline (n8n)

**n8n, self-hosted (Docker on a small VPS), chosen over Make.com and Zapier** for three concrete reasons relevant to this specific workload: (1) per-*execution* pricing (self-hosted = free beyond VPS cost) vs. Make's per-*operation* pricing, which matters because this pipeline has dozens of operations (shots × episodes) per single logical run; (2) native code nodes for arbitrary Python/JS, needed for FFmpeg orchestration and job-polling loops that don't map cleanly to no-code nodes; (3) a technical builder is the stated resourcing, so self-hosting's setup cost is a non-issue and its cost/flexibility upside is pure win. Make remains the better choice if the resourcing answer had been "no-code only."

**High-level n8n workflow (one drama = one workflow run, with sub-workflows per episode):**

1. **Webhook/Form trigger** — accepts the user's one-line prompt.
2. **Story Bible node** (HTTP → Claude API, structured output) → write to asset registry + episode table.
3. **Human Gate 1** — n8n `Wait` node + Slack/email approval message with the bible attached; resumes on approval webhook.
4. **Character Bible sub-workflow** — for each character/location/prop: generate reference images (Seedream/Kling API), create locked Elements, write IDs to asset registry.
5. **Human Gate 2** — same wait/approve pattern on the character sheets.
6. **Episode loop (×13, can fan out in parallel batches of 3–4 to respect API rate limits):**
   a. Script generation (Claude, per-episode)
   b. Runtime-check IF-node (trim/regen if outside 60–90s)
   c. Shot loop: build prompt from script + asset registry → submit to Kling/Seedance → poll → download
   d. TTS generation per dialogue line (ElevenLabs) → Sync.so lip-sync merge per shot
   e. FFmpeg sub-step: concatenate shots, mix BGM (mood-matched track from a royalty-free library API, e.g. Mubert/Soundstripe) + SFX, run Whisper on the final audio track for word-level timing, burn in subtitles (CapCut has no public API for this — see §9), export vertical 1080×1920 mp4
   f. Write finished episode + metadata to asset bucket
7. **Human Gate 3** — final QA pass, one review per episode (or spot-check every N once trust is established) before publish.
8. **Publishing sub-workflow** (§8).
9. **Analytics polling workflow** (separate, scheduled, cron-triggered) — pulls performance data on a delay and appends to a "what worked" table that's injected as extra context into the *next* drama's Story Bible prompt.

---

## 8. Social Media Publishing

**Captions/hashtags/thumbnail:** generated by the same Claude pipeline — one more structured-output call per episode taking the episode synopsis + genre/tropes and producing a hook-style caption, 5–8 hashtags (mix of broad + niche/trope-specific, e.g. `#shortdrama #CEOromance #revenge`), and a thumbnail prompt (usually the cliffhanger frame, run through the video model's image-export or a dedicated Seedream still).

**Posting, per platform, using official APIs (all reachable from n8n via HTTP Request nodes):**

| Platform | API | Automation reality | Workaround needed |
|---|---|---|---|
| TikTok | Content Posting API | Caps ~15–25 posts/day/account; **no `scheduled_publish_time` param** — API only supports immediate publish or draft | Build your own queue: store approved episodes with a target publish time in your DB, use an n8n Cron node to fire the immediate-publish call at the right moment. Also budget lead time — TikTok requires manual app review before it grants publishing access to real (non-sandboxed) accounts. |
| Instagram Reels | Graph API | Native scheduling supported; 25 posts/day cap; async two-step container model (create container → poll processing status → publish) | Straightforward — just implement the poll loop, don't fire "publish" before the container reports ready. |
| YouTube Shorts | Data API v3 | Native scheduling via `publishAt`; longest window (12 months) | Default quota (10,000 units/day, ~1,600/upload) caps you at ~6 uploads/day per app — fine at prototype scale (2–5 dramas/month), but file for a quota increase before scaling to a small studio. |
| Douyin / Xiaohongshu | No public posting API for third parties | Not automatable end-to-end today | Out of scope for Phase 1 per the chosen focus; if pursued later, the practical path is a human-in-the-loop upload (assisted by a browser-automation script for the mechanical parts) or a partnership with an MCN/agency that already has platform-approved access — do not attempt unofficial/reverse-engineered posting, it risks account bans. |

**Analytics/feedback loop:** each platform's own Insights/Analytics API (TikTok Business API, IG Insights, YouTube Analytics API) polled on a schedule, retention/completion-rate and engagement pulled into the same DB, and summarized (which tropes, cliffhanger styles, and episode lengths retained best) as an extra input block prepended to the next Story Bible prompt — this is the actual "learning" mechanism; there's no need for a fine-tuned model, in-context performance data is enough at this scale.

---

## 9. Explicit Platform Limitations & Workarounds (summary)

- **CapCut has no public API** for server-side captioning/rendering → don't route through it; use **Whisper (API) for word-level transcription timing + self-hosted FFmpeg** for subtitle burn-in. Fully automatable, just not through CapCut.
- **Midjourney has no official API** → don't rely on unofficial proxies for anything production-critical (ToS risk); use Seedream's or Kling's native text-to-image endpoints, which are officially supported and already in the pipeline.
- **TikTok's lack of native scheduling** → solved by an internal publish-queue + cron trigger, as above.
- **TikTok API approval is a manual, human-reviewed process** with lead time → apply early, in parallel with Phase 0/1 build-out, not as a blocker discovered at launch.
- **Voice cloning of real people** is a legal/ethical line this system should not cross → only use synthetic/designed character voices, never clone a real individual without consent.
- **Content moderation risk:** romance/revenge/wealth-fantasy tropes can brush against platform policy (suggestive content, "clickbait" cliffhanger rules). Human Gate 3 should explicitly include a policy-risk check, not just an artifact/quality check — an account strike is far costlier than one human review pass.

---

## 10. Monetization

- **Subscription (freemium):** first 2–3 episodes free, paywall the rest — the standard ReelShort/DramaBox model, applicable if this becomes its own app/channel rather than pure social distribution.
- **Custom drama generation:** paid one-off generation for creators/brands who supply their own prompt (essentially productizing this exact pipeline as a service).
- **Licensing:** sell finished IP/episodes to existing platforms (ReelShort, DramaBox, FlexTV) that license third-party content.
- **Advertising:** mid-roll/pre-roll on YouTube uploads, brand integration written into scripts (e.g., a prop or setting sponsorship) — cheap to add since props/locations are already modular in the asset registry.
- **White-label SaaS:** license the pipeline itself to other small studios/creators once it's proven, priced per-drama or per-seat.
- **Creator marketplace:** let outside creators submit prompts and share revenue on generated dramas — turns this from a content studio into a platform.
- **API access:** expose the Story Bible / Script Agent as a standalone API product for other short-drama studios who have their own video pipeline but want better writing.

Realistic sequencing: prove quality and retention with the Advertising/organic-growth model first (lowest friction, fastest feedback), then layer Subscription once there's a content library worth paywalling, then Licensing/SaaS/Marketplace once the pipeline itself is the proven asset.

---

## 11. Cost Estimate (prototype scale, per drama = 13 episodes, ~15–20 min total runtime)

| Component | Est. cost/drama |
|---|---|
| Story bible + 13 scripts (Claude API) | $10–25 |
| Character/location reference images (Seedream/Kling) | $10–20 |
| Video generation (Kling + Seedance, ~100–130 shots) | $150–450 |
| TTS (ElevenLabs) | $15–40 |
| Lip sync (Sync.so) | $50–150 |
| Music/SFX library | $5–15 |
| n8n VPS + storage (amortized/mo, not per-drama) | $15–30/mo flat |
| **Total per drama** | **≈ $250–700** |

At 2–5 dramas/month this lands comfortably inside the $500–3,000/mo prototype budget, with video generation as the dominant and most variable cost — the main lever for cost control is routing simpler B-roll/establishing shots to the cheaper Seedance tier and reserving Kling for hero dialogue shots.

---

## 12. Implementation Phases

- **Phase 0 — Manual dry run (1–2 weeks):** hand-execute every step once for a single drama (no automation) to validate that the story→script→video→voice→assembly quality bar is actually good before investing in pipeline plumbing. Cheapest place to discover "this doesn't look good enough" is here.
- **Phase 1 — Writing automation:** automate Story Bible + Script generation only (Claude + structured output + Human Gate 1). Everything downstream still manual. Validates the prompt engineering and asset-registry schema.
- **Phase 2 — Media automation:** wire up video gen, TTS, lip sync, and FFmpeg assembly in n8n; publishing still manual. This is where the asset registry / Elements consistency mechanism gets battle-tested.
- **Phase 3 — Publishing automation:** TikTok/IG/YT API integration, caption/hashtag/thumbnail generation, the publish-queue workaround for TikTok, and analytics polling.
- **Phase 4 — Feedback loop + scale:** wire analytics back into the Story Bible prompt, parallelize episode generation, evaluate moving from prototype to small-studio tooling tier (higher API quotas, dedicated review staff) once volume justifies it.

## 13. Where Manual Review Stays Valuable (recap)

1. **Story bible approval** — cheapest point to kill a bad concept.
2. **Character look-lock approval** — errors here replicate across all 13 episodes.
3. **Final episode QA** — catches AI artifacts, mistranslation, and platform-policy risk before anything goes live and risks the account.
4. **Voice pool curation** — one-time manual selection of good TTS voices, not per-drama.
5. **TikTok API approval process** — inherently requires a human review cycle on TikTok's side; plan lead time, don't block launch on it.

---

## Sources consulted (tool landscape, July 2026)

- [Best AI Video Generation Models in 2026](https://www.atlascloud.ai/blog/guides/best-ai-video-generation-models-2026), [Best AI Video Generators for Consistent Characters in 2026](https://blog.mage.space/article/best-ai-video-generators-consistent-characters-2026/9459a229-806d-4a73-8abf-a19db645a248)
- [HeyGen vs Hedra: AI Lip Sync Comparison (2026)](https://lipsync.com/compare/heygen-vs-hedra)
- [ElevenLabs Mandarin Chinese TTS](https://elevenlabs.io/text-to-speech/mandarin-chinese), [Maestra Chinese TTS](https://maestra.ai/tools/text-to-speech/chinese)
- [TikTok Content Posting API guide](https://zernio.com/blog/tiktok-posting-api), [TikTok API pricing/limits](https://www.blotato.com/blog/tiktok-api-pricing)
- [Instagram Graph API scheduling (n8n template)](https://n8n.io/workflows/4498-schedule-and-publish-all-instagram-content-types-with-facebook-graph-api/)
- [YouTube Shorts automation 2026](https://mobileproxy.space/en/pages/youtube-shorts-automation-in-2026-step-by-step-guide-from-idea-to-scaling.html)
- [Vertical Haus: Micro Dramas and AI Production](https://verticalhaus.ai/blog/micro-dramas-ai-production-june-18-2026), [Real Reel: AI Is Rewriting the Vertical Short Drama Industry](https://www.real-reel.com/ai-is-rewriting-vertical-drama-microdrama-industry/)
- [n8n vs Make 2026 comparison](https://www.autodida.com/post/n8n-vs-make-com-in-2026-which-platform-wins-for-ai-agent-automation), [Make vs n8n official](https://www.make.com/en/compare/make-vs-n8n)
- [Kling AI character consistency / Elements guide](https://kling.ai/blog/ai-character-consistency-guide), [Kling Elements technical guide](https://artcoreai.com/guides/v2-kling-elements-guide)
- [CapCut API status / ZapCap alternative](https://samautomation.work/capcut-api/)
