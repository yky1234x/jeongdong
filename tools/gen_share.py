# 공유 이미지 자동 생성: 오늘(한국 시간) 날짜로 농성 일수를 계산해 미리보기·공유 이미지를 다시 만듭니다.
# GitHub Actions가 매일 0시(KST)에 실행합니다. 직접 실행: python tools/gen_share.py
import datetime, glob, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'src')
SKY_START = datetime.date(2026, 9, 6)    # 고공 외줄 밧줄농성 1일차
TENT_START = datetime.date(2026, 8, 24)  # 천막농성 1일차
RED = (200, 16, 46); YEL = (255, 200, 0); DARK = (20, 16, 17)

def find_font(bold):
    pats = ['/usr/share/fonts/**/NotoSansCJK-%s.ttc' % ('Bold' if bold else 'Black'),
            '/usr/share/fonts/**/NotoSansCJK-Bold.ttc', '/usr/share/fonts/**/NotoSansCJK*.ttc']
    for p in pats:
        g = glob.glob(p, recursive=True)
        if g: return g[0]
    raise SystemExit('Noto CJK font not found (apt install fonts-noto-cjk)')
FB, FBo = find_font(False), find_font(True)

today = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()
sky = (today - SKY_START).days + 1
tent = (today - TENT_START).days + 1
M, D = today.month, today.day

T = {
 'ko': dict(i=1, days=f'고공 외줄 밧줄농성 {sky}일째 · 천막농성 {tent}일째', asof=f'({M}월 {D}일 기준)',
            h=['이 건물 외벽에', '사람이 있습니다'], sub=['서울 정동 · 경향신문사 본사', '민주노총 본부 건물'],
            cry=['민주노총은', '노동자를 살려라!'], first='사람이 먼저입니다', press='여러분이 글로벌 시민 언론사입니다',
            go='영상 · 사진 · 일지 · 후원 ▶ 링크', zoom='확대'),
 'en': dict(i=1, days=f'Wall: day {sky} · Tent: day {tent}', asof=f'(as of {today.strftime("%b")} {D})',
            h=['A person is living', 'on this wall'], sub=['Kyunghyang Shinmun HQ, Seoul', 'also home to KCTU headquarters'],
            cry=['KCTU,', 'save the workers!'], first='People come first', press='You are the global citizen press',
            go='Video · Photos · Log ▶ Link', zoom='ZOOM'),
 'zh': dict(i=2, days=f'高空单绳静坐第{sky}天 · 帐篷静坐第{tent}天', asof=f'（截至{M}月{D}日）',
            h=['这栋大楼外墙上', '有人'], sub=['首尔贞洞 · 京乡新闻总部', '民主劳总总部所在大楼'],
            cry=['民主劳总，', '救救劳动者！'], first='人比什么都重要', press='你们就是全球公民媒体',
            go='视频 · 照片 · 日志 ▶ 链接', zoom='放大'),
}

building = Image.open(os.path.join(SRC, 'building.jpg')).convert('RGB')
zoomimg = Image.open(os.path.join(SRC, 'zoom.jpg')).convert('RGB')

def landscape(L, t):
    def f(s, b=False): return ImageFont.truetype(FBo if b else FB, s, index=t['i'])
    def fit(lines, size, maxw, b=False):
        if isinstance(lines, str): lines = [lines]
        while any(f(size, b).getlength(s) > maxw for s in lines): size -= 2
        return f(size, b)
    W, H = 1280, 720
    im = Image.new('RGB', (W, H), DARK); d = ImageDraw.Draw(im)
    bx0, by0, bx1, by1 = 400, 0, 740, 680
    b = building.crop((bx0, by0, bx1, by1)); bw = int(H * b.width / b.height); im.paste(b.resize((bw, H)), (0, 0))
    s = H / (by1 - by0); cx = int((559 - bx0) * s); cy = int((148 - by0) * s); r = 38
    z = zoomimg.crop((280, 90, 800, 850)); zw = int(H * z.width / z.height); zx = bw + 18; im.paste(z.resize((zw, H)), (zx, 0))
    d.line((cx + r * .7, cy - r * .7, zx, 4), fill=YEL, width=6); d.line((cx + r * .7, cy + r * .7, zx, H - 4), fill=YEL, width=6)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=YEL, width=8); d.rectangle((zx, 0, zx + zw - 1, H - 1), outline=YEL, width=6)
    d.rounded_rectangle((zx + 16, 16, zx + 170, 62), radius=10, fill=YEL)
    d.text((zx + 93, 39), t['zoom'], font=fit(t['zoom'], 28, 140), fill='black', anchor='mm')
    x = zx + zw + 28; mw = W - x - 30
    d.rounded_rectangle((x, 30, x + mw, 122), radius=10, fill=RED)
    d.text((x + mw // 2, 62), t['days'], font=fit(t['days'], 30, mw - 20), fill='white', anchor='mm')
    d.text((x + mw // 2, 100), t['asof'], font=f(22, True), fill=(255, 225, 225), anchor='mm')
    y = 150; hf = fit(t['h'], 54, mw)
    for s_ in t['h']: d.text((x, y), s_, font=hf, fill='white'); y += int(hf.size * 1.22)
    sf = fit(t['sub'], 26, mw, True)
    for s_ in t['sub']: d.text((x, y + 4), s_, font=sf, fill=(220, 210, 210)); y += int(sf.size * 1.4)
    y += 14; cf = fit(t['cry'], 40, mw)
    for s_ in t['cry']: d.text((x, y), s_, font=cf, fill=YEL); y += int(cf.size * 1.25)
    y += 10; ff = fit(t['first'], 34, mw)
    d.rounded_rectangle((x, y + 2, x + mw, y + 2 + int(ff.size * 1.5)), radius=10, outline=YEL, width=3)
    d.text((x + mw // 2, y + 2 + int(ff.size * .75)), t['first'], font=ff, fill='white', anchor='mm'); y += int(ff.size * 1.5) + 16
    d.rounded_rectangle((x, y, x + mw, H - 30), radius=14, fill=YEL); mid = (y + H - 30) // 2
    d.text((x + mw // 2, mid - 20), t['press'], font=fit(t['press'], 38, mw - 24), fill='black', anchor='mm')
    d.text((x + mw // 2, mid + 26), t['go'], font=fit(t['go'], 24, mw - 24, True), fill=RED, anchor='mm')
    return im

def square(t):
    def f(s, b=False): return ImageFont.truetype(FBo if b else FB, s, index=1)
    def fit(s, size, maxw, b=False):
        while f(size, b).getlength(s) > maxw: size -= 2
        return f(size, b)
    S = 1080; sq = Image.new('RGB', (S, S), DARK); d = ImageDraw.Draw(sq)
    ph = zoomimg.crop((250, 60, 830, 900))
    p2 = ph.resize((S, int(S * ph.height / ph.width))).crop((0, 80, S, 700)); sq.paste(p2, (0, 0))
    d.rectangle((0, 0, S, 90), fill=RED)
    s = '서울 정동 경향신문사 외벽 고공 외줄 밧줄농성'; d.text((S // 2, 45), s, font=fit(s, 40, S - 60), fill='white', anchor='mm')
    d.rounded_rectangle((S // 2 - 400, 110, S // 2 + 400, 190), radius=40, fill=DARK)
    d.text((S // 2, 140), t['days'], font=fit(t['days'], 38, 760), fill=YEL, anchor='mm')
    d.text((S // 2, 176), t['asof'], font=f(22, True), fill=(230, 230, 230), anchor='mm')
    y = 640
    s = '이 건물 외벽에 사람이 있습니다'; d.text((S // 2, y + 40), s, font=fit(s, 70, S - 80), fill='white', anchor='mm')
    s = '민주노총은 노동자를 살려라! · 사람이 먼저입니다'; d.text((S // 2, y + 130), s, font=fit(s, 44, S - 80), fill=YEL, anchor='mm')
    d.rounded_rectangle((60, y + 190, S - 60, y + 400), radius=20, fill=YEL)
    s = '여러분이 글로벌 시민 언론사입니다'; d.text((S // 2, y + 255), s, font=fit(s, 62, S - 200), fill='black', anchor='mm')
    s = '링크에서 영상 · 사진 · 투쟁 일지 · 후원 안내'; d.text((S // 2, y + 340), s, font=fit(s, 36, S - 200, True), fill=RED, anchor='mm')
    return sq

for L, t in T.items():
    im = landscape(L, t)
    im.save(os.path.join(ROOT, f'share_{L}.jpg'), quality=88)
    if L == 'ko': im.save(os.path.join(ROOT, 'share.jpg'), quality=88)
square(T['ko']).save(os.path.join(ROOT, 'share_sq.jpg'), quality=85)
print(f'{today}: 고공 {sky}일째 · 천막 {tent}일째 이미지 생성 완료')
