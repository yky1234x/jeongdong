import asyncio, base64, subprocess, time, urllib.request
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT = "https://claude.ai/artifact/VqcYeCN2HkN21cMj1yPHUL"
IMAGE_NAME = "share_ko.jpg"
REPO = Path(__file__).resolve().parent
OUT = REPO / "share.jpg"
SITE_IMG = "https://yky1234x.github.io/jeongdong/share.jpg"

GRAB_JS = """async (name) => {
  const img = [...document.querySelectorAll('img')].find(x => (x.getAttribute('src') || '').includes(name));
  if (!img) return null;
  const r = await fetch(img.src, {cache: 'no-store'});
  const b = new Uint8Array(await r.arrayBuffer());
  let s = '';
  for (let k = 0; k < b.length; k += 32768) s += String.fromCharCode.apply(null, b.subarray(k, k + 32768));
  return btoa(s);
}"""

async def grab():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 420, "height": 900})
        await page.goto(ARTIFACT, wait_until="domcontentloaded", timeout=60000)
        deadline = time.time() + 60
        while time.time() < deadline:
            for frame in page.frames:
                try:
                    data = await frame.evaluate(GRAB_JS, IMAGE_NAME)
                    if data:
                        await browser.close()
                        return base64.b64decode(data)
                except Exception:
                    pass
            await page.wait_for_timeout(1500)
        await page.screenshot(path=str(REPO / "debug_page.png"))
        await browser.close()
        raise SystemExit("농성 페이지에서 공유 이미지를 찾지 못했습니다. debug_page.png 를 확인하세요.")

def run(*args):
    print("+", " ".join(args))
    subprocess.run(args, cwd=REPO, check=True)

def main():
    data = asyncio.run(grab())
    if data[:2] != b"\xff\xd8":
        raise SystemExit("가져온 파일이 JPEG가 아닙니다.")
    OUT.write_bytes(data)
    print(f"share.jpg 저장 완료: {len(data):,} bytes")
    run("git", "add", "share.jpg")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO).returncode == 0:
        print("사진이 이전과 같아서 올릴 변경이 없습니다.")
        return
    run("git", "commit", "-m", f"update share image {time.strftime('%Y-%m-%d %H:%M')}")
    run("git", "push")
    for _ in range(12):
        time.sleep(15)
        try:
            with urllib.request.urlopen(f"{SITE_IMG}?t={int(time.time())}") as r:
                print("사이트 확인:", r.status, r.headers.get("Content-Type"))
                if r.status == 200:
                    print("완료!")
                    return
        except Exception as e:
            print("반영 대기 중...", e)
    print("아직 사이트에 반영되지 않았습니다. 몇 분 뒤 다시 확인하세요.")

if __name__ == "__main__":
    main()
