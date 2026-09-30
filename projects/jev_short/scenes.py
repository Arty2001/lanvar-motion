"""Jev hardware short (lanvar.ai): 64 s, 1080x1920, 30 fps.
Every cue is a frame number measured from the cleaned voice track (see cues.md).
Render with:  python -m motion.render projects/jev_short final"""
import math
import numpy as np
from PIL import Image, ImageDraw
from motion.core import *
from motion import core

FRAMES = 1922
AUDIO = 'voice_cleaned.m4a'

# ================================================================== BEAT 1 — hook (0-299)
POSTS = [("Maya R.", "@mayabuilds", "jev is actually", "absurdly fast", VIO), ("Dev Patel", "@agentsmith", "replaced our whole", "router with jev", TAN),
         ("Kat Oyelaran", "@mlops_kat", "jev + browser agent", "= unfair advantage", PINK), ("Sam Q.", "@buildfast", "wait. jev did", "that in 9 ms??", VIO),
         ("Tiny GPU", "@tinygpu", "everyone is", "sleeping on jev", TAN), ("Noor", "@shipit", "ok jev is", "the real deal", PINK),
         ("Eval Goblin", "@evalgoblin", "ran the evals.", "jev wins. again.", VIO), ("Leo M.", "@nightshift", "can't stop", "building with jev", TAN)]

def ic_reply(d, x, y, s):
    d.rounded_rectangle([x, y - 16 * s, x + 24 * s, y + 2 * s], 7 * s, outline=MUTE, width=max(1, int(2 * s)))
    d.polygon([(x + 5 * s, y + 1 * s), (x + 5 * s, y + 8 * s), (x + 12 * s, y + 1 * s)], fill=MUTE)
def ic_views(d, x, y, s):
    for k, h in enumerate([8, 16, 12]): d.rectangle([x + k * 8 * s, y - h * s, x + (k * 8 + 4) * s, y], fill=MUTE)

def x_post_c(name, handle, a, b, col, m, embed=None):
    def c(d, x0, y0, x1, y1, s):
        d.ellipse([x0 + 24 * s, y0 + 22 * s, x0 + 80 * s, y0 + 78 * s], fill=col, outline=INK, width=max(1, int(2 * s)))
        tx(d, x0 + 52 * s, y0 + 51 * s, s, name[0], HEAD, 26, CARD if col == VIO else INK, anchor='mm')
        nw = tx(d, x0 + 96 * s, y0 + 46 * s, s, name, HEAD, 22, INK)
        bx = x0 + 96 * s + nw + 16 * s
        d.ellipse([bx - 11 * s, y0 + 27 * s, bx + 11 * s, y0 + 49 * s], fill=VIO)
        tx(d, bx, y0 + 38 * s, s, "✓", HEAD, 14, CARD, anchor='mm')
        mlabel(d, x0 + 96 * s, y0 + 72 * s, s, handle + " · 2h", MUTE, 15)
        tx(d, x1 - 26 * s, y0 + 40 * s, s, "···", HEAD, 22, MUTE, anchor='rs')
        tx(d, x0 + 26 * s, y0 + 124 * s, s, a, HEAD, 30, INK); tx(d, x0 + 26 * s, y0 + 164 * s, s, b, HEAD, 30, INK)
        if embed is not None:
            ex0, ey0, ex1, ey1 = x0 + 26 * s, y0 + 188 * s, x1 - 26 * s, y1 - 58 * s
            d.rounded_rectangle([ex0, ey0, ex1, ey1], 14 * s, fill=SCOPE, outline=INK, width=max(1, int(2 * s)))
            for k, line in enumerate(LOGS[embed % 3][:3]):
                tx(d, ex0 + 18 * s, ey0 + (38 + k * 36) * s, s, line, MONO, 20, VIO if line[0] in '✓→' else TAN)
            mlabel(d, ex1 - 16 * s, ey1 - 14 * s, s, "%d MS" % (7 + embed * 3), MUTE, 14, anchor='rs')
        fy = y1 - 22 * s
        ic_reply(d, x0 + 26 * s, fy, s); mlabel(d, x0 + 58 * s, fy, s, m[0], MUTE, 15)
        tx(d, x0 + 142 * s, fy, s, "⇄", HEAD, 22, MUTE); mlabel(d, x0 + 172 * s, fy, s, m[1], MUTE, 15)
        tx(d, x0 + 262 * s, fy, s, "♥", HEAD, 22, TAN); mlabel(d, x0 + 290 * s, fy, s, m[2], TAN, 15)
        ic_views(d, x0 + 386 * s, fy, s); mlabel(d, x0 + 418 * s, fy, s, m[3], MUTE, 15)
    return c

BENCH = [("TOKENS / SEC", [("JEV", 1.0, "4,812"), ("PREV SOTA", .34, "1,630"), ("BASELINE", .18, "870")]),
         ("MS / DECISION", [("JEV", .12, "9"), ("PREV SOTA", .55, "41"), ("BASELINE", 1.0, "76")]),
         ("ROUTING ACC.", [("JEV", .97, "97.4%"), ("PREV SOTA", .88, "88.1%"), ("BASELINE", .71, "71.0%")])]
def bench_c(title, rows):
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 26 * s, y0 + 42 * s, s, title, INK, 18)
        mlabel(d, x1 - 26 * s, y0 + 42 * s, s, "BENCH", TAN, 16, anchor='rs')
        for i, (n, v, lab) in enumerate(rows):
            y = y0 + (76 + i * 62) * s
            mlabel(d, x0 + 26 * s, y + 18 * s, s, n, INK if i == 0 else MUTE, 15)
            bx = x0 + 150 * s; bw = (x1 - 110 * s - bx) * v
            d.rounded_rectangle([bx, y, bx + max(bw, 10 * s), y + 26 * s], 6 * s, fill=VIO if i == 0 else CARD, outline=INK, width=max(1, int(2 * s)))
            tx(d, x1 - 24 * s, y + 21 * s, s, lab, MONO, 17, VIO if i == 0 else INK, anchor='rs')
    return c

PRICES = [("$0.03", "PER 1M TOKENS", "-81%"), ("$0.00", "TO SELF-HOST", "OPEN"), ("22×", "FASTER THAN LAST YEAR", "WILD")]
def price_c(big, lab, stamp):
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 26 * s, y0 + 42 * s, s, lab, INK, 16)
        tx(d, x0 + 24 * s, y1 - 36 * s, s, big, HEAD, 74, VIO)
        sw = tw(stamp, MONO, 18 * s, .14) + 30 * s
        d.rounded_rectangle([x1 - 24 * s - sw, y1 - 74 * s, x1 - 24 * s, y1 - 36 * s], 99 * s, fill=TAN, outline=INK, width=max(1, int(2 * s)))
        mlabel(d, x1 - 24 * s - sw / 2, y1 - 55 * s, s, stamp, INK, 18, anchor='mm')
    return c

LOGS = [["✓ open  checkout", "✓ fill  address", "✓ pay   ····4417"], ["→ route  billing", "→ route  refunds", "→ route  tech"],
        ["✓ allow  msg 2,041", "✕ block  msg 2,042", "✓ allow  msg 2,043"]]

def jev_c(size, sub=None):
    def c(d, x0, y0, x1, y1, s):
        tx(d, (x0 + x1) / 2, (y0 + y1) / 2 + (14 * s if sub else 0), s, "JEV", HEAD, size, CARD, anchor='mm')
        if sub: mlabel(d, (x0 + x1) / 2, y0 + 50 * s, s, sub, CARD, 18, anchor='mm')
    return c

RL, DROP1 = 146, 160          # rock lands (= the hard stop), then everything drops
B1 = []
def build_b1():
    r = np.random.RandomState(11)
    B1.append(dict(key='jev', t=4, tx=540, ty=900, dx=0, dy=-1, jev=True, rot=-2,
                   b=lambda: card_ss(620, 340, face=VIO, content=jev_c(160, "TRENDING  ·  #1"))))
    t, iv, k = 14.0, 11.0, 0
    kinds = ['post', 'bench', 'post', 'embed', 'price', 'post']
    while t < RL - 4:
        kind = kinds[k % 6]; rot = round(r.uniform(-3, 2) * 4) / 4
        m = ("%d" % r.randint(12, 400), "%.1fK" % r.uniform(.3, 9), "%.1fK" % r.uniform(2, 60), "%dK" % r.randint(40, 900))
        if kind in ('post', 'embed'):
            p = POSTS[k % 8]
            b = (lambda p=p, m=m, e=(k if kind == 'embed' else None): card_ss(540, 410 if e is not None else 250, content=x_post_c(*p, m, e)))
        elif kind == 'bench':
            bb = BENCH[(k // 6) % 3]; b = (lambda bb=bb: card_ss(500, 260, content=bench_c(*bb)))
        else:
            pp = PRICES[(k // 6) % 3]; face = [CARD, PINK, CARD][(k // 6) % 3]
            b = (lambda pp=pp, face=face: card_ss(420, 210, face=face, content=price_c(*pp)))
        dx, dy = [(-1, 0), (1, 0), (0, -1), (0, 1)][r.randint(4)]
        B1.append(dict(key='c%d' % k, t=int(t), tx=r.uniform(240, 940), ty=r.uniform(300, 1540), dx=dx, dy=dy, jev=False,
                       rot=rot, b=b, j=r.uniform(-340, 340)))
        t += iv; iv = max(2.0, iv * 0.87); k += 1

def rock_state(f):
    """position, scale-x, scale-y, rotation for the falling rock"""
    R0 = 125
    if f < R0: return None
    if f < RL:
        t = (f - R0) / (RL - R0)
        return 560, lerp(-420, 1180, t * t), 1.0, 1.0, rotm(.25 + .9 * (1 - t), .4 + 2.4 * (1 - t), .35 * (1 - t))
    df = f - RL
    sq = 0.17 * math.exp(-df / 3.0) * math.cos(df * 0.85)
    y = 1180 + (e_in((f - DROP1 - 4) / 14) * 2400 if f >= DROP1 + 4 else 0)
    return 560, y, 1 + sq * .6, 1 - sq, rotm(.25, .4, 0)

def beat1(f):
    z = lerp(1.0, 1.07, e_io5(clamp(f / 120)))
    fr = paper(z); d = ImageDraw.Draw(fr)
    fe = min(f, RL)
    jolt = 22 * math.exp(-(f - RL) / 3.0) * abs(math.cos((f - RL) * 1.2)) if RL <= f < RL + 16 else 0
    for i, c in enumerate(B1):
        df = fe - c['t']
        if df < 0: continue
        fl = 8; p = e_back(df / fl, 1.4)
        jx = c.get('j', 0) * (1 - p) if c['dy'] else 0
        jy = c.get('j', 0) * (1 - p) if c['dx'] else 0
        x = c['tx'] - c['dx'] * 1300 * (1 - p) + jx; y = c['ty'] - c['dy'] * 1500 * (1 - p) + jy + jolt * (0.4 + 0.6 * (c['ty'] > 900))
        sc = pop(df - fl) if df >= fl else 0.92
        rot = c['rot']
        if c['jev']:
            if f >= DROP1 + 12:
                sc = pop(f - DROP1 - 12, 12, 1.0, 1.2) * 1.14 if f - DROP1 - 12 < 12 else 1.14
                rot = c['rot'] + wob(f - DROP1 - 12, 2.0)
        elif f >= DROP1:
            y += e_in((f - DROP1 - (i % 4)) / 9) * 2300
        put(fr, spr(c['key'], c['b'], rot), 540 + (x - 540) * z, 960 + (y - 960) * z, sc * z)
    rs = rock_state(f)
    if rs:
        x, y, sx_, sy_, R = rs
        im = draw_mesh(mesh('rock', rock_mesh), R, 290, sx_, sy_, shadow=8, outline=1.5)
        put(fr, im, 540 + (x - 540) * z, 960 + (y - 960) * z, z)

    return fr

# ================================================================== BEAT 2/3 — setup + turn (300-809)
B2 = [(228, 700, "BROWSER AGENTS", VIO, "01", -1.5, ic_browser, "CLICKS · FORMS · CHECKOUTS"),
      (280, 960, "AGENT ROUTING", TAN, "02", 1.25, ic_route, "ONE CALL → RIGHT AGENT"),
      (319, 1220, "CONTENT MODERATION", PINK, "03", -2.25, ic_shield, "ALLOW · FLAG · BLOCK")]
FOLD, CUBE0, CAM0, CAM1, SLIDE, HW = 406, 416, 420, 438, 9999, 521
CHECKS = 380; ZEND = 0.6; CHIP0 = HW + 18

def setup_c(title, face, num, icon, meta):
    tcol = CARD if face == VIO else INK
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 30 * s, y0 + 44 * s, s, num + "  /  USE CASE", tcol, 18)
        tx(d, x0 + 30 * s, y1 - 78 * s, s, title, HEAD, 50 if len(title) < 16 else 42, tcol)
        mlabel(d, x0 + 30 * s, y1 - 34 * s, s, meta, tcol, 16)
        icon(d, x1 - 100 * s, (y0 + y1) / 2 - 10 * s, s, CARD)
    return c

def reveal_path(d, pts, frac, col=INK, width=3):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs); rem = L * clamp(frac)
    for a, b in segs:
        l = math.hypot(b[0] - a[0], b[1] - a[1])
        if rem <= 0: break
        t = min(1, rem / l); d.line([a, (lerp(a[0], b[0], t), lerp(a[1], b[1], t))], fill=col, width=width); rem -= l

HWX = []
def hw_letters():
    if HWX: return HWX
    f = F(HEAD, 150); word = "HARDWARE"; total = f.getlength(word); x = 540 - total / 2
    for ch in word:
        w = f.getlength(ch); HWX.append((ch, x + w / 2)); x += w
    return HWX

MORPH0, MORPH1 = 449, 513
CUBECOL = {'+z': VIO, '+x': TAN, '+y': CARD, '-x': PINK, '-z': PINK, '-y': TAN}
def colmix(a, b, t): return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))
def chip_morph(t):
    e = ss(t)
    f = box_faces((0, 0, 0), (1.0, lerp(1, .09, e), lerp(1, .72, e)), {k: colmix(c, CARD, e) for k, c in CUBECOL.items()})
    h = .07 * ss((e - .45) / .55)
    if h > .004:
        f += box_faces((0, .09 + h, 0), (.42 * ss((e - .45) / .55) + .01, h, .32 * ss((e - .45) / .55) + .01), {'*': VIO})
        f += box_faces((.72, .09 + h * .6, .48), (.08, h * .6, .08), {'*': TAN})
    p = ss((e - .6) / .4)
    if p > .02:
        for i in range(6):
            x = -.75 + i * .3
            for z in (.84, -.84): f += box_faces((x, -.03, z * lerp(.72, 1, p)), (.06 * p, .03, .12 * p), {'*': (205, 200, 214)})
    return Mesh(f)

HWT = [("EEG", ic_eeg, 170, 1330), ("WATCH", ic_watch, 400, 1400), ("CAMERA", ic_camera, 680, 1400), ("MOTION", ic_motion, 910, 1330)]
def hw_tile(k):
    lab, icon = HWT[k][0], HWT[k][1]
    def c(d, x0, y0, x1, y1, s):
        icon(d, (x0 + x1) / 2, y0 + 56 * s, s * .82, VIO)
        mlabel(d, (x0 + x1) / 2, y1 - 20 * s, s, lab, INK, 14, anchor='ms')
    return card_ss(150, 132, radius=16, shadow=5, content=c)

def beat23(f):
    if f < MORPH0: zoom = lerp(1.0, ZEND, e_io5((f - CAM0) / (CAM1 - CAM0)))
    else: zoom = lerp(ZEND, 1.0, e_io5((f - MORPH0) / (MORPH1 - MORPH0 - 10)))
    fr = paper(zoom) if f >= CAM0 else paper()
    d = ImageDraw.Draw(fr)
    if f < FOLD + 12:
        fp = e_in((f - FOLD) / 12) if f >= FOLD else 0
        def mv(x, y, s_): return lerp(x, 540, fp), lerp(y, 960, fp), (s_ * lerp(1, .15, fp) if s_ else s_)
        if fp == 0:
            for t0, y0, *_ in B2:
                reveal_path(d, [(540, 415), (540, 470), (66, 470), (66, y0), (100, y0)], (f - (t0 - 12)) / 10)
                if f >= t0: d.ellipse([58, y0 - 8, 74, y0 + 8], fill=VIO, outline=INK, width=2)
        x, y, s_ = mv(540, 330, pop(f - 191))
        put(fr, spr('b2hdr', lambda: card_ss(400, 170, face=VIO, content=jev_c(96)), -2 + wob(f - 191)), x, y, s_)
        for t0, y0, title, face, num, rot, icon, meta in B2:
            im = spr(('b2', num), lambda title=title, face=face, num=num, icon=icon, meta=meta:
                     card_ss(880, 220, face=face, content=setup_c(title, face, num, icon, meta)), rot + wob(f - t0))
            x, y, s_ = mv(560, y0, pop(f - t0)); put(fr, im, x, y, s_)
            if f >= CHECKS and fp == 0:
                i = int(num) - 1
                ck = spr('check', lambda: card_ss(64, 64, face=CARD, radius=999, shadow=4,
                                                  content=lambda dd, a, b, c_, e, s: tx(dd, (a + c_) / 2, (b + e) / 2, s, "✓", HEAD, 34, VIO, anchor='mm')), 0)
                ox, oy = rot_off(400, -96, rot); put(fr, ck, 560 + ox, y0 + oy, pop(f - CHECKS - 3 * i, 10, .6, 1.12))
    # connectors from the chip out to the sensors it will become (behind everything)
    if f >= HW + 8:
        for k, (lab, icon, tx_, ty_) in enumerate(HWT):
            reveal_path(d, [(540, 1100), (540, 1230), (tx_, 1230), (tx_, ty_ - 66)], (f - HW - 8 - 3 * k) / 10)
    if f >= CUBE0:
        mt = clamp((f - MORPH0) / (MORPH1 - MORPH0))
        if f < MORPH0:
            t = e_out((f - CUBE0) / 30); R = rotm(lerp(-.6, .42, t), lerp(.62 + 3.4, .62, t))
            m = mesh('cube', cube_mesh); ps = pop(f - CUBE0, 12, .5, 1.06) or 1
        else:
            e = e_io5(mt); R = rotm(lerp(.42, .5, e), .62 + 2 * math.pi * e)
            m = chip_morph(mt); ps = 1
        cy_ = 960 + (1000 - 960) * ss(mt)
        put(fr, draw_mesh(m, R, lerp(190, 250, ss(mt)) * zoom * ps, shadow=lerp(6, 7, mt)), 540, cy_)
        if CAM1 + 4 <= f < MORPH0 + 10:
            out = e_in((f - MORPH0) / 10) * 500 if f >= MORPH0 else 0
            b = 185 + 20 * (1 - e_out((f - CAM1 - 4) / 10)) + out; L = 34
            for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                px, py = 540 + sx * b, 960 + sy * b
                d.line([(px, py), (px - sx * L, py)], fill=INK, width=5); d.line([(px, py), (px, py - sy * L)], fill=INK, width=5)
        if CUBE0 + 6 <= f < MORPH0 + 22:
            ly = 1250 + (e_in((f - MORPH0 - 8) / 14) * 900 if f >= MORPH0 + 8 else 0)
            put(fr, spr('swlab', lambda: pill_ss("SOFTWARE", CARD, INK, 40, track=.14, dot=VIO), 1.5 + wob(f - CUBE0 - 6)), 540, ly, pop(f - CUBE0 - 6))
            if f >= MORPH0:   # strike it through before it falls
                w = 170 * e_out((f - MORPH0) / 6)
                d.line([(540 - w, ly - 2), (540 + w, ly + 4)], fill=TAN, width=8)
    if f >= HW:
        for i, (ch, x) in enumerate(hw_letters()):
            ox, oy = rot_off(x - 540, 0, -2)
            sc = slam(f - HW - 2 * i)
            if sc is None: continue
            drop_y = -60 * (1 - e_out((f - HW - 2 * i) / 5))
            put(fr, spr(('hwl', ch), lambda ch=ch: text_ss(ch, HEAD, 150, VIO), -2), 540 + ox, 560 + oy + drop_y, sc)
        impact_ticks(d, 540, 560, f - HW - 14, r0=440, n=12, rot=15, ey=0.3)
        for k, (lab, icon, tx_, ty_) in enumerate(HWT):
            dk = f - HW - 16 - 3 * k
            if dk >= 0: put(fr, spr(('hwt', k), lambda k=k: hw_tile(k), [-2, 1.5, -1, 2][k] + wob(dk)), tx_, ty_, pop(dk))
    return fr

# ================================================================== BEAT 4/5 — old way + flip (810-1679)
HX, HY = 540, 300
CY = [610, 790, 970, 1150]; TITLES = ["BANDPASS", "FFT", "THRESHOLD", "CALIBRATE"]; ROTS = [-1.25, 1.0, -1.75, .75]
ICONS = [ic_filter, ic_bars, ic_step, ic_dial]
PARAMS = [["0.5–40 HZ", "N = 1024", "τ = 0.62", "GAIN 1.14"], ["0.1–5 HZ", "N = 512", "τ = 0.40", "GAIN 0.87"], ["1–20 HZ", "N = 256", "τ = 0.91", "GAIN 1.32"]]
SIGY0, PILLY, CNTY, SCX = 480, 1300, 1440, 703
CW4, CH4 = 920, 150

def housing_c(slot_led):
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 28 * s, y0 + 42 * s, s, "SENSOR  ·  8 CH  ·  256 HZ", INK, 17)
        for i in range(3):
            cx = x1 - (40 + i * 28) * s; d.ellipse([cx - 8 * s, y0 + 26 * s, cx + 8 * s, y0 + 42 * s], fill=[VIO, TAN, PINK][i] if (i != 0 or slot_led) else CARD, outline=INK, width=max(1, int(2 * s)))
        mx = (x0 + x1) / 2; my = (y0 + y1) / 2 + 12 * s
        d.rounded_rectangle([mx - 124 * s, my - 48 * s, mx + 124 * s, my + 48 * s], 14 * s, fill=SCOPE, outline=INK, width=max(1, int(2 * s)))
        mlabel(d, mx, my + 6 * s, s, "EMPTY SLOT", DOT, 16, anchor='mm')
        for i in range(8):
            px = x0 + (44 + i * 72) * s; d.ellipse([px - 11 * s, y1 - 30 * s, px + 11 * s, y1 - 8 * s], fill=CARD, outline=INK, width=max(1, int(2 * s)))
            d.ellipse([px - 4 * s, y1 - 23 * s, px + 4 * s, y1 - 15 * s], fill=INK)
    return c

def stage_c(i, pi, active):
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 26 * s, y0 + 38 * s, s, "%02d" % (i + 1), TAN, 16)
        if active:
            d.ellipse([x0 + 64 * s, y0 + 25 * s, x0 + 78 * s, y0 + 39 * s], fill=VIO)
            mlabel(d, x0 + 86 * s, y0 + 38 * s, s, "RUNNING", VIO, 15)
        tx(d, x0 + 26 * s, y0 + 84 * s, s, TITLES[i], HEAD, 30, INK)
        mlabel(d, x0 + 26 * s, y0 + 118 * s, s, PARAMS[pi][i], MUTE, 17)
        sx0, sx1, sy0, sy1 = x0 + 330 * s, x1 - 22 * s, y0 + 18 * s, y1 - 18 * s
        d.rounded_rectangle([sx0, sy0, sx1, sy1], 12 * s, fill=SCOPE, outline=INK, width=max(1, int(2 * s)))
        for k in range(1, 6):
            gx = sx0 + (sx1 - sx0) * k / 6; d.line([(gx, sy0 + 6 * s), (gx, sy1 - 6 * s)], fill=DOT, width=max(1, int(2 * s)))
        d.line([(sx0 + 6 * s, (sy0 + sy1) / 2), (sx1 - 6 * s, (sy0 + sy1) / 2)], fill=DOT, width=max(1, int(2 * s)))
        ICONS[i](d, x0 + 265 * s, y0 + 78 * s, s * 0.62, VIO)
    return c


PAIN0 = -9999
def rattle(f, k):
    if not (PAIN0 <= f < PAIN0 + 22): return 0.0, 0.0
    a = 10 * math.exp(-(f - PAIN0) / 6.0)
    return a * math.sin((f - PAIN0) * 2.9 + k * 1.7), a * math.cos((f - PAIN0) * 3.3 + k)

def pain_c(fill):
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 34 * s, y0 + 48 * s, s, "INTEGRATION EXPERIENCE", INK, 18)
        tx(d, (x0 + x1) / 2, y0 + 128 * s, s, "PAIN IN THE ASS", HEAD, 62, INK, anchor='ms')
        bx0, bx1, by = x0 + 34 * s, x1 - 150 * s, y1 - 50 * s
        d.rounded_rectangle([bx0, by, bx1, by + 22 * s], 99 * s, fill=CARD, outline=INK, width=max(1, int(2 * s)))
        d.rounded_rectangle([bx0, by, bx0 + max(22 * s, (bx1 - bx0) * fill), by + 22 * s], 99 * s, fill=INK)
        mlabel(d, x1 - 34 * s, by + 19 * s, s, "%d%%" % round(fill * 110), INK, 20, anchor='rs')
    return c

def draw_pain(fr, f):
    if not (PAIN0 <= f < PAIN0 + 62): return
    d = ImageDraw.Draw(fr)
    impact_ticks(d, 540, 760, f - PAIN0 - 2, r0=440, n=14, rot=6, ey=0.4, col=INK)
    fill = round(e_out((f - PAIN0 - 3) / 14) * 10) / 10
    y = 760 + (e_in((f - PAIN0 - 48) / 12) * 1500 if f >= PAIN0 + 48 else 0)
    put(fr, spr(('pain', fill), lambda: card_ss(860, 250, face=TAN, radius=22, shadow=8, content=pain_c(fill)), -6 + wob(f - PAIN0, 2)), 540, y, slam(f - PAIN0))

PASSES = []
def build_passes():
    spec = [(642, 14, 29, 14, 16, 28, "focused: 0.87", 3, 45), (871, 5, 2, 6, 6, 6, "stressed: 0.12", 6, 90),
            (962, 4, 1, 5, 7, None, "fell: 0.99", 9, 135)]
    for (st, dr, wr, M, Hh, hold, val, mo, cost) in spec:
        t0 = st + dr + wr; arr = [t0 + i * (M + Hh) + M for i in range(4)]
        c0 = arr[3] + max(Hh, 6); d1 = c0 + 12 + M
        PASSES.append(dict(start=st, dr=dr, t0=t0, M=M, arr=arr, c0=c0, d1=d1, reset=(d1 + hold) if hold else None, val=val, mo=mo, cost=cost))

def pass_signal(p, f):
    if f < p['start'] or f >= p['d1']: return None
    st = dict(RAW)
    for ts, tgt in [(a, STAGES[i]) for i, a in enumerate(p['arr'])] + [(p['c0'], DOTS)]:
        if f < ts: break
        st = smix(st, tgt, ss((f - ts) / 12))
    if f < p['start'] + p['dr']:
        return st, 540, lerp(-200, SIGY0, e_back((f - p['start']) / p['dr'], 1.2))
    x, y = 540, SIGY0; px, py = 540, SIGY0
    for i, a in enumerate(p['arr']):
        if f >= a - p['M']:
            t = e_io((f - (a - p['M'])) / p['M']); x, y = lerp(px, SCX, t), lerp(py, CY[i] + 2, t)
        px, py = SCX, CY[i] + 2
    if f >= p['c0'] + 12:
        t = e_io((f - p['c0'] - 12) / p['M']); x, y = lerp(SCX, 540, t), lerp(py, PILLY, t)
    return st, x, y

WIPE0, JEV_IN, MOVE0, ASK0, ANS0 = 1018, 993, 1030, 1055, 1130

def wipe_put(fr, im, cx, cy, s, k, f):
    if f < WIPE0 + 3 * k: put(fr, im, cx, cy, s); return
    p = (f - WIPE0 - 3 * k) / 8
    if p >= 1.15 or s is None: return
    if s != 1: im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
    x = int(cx - im.width / 2); y = int(cy - im.height / 2); cut = int(clamp(p) * im.height)
    if cut < im.height:
        part = im.crop((0, cut, im.width, im.height)); fr.paste(part, (x, y + cut), part)
    if p < 1.1: ImageDraw.Draw(fr).rectangle([x + 10, y + cut - 24, x + im.width - 10, y + cut], fill=VIO)

def active_stage(f):
    for p in PASSES:
        if p['start'] <= f < p['c0'] + 12:
            cur = None
            for i, a in enumerate(p['arr']):
                if f >= a: cur = i
            return cur
    return None

def pass_index(f):
    idx = 0
    for i, p in enumerate(PASSES):
        if f >= p['start'] - 12: idx = i
    return idx

def beat45(f):
    fr = paper(); d = ImageDraw.Draw(fr)
    hy = HY + (e_io5((f - MOVE0) / 20) * (780 - HY) if f >= MOVE0 else 0)
    # flow spine behind the stack (visible in the gaps), wiped away with the stack
    if 637 <= f < WIPE0 + 22:
        top = 400 if f < WIPE0 else lerp(400, 1480, (f - WIPE0) / 22)
        grow = clamp((f - 637) / 16); bot = lerp(400, 1400, grow)
        y = top
        while y < bot:
            d.line([(540, y), (540, min(y + 12, bot))], fill=INK, width=3); y += 22
    seated = f >= JEV_IN + 10
    put(fr, spr(('hous', seated), lambda: card_ss(600, 200, content=housing_c(seated)), -1 + wob(f - 617, 1.6)), HX, hy, pop(f - 617))
    act = active_stage(f); pi = pass_index(f)
    resets = [p['reset'] for p in PASSES if p['reset'] and f >= p['reset']]
    for i in range(4):
        sc = pop(f - 625 - 3 * i); rot = ROTS[i] + wob(f - 625 - 3 * i)
        if resets:
            df = f - resets[-1] - 3 * i
            if 0 <= df < 14: sc = lerp(1.0, .93, ss(df / 4)) if df < 4 else pop(df - 4, 10); rot = ROTS[i] + wob(df, 1.8)
        im = spr(('stg', i, pi, act == i), lambda i=i, pi=pi, a=(act == i): card_ss(CW4, CH4, content=stage_c(i, pi, a)), rot)
        if sc is not None: wipe_put(fr, im, 540 + rattle(f, i)[0], CY[i] + rattle(f, i)[1], sc, i, f)
    for p in PASSES:
        sres = pass_signal(p, f)
        if sres and f < JEV_IN + 10: draw_signal(fr, sres[1], sres[2], sres[0], f)
        if f >= p['d1'] and p['d1'] < JEV_IN and (p['reset'] is None or f < p['reset'] + 12):
            im = spr(('val', p['val']), lambda p=p: pill_ss(p['val'], VIO, CARD, 38), -2 + wob(f - p['d1']))
            y = PILLY + (e_in((f - p['reset']) / 12) * 900 if p['reset'] and f >= p['reset'] else 0)
            wipe_put(fr, im, 540, y, pop(f - p['d1']), 4, f)
    if f >= 642:
        mo = cost = 0; n = 1; pm = pc = 0
        for i, p in enumerate(PASSES):
            if f >= p['start']:
                t = clamp((f - p['start']) / max(1, p['d1'] - p['start']))
                mo, cost, n = round(lerp(pm, p['mo'], t)), round(lerp(pc, p['cost'], t)), i + 1
            pm, pc = p['mo'], p['cost']
        txt = "PASS %02d  ·  %d MONTH%s  ·  $%dK" % (n, mo, "" if mo == 1 else "S", cost)
        wipe_put(fr, spr(('cnt', txt), lambda: pill_ss(txt, CARD, INK, 24, track=.14, dot=TAN), 1), 540, CNTY, pop(f - 642), 5, f)
    if f >= JEV_IN:
        df = f - JEV_IN
        if df <= 10: x = lerp(1400, 540, e_out(df / 10))
        elif df <= 13: x = lerp(540, 518, ss((df - 10) / 3))
        else: x = lerp(518, 540, ss((df - 13) / 2))
        put(fr, spr('chip', lambda: card_ss(226, 80, face=VIO, radius=12, shadow=0, content=jev_c(46)), -1), x, hy + 12)
        impact_ticks(d, 540, hy + 12, df - 10, r0=150, n=8)
    if f >= ASK0:
        df = f - ASK0
        q = spr('ask', lambda: pill_ss("ask({ focused: Boolean })", CARD, INK, 30), 1.5 + wob(df))
        if df < 30:
            put(fr, q, 540, 1110, pop(df))
            if df > 6: reveal_path(d, [(540, 1060), (540, hy + 110)], (df - 6) / 10, VIO, 3)
        elif df < 42:
            t = e_in((df - 30) / 12); put(fr, q, 540, lerp(1110, hy + 12, t), lerp(1, .3, t))
    if f >= ANS0:
        df = f - ANS0
        def ans_c(dd, x0, y0, x1, y1, s):
            mlabel(dd, x0 + 30 * s, y0 + 44 * s, s, "FOCUSED", CARD, 18)
            tx(dd, x0 + 30 * s, y0 + 112 * s, s, "true", HEAD, 56, CARD)
            mlabel(dd, x1 - 30 * s, y0 + 44 * s, s, "P 0.87", CARD, 22, anchor='rs')
            bx0, bx1, by = x0 + 30 * s, x1 - 30 * s, y1 - 40 * s
            dd.rounded_rectangle([bx0, by, bx1, by + 16 * s], 99 * s, fill=CARD, outline=INK, width=max(1, int(2 * s)))
            dd.rounded_rectangle([bx0, by, bx0 + (bx1 - bx0) * .87, by + 16 * s], 99 * s, fill=TAN, outline=INK, width=max(1, int(2 * s)))
        im = spr('ansc', lambda: card_ss(520, 200, face=VIO, content=ans_c), -2 + wob(df - 6))
        put(fr, im, 540, lerp(hy + 60, 1110, e_back(df / 9, 1.3)), pop(df - 6) if df >= 6 else .92)
    if f == JEV_IN + 10:
        fr = Image.blend(fr, Image.new('RGB', (W, H), WHITE), .9)
    return fr

# ================================================================== BEAT 6 — showcase (1635-2399)
B6, OUT6 = 1190, 1768
ROWS = [("EEG HEADSET", "8 CH · 256 HZ", [("ask(eeg, { focused: ", INK), ("Boolean", VIO), (" })", INK)], "true", .87),
        ("SMART WATCH", "PPG · HRV · 50 HZ", [("ask(watch, { stressed: ", INK), ("Boolean", VIO), (" })", INK)], "false", .12),
        ("CAMERA", "1080P · 30 FPS", [("ask(camera, { machine: ", INK), ('"running"', VIO), (" })", INK)], "running", .94),
        ("MOTION SENSOR", "IMU · 6-AXIS", [("ask(motion, { fell: ", INK), ("Boolean", VIO), (" })", INK)], "false", .99)]
RY = [430, 710, 990, 1270]; RROT = [-1.0, .75, -1.25, 1.0]; RW, RH = 1000, 250
RPOP = [1318, 1348, 1376, 1402]
MORE0 = 1424; MORE = ["ARMBAND", "MIC", "THERMAL", "LIDAR", "+ MORE"]
STAMP6, STAMPOFF = 1514, 1622; MONTHS = ["3 MONTHS", "4 MONTHS", "6 MONTHS", "2 MONTHS"]
TSTART = [1675, 1693, 1711, 1729]; TFPC = [.5, .45, .4, .35]
RLEN = [sum(len(t) for t, _ in r[2]) for r in ROWS]
TEND6 = [TSTART[i] + int(math.ceil(RLEN[i] * TFPC[i])) for i in range(4)]
RANS = [TEND6[i] + 6 for i in range(4)]
W2 = lambda s, v: max(1, int(v * s))

def row_c(i, n, cursor):
    name, spec, code, a, p = ROWS[i]
    def c(d, x0, y0, x1, y1, s):
        d.rounded_rectangle([x0 + 18 * s, y0 + 18 * s, x0 + 268 * s, y1 - 18 * s], 14 * s, fill=SCOPE, outline=INK, width=W2(s, 2))
        tx(d, x0 + 296 * s, y0 + 62 * s, s, name, HEAD, 30, INK)
        mlabel(d, x1 - 26 * s, y0 + 56 * s, s, spec, MUTE, 15, anchor='rs')
        d.line([(x0 + 296 * s, y0 + 84 * s), (x1 - 26 * s, y0 + 84 * s)], fill=DOT, width=W2(s, 2))
        f = F(MONO, 25 * s); x = x0 + 296 * s; y = y0 + 132 * s; left = n
        for t, col in code:
            seg = t[:max(0, left)]; left -= len(t)
            if seg: d.text((x, y), seg, font=f, fill=col, anchor='ls'); x += f.getlength(seg)
        if cursor: d.rectangle([x + 3 * s, y - 24 * s, x + 16 * s, y + 5 * s], fill=VIO)
    return c

def ans2(i, fill):
    a, p = ROWS[i][3], ROWS[i][4]
    fh = F(HEAD, 34 * SS); fm = F(MONO, 21 * SS)
    aw = fh.getlength("→ " + a); pw = fm.getlength("p %.2f" % p) + 40 * SS; bw = 150 * SS
    im = Image.new('RGBA', (int(aw + pw + bw + 90 * SS), int(70 * SS)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); cy = im.height / 2
    d.text((6 * SS, cy), "→ " + a, font=fh, fill=VIO, anchor='lm')
    px = 6 * SS + aw + 22 * SS; ph = 42 * SS
    d.rounded_rectangle([px + 4 * SS, cy - ph / 2 + 4 * SS, px + pw + 4 * SS, cy + ph / 2 + 4 * SS], ph / 2, fill=INK)
    d.rounded_rectangle([px, cy - ph / 2, px + pw, cy + ph / 2], ph / 2, fill=TAN, outline=INK, width=2 * SS)
    d.text((px + pw / 2, cy), "p %.2f" % p, font=fm, fill=INK, anchor='mm')
    bx = px + pw + 20 * SS
    d.rounded_rectangle([bx, cy - 8 * SS, bx + bw, cy + 8 * SS], 99 * SS, fill=CARD, outline=INK, width=2 * SS)
    d.rounded_rectangle([bx, cy - 8 * SS, bx + max(16 * SS, bw * p * fill), cy + 8 * SS], 99 * SS, fill=VIO, outline=INK, width=2 * SS)
    return im

# ---- sensor-in-use sketches (animated, drawn at SS into a 250x214 canvas)
def canvas(w, h):
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0)); return im, ImageDraw.Draw(im), w * SS / 2, h * SS / 2, SS

def sk_eeg(t):
    im, d, cx, cy, s = canvas(250, 214)
    d.ellipse([cx - 62 * s, cy - 40 * s, cx + 56 * s, cy + 78 * s], fill=PINK, outline=INK, width=W2(s, 3))
    d.polygon([(cx + 52 * s, cy + 10 * s), (cx + 74 * s, cy + 34 * s), (cx + 50 * s, cy + 40 * s)], fill=PINK, outline=INK, width=W2(s, 3))
    d.ellipse([cx + 22 * s, cy + 6 * s, cx + 34 * s, cy + 18 * s], fill=INK)
    d.arc([cx - 72 * s, cy - 50 * s, cx + 66 * s, cy + 88 * s], 195, 345, fill=VIO, width=W2(s, 12))
    for a in (215, 270, 325):
        r = math.radians(a); x, y = cx - 3 * s + 69 * s * math.cos(r), cy + 19 * s + 69 * s * math.sin(r)
        d.ellipse([x - 9 * s, y - 9 * s, x + 9 * s, y + 9 * s], fill=CARD, outline=INK, width=W2(s, 2))
    for k in range(3):
        ph = (t * 1.3 + k * 16) % 48; y = cy - 58 * s - ph * s
        pts = [(cx + (-40 + j * 4) * s, y + 5 * s * math.sin(j * .9 + t * .3)) for j in range(21)]
        d.line(pts, fill=VIO if k != 1 else TAN, width=W2(s, 3), joint='curve')
    return im

def sk_watch(t):
    im, d, cx, cy, s = canvas(250, 214)
    d.rounded_rectangle([cx - 125 * s, cy + 0 * s, cx + 125 * s, cy + 70 * s], 35 * s, fill=PINK, outline=INK, width=W2(s, 3))
    d.rectangle([cx - 24 * s, cy - 10 * s, cx + 24 * s, cy + 80 * s], fill=VIO, outline=INK, width=W2(s, 3))
    d.rounded_rectangle([cx - 44 * s, cy - 18 * s, cx + 44 * s, cy + 70 * s], 18 * s, fill=CARD, outline=INK, width=W2(s, 4))
    pts = []
    for j in range(29):
        k = (j + int(t * .8)) % 14
        v = {5: -18, 6: 14, 7: -6}.get(k, 0)
        pts.append((cx + (-34 + j * 2.4) * s, cy + 26 * s + v * s))
    d.line(pts, fill=VIO, width=W2(s, 3))
    b = 1 + .18 * max(0, math.sin(t * .45)) ** 8; hx, hy = cx + 70 * s, cy - 50 * s
    d.ellipse([hx - 14 * s * b, hy - 10 * s * b, hx, hy + 4 * s * b], fill=TAN); d.ellipse([hx, hy - 10 * s * b, hx + 14 * s * b, hy + 4 * s * b], fill=TAN)
    d.polygon([(hx - 13 * s * b, hy), (hx + 13 * s * b, hy), (hx, hy + 18 * s * b)], fill=TAN)
    return im

def gear(d, cx, cy, r, ang, s, col):
    pts = []
    for k in range(32):
        a = ang + k * math.pi / 16; rr = r * (1.0 if k % 4 < 2 else .78)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=INK, width=W2(s, 2)); d.ellipse([cx - r * .3, cy - r * .3, cx + r * .3, cy + r * .3], fill=CARD, outline=INK, width=W2(s, 2))

def sk_camera(t):
    im, d, cx, cy, s = canvas(250, 214)
    x0, y0 = cx - 90 * s, cy - 30 * s
    for k in range(0, 100, 12):
        d.line([(x0 + 44 * s + k * 1.4 * s, y0 + 10 * s - k * .25 * s), (x0 + 50 * s + k * 1.4 * s, y0 + 10 * s - k * .25 * s)], fill=VIO, width=W2(s, 2))
        d.line([(x0 + 44 * s + k * 1.4 * s, y0 + 20 * s + k * .45 * s), (x0 + 50 * s + k * 1.4 * s, y0 + 20 * s + k * .45 * s)], fill=VIO, width=W2(s, 2))
    d.line([(x0, y0 + 26 * s), (x0 - 18 * s, y0 + 100 * s)], fill=INK, width=W2(s, 3)); d.line([(x0, y0 + 26 * s), (x0 + 16 * s, y0 + 100 * s)], fill=INK, width=W2(s, 3))
    d.rounded_rectangle([x0 - 30 * s, y0, x0 + 34 * s, y0 + 36 * s], 8 * s, fill=CARD, outline=INK, width=W2(s, 3))
    d.ellipse([x0 + 26 * s, y0 + 6 * s, x0 + 50 * s, y0 + 30 * s], fill=VIO, outline=INK, width=W2(s, 3))
    d.ellipse([x0 - 22 * s, y0 + 6 * s, x0 - 14 * s, y0 + 14 * s], fill=TAN if (t // 8) % 2 else CARD)
    mx0, my0 = cx + 30 * s, cy - 50 * s
    d.rounded_rectangle([mx0, my0, mx0 + 90 * s, my0 + 110 * s], 10 * s, fill=CARD, outline=INK, width=W2(s, 3))
    gear(d, mx0 + 45 * s, my0 + 50 * s, 28 * s, t * .12, s, PINK)
    d.ellipse([mx0 + 70 * s, my0 + 88 * s, mx0 + 82 * s, my0 + 100 * s], fill=VIO)
    d.line([(cx - 120 * s, cy + 70 * s), (cx + 125 * s, cy + 70 * s)], fill=INK, width=W2(s, 3))
    return im

def sk_motion(t):
    im, d, cx, cy, s = canvas(250, 214)
    sw = math.sin(t * .22); bob = abs(math.cos(t * .22)) * 4 * s
    hip = (cx, cy + 28 * s - bob)
    for sg in (1, -1):
        d.line([hip, (cx + 26 * sw * sg * s, cy + 92 * s)], fill=INK, width=W2(s, 7))
        d.line([(cx, cy - 20 * s - bob), (cx - 24 * sw * sg * s, cy + 26 * s - bob)], fill=INK, width=W2(s, 6))
    d.rounded_rectangle([cx - 22 * s, cy - 38 * s - bob, cx + 22 * s, cy + 36 * s - bob], 18 * s, fill=PINK, outline=INK, width=W2(s, 3))
    d.ellipse([cx - 22 * s, cy - 86 * s - bob, cx + 22 * s, cy - 42 * s - bob], fill=PINK, outline=INK, width=W2(s, 3))
    sx, sy = cx + 18 * s, cy + 18 * s - bob
    d.rounded_rectangle([sx - 10 * s, sy - 12 * s, sx + 14 * s, sy + 12 * s], 5 * s, fill=VIO, outline=INK, width=W2(s, 2))
    for k in range(2):
        r = (18 + ((t * 1.5 + k * 14) % 28)) * s
        d.arc([sx - r, sy - r, sx + r, sy + r], -40, 40, fill=VIO, width=W2(s, 3))
    d.line([(cx - 110 * s, cy + 94 * s), (cx + 110 * s, cy + 94 * s)], fill=INK, width=W2(s, 3))
    return im
SKETCH = [sk_eeg, sk_watch, sk_camera, sk_motion]


RING0 = 1271
def draw_intro(fr, f):
    if f >= RPOP[0] + 8: return
    out = e_in((f - RPOP[0] + 10) / 10) if f >= RPOP[0] - 10 else 0
    k = 1 - out
    t = (f - B6 - 4)
    R = rotm(.5, .6 + t * .018)
    put(fr, draw_mesh(mesh('chip', chip_mesh), R, 230 * (pop(t, 12, .6, 1.05) or 0) * k if t >= 0 else 1, shadow=7), 540, 900)
    ring = [(ic_eeg, "EEG"), (ic_watch, "WATCH"), (ic_camera, "CAMERA"), (ic_motion, "MOTION"), (ic_band, "ARMBAND")]
    for j, (ic, lab) in enumerate(ring):
        dj = f - RING0 - 3 * j
        if dj < 0: continue
        a = math.radians(-90 + j * 72)
        x = 540 + 380 * math.cos(a) * lerp(1, .2, out); y = 900 + 380 * math.sin(a) * lerp(1, .2, out)
        def c(d, x0, y0, x1, y1, s, ic=ic, lab=lab):
            ic(d, (x0 + x1) / 2, y0 + 56 * s, s * .82, VIO); mlabel(d, (x0 + x1) / 2, y1 - 20 * s, s, lab, INK, 14, anchor='ms')
        put(fr, spr(('ring', j), lambda c=c: card_ss(150, 132, radius=16, shadow=5, content=c), [-2, 1.5, -1, 2, -1.5][j] + wob(dj)), x, y, (pop(dj) or 0) * k)

def beat6(f):
    fr = paper()
    drop = lambda i: e_in((f - OUT6 - 2 * i) / 9) * 2200 if f >= OUT6 else 0
    put(fr, spr('hdr6', lambda: pill_ss("ONE MODEL  ·  ANY SENSOR", CARD, INK, 22, track=.14, dot=VIO), 1.5 + wob(f - B6 - 6)), 540, 225 + drop(0), pop(f - B6 - 6))
    draw_intro(fr, f)
    for i in range(4):
        if f < RPOP[i]: continue
        typ = TSTART[i] <= f
        n = int(clamp((f - TSTART[i]) / TFPC[i], 0, RLEN[i])) if typ else 0
        cursor = typ and f < RANS[i] and ((f // 7) % 2 == 0 or n < RLEN[i])
        rot = RROT[i] + wob(f - RPOP[i])
        y = RY[i] + drop(i + 1); sc = pop(f - RPOP[i])
        im = cached(('row', i, n, cursor, rot), lambda: finish(card_ss(RW, RH, content=row_c(i, n, cursor)), rot))
        put(fr, im, 540, y, sc)
        ox, oy = rot_off(-RW / 2 + 143, 0, rot)
        put(fr, finish(SKETCH[i](f), rot), 540 + ox * sc, y + oy * sc, sc)
        if STAMP6 + 3 * i <= f < STAMPOFF + 3 * i + 14:
            sx = e_in((f - STAMPOFF - 3 * i) / 12) * 1300 if f >= STAMPOFF + 3 * i else 0
            st = spr(('mo', i), lambda i=i: pill_ss(MONTHS[i], TAN, INK, 28, track=.14, shadow=5), -7 + wob(f - STAMP6 - 3 * i, 3))
            ox2, oy2 = rot_off(250, 40, rot); put(fr, st, 540 + ox2 + sx, y + oy2, slam(f - STAMP6 - 3 * i))
        if f >= RANS[i]:
            fill = round(e_out((f - RANS[i]) / 12) * 12) / 12
            row = cached(('a2', i, fill), lambda: finish(ans2(i, fill), RROT[i]))
            ox3, oy3 = rot_off(-RW / 2 + 290 + row.width / 2, 72, RROT[i])
            put(fr, row, 540 + ox3, y + oy3, pop(f - RANS[i], 10, .8, 1.08))
    x = 540 - (sum(tw(m, MONO, 20, .14) + 64 for m in MORE) + 14 * 4) / 2
    for k, m in enumerate(MORE):
        w = tw(m, MONO, 20, .14) + 64
        if f >= MORE0 + 3 * k:
            put(fr, spr(('more', k), lambda m=m, k=k: pill_ss(m, [CARD, PINK, CARD, TAN, VIO][k], CARD if k == 4 else INK, 20, track=.14), [-2, 1.5, -1, 2, -1.5][k] + wob(f - MORE0 - 3 * k)),
                x + w / 2, 1490 + drop(6), pop(f - MORE0 - 3 * k))
        x += w + 14
    return fr

# ================================================================== BEAT 7 — landing + wall of integrations + spark (2400-2729)
TXT0, SHRINK0, WALL0, SPARK0, NFR = 1781, 99999, 1784, 1862, 1922
LT = [1781, 1799, 1823, 1837]; UL0 = 1831
LINES = [("I DON'T THINK", INK, -2), ("PEOPLE REALISE", INK, 1), ("HOW CRAZY", VIO, -1), ("THIS COULD GET.", INK, 2)]

def v_ring(d, cx, cy, s, t):
    d.rounded_rectangle([cx - 120 * s, cy - 4 * s, cx + 60 * s, cy + 44 * s], 24 * s, fill=PINK, outline=INK, width=W2(s, 3))
    d.rounded_rectangle([cx - 20 * s, cy - 12 * s, cx + 4 * s, cy + 52 * s], 8 * s, fill=VIO, outline=INK, width=W2(s, 3))
    for k in range(3):
        ph = (t * 1.1 + k * 18) % 54
        tx(d, cx + (50 + k * 20) * s, cy - 10 * s - ph * s, s, "z", HEAD, 18 + k * 4, VIO, anchor='mm')
def v_dash(d, cx, cy, s, t):
    d.ellipse([cx - 110 * s, cy - 40 * s, cx - 30 * s, cy + 40 * s], outline=INK, width=W2(s, 7))
    d.line([(cx - 70 * s, cy), (cx - 70 * s, cy + 40 * s)], fill=INK, width=W2(s, 6)); d.line([(cx - 110 * s, cy), (cx - 30 * s, cy)], fill=INK, width=W2(s, 6))
    lid = .5 + .5 * math.sin(t * .12)
    d.ellipse([cx + 20 * s, cy - 26 * s, cx + 110 * s, cy + 26 * s], fill=CARD, outline=INK, width=W2(s, 3))
    if lid > .25: d.ellipse([cx + 52 * s, cy - 14 * s * lid, cx + 78 * s, cy + 14 * s * lid], fill=VIO)
    d.rectangle([cx + 22 * s, cy - 26 * s, cx + 108 * s, cy - 26 * s + 44 * s * (1 - lid)], fill=PINK)
def v_soil(d, cx, cy, s, t):
    d.polygon([(cx - 60 * s, cy + 10 * s), (cx + 20 * s, cy + 10 * s), (cx + 8 * s, cy + 60 * s), (cx - 48 * s, cy + 60 * s)], fill=TAN, outline=INK, width=W2(s, 3))
    d.line([(cx - 20 * s, cy + 10 * s), (cx - 20 * s, cy - 36 * s)], fill=INK, width=W2(s, 4))
    dr = 10 + 6 * math.sin(t * .1)
    for sg in (1, -1):
        d.ellipse([cx - 20 * s + (sg * 28 - 18) * s, cy - (40 - dr) * s, cx - 20 * s + (sg * 28 + 18) * s, cy - (22 - dr) * s], fill=PINK, outline=INK, width=W2(s, 2))
    d.rectangle([cx + 50 * s, cy - 30 * s, cx + 62 * s, cy + 58 * s], fill=VIO, outline=INK, width=W2(s, 2))
    if (t // 10) % 2: d.polygon([(cx + 90 * s, cy - 40 * s), (cx + 80 * s, cy - 20 * s), (cx + 100 * s, cy - 20 * s)], fill=VIO); d.ellipse([cx + 80 * s, cy - 28 * s, cx + 100 * s, cy - 8 * s], fill=VIO)
def v_door(d, cx, cy, s, t):
    d.rounded_rectangle([cx - 110 * s, cy - 56 * s, cx - 30 * s, cy + 58 * s], 6 * s, fill=CARD, outline=INK, width=W2(s, 3))
    d.ellipse([cx - 44 * s, cy - 2 * s, cx - 36 * s, cy + 6 * s], fill=INK)
    d.ellipse([cx - 22 * s, cy - 40 * s, cx - 8 * s, cy - 26 * s], fill=VIO if (t // 6) % 2 else CARD, outline=INK, width=W2(s, 2))
    x = lerp(140, 20, e_out(((t % 70)) / 30))
    d.rectangle([cx + x * s, cy + 10 * s, cx + (x + 60) * s, cy + 58 * s], fill=TAN, outline=INK, width=W2(s, 3))
    d.line([(cx + (x + 30) * s, cy + 10 * s), (cx + (x + 30) * s, cy + 58 * s)], fill=INK, width=W2(s, 2))
def v_baby(d, cx, cy, s, t):
    d.rectangle([cx - 100 * s, cy + 36 * s, cx + 30 * s, cy + 50 * s], fill=CARD, outline=INK, width=W2(s, 3))
    for k in range(7): x = cx + (-96 + k * 20) * s; d.line([(x, cy - 30 * s), (x, cy + 36 * s)], fill=INK, width=W2(s, 3))
    d.line([(cx - 100 * s, cy - 30 * s), (cx + 30 * s, cy - 30 * s)], fill=INK, width=W2(s, 4))
    for k in range(3):
        r = (14 + (t * 1.4 + k * 14) % 42) * s
        d.arc([cx + 50 * s - r, cy - r, cx + 50 * s + r, cy + r], -45, 45, fill=TAN, width=W2(s, 4))
def v_fridge(d, cx, cy, s, t):
    d.rounded_rectangle([cx - 70 * s, cy - 58 * s, cx + 10 * s, cy + 60 * s], 8 * s, fill=CARD, outline=INK, width=W2(s, 3))
    op = .5 + .5 * math.sin(t * .08)
    d.rectangle([cx - 60 * s, cy + 6 * s, cx - 36 * s, cy + 50 * s], fill=CARD, outline=INK, width=W2(s, 2))
    d.rectangle([cx - 60 * s, cy + 40 * s, cx - 36 * s, cy + 50 * s], fill=VIO)
    d.polygon([(cx + 10 * s, cy - 58 * s), (cx + (10 + 70 * op) * s, cy - 48 * s), (cx + (10 + 70 * op) * s, cy + 50 * s), (cx + 10 * s, cy + 60 * s)], fill=PINK, outline=INK, width=W2(s, 3))
def v_guitar(d, cx, cy, s, t):
    for k in range(5):
        y = cy + (-40 + k * 20) * s; a = 8 * math.exp(-((t + k * 5) % 40) / 10) * s
        d.line([(cx - 130 * s + j * 13 * s, y + a * math.sin(j * 1.3 + t * 1.7) * math.sin(math.pi * j / 20)) for j in range(21)], fill=VIO if k == 2 else INK, width=W2(s, 3))
    d.rounded_rectangle([cx + 70 * s, cy - 54 * s, cx + 96 * s, cy + 54 * s], 6 * s, fill=TAN, outline=INK, width=W2(s, 3))
def v_drone(d, cx, cy, s, t):
    for k in range(3): r = (20 + k * 18) * s; d.ellipse([cx - r * 1.8, cy + 44 * s - r * .35, cx + r * 1.8, cy + 44 * s + r * .35], outline=TAN if k == 0 else DOT, width=W2(s, 3))
    y = cy - 20 * s + 6 * s * math.sin(t * .2)
    d.rounded_rectangle([cx - 34 * s, y - 12 * s, cx + 34 * s, y + 12 * s], 8 * s, fill=VIO, outline=INK, width=W2(s, 3))
    for sg in (-1, 1):
        px = cx + sg * 58 * s; d.line([(cx + sg * 30 * s, y), (px, y - 12 * s)], fill=INK, width=W2(s, 3))
        a = t * .9; L = 26 * s
        d.line([(px - L * math.cos(a), y - 14 * s - 4 * s * math.sin(a)), (px + L * math.cos(a), y - 14 * s + 4 * s * math.sin(a))], fill=INK, width=W2(s, 4))
def v_bike(d, cx, cy, s, t):
    wx, r = cx - 40 * s, 52 * s
    d.ellipse([wx - r, cy - r, wx + r, cy + r], fill=CARD, outline=INK, width=W2(s, 6))
    for k in range(6):
        a = t * .15 + k * math.pi / 3; d.line([(wx, cy), (wx + r * math.cos(a), cy + r * math.sin(a))], fill=INK, width=W2(s, 2))
    d.ellipse([wx - 10 * s, cy - 10 * s, wx + 10 * s, cy + 10 * s], fill=VIO, outline=INK, width=W2(s, 2))
    gx = cx + 80 * s; d.pieslice([gx - 36 * s, cy - 30 * s, gx + 36 * s, cy + 42 * s], 180, 360, fill=CARD, outline=INK, width=W2(s, 3))
    a = math.radians(200 + 10 * math.sin(t * .2)); d.line([(gx, cy + 6 * s), (gx + 30 * s * math.cos(a), cy + 6 * s + 30 * s * math.sin(a))], fill=TAN, width=W2(s, 4))
def v_hive(d, cx, cy, s, t):
    for k in range(4):
        w = (70 - k * 12) * s; y = cy + (44 - k * 24) * s
        d.rounded_rectangle([cx - w, y - 14 * s, cx + w, y + 12 * s], 12 * s, fill=TAN, outline=INK, width=W2(s, 3))
    d.ellipse([cx - 10 * s, cy + 30 * s, cx + 10 * s, cy + 50 * s], fill=INK)
    for k in range(6):
        a = t * .12 + k * math.pi / 3; x = cx + 110 * s * math.cos(a); y = cy - 10 * s + 48 * s * math.sin(a * 1.3)
        d.ellipse([x - 7 * s, y - 5 * s, x + 7 * s, y + 5 * s], fill=INK); d.ellipse([x - 4 * s, y - 12 * s, x + 6 * s, y - 3 * s], fill=CARD, outline=INK, width=1)
def v_glasses(d, cx, cy, s, t):
    for sg in (-1, 1):
        x0 = cx + sg * 64 * s - 54 * s
        d.rounded_rectangle([x0, cy - 34 * s, x0 + 108 * s, cy + 34 * s], 20 * s, fill=SCOPE, outline=INK, width=W2(s, 5))
        for k in range(4):
            y = cy - 20 * s + ((k * 16 - t * .8) % 64) * s - 6 * s
            if cy - 26 * s < y < cy + 26 * s: d.line([(x0 + 18 * s, y), (x0 + (80 - 18 * (k % 2)) * s, y)], fill=VIO, width=W2(s, 4))
    d.arc([cx - 14 * s, cy - 14 * s, cx + 14 * s, cy + 10 * s], 200, 340, fill=INK, width=W2(s, 5))
def v_arm(d, cx, cy, s, t):
    bx, by = cx - 70 * s, cy + 50 * s
    d.rounded_rectangle([bx - 30 * s, by - 10 * s, bx + 30 * s, by + 10 * s], 5 * s, fill=INK)
    a1 = math.radians(-70 + 20 * math.sin(t * .1)); a2 = a1 + math.radians(80 + 25 * math.sin(t * .1 + 1))
    j = (bx + 60 * s * math.cos(a1), by - 10 * s + 60 * s * math.sin(a1)); e = (j[0] + 70 * s * math.cos(a2), j[1] + 70 * s * math.sin(a2))
    d.line([(bx, by - 10 * s), j], fill=VIO, width=W2(s, 14)); d.line([j, e], fill=VIO, width=W2(s, 11))
    for p in [(bx, by - 10 * s), j]: d.ellipse([p[0] - 9 * s, p[1] - 9 * s, p[0] + 9 * s, p[1] + 9 * s], fill=CARD, outline=INK, width=W2(s, 3))
    d.rectangle([cx + 60 * s, cy + 26 * s, cx + 92 * s, cy + 58 * s], fill=TAN, outline=INK, width=W2(s, 3))
WALL = [("SMART RING", "asleep", .91, v_ring), ("DASHCAM", "drowsy", .88, v_dash), ("SOIL PROBE", "thirsty", .93, v_soil),
        ("DOORBELL", "package", .97, v_door), ("BABY MONITOR", "crying", .84, v_baby), ("FRIDGE CAM", "low on milk", .79, v_fridge),
        ("GUITAR PICKUP", "out of tune", .90, v_guitar), ("DRONE", "clear to land", .95, v_drone), ("BIKE HUB", "tire low", .86, v_bike),
        ("BEEHIVE MIC", "swarming", .72, v_hive), ("SMART GLASSES", "reading", .89, v_glasses), ("ROBOT ARM", "grasp ok", .98, v_arm)]
WX = [200, 540, 880]; WY = [420, 780, 1140, 1500]; TW_, TH_ = 320, 250
WROT = [-1.5, 1, -.75, 1.25, -1.25, .5, 1.5, -1, .75, -1.5, 1, -.5]

def wall_c(k):
    name, a, p, _ = WALL[k]
    def c(d, x0, y0, x1, y1, s):
        mlabel(d, x0 + 18 * s, y0 + 34 * s, s, name, INK, 15)
        d.ellipse([x1 - 30 * s, y0 + 20 * s, x1 - 18 * s, y0 + 32 * s], fill=VIO)
        d.rounded_rectangle([x0 + 16 * s, y0 + 48 * s, x1 - 16 * s, y1 - 62 * s], 12 * s, fill=SCOPE, outline=INK, width=W2(s, 2))
        tx(d, x0 + 18 * s, y1 - 24 * s, s, "→ " + a, HEAD, 22, VIO)
        lab = "p %.2f" % p; w = tw(lab, MONO, 15 * s) + 24 * s
        d.rounded_rectangle([x1 - 18 * s - w, y1 - 48 * s, x1 - 18 * s, y1 - 18 * s], 99 * s, fill=TAN, outline=INK, width=W2(s, 2))
        tx(d, x1 - 18 * s - w / 2, y1 - 33 * s, s, lab, MONO, 15, INK, anchor='mm')
    return c

def spark_frame(f):
    fr = Image.new('RGB', (W, H), VIO); df = f - SPARK0
    t = e_back(df / 20, 1.4)
    R = rotm(lerp(.5, .06, t), lerp(2.2, .12, t), lerp(.5, .1, t))
    put(fr, draw_mesh(mesh('spark', spark_mesh), R, 250, shadow=12, outline=2), 540, 880, pop(df, 12, .6, 1.05))
    put(fr, spr('lv', lambda: text_ss("LANVAR.AI", MONO, 32, CARD, track=.14), 0), 540, 1240, pop(df - 8))
    return fr

def beat7(f):
    if f >= SPARK0: return spark_frame(f)
    fr = beat6(f) if f < OUT6 + 20 else paper()
    d = ImageDraw.Draw(fr)
    if f >= WALL0:
        z = 1.0; rise = 0
        for j, (name, a, p, fn) in enumerate(WALL):
            dj = f - WALL0 - [0, 4, 1, 6, 9, 3, 8, 11, 5, 10, 2, 7][j] * 3
            if dj < 0: continue
            wx, wy = WX[j % 3], WY[j // 3]
            x = wx; y = wy + rise + 90 * (1 - e_out(dj / 12))
            rot = WROT[j] + wob(dj); sc = pop(dj) * z
            put(fr, spr(('wall', j), lambda j=j: card_ss(TW_, TH_, content=wall_c(j)), rot), x, y, sc)
            im, dd, cx, cy, s = canvas(288, 140); fn(dd, cx, cy, s, f)
            ox, oy = rot_off(0, -6, rot)
            put(fr, finish(im, rot), x + ox * sc, y + oy * sc, sc)
    k = e_io5((f - SHRINK0) / 16) if f >= SHRINK0 else 0
    if f >= LT[0] - 2: put(fr, spr('hcard', lambda: card_ss(960, 580, radius=24, shadow=8), -1 + wob(f - LT[0] + 2)), 540, 915, pop(f - LT[0] + 2))
    for i, (t, col, rot) in enumerate(LINES):
        sc = slam(f - LT[i])
        if sc is None: continue
        y = lerp(720 + i * 130, 245 + i * 50, k)
        put(fr, spr(('l7', i), lambda t=t, col=col: text_ss(t, HEAD, 92, col), rot), 540, y, sc * lerp(1, .4, k))
    if f >= UL0:
        t = e_out((f - UL0) / 10)
        pts = [(300 + 480 * j / 40, 1030 + 7 * math.sin(j * .5) - j * .35) for j in range(41)]
        pts = [(540 + (x - 540) * lerp(1, .4, k), lerp(y, 345 + (y - 980) * .4, k)) for x, y in pts]
        n = max(2, int(41 * t)); d.line(pts[:n], fill=TAN, width=int(lerp(10, 5, k)), joint='curve')
    return fr


# ================================================================== scene dispatch
_last = [None]
def render(f):
    beat = 1 if f < 185 else 2 if f < 611 else 4 if f < 1190 else 6 if f < SPARK0 else 7
    if beat != _last[0]:
        core.clear_cache(); _last[0] = beat
    if f < 185: return beat1(f)
    if f < 611: return beat23(f)
    if f < 1190: return beat45(f)
    if f < OUT6: return beat6(f)
    return beat7(f)

build_b1(); build_passes()
