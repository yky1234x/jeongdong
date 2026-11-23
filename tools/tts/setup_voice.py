"""AI 시사고발 쇼츠 내레이션 성우(Supertonic 3, sid=5) 모델 설치 스크립트.
npm 패키지 3개(@3sln/donki-lle-voice-multi, -2, -3 @0.1.1)에 base64로 나뉘어 든 모델을 내려받아 ./model/ 에 복원한다.
사용: python3 setup_voice.py   (npm, pip 필요. pip install sherpa-onnx==2.0.2 numpy)"""
import subprocess, tarfile, json, re, base64, hashlib, os, glob, tempfile
PKGS = ["@3sln/donki-lle-voice-multi@0.1.1", "@3sln/donki-lle-voice-multi-2@0.1.1", "@3sln/donki-lle-voice-multi-3@0.1.1"]
MD5 = {"duration_predictor.onnx": "f85f44db6dcf2a5ceb99fe8ee297620d", "text_encoder.onnx": "94ee39e5d93fd5d590c1b158c20f35fc",
       "tts.json": "ccd1012302c3eef729dd5835fd6f2129", "unicode_indexer.bin": "d40f8079db08a219dc13510481672c93",
       "vector_estimator.onnx": "fcee9c62eb1b29461f4d088c3ab07bc2", "vocoder.onnx": "7b7be74ba7fa0dc48b27426843ee7c12",
       "voice.bin": "a90a0e19b45c5399415afbd6941df8d7"}
tmp = tempfile.mkdtemp(); roots = {}
for p in PKGS:
    tgz = subprocess.run(["npm", "pack", p, "--silent"], cwd=tmp, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
    d = os.path.join(tmp, tgz[:-4]); tarfile.open(os.path.join(tmp, tgz)).extractall(d)
    roots[p] = os.path.join(d, "package")
src = open(os.path.join(roots[PKGS[0]], "voice.js"), encoding="utf-8").read()
manifest = json.loads(src[src.index("{"):src.rindex("}") + 1])
os.makedirs("model", exist_ok=True)
for name, info in manifest["files"].items():
    buf = b""
    for part in info["parts"]:
        pkg, rel = re.match(r"(@[^/]+/[^/]+)/(.+)", part).groups()
        txt = open(os.path.join(roots[pkg], rel), encoding="utf-8").read()
        buf += base64.b64decode(txt.split('"')[1])
    assert len(buf) == info["size"], name
    open(os.path.join("model", name), "wb").write(buf)
    ok = hashlib.md5(buf).hexdigest() == MD5.get(name)
    print(f"{name:26s} {len(buf):>10d}  {'OK' if ok else 'MD5 불일치!'}")
