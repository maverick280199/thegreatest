"""sfx.py <reelDir> : synthesise sound effects (procedural, no licences) at events.json cues, mix under voice.mp3 -> mix.mp3"""
import json, os, sys, subprocess
import numpy as np
SR = 44100; rng = np.random.default_rng(7)
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, k):  # crude one-pole low-pass
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y
def hp(x, k): return x - lp(x, k)
def stamp():
    n = int(.45 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (95 * np.exp(-t * 9) + 45) * t) * env(n, .001, .12)
    slap = lp(rng.standard_normal(n), .25) * env(n, .0005, .03)
    return 0.9 * thump + 0.6 * slap
def paper():
    n = int(.38 * SR); x = hp(rng.standard_normal(n), .08)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2 * (0.6 + 0.4 * np.sin(np.linspace(0, 18, n)))
    return 0.35 * x * e
def click():
    n = int(.028 * SR); t = np.arange(n) / SR
    return (0.5 * hp(rng.standard_normal(n), .3) * env(n, .0003, .004) + 0.35 * np.sin(2 * np.pi * 1900 * t) * env(n, .0003, .006))
def typing(chars):
    k = max(3, min(int(chars), 40)); dur = k / 28 + .1; out = np.zeros(int(dur * SR))
    for i in range(k):
        s = int((i / 28 + rng.uniform(-.008, .008)) * SR); c = click() * rng.uniform(.6, 1)
        if 0 <= s < len(out) - len(c): out[s:s + len(c)] += c
    return out
def marker():
    n = int(.55 * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * (2300 + 500 * np.sin(2 * np.pi * 3 * t)) * t) * 0.08
    hiss = hp(rng.standard_normal(n), .2) * 0.12
    return (tone + hiss) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
def whoosh(dur=.5, up=True):
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); acc = 0.0
    ks = np.linspace(.02, .25, n) if up else np.linspace(.25, .02, n)
    for i in range(n): acc += ks[i] * (x[i] - acc); out[i] = acc
    return 0.5 * out * np.sin(np.linspace(0, np.pi, n)) ** 2
def crack():
    n = int(1.3 * SR); out = np.zeros(n); t = np.arange(n) / SR
    for _ in range(26):
        s = int(rng.uniform(0, 1.1) * SR); m = int(rng.uniform(.01, .05) * SR)
        out[s:s + m] += hp(rng.standard_normal(m), .35) * env(m, .0005, .01) * rng.uniform(.4, 1)
    rumble = lp(rng.standard_normal(n), .01) * 3 * np.exp(-t * 2.5)
    return 0.6 * out + 0.5 * rumble
def pop():
    n = int(.12 * SR); t = np.arange(n) / SR
    return 0.45 * np.sin(2 * np.pi * (520 + 900 * t / .12) * t) * env(n, .001, .05)
def ticks():
    out = np.zeros(int(1.1 * SR))
    for i in range(14):
        s = int((i * .075 + .02) * SR); c = click() * .7
        out[s:s + len(c)] += c
    return out
GAIN = {'stamp': 1.0, 'paper': .9, 'type': .55, 'marker': .8, 'thread': .5, 'crack': .9, 'pop': .6, 'ticks': .45, 'whoosh': .35, 'scene': .45}
d = sys.argv[1]
ev = json.load(open(os.path.join(d, 'events.json')))
voice = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', os.path.join(d, 'voice.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'])
v = np.frombuffer(voice, dtype=np.float32).copy()
T = json.load(open(os.path.join(d, 'timing.json')))['duration']
fx = np.zeros(max(len(v), int(T * SR)) + SR * 2, dtype=np.float32); last = {}
for e in ev:
    k = e['kind']
    if e['t'] - last.get(k, -9) < .12: continue
    last[k] = e['t']
    s = {'stamp': stamp, 'paper': paper, 'marker': marker, 'crack': crack, 'pop': pop, 'ticks': ticks}.get(k)
    snd = s() if s else typing(e.get('n', 12)) if k == 'type' else whoosh(.55, True) if k == 'thread' else whoosh(.35, False) if k == 'whoosh' else whoosh(.45, False) if k == 'scene' else None
    if snd is None: continue
    i = int(max(0, e['t'] - (.02 if k == 'stamp' else 0)) * SR)
    fx[i:i + len(snd)] += GAIN[k] * snd[:len(fx) - i]
fx = fx / (np.max(np.abs(fx)) + 1e-6) * 0.5
mix = fx.copy(); mix[:len(v)] += v
# light ducking: lower SFX where voice is loud is unnecessary at this level; just limit peaks
mix = np.tanh(mix * 1.1) * 0.95
raw = os.path.join(d, 'mix.f32'); mix.astype(np.float32).tofile(raw)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5', '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(d, 'mix.mp3')], check=True)
os.remove(raw); print('mixed', len(ev), 'cues ->', os.path.join(d, 'mix.mp3'))
