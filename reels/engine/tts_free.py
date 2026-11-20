"""tts_free.py <reelDir> [voice] [speed]: free local AI voice (Kokoro-82M, Apache-2.0, Hindi voices).
Reads voice_hi.txt (one Devanagari line per script.json sentence), writes voice.mp3 + exact timing.json + amp.json.
Model files: $KOKORO_DIR/model.onnx and voices.npz (download: huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX)."""
import json, os, sys, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
d = sys.argv[1]; voice = sys.argv[2] if len(sys.argv) > 2 else 'hm_psi'; speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.05
K = os.environ.get('KOKORO_DIR', os.path.expanduser('~/.cache/kokoro'))
k = Kokoro(os.path.join(K, 'model.onnx'), os.path.join(K, 'voices.npz'))
sc = json.load(open(os.path.join(d, 'script.json')))['sentences']
hi = [l.strip() for l in open(os.path.join(d, 'voice_hi.txt'), encoding='utf-8') if l.strip()]
assert len(hi) == len(sc), f'{len(hi)} voice lines vs {len(sc)} script sentences'
GAP, LEAD = 0.38, 0.25
chunks, S, t, sr = [], [], LEAD, 24000
for s, line in zip(sc, hi):
    a, sr = k.create(line, voice=voice, speed=speed, lang='hi')
    a = np.trim_zeros(a, 'fb')
    S.append({'text': s['text'], 'scene': s['scene'], 'start': round(t, 3), 'end': round(t + len(a) / sr, 3)})
    chunks += [a, np.zeros(int(GAP * sr), dtype=a.dtype)]; t += len(a) / sr + GAP
audio = np.concatenate([np.zeros(int(LEAD * sr), dtype=chunks[0].dtype)] + chunks)
wav = os.path.join(d, 'voice.wav'); sf.write(wav, audio, sr)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '44100', '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(d, 'voice.mp3')], check=True)
os.remove(wav)
scenes = []
for s in S:
    if not scenes or scenes[-1]['i'] != s['scene']:
        scenes.append({'i': s['scene'], 'start': 0 if not scenes else round(s['start'] - 0.12, 3)})
json.dump({'duration': round(t + 1.0, 2), 'sentences': S, 'scenes': scenes}, open(os.path.join(d, 'timing.json'), 'w'), indent=1, ensure_ascii=False)
x = audio.astype(np.float32); hop = sr // 30
r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
r = np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1); r[r < 0.12] = 0
json.dump({'fps': 30, 'rms': [round(float(v), 3) for v in r]}, open(os.path.join(d, 'amp.json'), 'w'))
print(f'voice={voice} duration={t:.1f}s sentences={len(S)}')
