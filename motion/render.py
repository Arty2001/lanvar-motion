"""Render a project.

  python -m motion.render PROJECT preview 0 120 450 ...   still frames + a contact sheet (fast, for checking)
  python -m motion.render PROJECT video [START END]        silent master, CRF 18 H.264 (out/video.mp4)
  python -m motion.render PROJECT final                    master + voice + phone preview (out/final.mp4, out/final_preview.mp4)

A project is a folder with scenes.py defining FRAMES (int), render(f) -> PIL RGB image,
and optionally AUDIO (a file name inside the project folder)."""
import sys, os, subprocess, importlib.util, time
import numpy as np
from PIL import Image
from motion.core import W, H, FPS, grain

def load(project):
    path = os.path.join(project, 'scenes.py')
    spec = importlib.util.spec_from_file_location('scenes', path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def ff(*args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)

def preview(mod, out, frames):
    ims = []
    for f in frames:
        im = Image.fromarray(grain(mod.render(f), f)); p = os.path.join(out, 'frame_%05d.png' % f); im.save(p); ims.append(im)
        print('wrote', p)
    cols = min(6, len(ims)); rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 364, rows * 644), (60, 60, 60))
    for i, im in enumerate(ims): sheet.paste(im.resize((360, 640)), ((i % cols) * 364, (i // cols) * 644))
    sheet.save(os.path.join(out, 'contact_sheet.png')); print('wrote', os.path.join(out, 'contact_sheet.png'))

def video(mod, out, a=0, b=None):
    b = mod.FRAMES if b is None else b
    dst = os.path.join(out, 'video.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', dst],
                         stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(a, b):
        p.stdin.write(grain(mod.render(f), f).tobytes())
        if f % 100 == 0:
            done = f - a + 1; eta = (time.time() - t0) / done * (b - f)
            print('frame %d / %d   ~%d s left' % (f, b, eta), flush=True)
    p.stdin.close(); p.wait(); print('wrote', dst); return dst

def final(mod, project, out):
    src = video(mod, out)
    dur = mod.FRAMES / FPS
    audio = getattr(mod, 'AUDIO', None)
    dst = os.path.join(out, 'final.mp4')
    if audio:
        ff('-i', src, '-i', os.path.join(project, audio), '-filter_complex', '[1:a]apad[a]', '-map', '0:v', '-map', '[a]',
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', '%.4f' % dur, '-movflags', '+faststart', dst)
    else:
        ff('-i', src, '-c', 'copy', '-movflags', '+faststart', dst)
    ff('-i', dst, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '26', '-pix_fmt', 'yuv420p', '-c:a', 'copy',
       '-movflags', '+faststart', os.path.join(out, 'final_preview.mp4'))
    print('wrote', dst, 'and final_preview.mp4')

if __name__ == '__main__':
    project, mode, rest = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3:]]
    out = os.path.join(project, 'out'); os.makedirs(out, exist_ok=True)
    mod = load(project)
    if mode == 'preview': preview(mod, out, rest or [0, mod.FRAMES // 4, mod.FRAMES // 2, 3 * mod.FRAMES // 4, mod.FRAMES - 1])
    elif mode == 'video': video(mod, out, *(rest or []))
    elif mode == 'final': final(mod, project, out)
    else: sys.exit(__doc__)
