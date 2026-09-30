"""Starter project: a 6-second tour of the building blocks. Copy this folder to start a new video:
    cp -r projects/_template projects/my_idea
then edit scenes.py, preview a few frames, and render.

Rules of thumb (see docs/STYLE.md): cards snap in with pop(), settle with wob(), group items
stagger 3 frames, headlines slam(), every camera move ends in a full stop of 12+ frames."""
import math
from PIL import Image, ImageDraw
from motion.core import *

FRAMES = 180          # 6 s at 30 fps
AUDIO = None          # e.g. 'voice_cleaned.m4a' (put it in this folder)

CODE = 'ask(sensor, { question: Boolean })'

def card_c(dd, x0, y0, x1, y1, s):
    mlabel(dd, x0 + 30 * s, y0 + 44 * s, s, "01  /  EXAMPLE CARD", INK, 18)
    tx(dd, x0 + 30 * s, y1 - 44 * s, s, "Cards snap in", HEAD, 46, INK)
    ic_route(dd, x1 - 100 * s, (y0 + y1) / 2, s, CARD)

def render(f):
    if f >= 150:                                   # hard cut to the end card
        fr = Image.new('RGB', (W, H), VIO); df = f - 150
        t = e_back(df / 20, 1.4)
        put(fr, draw_mesh(mesh('spark', spark_mesh), rotm(lerp(.5, .06, t), lerp(2.2, .12, t), .1), 230, shadow=12), 540, 880, pop(df, 12, .6, 1.05))
        put(fr, spr('lv', lambda: text_ss("LANVAR.AI", MONO, 32, CARD, track=.14), 0), 540, 1220, pop(df - 8))
        return fr
    fr = paper(); d = ImageDraw.Draw(fr)
    put(fr, spr('title', lambda: text_ss("YOUR IDEA", HEAD, 120, VIO), -2), 540, 360, slam(f - 4))
    put(fr, spr('sub', lambda: pill_ss("THINKING OUT LOUD", CARD, INK, 22, track=.14, dot=TAN), 1.5 + wob(f - 14)), 540, 500, pop(f - 14))
    put(fr, spr('card', lambda: card_ss(880, 200, content=card_c), -1.5 + wob(f - 28)), 540, 720, pop(f - 28))
    if f >= 50:                                    # messy multi-channel data that cleans itself up
        st = smix(RAW, BAND, ss((f - 80) / 12))
        draw_signal(fr, 540, 980, st, f)
    if f >= 96:                                    # flat-shaded 3D object
        put(fr, draw_mesh(mesh('cube', cube_mesh), rotm(.42, .62 + (f - 96) * .04), 120, shadow=6), 540, 1250, pop(f - 96, 12, .5, 1.06))
    if f >= 118:                                   # code types on, answer snaps
        n = int(clamp((f - 118) / 0.6, 0, len(CODE)))
        tx(d, 110, 1520, 1, CODE[:n], MONO, 34, INK)
        if n == len(CODE):
            put(fr, spr('ans', lambda: pill_ss("true   p 0.93", VIO, CARD, 30), -2 + wob(f - 118 - int(len(CODE) * .6) - 4)), 540, 1610,
                pop(f - 118 - int(len(CODE) * .6) - 4))
    return fr
