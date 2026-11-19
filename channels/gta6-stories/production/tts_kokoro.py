"""Free Hinglish voiceover with Kokoro-82M (Apache-2.0), run locally with onnxruntime.

    python tts_kokoro.py <voice> <speed> out.wav text.txt

Setup: apt-get install espeak-ng; pip install kokoro-onnx soundfile. From huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX
download onnx/model.onnx and voices/hm_omega.bin, voices/hm_psi.bin (male Hindi voices), then pack the .bin files into
voices.npz (each is float32 reshaped to (-1, 1, 256)). Write the Hinglish text in Devanagari, with English words spelled
phonetically; the model reads that most naturally. Keep on-screen captions in Roman Hinglish.
"""
import sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro("model.onnx", "voices.npz")
voice, speed, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
text = open(sys.argv[4], encoding="utf-8").read().strip()
samples, sr = k.create(text, voice=voice, speed=speed, lang="hi")
sf.write(out, samples, sr)
print(out, sr, round(len(samples)/sr, 2), "s")
