# lanvar-motion

Code-driven motion graphics for lanvar.ai shorts. Every frame is drawn in Python, so text stays sharp,
geometry never drifts, and a whole video can be retimed to a voiceover by changing a few frame numbers.

It produces 1080x1920, 30 fps vertical video in the Lanvar look: flat chalk paper, hard offset shadows,
violet / tangerine / pink accents, snappy overshoot motion, and flat-shaded 3D objects.

## Setup

```
pip install -r requirements.txt       # Pillow + NumPy
# ffmpeg must be on your PATH (brew install ffmpeg / apt install ffmpeg)
```

Fonts: drop `Unbounded-Bold.ttf` and `SplineSansMono-SemiBold.ttf` (free on Google Fonts) into `fonts/`.
Without them it falls back to DejaVu / Arial / Menlo, which works but looks less on-brand.

Run everything from the repo root.

## Making a new video

1. **Write the script** in `projects/<idea>/script.txt`. Keep it spoken, short sentences, ~2.5–4 words per second.
2. **Record it** in one take (phone voice memo is fine), small pauses between sentences.
3. **Clean the voice** (trim the first/last seconds of silence with START END):
   ```
   python -m motion.audio clean raw_take.m4a projects/<idea>/voice_cleaned.wav 0.8 63.2
   ```
   Result: mono-centered, de-noised, de-essed, compressed, -14 LUFS (Reels / TikTok loudness).
4. **Find your cue times**:
   ```
   python -m motion.audio segments projects/<idea>/voice_cleaned.wav
   ```
   This lists every stretch of speech with its start/end frame and a syllable estimate. Match each
   one to a line of your script (syllable counts line up at ~70–80%), and write the mapping down in
   `cues.md`. Those frame numbers are your animation cues.
5. **Start from the template**:
   ```
   cp -r projects/_template projects/<idea>
   ```
   Set `FRAMES` (voice length + ending, x30) and `AUDIO`, then build scenes in `scenes.py`
   using the cue frames. `projects/jev_short/scenes.py` is a complete real example.
6. **Preview stills** while you work (seconds, not minutes):
   ```
   python -m motion.render projects/<idea> preview 0 120 450 900
   ```
   Opens nothing; writes PNGs + `out/contact_sheet.png`.
7. **Render the final**:
   ```
   python -m motion.render projects/<idea> final
   ```
   Writes `out/final.mp4` (CRF 18 master with voice) and `out/final_preview.mp4` (small, for your phone).
   Speed is roughly 2–3 frames per second per CPU core, so a 60 s video takes ~15 minutes.

## What's in the toolkit (`motion/core.py`)

| Area | Functions |
|---|---|
| Easing | `ss`, `e_out`, `e_in`, `e_io`, `e_io5`, `e_back`, `lerp`, `clamp` |
| Motion | `pop(df)` overshoot snap 0.92→1.03→1, `slam(df)` headline 1.4→0.96→1, `wob(df)` rotation settle |
| Drawing | `card_ss` card with border + hard shadow, `pill_ss`, `text_ss`, `tx` text with tracking, `mlabel` mono label |
| Placement | `spr(key, builder, rot)` cached rotated sprite, `put(frame, sprite, x, y, scale)`, `rot_off` |
| Background | `paper(zoom, cx, cy)` chalk paper with a dot grid that moves with the camera |
| Icons | `ic_eeg ic_watch ic_camera ic_motion ic_band ic_filter ic_bars ic_step ic_dial ic_browser ic_route ic_shield` |
| Data | `draw_signal(frame, x, y, state, t)` thin multi-channel lines; states `RAW BAND FFT THR CAL DOTS`, blend with `smix` |
| 3D | `draw_mesh(mesh, rotm(ax, ay, az), scale)` flat-shaded, ink-outlined, hard shadow; meshes `cube_mesh rock_mesh chip_mesh spark_mesh`, build your own with `box_faces` / `Mesh` |
| Effects | `impact_ticks`, `grain` (applied automatically at render) |
| Timing | `T(seconds)` voice time → frame |

The palette constants are `PAPER CARD INK VIO TAN PINK MUTE DOT SCOPE`. See `docs/STYLE.md` for the rules.

## Projects

- `projects/_template/`: 6-second tour of the building blocks. Copy it to start.
- `projects/jev_short/`: the Jev hardware short, fully timed to the recorded voice (`script.txt`, `cues.md`).
