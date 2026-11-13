"""align.py <reelDir>: script.json + asr.json (faster-whisper words) + voice.mp3 -> timing.json, amp.json.
Subtitles show the script's words; timings come from the speaker's real delivery."""
import json, re, sys, os, subprocess, difflib
import numpy as np
d = sys.argv[1]
sc = json.load(open(os.path.join(d, 'script.json')))['sentences']
asr = json.load(open(os.path.join(d, 'asr.json')))
def norm(w):
    w = re.sub(r'[^a-z0-9]', '', w.lower())
    for a, b in (('aa','a'),('ee','i'),('oo','u'),('sh','s'),('ph','f'),('z','j'),('w','v'),('y','i'),('h','')):
        w = w.replace(a, b)
    return re.sub(r'(.)\1+', r'\1', w)
A = [(norm(x['w']), x['s'], x['e']) for s in asr for x in s['words'] if norm(x['w'])]
T = []  # script tokens: (norm, sentence index)
for i, s in enumerate(sc):
    for w in s['text'].split():
        if norm(w): T.append((norm(w), i))
sm = difflib.SequenceMatcher(None, [t[0] for t in T], [a[0] for a in A], autojunk=False)
st = [None]*len(T); en = [None]*len(T)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        st[blk.a+k] = A[blk.b+k][1]; en[blk.a+k] = A[blk.b+k][2]
# interpolate unmatched tokens
known = [k for k in range(len(T)) if st[k] is not None]
for k in range(len(T)):
    if st[k] is None:
        lo = max([j for j in known if j < k], default=None); hi = min([j for j in known if j > k], default=None)
        a0 = en[lo] if lo is not None else 0.0; b0 = st[hi] if hi is not None else A[-1][2]
        n0 = (lo if lo is not None else -1); n1 = (hi if hi is not None else len(T))
        f0 = (k - n0) / (n1 - n0); f1 = (k + 1 - n0) / (n1 - n0)
        st[k] = a0 + (b0 - a0) * f0; en[k] = a0 + (b0 - a0) * f1
S = []
for i, s in enumerate(sc):
    ks = [k for k in range(len(T)) if T[k][1] == i]
    S.append({'text': s['text'], 'scene': s['scene'], 'start': round(st[ks[0]], 3), 'end': round(en[ks[-1]], 3)})
scenes = []
for s in S:
    if not scenes or scenes[-1]['i'] != s['scene']:
        scenes.append({'i': s['scene'], 'start': 0 if not scenes else round(s['start'] - 0.12, 3)})
mp3 = os.path.join(d, 'voice.mp3')
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mp3]))
total = round(min(dur, S[-1]['end'] + 1.4), 2)
json.dump({'duration': total, 'sentences': S, 'scenes': scenes}, open(os.path.join(d, 'timing.json'), 'w'), indent=1)
pcm = subprocess.check_output(['ffmpeg','-v','error','-i',mp3,'-ac','1','-ar','16000','-f','s16le','-'])
x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)/32768; hop = 16000//30
r = np.array([np.sqrt(np.mean(x[i:i+hop]**2)) for i in range(0, len(x), hop)])
r = np.clip(r/(np.percentile(r, 95)+1e-6), 0, 1); r[r < 0.12] = 0
json.dump({'fps': 30, 'rms': [round(float(v),3) for v in r]}, open(os.path.join(d, 'amp.json'), 'w'))
matched = sum(1 for k in range(len(T)) if k in set(known)); print(f'matched {matched}/{len(T)} script words')
for s in S: print(f"{s['start']:6.2f}-{s['end']:6.2f} sc{s['scene']:<2} {s['text']}")
print('duration', total)
