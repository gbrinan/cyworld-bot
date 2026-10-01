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
# 정본은 D 모듈이다. 제안 묶음은 거기서 그대로 가져온다 — 사본을 따로 두면 반드시 어긋난다.
M = "context_pack/modules/D_analysis/"
FILES = [
    (M + "04_기준본/대시보드.html", "세션2_데이터분석/대시보드.html",
     "결과 화면 기준본. <strong>필터가 실제로 동작합니다.</strong> 기간·조직·주문유형을 바꾸면 아래 숫자가 전부 다시 계산됩니다"),
    ("세션2_대시보드_제안/README.md", "세션2_데이터분석/README.md",
     "<strong>헤더 16열을 어떻게 넣었는지</strong>와 확인 부탁드리는 여덟 가지"),
    (M + "02_지시문/지시문_1_대시보드.md", "세션2_데이터분석/지시문_1_대시보드.md",
     "<strong>세션2 전반.</strong> 참가자가 「지침」란에 붙여넣는 지시문. <code>✂</code> 사이가 붙여넣는 부분입니다"),
    (M + "02_지시문/지시문_2_분석.md", "세션2_데이터분석/지시문_2_분석.md",
     "<strong>세션2 후반.</strong> 같은 파일로 읽는 글(인사이트)을 만드는 지시문"),
    (M + "01_데이터/매출데이터.csv", "세션2_데이터분석/매출데이터.csv",
     "가상 매출데이터 54행. 공유해 주신 16개 열 그대로입니다"),
    (M + "01_데이터/매출데이터_소계.csv", "세션2_데이터분석/매출데이터_소계.csv",
     "축별 합계. <strong>검산 대조용</strong>입니다 (단가 열이 없어 이 파일이 검산 장치를 대신합니다)"),
    (M + "03_테스트/매출데이터_함정.csv", "세션2_데이터분석/매출데이터_함정.csv",
     "일부러 어긋낸 판. 0번 점검이 무엇을 잡는지 볼 때만 바꿔 올립니다"),
    (M + "04_기준본/리뷰.md", "세션2_데이터분석/리뷰.md",
     "후반 지시문의 <strong>기준본</strong>. 데이터에서 직접 계산한 값입니다"),
    (M + "04_기준본/대상수요처.md", "세션2_데이터분석/대상수요처_세션3인계.md",
     "세션2에서 고른 수요처 한 곳. <strong>세션3으로 넘어가는 유일한 것</strong>입니다"),
    ("context_pack/modules/C_proposal/01_데이터/고객요구조건.md", "세션3_제안자료/고객요구조건.md",
     "세션3이 받는 요구조건. <strong>제안 대상이 세션2가 넘긴 미래로병원</strong>입니다"),
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
<p class="lead">공유해 주신 매출 데이터 16개 열을 세션2 전체(대시보드 + 데이터 분석)에 반영하고, 고객사 6곳을 세션1·2·3 전부에 맞췄습니다. 지시문은 "프롬프트만 읽어도 명확하게"라는 요청에 맞춰 다시 썼습니다. 1차 안입니다. 디자인은 아직 손대지 않았습니다.</p>
<div class="warn"><strong>데이터는 전부 가상입니다.</strong> 수요처명 · 판매처명 · 모델명 · 금액은 모두 지어낸 값이며 삼성전자 실제 정보와 무관합니다. 열 이름과 값의 성격만 공유해 주신 헤더에 맞췄습니다.</div>

<h2>들어 있는 것</h2>
<table><thead><tr><th>파일</th><th>무엇인가</th></tr></thead><tbody>__ROWS__</tbody></table>
<p class="lead" style="font-size:13px;margin-top:10px">먼저 <strong>대시보드.html</strong>을 열어 필터를 몇 번 바꿔 보시고, 그다음 <strong>README.md</strong>의 헤더 16열 대조표를 봐 주시면 가장 빠릅니다.</p>

<h2>확인 부탁드리는 것</h2>
<ol class="ask">
<li><strong>한 영업기회에 매출이 여러 번</strong> 잡히는 게 정상입니까. 지금은 1건 = 1행으로 만들었습니다.</li>
<li><strong>파트명과 주문유형이 1:1</strong>이 맞습니까. 지금 데이터는 직판파트가 직판주문만 가지고 있습니다.</li>
<li>직판일 때 <strong>판매처 주소</strong>에 무엇이 들어갑니까. 지금은 <code>—</code>로 비워 두었습니다.</li>
<li><strong>실제 모델명</strong>을 주실 수 있습니까. 지금은 가상 모델명입니다. 조회 가능한 실제 모델명이면 세션3에서 사양을 찾아보는 흐름과 이어집니다.</li>
<li><strong>단가(공급가) 열</strong>을 넣을 수 있습니까. <strong>이것 하나는 꼭 봐 주십시오</strong> — 아래에 따로 적었습니다.</li>
<li>실제 데이터의 <strong>수요처는 몇 곳 규모</strong>입니까. 15곳이 넘으면 표가 길어져 화면이 깨집니다.</li>
<li><strong>집계 축 셋(품목구분·주문유형·수요처명)과 필터 셋(기간·조직·주문유형)</strong>이 현장 기준에 맞습니까.</li>
<li><code>매출일자</code> 말고 <strong>수주일자나 예상 매출일</strong>이 따로 있습니까.</li>
</ol>

<h2>단가 열 하나만 따로 말씀드립니다</h2>
<p class="lead">기존 데이터 분석 실습의 중심은 <strong>단가 × 수량 = 금액을 전 행에서 맞춰 보고, 어긋나면 멈추는 것</strong>이었습니다. "AI가 낸 숫자를 그대로 믿지 않는다"를 손으로 겪게 하는 장치였는데, 새 헤더에는 단가가 없어 그대로는 성립하지 않습니다.</p>
<p class="lead">그래서 <strong>소계 파일을 따로 내려 주고 원본에서 다시 더해 대조하게</strong> 바꿨습니다. 검산은 살아 있지만 한 단계 약합니다. 행 단위로 틀린 것은 못 잡고 합계만 맞춰 보기 때문입니다.<br>
단가 열을 주실 수 있으면 원래 실습을 되살리고 둘 다 돌리겠습니다. 어려우시면 지금 안(소계 대조)으로 가겠습니다.</p>

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
