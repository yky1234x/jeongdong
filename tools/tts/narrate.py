"""AI 시사고발 쇼츠 내레이션 생성 (3탄~7탄과 같은 목소리·같은 처리).
사용:
  python3 narrate.py out.wav "문장 하나"                 # 한 문장
  python3 narrate.py out.wav "그런데 사대문|안 정동…"     # '|' 위치에서 끊어 0.16초 쉼
  python3 narrate.py narr.wav -f script.txt              # 한 줄 = 한 장면, 장면별 파일+전체 파일
숫자는 한글로 풀어 쓸 것(77일 → 칠십칠 일). 영어 약어도 한글로(AI → 에이아이, QR → 큐알)."""
import sys, subprocess, wave, numpy as np, sherpa_onnx as s, os, json
M = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model") + "/"
SID, SPEED, STEPS = 5, 1.05, 8          # 성우 번호 5, 속도 1.05, 스텝 8 (고정)
AF = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
      "silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.15")
T = s.OfflineTts(s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(supertonic=s.OfflineTtsSupertonicModelConfig(
    M+"duration_predictor.onnx", M+"text_encoder.onnx", M+"vector_estimator.onnx", M+"vocoder.onnx",
    M+"tts.json", M+"unicode_indexer.bin", M+"voice.bin"), num_threads=8)))
ff = lambda *a: subprocess.run(["ffmpeg", "-v", "error", *a, "-y"], check=True)
def raw(text, out):
    g = s.GenerationConfig(); g.sid = SID; g.speed = SPEED; g.num_steps = STEPS; g.extra = {"lang": "ko"}
    a = T.generate(text, g); x = np.clip(np.array(a.samples, dtype=np.float32), -1, 1)
    with wave.open(out + "_raw.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(a.sample_rate); w.writeframes((x * 32767).astype(np.int16).tobytes())
    ff("-i", out + "_raw.wav", "-af", AF, "-ar", "44100", "-ac", "1", out + ".wav")
def scene(text, out, gap=0.16):
    """한 장면: 앞 0.25초 + 음성 + 뒤 0.3초. '|'는 끊어 읽기."""
    parts = text.split("|"); files = []
    ff("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(gap), "/tmp/_gap.wav")
    for i, p in enumerate(parts):
        raw(p.strip(), f"{out}_k{i}"); files += [f"{out}_k{i}.wav"] + (["/tmp/_gap.wav"] if i < len(parts) - 1 else [])
    open(out + "_k.txt", "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f in files))
    ff("-f", "concat", "-safe", "0", "-i", out + "_k.txt", "-ar", "44100", "-ac", "1", out + "_j.wav")
    ff("-i", out + "_j.wav", "-af", "adelay=250:all=1,apad=pad_dur=0.3", "-ar", "44100", "-ac", "1", out + "c.wav")
    return out + "c.wav"
def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
if __name__ == "__main__":
    out = sys.argv[1]; base = out[:-4]
    lines = [l.strip() for l in open(sys.argv[3], encoding="utf-8") if l.strip()] if sys.argv[2] == "-f" else [sys.argv[2]]
    files = [scene(t, f"{base}_s{i}") for i, t in enumerate(lines)]
    open(base + "_list.txt", "w").write("".join(f"file '{os.path.abspath(f)}'\n" for f in files))
    ff("-f", "concat", "-safe", "0", "-i", base + "_list.txt", "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "44100", out)
    d = [round(dur(f), 3) for f in files]; json.dump(d, open(base + "_durs.json", "w"))
    print("장면별 길이(초):", d, "합계", round(sum(d), 2), "→", out)
