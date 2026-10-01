# -*- coding: utf-8 -*-
"""세션1·세션2 제안본을 zip 하나로 묶는다. 메일에 그대로 붙일 수 있게 만드는 게 목적이다.
묶음 안에 '먼저보기.html'을 넣어서, 압축을 풀고 그것만 더블클릭하면 나머지로 갈 수 있게 한다.
사용: python3 tools/build_proposal_pack.py"""
import os, zipfile, datetime, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.abspath(os.path.join(HERE, ".."))
DIST = os.path.join(AX, "dist"); os.makedirs(DIST, exist_ok=True)
TODAY = datetime.date.today().strftime("%Y%m%d")
ROOT = "AX_세션1_2_제안"                       # 압축을 풀면 생기는 폴더 이름
OUTZIP = os.path.join(DIST, f"{ROOT}_{TODAY}.zip")

# (원본 경로, 묶음 안 경로, 화면에 적을 설명)
FILES = [
    ("세션2_대시보드_제안/대시보드_예시.html", "세션2_대시보드/대시보드_예시.html",
     "결과 화면. <strong>필터가 실제로 동작합니다.</strong> 기간·조직·주문유형을 바꾸면 아래 숫자가 전부 다시 계산됩니다"),
    ("세션2_대시보드_제안/지시문_대시보드.md", "세션2_대시보드/지시문_대시보드.md",
     "참가자가 에이전트 「지침」란에 붙여넣는 지시문. <code>✂</code> 사이가 붙여넣는 부분입니다"),
    ("세션2_대시보드_제안/매출데이터_예시.csv", "세션2_대시보드/매출데이터_예시.csv",
     "가상 매출데이터 57행. 공유해 주신 16개 열 그대로입니다"),
    ("세션2_대시보드_제안/README.md", "세션2_대시보드/README.md",
     "세션2 제안 설명과 확인 요청 다섯 가지"),
    ("세션1_뉴스수집_제안/지시문_뉴스수집.md", "세션1_뉴스수집/지시문_뉴스수집.md",
     "세션1 마지막 5~10분. 고객사·경쟁사 기사를 Gemini / ChatGPT에 예약해 두는 실습"),
]

CSS = """
:root{--paper:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--mute:#7a7873;--line:#e4e2db;--panel:#f3f2ee;
--accent:#2a78d6;--rule:#d9d7d0}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;
--mute:#9b998f;--line:#343330;--panel:#242320;--accent:#3987e5;--rule:#3a3936}}
:root[data-theme="dark"]{--paper:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--mute:#9b998f;--line:#343330;
--panel:#242320;--accent:#3987e5;--rule:#3a3936}
html{color-scheme:light dark}
body{margin:0;background:var(--paper);color:var(--ink);font-size:15px;line-height:1.65;
font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:820px;margin:0 auto;padding:40px 20px 72px}
.eyebrow{font-size:12px;letter-spacing:.1em;color:var(--accent);font-weight:700}
h1{font-size:25px;margin:6px 0 6px;line-height:1.3}
.lead{color:var(--ink2);margin:0 0 6px}
.warn{background:var(--panel);border-left:3px solid var(--accent);padding:11px 14px;font-size:14px;margin:18px 0 26px}
h2{font-size:17px;margin:32px 0 10px;padding-top:14px;border-top:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-size:14px;margin:6px 0}
th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
thead th{font-size:12px;color:var(--mute);font-weight:600;border-bottom:1px solid var(--rule)}
a{color:var(--accent)}
code{font-family:ui-monospace,monospace;font-size:13px;background:var(--panel);padding:1px 4px;border-radius:3px}
ol{padding-left:20px}ol li{margin:7px 0}
.ask li{margin:10px 0}
.foot{margin-top:44px;padding-top:12px;border-top:1px solid var(--rule);font-size:12px;color:var(--mute)}
"""

rows = "".join(
    '<tr><td><a href="%s">%s</a></td><td>%s</td></tr>' % (urllib.parse.quote(z), z, d)
    for _, z, d in FILES)

HTML = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AX 과정 세션1·세션2 제안</title><style>__CSS__</style></head><body><div class="wrap">
<div class="eyebrow">삼성전자 B2B 영업 AX 과정</div>
<h1>세션1 · 세션2 제안본</h1>
<p class="lead">공유해 주신 매출 데이터 16개 열과, "프롬프트만 읽어도 명확하게"라는 요청에 맞춰 만든 1차 안입니다. 디자인은 아직 손대지 않았습니다.</p>
<div class="warn"><strong>데이터는 전부 가상입니다.</strong> 수요처명 · 판매처명 · 모델명 · 금액은 모두 지어낸 값이며 삼성전자 실제 정보와 무관합니다. 열 이름과 값의 성격만 공유해 주신 헤더에 맞췄습니다.</div>

<h2>들어 있는 것</h2>
<table><thead><tr><th>파일</th><th>무엇인가</th></tr></thead><tbody>__ROWS__</tbody></table>
<p class="lead" style="font-size:13px;margin-top:10px">먼저 <strong>대시보드_예시.html</strong>을 열어 필터를 몇 번 바꿔 보시는 게 가장 빠릅니다.</p>

<h2>확인 부탁드리는 것</h2>
<ol class="ask">
<li><strong>단가(또는 공급가) 열</strong>을 넣을 수 있을까요. 지금 헤더로는 <code>단가 × 수량 = 금액</code> 검산을 할 수 없어, 숫자를 의심하는 법을 가르치는 대목이 약해집니다.</li>
<li><strong>한 영업기회 번호에 매출이 여러 번</strong> 잡히는 경우가 실제로 있습니까. 지금 지시문은 중복을 만나면 멈추고 물어보게 되어 있습니다.</li>
<li>실제 데이터의 <strong>수요처는 몇 곳 규모</strong>입니까. 15곳이 넘으면 표가 길어져 화면이 깨집니다.</li>
<li><strong>집계 축 세 개(품목구분·주문유형·수요처명)와 필터 세 개(기간·조직·주문유형)</strong>가 현장에서 실제로 쪼개 보는 기준이 맞습니까. 필터의 '조직'을 파트명으로 뒀는데 그룹명이 맞는지도 봐 주십시오.</li>
<li><code>매출일자</code> 말고 <strong>수주일자나 예상 매출일</strong>이 따로 있습니까. 선행영업과 트렌드를 기간으로 구분하려면 부족할 수 있습니다.</li>
<li><strong>세션2와 세션3의 연결</strong>을 (가) 세션2에서 수요처 한 곳을 골라 세션3으로 넘기는 방식과 (나) 두 세션을 각자 완결시키는 방식 중 어느 쪽으로 할지. 저는 (가)를 제안드립니다.</li>
</ol>

<h2>세션1 실습에서 미리 봐 주실 것</h2>
<p class="lead">예약 기능은 Gemini · ChatGPT 둘 다 <strong>유료 플랜에서만</strong> 됩니다. 무료 계정 참가자는 프롬프트만 저장해 두었다가 아침에 직접 붙여넣어도 된다는 안내를 교안에 한 줄 넣어 주시면 실습이 멈추지 않습니다.</p>

<div class="foot">__DATE__ 기준 · 모든 데이터는 가상이며 삼성전자 실제 정보와 무관합니다</div>
</div></body></html>"""

# %% 서식 대신 자리표시자로 바꾼다. CSS 안에 % 가 생기면 서식이 깨지기 때문이다.
HTML = (HTML.replace("__CSS__", CSS).replace("__ROWS__", rows)
            .replace("__DATE__", datetime.date.today().strftime("%Y-%m-%d")))

with zipfile.ZipFile(OUTZIP, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr(f"{ROOT}/먼저보기.html", HTML)
    for src, dst, _ in FILES:
        p = os.path.join(AX, src)
        if not os.path.exists(p):
            raise SystemExit("없는 파일: " + src)
        z.write(p, f"{ROOT}/{dst}")

size = os.path.getsize(OUTZIP)
print(f"{os.path.relpath(OUTZIP, AX)}  파일 {len(FILES)+1}개 · {size/1024:.0f} KB")
