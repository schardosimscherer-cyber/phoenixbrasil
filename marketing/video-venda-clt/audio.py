"""Score + sound effects for the Phoenix Brasil sales video, synthesized in code.

usage: python3 audio.py cues.json out.wav
cues.json comes from `node render.js cues <query> cues.json` and carries duration, bpm and the
SFX hit list placed on the same beat grid as the animation. No samples, no third-party audio.

Phone speakers barely reproduce < 150 Hz, so the kick and bass carry harmonics up into the mids.
"""
import json
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(2024)


# ---------- building blocks ----------

def t_axis(n):
    return np.arange(n) / SR


def env(n, a, d):
    t = t_axis(n)
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-t / d)


def adsr(n, a, r):
    """Attack, hold, release envelope over n samples."""
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def osc_sine(f, n, ph=0.0):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return np.sin(ph + 2 * np.pi * np.cumsum(f) / SR)


def osc_saw(f, n, top=7000):
    """Band-limited saw (additive)."""
    out = np.zeros(n)
    k = 1
    while k * f < top and k < 60:
        out += np.sin(2 * np.pi * k * f * t_axis(n) + rng.uniform(0, 0.2)) / k
        k += 1
    return out * 0.6


def osc_square(f, n, top=6000):
    out = np.zeros(n)
    k = 1
    while k * f < top:
        out += np.sin(2 * np.pi * k * f * t_axis(n)) / k
        k += 2
    return out * 0.7


def fft_filter(x, lo=None, hi=None, order=2):
    """Zero-phase Butterworth-shaped magnitude filter in the frequency domain."""
    n = len(x)
    size = 1 << int(np.ceil(np.log2(max(n, 2))))
    X = np.fft.rfft(x, size)
    f = np.fft.rfftfreq(size, 1 / SR)
    g = np.ones_like(f)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * g, size)[:n]


def noise(n):
    return rng.standard_normal(n)


def place(buf, s, start):
    start = int(start)
    if start >= len(buf): return
    end = min(len(buf), start + len(s))
    if start < 0:
        s = s[-start:]; start = 0; end = min(len(buf), len(s))
    buf[start:end] += s[:end - start]


# ---------- score instruments ----------

def kick():
    n = int(0.42 * SR)
    f = 62 + 120 * np.exp(-t_axis(n) / 0.035)
    body = osc_sine(f, n) * env(n, 0.001, 0.16)
    body = np.tanh(2.6 * body)                       # saturation → audible harmonics
    click = fft_filter(noise(n), lo=2500) * env(n, 0.0002, 0.004) * 0.5
    return 0.9 * body + click


def clap():
    n = int(0.3 * SR)
    x = fft_filter(noise(n), lo=900, hi=5000)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        s = int(o * SR)
        e[s:] += env(n - s, 0.0005, 0.012 if o < 0.02 else 0.11)
    return 0.55 * x * e


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    x = fft_filter(noise(n), lo=7000)
    return 0.22 * x * env(n, 0.0005, 0.06 if open_ else 0.014)


def bass_note(freq, dur):
    n = int(dur * SR)
    x = osc_saw(freq, n, top=4000)
    x = fft_filter(x, hi=2200)
    return 0.42 * x * adsr(n, 0.004, 0.04) * (0.6 + 0.4 * env(n, 0.001, 0.25))


def pad_chord(freqs, dur, bright=2600):
    n = int(dur * SR)
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            x += osc_saw(f * 2 ** (det / 12), n, top=bright * 2)
    x = fft_filter(x, hi=bright)
    return 0.05 * x * adsr(n, 0.25, 0.3)


def pluck(freq, dur=0.3):
    n = int(dur * SR)
    x = osc_square(freq, n) * 0.6 + osc_saw(freq * 2, n) * 0.25
    x = fft_filter(x, hi=4500)
    return 0.16 * x * env(n, 0.002, 0.09)


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


# A minor: Am – F – C – G (one chord per bar)
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
ROOTS = [45, 41, 48, 43]  # A2 F2 C3 G2


def score(duration, bpm):
    b = 60 / bpm
    n = int((duration + 1.0) * SR)
    drums, bass, pads, arp = (np.zeros(n) for _ in range(4))
    duck = np.ones(n)
    total_beats = int(duration / b)
    end_beat = 36                       # end card: switch to half-time + resolve
    K, C = kick(), clap()

    for beat in range(total_beats + 1):
        t0 = beat * b
        s = int(t0 * SR)
        bar = beat // 4
        chord = CHORDS[bar % 4]
        root = ROOTS[bar % 4]
        pre_end = beat < end_beat
        # drums
        if pre_end or beat in (36, 38, 40, 42):
            place(drums, K, s)
            dk = 1 - 0.55 * env(int(0.25 * SR), 0.003, 0.09)
            duck[s:s + len(dk)] = np.minimum(duck[s:s + len(dk)], dk[:max(0, min(len(dk), n - s))])
        if pre_end and beat % 2 == 1 and beat >= 4:
            place(drums, C, s)
        if pre_end:
            place(drums, hat(), s + int(b / 2 * SR))
            if beat >= 12:
                place(drums, hat() * 0.6, s + int(b / 4 * SR))
                place(drums, hat() * 0.6, s + int(3 * b / 4 * SR))
        # bass: 8ths with octave bounce
        if pre_end:
            for k in range(2):
                f = midi(root + (12 if k == 1 and beat >= 12 else 0))
                place(bass, bass_note(f, b / 2 * 0.92), s + int(k * b / 2 * SR))
        # pads once per bar
        if beat % 4 == 0 and beat < 44:
            bright = 1400 if beat < 12 else 2800
            place(pads, pad_chord([midi(m) for m in chord], 4 * b + 0.3, bright), s)
        # arp in the middle section
        if 12 <= beat < 36:
            seq = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 24]
            for k in range(4):
                place(arp, pluck(midi(seq[(beat * 4 + k) % 4])), s + int(k * b / 4 * SR))
    # resolution: long C-major chord + low root under the end card
    s = int(44 * b * SR)
    place(pads, pad_chord([midi(m) for m in (48, 55, 60, 64, 67)], 7 * b + 1.0, 2400) * 1.6, s)
    place(bass, bass_note(midi(36), 5 * b) * 0.9, s)
    mix = drums * 0.9 + (bass * 0.8 + pads + arp * 0.8) * duck
    return mix[:int(duration * SR)]


# ---------- sound effects ----------

def sfx_whoosh(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / n
    x = noise(n)
    lo = fft_filter(x, lo=400, hi=1500); hi = fft_filter(x, lo=1500, hi=6000)
    w = np.sin(np.pi * t) ** 1.5
    return 0.45 * (lo * (1 - t) + hi * t) * w


def sfx_hit():
    n = int(0.5 * SR)
    f = 90 + 220 * np.exp(-t_axis(n) / 0.02)
    body = np.tanh(3 * osc_sine(f, n) * env(n, 0.001, 0.12))
    snap = fft_filter(noise(n), lo=1200, hi=7000) * env(n, 0.0005, 0.03)
    return 0.6 * body + 0.35 * snap


def sfx_tick():
    n = int(0.03 * SR)
    return 0.55 * osc_sine(2400 * (1 + 0.03 * rng.standard_normal()), n) * env(n, 0.0005, 0.008)


def sfx_tick2():
    n = int(0.06 * SR)
    return 0.5 * osc_sine(1600, n) * env(n, 0.0005, 0.015)


def sfx_pop():
    n = int(0.14 * SR)
    return 0.7 * osc_sine(np.linspace(900, 380, n), n) * env(n, 0.001, 0.045)


def sfx_swipe():
    n = int(0.35 * SR); t = np.arange(n) / n
    return 0.35 * fft_filter(noise(n), lo=2500, hi=9000) * np.sin(np.pi * t) ** 2


def sfx_slash():
    n = int(0.3 * SR)
    x = fft_filter(noise(n), lo=1500, hi=8000) * env(n, 0.002, 0.06)
    return 0.6 * x + 0.4 * np.tanh(3 * osc_sine(np.linspace(300, 80, n), n) * env(n, 0.001, 0.08))


def sfx_bell(freqs, dur, decay, gain):
    n = int(dur * SR)
    return gain * sum(a * osc_sine(f, n) * env(n, 0.002, decay * d) for f, a, d in freqs)


def sfx_ding():
    return sfx_bell([(1318.5, 1, 1), (2637, 0.4, 0.6), (3951, 0.15, 0.4)], 1.6, 0.5, 0.4)


def sfx_shimmer():
    n = int(1.0 * SR); out = np.zeros(n)
    for i, f in enumerate((2093, 2637, 3136, 4186)):
        s = int(i * 0.06 * SR)
        out[s:] += 0.2 * osc_sine(f, n - s) * env(n - s, 0.002, 0.2)
    return out


def sfx_stamp():
    n = int(0.6 * SR)
    thud = np.tanh(4 * osc_sine(np.linspace(180, 60, n), n) * env(n, 0.001, 0.09))
    crack = fft_filter(noise(n), lo=800, hi=6000) * env(n, 0.0005, 0.025)
    return 0.7 * thud + 0.5 * crack


def sfx_riser(dur=0.6):
    n = int(dur * SR); t = np.arange(n) / n
    x = fft_filter(noise(n), lo=800, hi=8000)
    return 0.35 * x * t ** 2


def sfx_boom():
    n = int(2.8 * SR)
    f = 70 + 80 * np.exp(-t_axis(n) / 0.06)
    sub = np.tanh(2.2 * osc_sine(f, n) * env(n, 0.003, 0.8))
    air = fft_filter(noise(n), lo=200, hi=1500) * env(n, 0.002, 0.3) * 0.25
    return 0.9 * (sub + air)


SFX = {'whoosh': sfx_whoosh, 'hit': sfx_hit, 'tick': sfx_tick, 'tick2': sfx_tick2, 'pop': sfx_pop,
       'swipe': sfx_swipe, 'slash': sfx_slash, 'ding': sfx_ding, 'shimmer': sfx_shimmer,
       'stamp': sfx_stamp, 'riser': sfx_riser, 'boom': sfx_boom}


def reverb(x, seconds=1.2, mix=0.14):
    n = int(seconds * SR)
    ir = fft_filter(noise(n), hi=5000) * np.exp(-np.arange(n) / (0.25 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    return x + mix * np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]


def main(cue_path, out_path):
    data = json.load(open(cue_path))
    dur, bpm = data['duration'], data['bpm']
    n = int(dur * SR)
    music = score(dur, bpm)
    L = np.zeros(n); R = np.zeros(n)
    for c in data['cues']:
        s = SFX[c['type']]() * c.get('gain', 1)
        start = int(c['t'] * SR)
        if c['type'] == 'riser': start -= len(s) - int(0.55 * 60 / bpm * SR)
        pan = 0.5 if c['type'] in ('boom', 'hit', 'stamp', 'riser') else 0.5 + 0.15 * rng.uniform(-1, 1)
        place(L, s * np.cos(pan * np.pi / 2) * 1.414, start)
        place(R, s * np.sin(pan * np.pi / 2) * 1.414, start)
    L, R = reverb(L), reverb(R)
    m = reverb(music, 1.6, 0.18)
    # music sits under the effects
    L = L + 0.75 * m[:n]; R = R + 0.75 * m[:n]
    # short fade-out on the tail
    f = int(1.2 * SR); L[-f:] *= np.linspace(1, 0, f); R[-f:] *= np.linspace(1, 0, f)
    # phone-speaker master: cut sub rumble, lift presence so the mix reads on small speakers
    def master(x):
        x = fft_filter(x, lo=95, order=3)
        pres = fft_filter(x, lo=1200, hi=5000)
        return x + 0.6 * pres
    L, R = master(L), master(R)
    peak = max(np.abs(L).max(), np.abs(R).max())
    pcm = (np.stack([L, R], 1) / peak * 0.89 * 32767).astype(np.int16)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
