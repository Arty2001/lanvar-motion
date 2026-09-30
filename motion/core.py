"""motion.core: the Lanvar flat-paper design system. Palette, easing, cards, pills, text,
icons, dot-grid paper, the thin-line signal, a flat-shaded 3D engine, and film grain.
Every project imports it with `from motion.core import *`."""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
PAPER = (243, 242, 236); CARD = (251, 250, 246); INK = (34, 29, 51)
VIO = (91, 61, 245); TAN = (255, 99, 32); PINK = (246, 168, 222); WHITE = (255, 255, 255)
DOT = (224, 222, 211); MUTE = (122, 116, 140); SCOPE = (240, 238, 230)
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONTS = os.path.join(os.path.dirname(_HERE), 'fonts')
def find_font(names):
    """first font that exists: the repo fonts/ folder first, then common system locations"""
    dirs = [_FONTS, '/usr/share/fonts/truetype/dejavu', '/Library/Fonts', os.path.expanduser('~/Library/Fonts'),
            '/System/Library/Fonts/Supplemental', 'C:/Windows/Fonts']
    for n in names:
        for d in dirs:
            p = os.path.join(d, n)
            if os.path.exists(p): return p
    raise FileNotFoundError("No font found from %s. Drop a .ttf into %s" % (names, _FONTS))
# brand fonts first (put the .ttf files in fonts/), fallbacks after
HEAD = find_font(['Unbounded-Bold.ttf', 'Unbounded-VariableFont_wght.ttf', 'DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf'])
MONO = find_font(['SplineSansMono-SemiBold.ttf', 'SplineSansMono-VariableFont_wght.ttf', 'DejaVuSansMono-Bold.ttf', 'Menlo.ttc', 'consolab.ttf'])
SS = 2

# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def ss(t): t = clamp(t); return t * t * (3 - 2 * t)
def e_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def e_in(t): t = clamp(t); return t ** 3
def e_io(t): t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def e_io5(t): t = clamp(t); return 16 * t ** 5 if t < .5 else 1 - (-2 * t + 2) ** 5 / 2
def e_back(t, c=1.7):
    t = clamp(t); return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def pop(df, n=12, a=0.92, o=1.03):
    if df < 0: return None
    k = n * 7 / 12
    if df <= k: return lerp(a, o, ss(df / k))
    if df <= n: return lerp(o, 1.0, ss((df - k) / (n - k)))
    return 1.0

def slam(df):
    if df < 0: return None
    if df <= 5: return lerp(1.4, 0.96, e_out(df / 5))
    if df <= 8: return lerp(0.96, 1.0, ss((df - 5) / 3))
    return 1.0

def wob(df, amp=2.4):
    """secondary rotation settle that rides on a pop; quantised so sprites cache"""
    if df < 0 or df > 16: return 0.0
    v = amp * math.exp(-df / 4.0) * math.cos(df * 0.62)
    return round(v * 4) / 4

# ------------------------------------------------------------------ text + sprites
_fonts = {}
def F(path, size):
    k = (path, int(size))
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, int(size))
    return _fonts[k]

def tx(d, x, y, s, text, path, size, fill, anchor='ls', track=0.0):
    f = F(path, size * s)
    if not track:
        d.text((x, y), text, font=f, fill=fill, anchor=anchor); return f.getlength(text)
    sp = track * size * s
    total = sum(f.getlength(c) for c in text) + sp * (len(text) - 1)
    if anchor[0] == 'm': x -= total / 2
    elif anchor[0] == 'r': x -= total
    for c in text:
        d.text((x, y), c, font=f, fill=fill, anchor='l' + anchor[1]); x += f.getlength(c) + sp
    return total

def tw(text, path, size, track=0.0):
    f = F(path, size); return f.getlength(text) + track * size * (len(text) - 1)

_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]
def evict(prefix):
    for k in [k for k in _cache if isinstance(k, tuple) and k and k[0] == prefix]: del _cache[k]

def finish(im, rot):
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im.resize((max(1, im.width // SS), max(1, im.height // SS)), Image.LANCZOS)

def card_ss(w, h, face=CARD, radius=18, shadow=6, border=2, content=None, bcol=INK):
    m = shadow + 8
    im = Image.new('RGBA', ((w + 2 * m) * SS, (h + 2 * m) * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0 = m * SS, m * SS; x1, y1 = x0 + w * SS, y0 + h * SS
    r = min(radius, h / 2, w / 2) * SS
    if shadow: d.rounded_rectangle([x0 + shadow * SS, y0 + shadow * SS, x1 + shadow * SS, y1 + shadow * SS], r, fill=INK)
    d.rounded_rectangle([x0, y0, x1, y1], r, fill=face, outline=bcol, width=border * SS)
    if content: content(d, x0, y0, x1, y1, SS)
    return im

def spr(key, builder, rot):
    """builder -> supersampled unrotated RGBA; rotated+downsampled copies cached per angle"""
    base = cached(('b', key), builder)
    return cached(('r', key, rot), lambda: finish(base, rot))

def put(fr, im, cx, cy, s=1.0, alpha=1.0):
    if s is None or s <= 0.01 or alpha <= 0: return
    if abs(s - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    fr.paste(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))), im)

def rot_off(dx, dy, deg):
    a = math.radians(deg); return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)

def text_ss(text, path, size, fill, track=0.0):
    f = F(path, size * SS)
    w = tw(text, path, size * SS, track) + 60 * SS
    im = Image.new('RGBA', (int(w), int(size * 1.7 * SS)), (0, 0, 0, 0))
    tx(ImageDraw.Draw(im), im.width / 2, im.height / 2, SS, text, path, size, fill, anchor='mm', track=track)
    return im

def pill_ss(text, face, tcol, size=32, font=MONO, track=.1, pad=30, shadow=5, dot=None):
    w = int(tw(text, font, size, track) + pad * 2 + (26 if dot else 0)); h = int(size * 2.0)
    def c(d, x0, y0, x1, y1, s):
        x = (x0 + x1) / 2 + (13 * s if dot else 0)
        if dot:
            d.ellipse([x0 + 22 * s, (y0 + y1) / 2 - 7 * s, x0 + 36 * s, (y0 + y1) / 2 + 7 * s], fill=dot)
        tx(d, x, (y0 + y1) / 2, s, text, font, size, tcol, anchor='mm', track=track)
    return card_ss(w, h, face=face, radius=999, shadow=shadow, content=c)

def mlabel(d, x, y, s, text, col=INK, size=20, anchor='ls'):
    return tx(d, x, y, s, text, MONO, size, col, anchor=anchor, track=0.14)

# ------------------------------------------------------------------ icons (drawn at SS inside content fns)
def ic_filter(d, cx, cy, s, col=VIO):
    pts = [(cx + (i - 20) * 3 * s, cy + 24 * s - 46 * s * math.exp(-((i - 20) / 7) ** 2)) for i in range(41)]
    d.line([(cx - 64 * s, cy + 26 * s), (cx + 64 * s, cy + 26 * s)], fill=INK, width=max(1, int(2 * s)))
    d.line(pts, fill=col, width=max(1, int(4 * s)), joint='curve')
def ic_bars(d, cx, cy, s, col=VIO):
    for i, h in enumerate([18, 44, 30, 52, 14]):
        x = cx + (i - 2) * 22 * s
        d.rounded_rectangle([x - 7 * s, cy + 26 * s - h * s, x + 7 * s, cy + 26 * s], 3 * s, fill=col if i == 3 else CARD, outline=INK, width=max(1, int(2 * s)))
def ic_step(d, cx, cy, s, col=VIO):
    for x in range(-64, 64, 14): d.line([(cx + x * s, cy), (cx + (x + 7) * s, cy)], fill=TAN, width=max(1, int(3 * s)))
    d.line([(cx - 64 * s, cy + 22 * s), (cx - 6 * s, cy + 22 * s), (cx - 6 * s, cy - 24 * s), (cx + 64 * s, cy - 24 * s)], fill=col, width=max(1, int(4 * s)))
def ic_dial(d, cx, cy, s, col=VIO):
    d.pieslice([cx - 34 * s, cy - 30 * s, cx + 34 * s, cy + 38 * s], 180, 360, fill=CARD, outline=INK, width=max(1, int(2 * s)))
    for a in range(0, 181, 30):
        r = math.radians(180 + a); d.line([(cx + 26 * s * math.cos(r), cy + 4 * s + 26 * s * math.sin(r)), (cx + 32 * s * math.cos(r), cy + 4 * s + 32 * s * math.sin(r))], fill=INK, width=max(1, int(2 * s)))
    r = math.radians(300); d.line([(cx, cy + 4 * s), (cx + 26 * s * math.cos(r), cy + 4 * s + 26 * s * math.sin(r))], fill=col, width=max(1, int(4 * s)))
    d.ellipse([cx - 5 * s, cy - 1 * s, cx + 5 * s, cy + 9 * s], fill=INK)
def ic_browser(d, cx, cy, s, col=CARD):
    d.rounded_rectangle([cx - 56 * s, cy - 40 * s, cx + 56 * s, cy + 40 * s], 10 * s, fill=col, outline=INK, width=max(1, int(3 * s)))
    d.line([(cx - 56 * s, cy - 20 * s), (cx + 56 * s, cy - 20 * s)], fill=INK, width=max(1, int(3 * s)))
    for i in range(3): d.ellipse([cx + (-46 + i * 12) * s, cy - 34 * s, cx + (-40 + i * 12) * s, cy - 28 * s], fill=INK)
    a = [(cx + 6 * s, cy - 6 * s), (cx + 6 * s, cy + 30 * s), (cx + 15 * s, cy + 22 * s), (cx + 23 * s, cy + 36 * s), (cx + 29 * s, cy + 32 * s), (cx + 21 * s, cy + 18 * s), (cx + 33 * s, cy + 16 * s)]
    d.polygon(a, fill=INK)
def ic_route(d, cx, cy, s, col=CARD):
    n0 = (cx - 44 * s, cy)
    for j in (-1, 0, 1):
        n1 = (cx + 44 * s, cy + j * 32 * s)
        d.line([n0, (cx, cy), (cx, n1[1]), n1], fill=INK, width=max(1, int(3 * s)))
        d.ellipse([n1[0] - 11 * s, n1[1] - 11 * s, n1[0] + 11 * s, n1[1] + 11 * s], fill=col, outline=INK, width=max(1, int(3 * s)))
    d.ellipse([n0[0] - 15 * s, n0[1] - 15 * s, n0[0] + 15 * s, n0[1] + 15 * s], fill=INK)
def ic_shield(d, cx, cy, s, col=CARD):
    p = [(cx, cy - 44 * s), (cx + 40 * s, cy - 30 * s), (cx + 36 * s, cy + 12 * s), (cx, cy + 44 * s), (cx - 36 * s, cy + 12 * s), (cx - 40 * s, cy - 30 * s)]
    d.polygon(p, fill=col, outline=INK, width=max(1, int(3 * s)))
    d.line([(cx - 16 * s, cy), (cx - 3 * s, cy + 13 * s), (cx + 19 * s, cy - 13 * s)], fill=INK, width=max(1, int(6 * s)), joint='curve')
def ic_eeg(d, cx, cy, s, col=VIO):
    d.ellipse([cx - 30 * s, cy - 34 * s, cx + 30 * s, cy + 30 * s], fill=CARD, outline=INK, width=max(1, int(3 * s)))
    for a in (-50, 0, 50):
        r = math.radians(a - 90); x, y = cx + 30 * s * math.cos(r), cy - 2 * s + 32 * s * math.sin(r)
        d.ellipse([x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s], fill=col, outline=INK, width=max(1, int(2 * s)))
def ic_watch(d, cx, cy, s, col=VIO):
    d.rounded_rectangle([cx - 13 * s, cy - 42 * s, cx + 13 * s, cy + 42 * s], 6 * s, fill=CARD, outline=INK, width=max(1, int(3 * s)))
    d.rounded_rectangle([cx - 24 * s, cy - 24 * s, cx + 24 * s, cy + 24 * s], 10 * s, fill=col, outline=INK, width=max(1, int(3 * s)))
    d.line([(cx - 12 * s, cy + 2 * s), (cx - 4 * s, cy + 2 * s), (cx, cy - 10 * s), (cx + 5 * s, cy + 10 * s), (cx + 12 * s, cy + 2 * s)], fill=CARD, width=max(1, int(3 * s)))
def ic_camera(d, cx, cy, s, col=VIO):
    d.rounded_rectangle([cx - 38 * s, cy - 24 * s, cx + 38 * s, cy + 28 * s], 8 * s, fill=CARD, outline=INK, width=max(1, int(3 * s)))
    d.rectangle([cx - 14 * s, cy - 32 * s, cx + 8 * s, cy - 24 * s], fill=INK)
    d.ellipse([cx - 17 * s, cy - 15 * s, cx + 17 * s, cy + 19 * s], fill=col, outline=INK, width=max(1, int(3 * s)))
def ic_motion(d, cx, cy, s, col=VIO):
    d.line([(cx - 30 * s, cy + 26 * s), (cx + 34 * s, cy + 26 * s)], fill=INK, width=max(1, int(3 * s)))
    d.line([(cx - 30 * s, cy + 26 * s), (cx - 30 * s, cy - 36 * s)], fill=INK, width=max(1, int(3 * s)))
    d.line([(cx - 30 * s, cy + 26 * s), (cx + 14 * s, cy - 14 * s)], fill=col, width=max(1, int(4 * s)))
    d.ellipse([cx + 6 * s, cy - 22 * s, cx + 22 * s, cy - 6 * s], fill=col, outline=INK, width=max(1, int(2 * s)))
def ic_band(d, cx, cy, s, col=VIO):
    d.rounded_rectangle([cx - 42 * s, cy - 20 * s, cx + 42 * s, cy + 20 * s], 20 * s, fill=col, outline=INK, width=max(1, int(3 * s)))
    for i in range(3): d.ellipse([cx + (-22 + i * 22 - 5) * s, cy - 5 * s, cx + (-22 + i * 22 + 5) * s, cy + 5 * s], fill=CARD)
SENS_ICONS = [ic_eeg, ic_watch, ic_camera, ic_motion, ic_band]

# ------------------------------------------------------------------ paper + dot grid (moves with the camera)
GRID = 64
def paper(zoom=1.0, cx=540, cy=960):
    if zoom == 1.0 and cx == 540 and cy == 960:
        return cached(('paper',), lambda: paper_draw(1.0, 540, 960)).copy()
    return paper_draw(zoom, cx, cy)
def paper_draw(zoom, cx, cy):
    im = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(im)
    step = GRID * zoom; k = 1
    while step * k < 36: k *= 2
    st = step * k; r = max(1.0, 2.2 * zoom * (1 if k == 1 else 1.4))
    ox = (540 - (cx - 32) * zoom) % st; oy = (960 - (cy - 32) * zoom) % st
    y = oy
    while y < H:
        x = ox
        while x < W:
            d.ellipse([x - r, y - r, x + r, y + r], fill=DOT); x += st
        y += st
    return im

# ------------------------------------------------------------------ the signal
_sph = {}
def sphere(r, shadow=False):
    r = max(2, int(round(r))); key = (r, shadow)
    if key in _sph: return _sph[key]
    R = r * SS; n = 2 * R + 4; c = n / 2
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + 0.5
    nx = (xx - c) / R; ny = -(yy - c) / R; d2 = nx * nx + ny * ny
    a = np.clip(R - np.sqrt(d2) * R + 0.5, 0, 1)
    if shadow:
        col = np.broadcast_to(np.array(INK, np.float32) / 255, (n, n, 3))
    else:
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        col = (np.stack([nx, ny, nz], -1) * 0.5 + 0.5) * 0.78 + 0.22
    rgba = np.dstack([np.clip(col * 255, 0, 255), a[..., None] * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, 'RGBA').resize((n // SS, n // SS), Image.LANCZOS)
    _sph[key] = im; return im

rng = np.random.RandomState(7)
NF = rng.uniform(9, 26, 7); NP = rng.uniform(0, 6.28, 7); NA = rng.uniform(.4, 1, 7); NS = rng.uniform(.18, .42, 7) * rng.choice([-1, 1], 7)
KEYS = ['noise', 'wave', 'peaks', 'step', 'bump', 'L', 'amp', 'r', 'z', 'spread']
def S(**k):
    d = dict(noise=0, wave=0, peaks=0, step=0, bump=0, L=0, amp=0, r=10, z=.4, spread=0); d.update(k); return d
RAW = S(noise=1, wave=.5, L=920, amp=40, r=16, z=1.0, spread=24)
BAND = S(wave=1, L=470, amp=30, r=10, z=.6, spread=9)
FFT = S(peaks=1, L=460, amp=58, r=10, z=.4)
THR = S(step=1, L=440, amp=26, r=10, z=.3)
CAL = S(bump=1, L=300, amp=28, r=10, z=.3)
DOTS = S(L=0, amp=0, r=15, z=0)
STAGES = [BAND, FFT, THR, CAL]
def smix(a, b, t): return {k: lerp(a[k], b[k], t) for k in KEYS}

def sig_y(u, t, st):
    y = np.zeros_like(u)
    if st['noise'] > 1e-3:
        n = sum(NA[i] * np.sin(NF[i] * u + NP[i] + t * NS[i]) for i in range(7)) / NA.sum() * 2.2
        y += st['noise'] * n * (0.8 + 0.2 * np.sin(t * .21))
    if st['wave'] > 1e-3: y += st['wave'] * (0.6 * np.sin(3.3 * u + t * .13) + 0.4 * np.sin(5.4 * u - t * .09))
    if st['peaks'] > 1e-3:
        p = sum(h * np.exp(-((u - c) / .06) ** 2) for c, h in [(-.55, .55), (-.12, 1.0), (.3, .7), (.62, .35)])
        y += st['peaks'] * (-(p * (1 + .06 * np.sin(t * .3))) + .35)
    if st['step'] > 1e-3: y += st['step'] * np.tanh(9 * np.sin(2.6 * u + t * .04)) * .8
    if st['bump'] > 1e-3: y += st['bump'] * (-np.exp(-(u / .28) ** 2) + .3)
    return y

def draw_signal(fr, cx, cy, st, t):
    L, amp, sp = st['L'], st['amp'], st['spread']
    if L < 10:   # collapsed to a single value
        r = int(st['r'])
        dot = cached(('dot', r), lambda: card_ss(2 * r, 2 * r, face=VIO, radius=999, shadow=4))
        put(fr, dot, cx, cy); return
    u = np.linspace(-1, 1, 280)
    w = int(L + 60); h = int(amp * 2.8 + sp * 2 + 70)
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    chans = [(1, VIO)] + ([(0, INK), (2, TAN)] if sp > 1.5 else [])
    for k, col in sorted(chans, key=lambda c: c[0] != 1):
        y = sig_y(u, t + k * 37, st) * amp + (k - 1) * sp
        pts = [((x + w / 2) * SS, (yy + h / 2) * SS) for x, yy in zip(u * L / 2, y)]
        d.line(pts, fill=col, width=3 * SS, joint='curve')
    im = im.resize((w, h), Image.LANCZOS)
    fr.paste(im, (int(cx - w / 2), int(cy - h / 2)), im)

def impact_ticks(d, cx, cy, df, r0=70, n=6, col=TAN, rot=0, ey=1.0):
    if df < 0 or df > 9: return
    t = df / 9
    for k in range(n):
        a = math.radians(rot + k * 360 / n)
        r1 = r0 + 60 * e_out(t); r2 = r1 + 36 * (1 - t)
        d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a) * ey), (cx + r2 * math.cos(a), cy + r2 * math.sin(a) * ey)], fill=col, width=6)

# ------------------------------------------------------------------ tiny flat-shaded 3D engine (painter's algorithm, ink outlines, hard shadow)
def _n(v):
    v = np.asarray(v, float); return v / (np.linalg.norm(v) + 1e-9)
def rotm(ax, ay, az=0.0):
    ca, sa, cb, sb, cc, sc = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]]); Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    Rz = np.array([[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]])
    return Rz @ Rx @ Ry
LIGHT = _n([-0.45, 0.75, 0.55])

class Mesh:
    def __init__(self, faces):
        self.P, self.C, self.N = [], [], []
        self.O = []
        for fc in faces:
            p, c, ref = fc[:3]; self.O.append(fc[3] if len(fc) > 3 else True)
            p = np.asarray(p, float); n = _n(sum(np.cross(p[i], p[(i + 1) % len(p)]) for i in range(len(p))))
            if np.dot(n, p.mean(0) - np.asarray(ref, float)) < 0: n = -n
            self.P.append(p); self.C.append(c); self.N.append(n)

def draw_mesh(mesh, R, scale, sx=1.0, sy=1.0, shadow=6, outline=2):
    proj = []; ext = 1.0
    for p, n, c, ol in zip(mesh.P, mesh.N, mesh.C, mesh.O):
        nn = R @ n
        if nn[2] <= 1e-3: continue
        q = p @ R.T
        xy = np.stack([q[:, 0] * scale * sx, -q[:, 1] * scale * sy], 1)
        ext = max(ext, float(np.abs(xy).max()))
        k = 0.62 + 0.38 * clamp((float(np.dot(nn, LIGHT)) + 0.2) / 0.9)
        proj.append((float(q[:, 2].mean()), xy, tuple(int(v * k) for v in c), ol))
    half = int(ext + shadow + 12); o = half * SS
    im = Image.new('RGBA', (2 * o, 2 * o), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    proj.sort(key=lambda t: t[0])
    if shadow:
        for _, xy, _, _ in proj: d.polygon([(o + (x + shadow) * SS, o + (y + shadow) * SS) for x, y in xy], fill=INK)
    for _, xy, col, ol in proj:
        d.polygon([(o + x * SS, o + y * SS) for x, y in xy], fill=col, outline=INK if ol else col, width=max(1, int(outline * SS)) if ol else 2)
    return finish(im, 0)

def icosphere(sub=1):
    t = (1 + 5 ** .5) / 2
    V = [list(_n(v)) for v in [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]]
    Fc = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(sub):
        cache = {}; nf = []
        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache: V.append(list(_n(np.add(V[a], V[b]) / 2))); cache[k] = len(V) - 1
            return cache[k]
        for a, b, c in Fc:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a); nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        Fc = nf
    return np.array(V), Fc

ROCK = (190, 184, 172)
def rock_mesh():
    V, Fc = icosphere(1); r = np.random.RandomState(4)
    V = V * r.uniform(.84, 1.12, (len(V), 1)) * np.array([1.3, .8, 1.0])
    V[:, 1] = np.where(V[:, 1] < -.5, -.5 + (V[:, 1] + .5) * .15, V[:, 1])
    cols = [ROCK if r.rand() > .12 else (206, 200, 188) for _ in Fc]
    return Mesh([(V[list(fc)], cols[i], (0, 0, 0)) for i, fc in enumerate(Fc)])

def box_faces(c, s, cols):
    cx, cy, cz = c; sx, sy, sz = s
    v = np.array([[cx + x * sx, cy + y * sy, cz + z * sz] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)])
    quads = {'+x': [4, 5, 7, 6], '-x': [0, 2, 3, 1], '+y': [2, 6, 7, 3], '-y': [0, 1, 5, 4], '+z': [1, 3, 7, 5], '-z': [0, 4, 6, 2]}
    return [(v[q], cols.get(k, cols.get('*', CARD)), c) for k, q in quads.items()]

def cube_mesh():
    return Mesh(box_faces((0, 0, 0), (1, 1, 1), {'+z': VIO, '+x': TAN, '+y': CARD, '-x': PINK, '-z': PINK, '-y': TAN}))

def chip_mesh():
    f = box_faces((0, 0, 0), (1.0, .09, .72), {'*': CARD})
    f += box_faces((0, .16, 0), (.42, .07, .32), {'*': VIO})
    f += box_faces((.72, .12, .48), (.08, .04, .08), {'*': TAN})
    for i in range(6):
        x = -.75 + i * .3
        for z in (.84, -.84): f += box_faces((x, -.03, z), (.06, .03, .12), {'*': (205, 200, 214)})
    return Mesh(f)

def spark_mesh():
    ts = np.linspace(0, 2 * math.pi, 64, endpoint=False); h = .11
    pts = np.stack([np.sign(np.cos(ts)) * np.abs(np.cos(ts)) ** 3, np.sign(np.sin(ts)) * np.abs(np.sin(ts)) ** 3], 1)
    front = np.c_[pts, np.full(len(pts), h)]; back = np.c_[pts, np.full(len(pts), -h)]
    f = [(front, WHITE, (0, 0, 0)), (back[::-1], WHITE, (0, 0, 0))]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        f.append((np.array([front[i], front[j], back[j], back[i]]), (236, 232, 250), (0, 0, 0), False))
    return Mesh(f)

MESH = {}
def mesh(name, fn):
    if name not in MESH: MESH[name] = fn()
    return MESH[name]


# ------------------------------------------------------------------ cache control, grain, timing
def clear_cache():
    """call when a scene changes so sprite memory doesn't pile up"""
    _cache.clear()

def grain(fr, f, strength=13):
    """~5% fractal grain, regenerated every frame (deterministic per frame number)"""
    a = np.asarray(fr, dtype=np.int16); g = np.random.default_rng(f)
    h, w = a.shape[:2]
    n1 = g.random((h, w), dtype=np.float32)
    n2 = np.repeat(np.repeat(g.random((h // 2, w // 2), dtype=np.float32), 2, 0), 2, 1)
    n3 = np.repeat(np.repeat(g.random((h // 4, w // 4), dtype=np.float32), 4, 0), 4, 1)
    n = (0.5 * n1 + 0.3 * n2 + 0.2 * n3 - 0.5) * 2 * strength
    return np.clip(a + n.astype(np.int16)[..., None], 0, 255).astype(np.uint8)

def T(seconds, offset=0.0):
    """a time in the voice track (seconds) -> frame number"""
    return int(round((seconds - offset) * FPS))
