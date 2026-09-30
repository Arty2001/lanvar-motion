# Lanvar motion style

## Look: flat paper, not dark-mode neon
- Ground: chalk paper `#F3F2EC`, flat, with a faint dot grid. Never black, never a gradient.
- Cards: `#FBFAF6` face, 2 px `#221D33` border, 6 px HARD offset shadow down-right. No soft shadows, glow or blur.
- Accents: violet `#5B3DF5`, tangerine `#FF6320`, pink `#F6A8DE`. Ink `#221D33`.
- Corners: 18 px on cards, fully round on pills and stamps.
- Rotation: cards and stamps sit between -3° and +2°, never square to the frame.
- Type: Unbounded 700 for headlines and card titles; Spline Sans Mono 600 uppercase, 0.14em tracking, for labels.
- Code: mono, ink on card, violet for values.
- 3D: flat-shaded faces, ink outlines, the same hard shadow as cards. No lights, specular or blur.
- Grain: ~5% fractal noise over everything, new every frame.

## Motion rules (these matter more than the shapes)
- Every camera move ends in a full stop of 12+ frames.
- Cards snap in with overshoot: `pop()` (0.92 → 1.03 → 1.0 over 12 frames), then `wob()` settles the rotation. Never a linear fade.
- Grouped elements stagger 3 frames apart; never arrive together.
- Headlines `slam()` in (1.4 → 0.96 → 1.0 over 8 frames).
- Data morphs continuously between states (10–14 frames per step), never swaps.
- Hard cuts between beats are good.
- Code types on character by character; answers snap in.
- No motion blur, so never speed-ramp the finished clip. Change frame numbers and re-render.

## Layout
- Keep important content between y = 200 and y = 1560: platform UI covers the top and the bottom ~360 px.
- Right edge ~120 px is under the like/comment buttons on Reels and TikTok.
- A frame should never sit empty while the voice is talking about something; give every sentence a visual.
