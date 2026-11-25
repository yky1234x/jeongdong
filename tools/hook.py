# 매일 바뀌는 썸네일 색 테마와 '후킹' 메인 문구.
# gen_share.py(이미지)와 bump_preview.py(카톡·텔레그램 미리보기 제목)가 함께 씁니다.
# - 색: 날짜마다 다음 테마로 넘어감(7일 주기라 어제·오늘이 항상 다르게 보임)
# - 문구: headline.json 에 오늘·어제 날짜 소식이 있으면 그 문구, 없으면 아래 HOOKS 를 날짜별로 돌려 씀
import datetime, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKY_START = datetime.date(2026, 9, 6)
TENT_START = datetime.date(2026, 8, 24)

def today():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()

# bg: 바탕, ink: 큰 글씨, muted: 작은 글씨, acc: 강조(키커·인용·버튼), on: 강조 위 글씨
THEMES = [
    dict(name='신문지',   bg=(244, 238, 226), ink=(20, 16, 17),    muted=(90, 70, 70),    acc=(200, 16, 46),  on=(255, 255, 255)),
    dict(name='밤',       bg=(20, 16, 17),    ink=(255, 255, 255), muted=(200, 190, 190), acc=(255, 200, 0),  on=(20, 16, 17)),
    dict(name='경고 노랑', bg=(255, 200, 0),   ink=(20, 16, 17),    muted=(70, 50, 0),     acc=(200, 16, 46),  on=(255, 255, 255)),
    dict(name='투쟁 빨강', bg=(200, 16, 46),   ink=(255, 255, 255), muted=(255, 215, 215), acc=(255, 200, 0),  on=(20, 16, 17)),
    dict(name='남색',     bg=(16, 32, 68),    ink=(255, 255, 255), muted=(190, 205, 235), acc=(255, 140, 0),  on=(16, 16, 16)),
    dict(name='흰 종이',   bg=(250, 250, 250), ink=(10, 10, 10),    muted=(80, 80, 80),    acc=(220, 0, 110),  on=(255, 255, 255)),
    dict(name='짙은 초록', bg=(12, 52, 40),    ink=(255, 255, 255), muted=(190, 225, 210), acc=(255, 214, 10), on=(12, 30, 24)),
]

# 뉴스가 없는 날 쓰는 후킹 문구 ({sky}: 고공 일수, {tent}: 천막 일수)
HOOKS = [
    {'ko': dict(kicker='지금 이 순간', head=['노동자 편이라는 민주노총,', '그 산하 노조가 직원을 해고했다'], quote='“민주노총은 노동자를 살려라!”'),
     'en': dict(kicker='Right now', head=['A union that fights for workers', 'fired its own staff'], quote='“KCTU, save the workers!”'),
     'zh': dict(kicker='此时此刻', head=['号称站在劳动者一边的工会，', '解雇了自己的职员'], quote='“民主劳总，救救劳动者！”')},
    {'ko': dict(kicker='{sky}일째', head=['밧줄 하나에 매달려', '{sky}번째 밤을 맞습니다'], quote='“내려와서 같이 밥 먹자” — 정동 할머니'),
     'en': dict(kicker='Day {sky}', head=['Hanging from one rope,', 'night number {sky}'], quote='“Come down, let’s eat together.” — a neighbor'),
     'zh': dict(kicker='第{sky}天', head=['悬在一根绳子上，', '迎来第{sky}个夜晚'], quote='“下来吧，我们一起吃饭” —— 贞洞奶奶')},
    {'ko': dict(kicker='질문합니다', head=['5인 미만이면', '해고해도 됩니까?'], quote='“노동조합 상근자도 노동자다”'),
     'en': dict(kicker='We ask', head=['Fewer than 5 staff —', 'so firing is fine?'], quote='“Union staff are workers too.”'),
     'zh': dict(kicker='我们要问', head=['不到5个人，', '就可以随便解雇吗？'], quote='“工会专职人员也是劳动者”')},
    {'ko': dict(kicker='고개를 들어 보세요', head=['민주노총 본부 건물 외벽,', '저기 사람이 있습니다'], quote='“사람이 먼저입니다”'),
     'en': dict(kicker='Look up', head=['On the wall of the KCTU HQ building', 'there is a person'], quote='“People come first.”'),
     'zh': dict(kicker='请抬头看', head=['民主劳总总部大楼外墙上，', '有一个人'], quote='“人比什么都重要”')},
    {'ko': dict(kicker='부부의 싸움', head=['남편은 외벽에, 아내는 천막에', '{tent}일째 버팁니다'], quote='“제가 무엇을 잘못했을까요?” — 함계남'),
     'en': dict(kicker='A couple’s fight', head=['He is on the wall, she is in the tent', 'day {tent} and holding'], quote='“What did I do wrong?” — Ham Gye-nam'),
     'zh': dict(kicker='夫妇的抗争', head=['丈夫在外墙，妻子在帐篷，', '坚持到第{tent}天'], quote='“我做错了什么？” —— Ham Gye-nam')},
    {'ko': dict(kicker='겨울이 옵니다', head=['칼바람 속 {sky}일,', '그는 아직 내려오지 못했습니다'], quote='“해고 없다는 합의 전엔 못 내려간다”'),
     'en': dict(kicker='Winter is coming', head=['{sky} days in the biting wind —', 'he still can’t come down'], quote='“Not until they agree: no more firings.”'),
     'zh': dict(kicker='冬天来了', head=['寒风中{sky}天，', '他仍然无法下来'], quote='“不承诺不解雇，我就不下来”')},
    {'ko': dict(kicker='모르셨죠?', head=['근로기준법 밖 300만 명,', '그 틈으로 노조가 해고했습니다'], quote='“비영리 5인 미만에도 근로기준법을”'),
     'en': dict(kicker='Did you know?', head=['3 million workers outside labor law —', 'and a union used that gap'], quote='“Labor law for small workplaces too.”'),
     'zh': dict(kicker='你知道吗？', head=['300万人在劳动法之外，', '工会也利用了这个漏洞'], quote='“5人以下单位也要适用劳动基准法”')},
]

DEFAULT_SUB = {
    'ko': ['30m 넘는 외벽, 구조물 없이 밧줄 하나', '▶ 영상 · 사진 · 투쟁 일지 보기'],
    'en': ['Over 30 m up, hanging from a single rope', '▶ Video · photos · daily log'],
    'zh': ['30多米高的外墙，只靠一根绳子', '▶ 视频 · 照片 · 抗争日志'],
}

def theme(d=None):
    d = d or today()
    return THEMES[d.toordinal() % len(THEMES)]

def counts(d=None):
    d = d or today()
    return (d - SKY_START).days + 1, (d - TENT_START).days + 1

def headline(lang, d=None):
    """오늘 쓸 메인 문구 dict(kicker, head[2], quote, sub[2]) — 일수 치환 완료."""
    d = d or today()
    sky, tent = counts(d)
    HL = json.load(open(os.path.join(ROOT, 'tools', 'headline.json'), encoding='utf-8'))
    fresh = [k for k in HL if k[:1].isdigit() and (d - datetime.timedelta(days=1)).isoformat() <= k <= d.isoformat()]
    if fresh and HL[max(fresh)].get(lang):
        c = dict(HL[max(fresh)][lang])
    else:
        c = dict(HOOKS[d.toordinal() % len(HOOKS)][lang]); c['sub'] = DEFAULT_SUB[lang]
    fm = lambda x: x.format(sky=sky, tent=tent)
    return dict(kicker=fm(c['kicker']), head=[fm(h) for h in c['head']], quote=fm(c['quote']), sub=[fm(s) for s in c['sub']])
