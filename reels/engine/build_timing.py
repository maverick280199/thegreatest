"""build_timing.py <reelDir>: reads script.json + voice.mp3 -> timing.json, amp.json"""
import json, re, subprocess, sys, os
import numpy as np
d = sys.argv[1]
sc = json.load(open(os.path.join(d, 'script.json')))
sents = [(s['text'], s['scene']) for s in sc['sentences']]
mp3 = os.path.join(d, 'voice.mp3')
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mp3]))
log = subprocess.run(['ffmpeg','-hide_banner','-i',mp3,'-af','silencedetect=noise=-35dB:d=0.15','-f','null','-'],capture_output=True,text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
sil = [(a,b) for a,b in zip(st,en) if a > 0.05 and b < dur-0.05]
lead = en[0] if st and st[0] <= 0.05 else 0.0
tail = st[-1] if len(st) > len(en) or (st and en and st[-1] > en[-1]) else dur
# expected sentence ends by character share
L = [len(t) + 6 for t,_ in sents]; tot = sum(L); acc = 0; exp = []
for l in L[:-1]:
    acc += l; exp.append(lead + (tail-lead)*acc/tot)
chosen = []; j = 0
for k, e in enumerate(exp):
    remaining = len(exp) - k - 1
    cands = [i for i in range(j, len(sil) - remaining)]
    i = min(cands, key=lambda i: abs((sil[i][0]+sil[i][1])/2 - e)); chosen.append(i); j = i + 1
bounds = [lead] + [ (sil[i][0], sil[i][1]) for i in chosen ]
S = []; start = lead
for k,(t,s) in enumerate(sents):
    end = sil[chosen[k]][0] if k < len(chosen) else tail
    S.append({'text': t, 'scene': s, 'start': round(start,3), 'end': round(end,3)})
    if k < len(chosen): start = sil[chosen[k]][1]
scenes = []
for s in S:
    if not scenes or scenes[-1]['i'] != s['scene']:
        scenes.append({'i': s['scene'], 'start': 0 if not scenes else s['start'] - 0.15})
total = round(tail + 1.2, 2)
json.dump({'duration': total, 'sentences': S, 'scenes': scenes}, open(os.path.join(d,'timing.json'),'w'), indent=1)
pcm = subprocess.check_output(['ffmpeg','-v','error','-i',mp3,'-ac','1','-ar','16000','-f','s16le','-'])
x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)/32768; hop = 16000//30
r = np.array([np.sqrt(np.mean(x[i:i+hop]**2)) for i in range(0, len(x), hop)])
r = np.clip(r/ (np.percentile(r, 95) + 1e-6), 0, 1); r[r < 0.12] = 0
json.dump({'fps': 30, 'rms': [round(float(v),3) for v in r]}, open(os.path.join(d,'amp.json'),'w'))
for s in S: print(f"{s['start']:6.2f}-{s['end']:6.2f} sc{s['scene']} {s['text']}")
print('duration', total)
