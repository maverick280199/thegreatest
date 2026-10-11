"""Cut the nine cards to the narration and mux. Usage: python3 -I assemble.py <vid_dir> <vo.mp3> <out.mp4>"""
import re, subprocess, sys

D, VO, OUT = sys.argv[1:4]
SEGS = [
    "Your client's cheque bounced? You have 30 days to act, but almost nobody knows what to send before the clock runs out.",
    "Here's the full clock under Section 138 of the Negotiable Instruments Act.",
    "One: present the cheque within three months of its date.",
    "Two: when it bounces, send a written legal notice within thirty days of the bank's return memo.",
    "Three: give them fifteen full days to pay. File early, and the Supreme Court says your complaint is premature.",
    "Four: if they still don't pay, file your complaint within one month, in the court where your own bank branch is.",
    "And if a company issued the cheque, make the company an accused, not just the director.",
    "Three months. Thirty days. Fifteen days. One month.",
    "Save this before the next cheque bounces. General information, not legal advice.",
]
CARD_LEN = [9, 8, 7, 9, 10, 10, 9, 7, 9]

def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True)

dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VO).stdout)
log = run("ffmpeg", "-i", VO, "-af", "silencedetect=n=-35dB:d=0.25", "-f", "null", "-").stderr
sil = [(float(a), float(b)) for a, b in zip(re.findall(r"silence_start: ([\d.]+)", log),
                                             re.findall(r"silence_end: ([\d.]+)", log))]
mids = [(a + b) / 2 for a, b in sil]

# Proportional estimate of each boundary, snapped to the nearest pause.
total = sum(len(s) for s in SEGS)
cuts, acc = [], 0
for s in SEGS[:-1]:
    acc += len(s)
    est = dur * acc / total
    near = min(mids, key=lambda m: abs(m - est)) if mids else est
    cuts.append(near if abs(near - est) < 2.0 else est)
if len(sys.argv) > 4:  # explicit cut points, comma-separated seconds
    cuts = [float(x) for x in sys.argv[4].split(",")]
bounds = [0.0] + cuts + [dur + 0.6]
lens = [round(b - a, 3) for a, b in zip(bounds, bounds[1:])]
print("voiceover", round(dur, 2), "s; card windows", lens)

# Each window must fit inside its card; pad by holding the last frame if not.
parts = []
for i, L in enumerate(lens, 1):
    p = f"{D}/p{i}.mp4"
    pad = max(0.0, L - CARD_LEN[i - 1])
    vf = f"tpad=stop_mode=clone:stop_duration={pad:.3f}," if pad else ""
    run("ffmpeg", "-y", "-loglevel", "error", "-i", f"{D}/c{i}.mp4", "-t", f"{L}",
        "-vf", vf + "fps=30,format=yuv420p", "-an", "-c:v", "libx264", "-crf", "20", p)
    parts.append(p)
with open(f"{D}/list.txt", "w") as f:
    f.writelines(f"file '{p}'\n" for p in parts)
run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{D}/list.txt",
    "-i", VO, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-af", "apad", "-shortest", "-movflags", "+faststart", OUT)
print("wrote", OUT)
