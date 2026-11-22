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


import json
HL = json.load(open(os.path.join(ROOT, 'tools', 'headline.json'), encoding='utf-8'))
HL_DATES = sorted(k for k in HL if k[:1].isdigit() and k <= today.isoformat())
DEFAULT = {
 'ko': {"kicker": "오늘의 외벽", "head": ["{sky}일째,", "그는 아직 외벽 위에 있습니다"], "quote": "“민주노총은 노동자를 살려라!”", "sub": ["30m 넘는 외벽, 구조물 없이 밧줄 하나", "▶ 영상 · 사진 · 투쟁 일지 보기"]},
 'en': {"kicker": "Today on the wall", "head": ["Day {sky}:", "he is still on the wall"], "quote": "“KCTU, save the workers!”", "sub": ["Over 30 m up, hanging from a single rope", "▶ Video · photos · daily log"]},
 'zh': {"kicker": "今日外墙", "head": ["第{sky}天，", "他仍在外墙上"], "quote": "“民主劳总，救救劳动者！”", "sub": ["30多米高的外墙，只靠一根绳子", "▶ 视频 · 照片 · 抗争日志"]},
}
MAST = {'ko': ('정동 농성 일보', '{y}년 {m}월 {d}일 · 제{sky}호 · 고공 외줄 밧줄농성 {sky}일째 · 천막농성 {tent}일째', '이 건물 외벽에 사람이 있습니다', '여러분이 글로벌 시민 언론사입니다', '눌러서 보기 ▶', '서울 정동 경향신문사(민주노총 본부 건물) 외벽 · 지금 이 순간에도'),
        'en': ('Jeongdong Sit-in Daily', '{mon} {d}, {y} · No. {sky} · Wall: day {sky} · Tent: day {tent}', 'A person is living on this wall', 'You are the global citizen press', 'Tap to see ▶', 'Kyunghyang Shinmun / KCTU HQ, Seoul · right now'),
        'zh': ('贞洞静坐日报', '{y}年{m}月{d}日 · 第{sky}期 · 高空单绳静坐第{sky}天 · 帐篷第{tent}天', '这栋大楼外墙上有人', '你们就是全球公民媒体', '点击查看 ▶', '首尔贞洞京乡新闻（民主劳总总部大楼）外墙 · 此时此刻')}

def daily(L, t):
    def f(sz, b=False, serif=False):
        if serif:
            g = glob.glob('/usr/share/fonts/**/NotoSerifCJK-Bold.ttc', recursive=True)
            if g: return ImageFont.truetype(g[0], sz, index=t['i'])
        return ImageFont.truetype(FBo if b else FB, sz, index=t['i'])
    def fit(lines, size, maxw, **k):
        if isinstance(lines, str): lines = [lines]
        while any(f(size, **k).getlength(x) > maxw for x in lines): size -= 2
        return f(size, **k)
    c = dict((HL[HL_DATES[-1]] if HL_DATES else {}).get(L) or DEFAULT[L])
    fm = lambda x: x.format(sky=sky, tent=tent)
    W, H = 1280, 720; PAPER = (244, 238, 226); INK = (20, 16, 17)
    im = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(im)
    mt, mline, tag, press, cta, cap = MAST[L]
    d.text((44, 18), mt, font=fit(mt, 56, 400, serif=True), fill=INK)
    ml = mline.format(y=today.year, m=M, d=D, mon=today.strftime('%b'), sky=sky, tent=tent)
    d.text((W - 44, 50), ml, font=fit(ml, 24, W - 44 - 470), fill=(90, 70, 70), anchor='rm')
    d.line([(44, 100), (W - 44, 100)], fill=INK, width=5); d.line([(44, 108), (W - 44, 108)], fill=INK, width=1)
    # 오른쪽: 고정 사진 (외벽 고공농성)
    PW, PY, PH = 440, 128, 572; px = W - 44 - PW
    z = zoomimg.crop((280, 90, 800, 850)); r = max(PW / z.width, PH / z.height)
    z = z.resize((int(z.width * r) + 1, int(z.height * r) + 1)); ox = (z.width - PW) // 2
    im.paste(z.crop((ox, 0, ox + PW, PH)), (px, PY))
    d.rectangle([px, PY, px + PW - 1, PY + PH - 1], outline=INK, width=3)
    d.rounded_rectangle((px + 14, PY + 14, px + 14 + 200, PY + 58), radius=8, fill=RED)
    d.text((px + 114, PY + 36), {'ko':'외벽 위 양규서','en':'ON THE WALL','zh':'外墙上'}[L], font=f(26, True), fill='white', anchor='mm')
    d.rectangle([px, PY + PH - 46, px + PW, PY + PH], fill=(20, 16, 17))
    d.text((px + PW // 2, PY + PH - 23), cap, font=fit(cap, 20, PW - 20, b=True), fill='white', anchor='mm')
    # 왼쪽: 날짜별 1면
    LW = px - 44 - 34; x = 44; y = 128
    kf = f(28, True); kw = int(kf.getlength(c['kicker'])) + 28
    d.rectangle([x, y, x + kw, y + 44], fill=RED); d.text((x + 14, y + 22), c['kicker'], font=kf, fill='white', anchor='lm')
    y += 62
    head = [fm(h) for h in c['head']]; hf = fit(head, 60, LW, serif=True)
    for h in head: d.text((x, y), h, font=hf, fill=INK); y += int(hf.size * 1.28)
    y += 6; qf = fit(c['quote'], 30, LW, b=True)
    d.rectangle([x, y, x + 6, y + int(qf.size * 1.5)], fill=RED)
    d.text((x + 18, y + int(qf.size * .75)), c['quote'], font=qf, fill=RED, anchor='lm'); y += int(qf.size * 1.5) + 20
    sf = fit(c['sub'], 25, LW)
    for s_ in c['sub']: d.text((x, y), s_, font=sf, fill=(60, 50, 50)); y += int(sf.size * 1.5)
    # 아래: 고정 문구 + 누르기 버튼
    by = H - 132
    d.line([(x, by - 14), (x + LW, by - 14)], fill=INK, width=2)
    tf = fit(tag, 36, LW, b=True); d.text((x, by), tag, font=tf, fill=INK)
    bf = f(24, True); bw = int(bf.getlength(cta)) + 36
    d.text((x, H - 54), press, font=fit(press, 24, LW - bw - 20, b=True), fill=RED, anchor='lm')
    d.rounded_rectangle((x + LW - bw, H - 76, x + LW, H - 32), radius=22, fill=RED)
    d.text((x + LW - bw // 2, H - 54), cta, font=bf, fill='white', anchor='mm')
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
    im = daily(L, t)
    im.save(os.path.join(ROOT, f'share_{L}.jpg'), quality=88)
    if L == 'ko': im.save(os.path.join(ROOT, 'share.jpg'), quality=88)
square(T['ko']).save(os.path.join(ROOT, 'share_sq.jpg'), quality=85)
print(f'{today}: 고공 {sky}일째 · 천막 {tent}일째 이미지 생성 완료')
