#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, time
from faster_whisper import WhisperModel

SRC = os.environ.get("WDIR", r"C:\Users\13364\WorkBuddy\2026-07-10-17-28-23\materials\零失误社交搭讪全指南，进可攻退可守")
OUT = os.environ.get("WOUT", r"C:\Users\13364\WorkBuddy\2026-07-10-17-28-23\materials\transcribed_audio")
os.makedirs(OUT, exist_ok=True)

model_size = os.environ.get("WMODEL", "small")
model_path = os.environ.get("WPATH", model_size)
fname = sys.argv[1] if len(sys.argv) > 1 else None

print(f"loading model {model_path} ...", flush=True)
t0 = time.time()
model = WhisperModel(model_path, device="cpu", compute_type="int8")
print(f"model loaded in {time.time()-t0:.1f}s", flush=True)

if fname:
    files = [fname]
else:
    files = sorted(os.listdir(SRC))

for f in files:
    if not f.lower().endswith((".m4a", ".mp3", ".wav", ".mp4", ".mov")):
        continue
    path = os.path.join(SRC, f)
    if not os.path.isfile(path):
        continue
    base = os.path.splitext(f)[0]
    print(f"\n=== {f} ===", flush=True)
    t1 = time.time()
    segments, info = model.transcribe(path, language="zh", beam_size=5, vad_filter=True)
    print(f"detected lang={info.language} prob={info.language_probability:.2f}", flush=True)
    txt_path = os.path.join(OUT, base + ".txt")
    srt_path = os.path.join(OUT, base + ".srt")
    with open(txt_path, "w", encoding="utf-8") as wt, open(srt_path, "w", encoding="utf-8") as ws:
        idx = 0
        for seg in segments:
            idx += 1
            line = seg.text.strip()
            wt.write(line + "\n")
            ws.write(f"{idx}\n{seg.start:.2f} --> {seg.end:.2f}\n{line}\n\n")
    dt = time.time() - t1
    print(f"done {f}: {dt:.1f}s, {idx} segs -> {txt_path}", flush=True)
