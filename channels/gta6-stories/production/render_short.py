"""Render a vertical 9:16 Short from gameplay segments, voiceover clips and captions.

    <python with Pillow+raqm> render_short.py spec.json

spec.json:
{
  "out": "short.mp4",
  "font": "fonts/nsdl800.ttf",          # Noto Sans Devanagari + Latin, merged (OFL); captions are drawn with Pillow+raqm
  "segments": [                         # played in order
    {"src": "clip.mp4", "start": 12.0, "dur": 5.0, "native": 0.0}   # native = game-audio gain (0 = mute)
  ],
  "voice": [ {"file": "l5.wav", "at": 0.0, "gain": 1.0} ],          # placed on the output timeline
  "captions": [ {"start": 0, "end": 5, "text": "...", "pos": "bottom" | "top"} ],
  "credit": "Gameplay: Champs Network"
}

Layout: blurred, darkened copy of the frame fills 1080x1920; the 16:9 gameplay sits full-width in the middle.
Headline captions go above the gameplay, subtitle captions below it. Only game footage is used: no facecam.
"""
import json
import os
import subprocess
import sys
import tempfile

W, H = 1080, 1920


def render_caption(text, path, size, color, font_path, width=W - 120):
    """Draw one caption to a transparent PNG. Needs Pillow built with raqm, so Hindi conjuncts and matras shape correctly."""
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            trial = (cur + " " + w).strip()
            if font.getlength(trial) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    lh = int(size * 1.45)
    im = Image.new("RGBA", (W, lh * len(lines) + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text((W // 2, 15 + lh * i + lh // 2), ln, font=font, anchor="mm", fill=color,
               stroke_width=max(3, size // 12), stroke_fill="black")
    im.save(path)
    return im.size[1]


def build_overlays(spec, tmp):
    """Return (png paths, overlay filter chain) for the captions and the credit line."""
    font = os.path.abspath(spec.get("font", "fonts/nsdl800.ttf"))
    total = sum(s["dur"] for s in spec["segments"])
    items = []
    for k, c in enumerate(spec.get("captions", [])):
        top = c.get("pos") == "top"
        png = os.path.join(tmp, f"cap{k:02d}.png")
        h = render_caption(c["text"], png, 76 if top else 60, "white" if top else "#FFE600", font)
        y = 300 if top else 1360
        items.append((png, y, c["start"], c["end"]))
    if spec.get("credit"):
        png = os.path.join(tmp, "credit.png")
        render_caption(spec["credit"], png, 30, "white", font)
        items.append((png, 1790, 0, total))
    return items


def main(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(spec_path))
    os.chdir(base)
    tmp = tempfile.mkdtemp(dir=base)
    parts = []
    for i, s in enumerate(spec["segments"]):
        p = os.path.join(tmp, f"seg{i:02d}.mp4")
        vf = (
            "split[a][b];"
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:4,eq=brightness=-0.25[bg];"
            f"[b]scale={W}:-2[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30,format=yuv420p"
        )
        af = f"volume={s.get('native', 0.0)},aresample=48000,aformat=channel_layouts=stereo"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-ss", str(s["start"]), "-t", str(s["dur"]), "-i", s["src"],
             "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]", "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "pcm_s16le", p],
            check=True,
        )
        parts.append(p)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    joined = os.path.join(tmp, "joined.mkv")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined], check=True)

    total = sum(s["dur"] for s in spec["segments"])
    overlays = build_overlays(spec, tmp)

    inputs = ["-i", joined]
    mix = ["[0:a]anull[g]"]
    labels = ["[g]"]
    for j, v in enumerate(spec.get("voice", [])):
        inputs += ["-i", v["file"]]
        ms = int(v["at"] * 1000)
        mix.append(f"[{j + 1}:a]aresample=48000,aformat=channel_layouts=stereo,volume={v.get('gain', 1.0)},adelay={ms}|{ms}[v{j}]")
        labels.append(f"[v{j}]")
    mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    n_audio = len(inputs) // 2
    vchain, last = [], "[0:v]"
    for k, (png, y, t0, t1) in enumerate(overlays):
        inputs += ["-loop", "1", "-i", png]
        idx = n_audio + k
        out = f"[ov{k}]"
        vchain.append(f"{last}[{idx}:v]overlay=0:{y}:enable='between(t,{t0},{t1})':shortest=1{out}")
        last = out
    vchain.append(f"{last}null[vout]")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs,
         "-filter_complex", ";".join(mix) + ";" + ";".join(vchain),
         "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", spec["out"]],
        check=True,
    )
    print(spec["out"], f"{total:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1])
