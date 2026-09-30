"""Voice tools.

  python -m motion.audio clean IN OUT.wav [START END]   clean + level a voice take (trim to START..END seconds)
  python -m motion.audio segments VOICE.wav              list every stretch of speech with its frame number
                                                         and a syllable estimate, to match against the script

Cleaning chain: mono, 75 Hz high-pass, light noise reduction, -2.5 dB at 220 Hz (mud),
+2.5 dB at 3.2 kHz (clarity), +1.5 dB at 10 kHz (air), de-esser, 3:1 compressor, peak limiter,
then two-pass loudness normalisation to -14 LUFS / -1.5 dBTP (Instagram / TikTok / Reels level)."""
import sys, json, subprocess, re
import numpy as np

CHAIN = ("pan=mono|c0=0.5*c0+0.5*c1,highpass=f=75,afftdn=nr=10:nf=-52:tn=1,"
         "equalizer=f=220:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=10000:t=q:w=1.5:g=1.5,"
         "deesser=i=0.35,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,"
         "alimiter=limit=0.7:level=false,afade=t=in:d=0.05")

def clean(src, dst, start=None, end=None):
    trim = (['-ss', str(start)] if start is not None else []) + (['-to', str(end)] if end is not None else [])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-y', *trim, '-i', src, '-af', CHAIN + ',loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    ln = ("loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
          "measured_thresh={input_thresh}:offset={target_offset}:linear=true").format(**m)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *trim, '-i', src, '-af', CHAIN + ',' + ln,
                    '-ar', '48000', '-ac', '2', dst], check=True)
    def measure():
        r = subprocess.run(['ffmpeg', '-hide_banner', '-i', dst, '-af', 'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'],
                           capture_output=True, text=True)
        I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1]); P = float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)[-1])
        return I, P
    I, P = measure()
    gain = min(-14.0 - I, -1.5 - P)          # top up to -14 LUFS without pushing peaks past -1.5 dB
    if gain > 0.1:
        tmp = dst + '.tmp.wav'
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', dst, '-af', 'volume=%.2fdB' % gain, tmp], check=True)
        import os; os.replace(tmp, dst); I, P = measure()
    print('wrote %s   loudness %.1f LUFS   peak %.1f dBFS' % (dst, I, P))

def segments(src, fps=30, min_gap=0.12):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', src, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; sr = 16000
    hop = sr // 50; n = len(a) // hop
    db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)]))
    th = np.percentile(db, 20) + 10; m = db > th
    segs, s = [], None
    for i, v in enumerate(m):
        if v and s is None: s = i
        if not v and s is not None: segs.append([s, i]); s = None
    if s is not None: segs.append([s, n])
    merged = []
    for g in segs:
        if merged and g[0] - merged[-1][1] < min_gap * 50: merged[-1][1] = g[1]
        else: merged.append(g)
    merged = [g for g in merged if g[1] - g[0] >= 3]
    # syllable estimate: prominent peaks in 300-3000 Hz band energy (10 ms hop)
    hop2, win = 160, 400; w = np.hanning(win); fr = np.fft.rfftfreq(win, 1 / sr); band = (fr > 300) & (fr < 3000)
    E = np.array([np.sum(np.abs(np.fft.rfft(a[i * hop2:i * hop2 + win] * w))[band] ** 2) for i in range((len(a) - win) // hop2)])
    E = np.convolve(10 * np.log10(E + 1e-9), np.ones(5) / 5, 'same'); mx = np.percentile(E, 95)
    print('  #   start    end   frames        syllables~   (detector usually reads ~70-80% of real syllables)')
    for k, (s0, s1) in enumerate(merged):
        x = E[int(s0 * 2):int(s1 * 2)]; pk, last = 0, -99
        for j in range(2, len(x) - 2):
            if x[j] == max(x[j - 2:j + 3]) and x[j] > mx - 22:
                l = x[max(0, j - 8):j].min(); r = x[j + 1:j + 9].min() if j < len(x) - 1 else x[j]
                if x[j] - max(l, r) > 2.5 and j - last >= 8: pk += 1; last = j
        print('%3d  %6.2f %6.2f   %5d-%-5d   %d' % (k + 1, s0 / 50, s1 / 50, round(s0 / 50 * fps), round(s1 / 50 * fps), pk))

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'clean': clean(sys.argv[2], sys.argv[3], *(float(x) for x in sys.argv[4:6]))
    elif cmd == 'segments': segments(sys.argv[2])
    else: sys.exit(__doc__)
