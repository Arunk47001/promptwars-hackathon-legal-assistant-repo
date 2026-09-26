# Hyperframes Composition Brief: Namma Nyaya

## Objective
Create a short launch-style brag video for Namma Nyaya, a GenAI legal
companion for Bengaluru migrant tech workers.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: 18-19 seconds

## Source Material
- Project root: `C:\Users\akmr4\OneDrive\Desktop\cloned_repo\promptwars-hackathon-legal-assistant-repo`
- Primary files read: `frontend/app/page.tsx`, `frontend/app/layout.tsx`,
  `frontend/app/globals.css`, `frontend/components/TopNav.tsx`,
  `frontend/components/RedFlagList.tsx`, `frontend/components/DisclaimerBanner.tsx`,
  `frontend/app/navigator/page.tsx`, `frontend/lib/samples.ts`, `README.md`
- Product name: Namma Nyaya (ನಮ್ಮ ನ್ಯಾಯ)
- Tagline / strongest claim: "Understand your rental agreement or offer
  letter before you sign it."
- Key UI or visual moment to recreate: the upload card → red-flag card
  (brick-red left border, severity badge, citation) → EN/KN language toggle
  switching the explanation into Kannada script
- Copy that must appear verbatim:
  - "Understand your rental agreement before you sign it."
  - "SECURITY DEPOSIT" / "high" severity badge (red-flag card)
  - "Namma Nyaya" and "ನಮ್ಮ ನ್ಯಾಯ" (wordmark, bilingual)
  - "Information, not advice. But information you can finally read."
    (adapted outro line, rooted in the app's real disclaimer: "Information,
    not advice. Namma Nyaya explains documents. It isn't a lawyer and can
    be wrong.")

## Creative Direction
- Tone preset: polished
- Creative direction: quiet, premium civic-tech film — a legal document
  brought to life, not a startup pitch
- Interpretation: fewer scenes (4), longer holds, confident restraint.
  Smooth crossfades/slides only — no hard cuts, no flashes, no chaotic
  motion. Typography and real UI carry the video; color stays warm and
  paper-toned.
- Angle: built for one specific moment — a newcomer to Bengaluru, PDF in
  hand, about to sign something they don't fully understand. The video
  shows that moment getting defused: upload, red flag caught, explained in
  the language the viewer actually thinks in.
- Hook: the real hero headline slams onto a cream page in serif display
  type: "Understand your rental agreement before you sign it." — no logo
  yet, just the sentence.
- Outro / punchline: the bilingual wordmark locks ("Namma Nyaya" /
  "ನಮ್ಮ ನ್ಯಾಯ") under the app's own honest disclaimer line, adapted:
  "Information, not advice. But information you can finally read."
- Avoid:
  - Generic SaaS language ("streamline your workflow", etc.)
  - Abstract filler visuals (no stock gavels, scales-of-justice icons, or
    generic "AI brain" graphics)
  - Unrelated visual redesign — stay inside the project's real cream/serif
    editorial palette, don't invent a glossy tech look

## Visual Identity
- Background: `#f5f3ee` (warm cream); card surface `#fffdf9`;
  soft surface `#efece4`; borders `#e3ded3` / `#d9d3c6` / `#bdb5a4`
- Text: `#1d1b17` (ink), secondary `#4f4a41`, muted `#5f5a50`, faint `#6b665b`
- Accent: `#8c2f27` (danger/red-flag) on `#fbe9e6` bg; `#2f6b46` (ok/trust)
  on `#e4efe4` bg; warning `#6b5417` on `#f6efd8` bg
- Display font: Source Serif 4 (headlines/wordmark) — Georgia/serif fallback
- Body font: Public Sans — system-ui/sans-serif fallback
- Mono accent font: IBM Plex Mono (labels, badges, citations)
- Kannada font: Noto Sans Kannada (wordmark's Kannada line, KN toggle result)
- Visual references from the project:
  - Upload card: dashed border, circular upload icon button, "Drop a file"
    copy (`.upload-card`, `.upload-icon-btn` in `app/globals.css`)
  - Red-flag card: `border-left: 4px solid #8c2f27`, `background: #fbe9e6`,
    rounded corners, severity badge pill (`.red-flag`, `.severity-badge`,
    `.severity-high` in `app/globals.css`)
  - EN/KN language toggle: pill-shaped two-segment toggle
    (`.lang-toggle`, `.lang-toggle-btn` in `app/globals.css`)
  - Bilingual brand lockup: "Namma Nyaya" (serif) + "ನಮ್ಮ ನ್ಯಾಯ" (Kannada,
    faint) as seen in `TopNav.tsx`'s `.brand-name` / `.brand-kannada`

## Storyboard
Use the storyboard in `brag-output/brag-plan.md` as the creative contract.

Scene summary:
1. Hook — 3.0s — hero headline "Understand your rental agreement before you
   sign it." settles fully on cream background before transitioning.
2. Upload & red flag — 6.5s — simulated PDF drag-drop onto the upload card,
   then clause text fills the document panel, then the red-flag card
   ("SECURITY DEPOSIT", high severity, citation) slides in as one
   deliberate arrival.
3. Bilingual explanation — 5.0s — simulated click on the KN segment of the
   language toggle; explanation text cross-dissolves from English to
   Kannada (Noto Sans Kannada), with ನಮ್ಮ ನ್ಯಾಯ visible as a small aside.
4. Outro / wordmark — 4.0s — cream background returns; "Namma Nyaya" over
   "ನಮ್ಮ ನ್ಯಾಯ" locks center frame with the adapted disclaimer line beneath
   it in small type; hold the final ~1.5s.

## Audio
- Audio role: sparse professional accents over a steady, clean bed
- Audio arc: bed fades in under the hook at low volume (~0.3), stays
  unobtrusive through the flow, small swell into the outro lock, fades to
  silence by the final hold
- Music: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`
- Music treatment: volume ~0.3 throughout, fade-in over the first ~0.5s,
  gentle swell approaching the outro lock, fade-out over the last ~1s
- Music cue guidance: bundled preset at
  `brag-output/composition/assets/music/cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json`
  (also `.md`). Tempo ~109.96 BPM. Target strong cues near 8.74s (red-flag
  card lands in Scene 2), 13.11s (language toggle click in Scene 3), and
  17.47s/18.56s (wordmark lock in Scene 4). These are timing hints — shift
  by up to ±0.15s to fit the actual animation, and skip if it hurts
  readability or pacing.
- Audio-reactive treatment: subtle; the cream background or card panel may
  gain a faint warmth/presence that breathes with RMS. No
  waveform/equalizer visuals, no pulsing text, no strobing.
- Audio-coupled moments:
  - Scene 2, red-flag card arrival — soft drop/thud SFX at the card's
    landing, timed near the 8.74s strong cue
  - Scene 3, language toggle click — clean switch/click SFX at the tap,
    timed near the 13.11s strong cue
  - Scene 4, wordmark lock — single soft bell/impact SFX at full settle,
    timed near the 17.47s/18.56s strong cues
- SFX selection guidance: match the gesture — a card-style arrival for the
  red-flag card, a toggle/switch sound for the language click, a gentle
  bell or soft impact (not a heavy hit) for the wordmark lock. Keep the
  total SFX count to 2-3; this is a trust product, so sound should feel
  calm and exact, not hyped.
- SFX analysis guidance: read `sfx-analysis.md` in the SFX library and
  prefer low/medium high-frequency-risk files, since these are polished,
  repeated-feeling moments rather than isolated chaotic accents.
- Exact SFX choice: Hyperframes should choose filenames, timestamps,
  density, and volume based on the implemented animation.
- Audio files: copy the chosen music into
  `brag-output/composition/assets/music/`; copy any Hyperframes-selected
  SFX into `brag-output/composition/assets/sfx/`.

## Hyperframes Instructions
Load the composition-building Hyperframes domain skills — `hyperframes-core`
(composition contract + `data-*` timing), `hyperframes-animation` (motion),
`hyperframes-creative` (design spec, beats, audio-reactive),
`hyperframes-keyframes` (seek-safe keyframes), and `hyperframes-cli`
(lint/check/render). `/brag` is its own workflow: do not enter the
`hyperframes` entry-point intent interview and do not route into its
generic promo / launch-video workflow. Prefer native Hyperframes
conventions over anything in `/brag`.

Requirements:
- Show at least one real UI, copy, or visual element from the source
  project (the upload card, the red-flag card, and the language toggle all
  qualify — use all three, they are the centerpiece).
- Keep all text readable in the final render — this is a polished-tone
  video, hold every readable line to at least its reading-time floor.
- Keep the video within 15-25 seconds (target 18-19s).
- Include the planned music/SFX layer.
- Treat `/brag` audio notes as guidance, not a fixed cue sheet. Choose SFX
  after the visual animation exists.
- Treat music cue metadata as optional timing hints; ignore cues that hurt
  readability, scene pacing, or the product story. Use only 1-3 strong cue
  locks in this 18-19s video.
- Use SFX to support motion and interaction, with restraint appropriate to
  the polished tone.
- Honor the planned music treatment (fade-in, low sustained volume, swell
  into outro, fade-out).
- Consider the Hyperframes audio-reactive workflow for a subtle
  RMS-driven warmth/presence effect on the background or card panel. Avoid
  waveform/equalizer visuals, musical-note graphics, particle systems,
  strobing, or heavy pulsing.
- Use local assets for audio and any required runtime/media dependencies.
- Run `hyperframes check` before render — it is brag's single gate.
