# 카톡·텔레그램 미리보기(썸네일 사진 주소, 설명 문구)를 오늘 날짜(서울 시간) 기준으로 갱신합니다.
# 매일 0시 GitHub Actions가 실행하고, 내용 수정 동기화 때도 실행합니다. 직접 실행: python tools/bump_preview.py
# - 썸네일 사진 주소: share.jpg?v=YYYYMMDDHHMM  (주소가 바뀌어야 카톡·텔레그램이 새 사진을 받아 감)
# - 설명 문구: "[오늘 소식] (실제 날짜) 투쟁 일지 최신 내용 / 특종 ... · 여러분이 글로벌 시민 언론사입니다"
import datetime, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'index.html')
s = open(P, encoding='utf-8').read()

now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
rows = re.findall(r'\{d:"(\d{4}-\d\d-\d\d)",ko:"((?:[^"\\]|\\.)*)"', s)
d, ko = max(rows)
em, ed = int(d[5:7]), int(d[8:10])
same = (now.month, now.day) == (em, ed)
news = f'[{now.month}.{now.day} 소식] ' + ('' if same else f'({em}.{ed}) ') + ko
desc = news + (' / 특종: 집단사직 종용 녹취록 공개' if 'class="scoop"' in s else '') + ' · 여러분이 글로벌 시민 언론사입니다'
desc = desc.replace('"', '&quot;')

s = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', lambda m: m.group(1) + desc + m.group(2), s)
s = re.sub(r'(<meta name="description" content=")[^"]*(">)', lambda m: m.group(1) + desc + m.group(2), s)
s = re.sub(r'(jeongdong/share\.jpg)(\?v=\d+)?"', lambda m: m.group(1) + '?v=' + now.strftime('%Y%m%d%H%M') + '"', s)
open(P, 'w', encoding='utf-8').write(s)
print('preview:', desc)
