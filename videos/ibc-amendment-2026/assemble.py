"""Cut cards c1..cN to a voiceover at explicit cut points and mux.
Usage: python3 -I assemble2.py <dir> <vo.mp3> <out.mp4> <cut1,cut2,...>   (N = cuts + 1)"""
import subprocess, sys

D, VO, OUT, CUTS = sys.argv[1:5]

def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True)

def length(p):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p).stdout)

cuts = [float(x) for x in CUTS.split(",")]
bounds = [0.0] + cuts + [length(VO) + 0.6]
lens = [round(b - a, 3) for a, b in zip(bounds, bounds[1:])]
print("card windows", lens)
parts = []
for i, L in enumerate(lens, 1):
    src, p = f"{D}/c{i}.mp4", f"{D}/p{i}.mp4"
    pad = max(0.0, L - length(src))  # hold the last frame if the window outruns the card
    vf = (f"tpad=stop_mode=clone:stop_duration={pad:.3f}," if pad else "") + "fps=30,format=yuv420p"
    run("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-t", f"{L}", "-vf", vf, "-an",
        "-c:v", "libx264", "-crf", "20", p)
    parts.append(p)
with open(f"{D}/list.txt", "w") as f:
    f.writelines(f"file '{p}'\n" for p in parts)
run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{D}/list.txt",
    "-i", VO, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-af", "apad", "-shortest", "-movflags", "+faststart", OUT)
print("wrote", OUT)
