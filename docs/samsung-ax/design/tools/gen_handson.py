# -*- coding: utf-8 -*-
"""실습 슬라이드 10장을 한 구조로 생성한다. 내용은 각 모듈 03_테스트·모듈카드.md에서 가져왔다.
사용: python3 gen_handson.py  (design/ 안에 Hands*.dc.html을 쓴다)"""
import html, os, sys

OUT = os.path.join(os.path.dirname(__file__), "..")


CORE_SLIDES = ['DeckD1', 'DeckD10', 'DeckD3', 'DeckD5', 'DeckM4', 'DeckO2', 'DeckO4', 'DeckO5', 'DeckW7', 'DeckZ2', 'HandsD1']
SECTION_OF = {'DeckD2': '§1', 'DeckD3': '§2', 'DeckD4': '§3', 'DeckD6': '§4', 'DeckD7': '§3', 'DeckD8': '§3', 'DeckD10': '§7', 'DeckD12': '§9', 'DeckA2': '§1', 'DeckA3': '§6', 'DeckA4': '§3', 'DeckA5': '§4', 'DeckA6': '§4', 'DeckA7': '§6', 'DeckA8': '§5', 'DeckA12': '§9', 'DeckB2': '§1', 'DeckB3': '§6', 'DeckB4': '§3', 'DeckB5': '§4', 'DeckB6': '§4', 'DeckB7': '§6', 'DeckB8': '§5', 'DeckB12': '§9', 'DeckC2': '§1', 'DeckC3': '§2', 'DeckC4': '§3', 'DeckC5': '§5', 'DeckC6': '§5', 'DeckC7': '§6', 'DeckC8': '§4', 'DeckC10': '§8', 'HandsD1': '§7', 'HandsD2': '§7·8', 'HandsA1': '§7', 'HandsA2': '§7', 'HandsA3': '§7·8', 'HandsB1': '§7', 'HandsB2': '§7', 'HandsB3': '§7·8', 'HandsC1': '§7', 'HandsC2': '§7·8'}
def footer_tag(name, page):
    parts = []
    if name not in CORE_SLIDES: parts.append('<span style="color: #c9c5bd;">90분 제외</span>')
    if name in SECTION_OF: parts.append('<span style="color: #9a958d;">모듈카드.md ' + SECTION_OF[name] + '</span>')
    parts.append(page)
    return " &nbsp;·&nbsp; ".join(parts)

HEAD = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
  <style>
    body { margin: 0; font-family: 'IBM Plex Sans KR', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif; -webkit-font-smoothing: antialiased; }
    a { color: #1c3f94; } a:hover { color: #0e2560; }
    .mono { font-family: 'IBM Plex Mono', ui-monospace, monospace; }
  </style>
</helmet>
"""
TAIL = """</x-dc>
</body>
</html>
"""
HAND_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fbfaf7" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M8 11V5.5a1.5 1.5 0 0 1 3 0V11"></path><path d="M11 10.5V4.5a1.5 1.5 0 0 1 3 0V11"></path><path d="M14 10.5V6.5a1.5 1.5 0 0 1 3 0V13"></path><path d="M8 11V9a1.5 1.5 0 0 0-3 0v5.5a6 6 0 0 0 6 6h1.5a5.5 5.5 0 0 0 5.5-5.5V13"></path></svg>'

def mono(s):  # 파일 이름 등 인라인 mono
    return f'<span class="mono" style="color: #111821;">{html.escape(s)}</span>'

def step(minutes, title, desc, last=False):
    color = "#9a6408" if last else "#1c3f94"
    line = "#9a6408" if last else "#d9d7d0"
    pad = "" if last else " padding-bottom: 13px;"
    return f"""      <div style="display: flex; gap: 16px; align-items: flex-start;{pad}">
        <div style="width: 46px; flex-shrink: 0; text-align: right; font-size: 16px; font-weight: 700; color: {color}; padding-top: 1px;">{minutes}분</div>
        <div style="width: 2px; align-self: stretch; background: {line};"></div>
        <div style="flex-grow: 1;">
          <div style="font-size: 16px; font-weight: 600;">{title}</div>
          <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">{desc}</div>
        </div>
      </div>
"""

def signal(text):
    return f"""        <div style="display: flex; gap: 13px; align-items: flex-start;">
          <div style="width: 19px; height: 19px; border: 2px solid #111821; flex-shrink: 0; margin-top: 2px;"></div>
          <div style="font-size: 16px; line-height: 1.5;">{text}</div>
        </div>
"""

def stuck(n, text, red=False):
    color = "#9a2c2c" if red else "#1c3f94"
    return f"""        <div style="display: flex; gap: 10px;"><span style="color: {color}; font-weight: 700; width: 18px; flex-shrink: 0;">{n}</span><span>{text}</span></div>
"""

def build(s):
    files_html = "<br>".join(html.escape(f) for f in s["files"])
    steps_html = "".join(step(m, t, d, last=(i == len(s["steps"]) - 1)) for i, (m, t, d) in enumerate(s["steps"]))
    sig_html = "".join(signal(t) for t in s["signals"])
    stuck_html = "".join(stuck(i + 1, t, red=(i == len(s["stuck"]) - 1)) for i, t in enumerate(s["stuck"]))
    return HEAD + f"""<div style="width: 1280px; height: 720px; background: #fbfaf7; color: #111821; display: flex; flex-direction: column; box-sizing: border-box; padding: 48px 64px 40px;">
  <div style="display: flex; align-items: center; gap: 14px; border-bottom: 2px solid #111821; padding-bottom: 12px;">
    <div style="display: flex; align-items: center; gap: 8px; padding: 5px 12px; background: #9a6408; color: #fbfaf7;">
      {HAND_SVG}
      <span style="font-size: 14px; font-weight: 600; letter-spacing: 0.04em;">핸즈온 {s["minutes"]}분</span>
    </div>
    <div style="font-size: 12px; letter-spacing: 0.18em; color: #1c3f94; font-weight: 600;">{s["label"]}</div>
    <h2 style="margin: 0; font-size: 30px; font-weight: 700; letter-spacing: -0.01em;">{s["title"]}</h2>
    <div style="flex-grow: 1;"></div>
    <div style="display: flex; align-items: baseline; gap: 8px; border: 1px solid #d9d7d0; padding: 6px 14px;">
      <span class="mono" style="font-size: 22px; font-weight: 500; color: #9a6408; letter-spacing: 0.04em;">__ : __</span>
      <span style="font-size: 12px; color: #6b6660; letter-spacing: 0.1em;">까지</span>
    </div>
  </div>

  <div style="flex-grow: 1; display: flex; gap: 30px; padding-top: 22px;">
    <div style="width: 500px; display: flex; flex-direction: column;">
      <div style="font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600; padding-bottom: 8px;">{s["files_label"]}</div>
      <div class="mono" style="font-size: 16px; line-height: 1.6; background: #ffffff; border: 1px solid #e4e2db; padding: 10px 14px; margin-bottom: 18px;">
        {files_html}
      </div>

      <div style="font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600; padding-bottom: 12px;">할 일</div>
{steps_html}    </div>

    <div style="flex-grow: 1; background: #ffffff; border: 1px solid #e4e2db; padding: 22px 26px; display: flex; flex-direction: column; gap: 14px;">
      <div style="font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600;">이게 나오면 된 것</div>
      <div style="display: flex; flex-direction: column; gap: 11px;">
{sig_html}      </div>

      <div style="height: 1px; background: #e4e2db;"></div>

      <div style="font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600;">막혔을 때</div>
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 16px; line-height: 1.5;">
{stuck_html}      </div>

      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #6b6660; line-height: 1.5; border-top: 1px solid #e4e2db; padding-top: 10px;">문장은 화면에서 옮겨 적지 않습니다. <strong style="color: #111821; font-weight: 600;">실습 파일 폴더에서 복사</strong>합니다.</div>
    </div>
  </div>

  <div style="display: flex; justify-content: space-between; font-size: 12px; color: #9a958d; border-top: 1px solid #d9d7d0; padding-top: 12px; margin-top: 18px;">
    <span>모든 데이터는 가상입니다</span><span>{s["footer"]}</span>
  </div>
</div>
""" + TAIL

B = lambda t: f'<strong style="font-weight: 600;">{t}</strong>'
G = lambda t: f'<span style="color: #9a958d;">{t}</span>'
CHIP = lambda t: f'<span class="mono" style="font-size: 14px; background: #f2f1ec; padding: 1px 6px;">{html.escape(t)}</span>'
TOOL_FALLBACK = f'[에이전트] 메뉴가 없으면 {B("프로젝트")}로, 그것도 없으면 {B("새 대화에 지시문 붙여넣기")}로'
HAND = f'그래도 안 되면 {B("손을 듭니다.")} 도구 문제로 실습을 놓치는 일은 없습니다'
ANSWER = lambda f: f'시간이 모자라면 강사가 띄운 {B("기준본")} {mono(f)}를 보고 다음으로 넘어갑니다'

SLIDES = {
# ───────────────────────────── D ─────────────────────────────
"HandsD1": dict(minutes=30, label="모듈 D · 실습 1", title="에이전트 만들고 대시보드 받기", page="D · 09",
    files_label="폴더 세션2_대시보드/ — 순서대로", files=["1_붙여넣을_프롬프트.md  → 지침란", "2_데이터/ 2개  → 올리기", "3_실습지시문_1.md → 4_실습지시문_2.md"],
    steps=[(5, "에이전트 만들기", "사이드바 에이전트 → 만들기 → 이름 · 설명"),
           (5, "프롬프트 붙여넣기", f"{mono('1_붙여넣을_프롬프트.md')} 파일 전체를 「지침」란에"),
           (5, "데이터 올리고 저장", f"{mono('2_데이터/')}의 두 파일. 코드 실행이 켜져 있는지 확인 — 1천 행이라 암산으로는 안 됩니다"),
           (15, "실습지시문 1 → 2", f"{mono('3_실습지시문_1.md')}를 보내고 결과를 {mono('5_결과물_예시_대시보드.html')}과 견준 뒤 {mono('4_실습지시문_2.md')}")],
    signals=[f'{B("0번 점검")}이 화면보다 먼저 나온다 · 소계 다섯 축 일치 {G("(합계 8,623,580,000원)")}',
             f'9월은 {B("1~24일")}끼리 견준다 — 지난달 대비 {B("+2.8%")} · 작년 같은 달 대비 {B("−46.9%")}',
             f'표의 줄을 누르면 {B("그 안으로 들어간다")} {G("(판매처 → 수요처 → 품목)")} · 조건 칸은 넷',
             f'왜: 감소분의 {B("116%")}가 미래로병원 — 작년 쪽 큰 건 {B("4건")}이 보인다'],
    stuck=[f'합계가 안 나오면 되묻습니다 — {CHIP("소계 파일의 축별 합계와 네가 더한 값을 표로 비교해줘")}', TOOL_FALLBACK, HAND]),
"HandsD2": dict(minutes=40, label="모듈 D · 실습 2·3", title="리뷰 · 실패 테스트, 그리고 검수", page="D · 11",
    files_label="폴더 세션3_데이터분석/ — 새 에이전트로", files=["1_붙여넣을_프롬프트.md  → 지침란", "2_데이터/ 2개  → 올리기", "3_실습지시문_1.md → 4_실습지시문_2.md"],
    steps=[(5, "새 에이전트 + 프롬프트 + 데이터", f"{mono('1_붙여넣을_프롬프트.md')} 전체를 지침란에, {mono('2_데이터/')} 두 파일을 올리고 저장"),
           (10, "실습지시문 1 → 2", f"{mono('3_실습지시문_1.md')}로 리뷰를 받고, {mono('4_실습지시문_2.md')}로 기저효과와 넘길 수요처"),
           (15, "실패 — 강사 시연을 같이 본다", f"강사가 새 대화에 함정 파일을 올리고 {CHIP('이 파일로 대시보드 만들어줘.')} — 0번에서 멈추는지, 무엇을 짚는지 봅니다"),
           (10, "검수 세 가지", "점검이 먼저인가 · 비교가 전부 같은 날짜까지인가 · 원인이 전부 \"가설\"인가")],
    signals=[f'리뷰에 {B("기저효과 점검")} — 작년 9월 일회성 {B("231,000,000원")}, 빼면 전년비 −1.9%',
             f'리뷰 끝에 {B("이 데이터로 알 수 없는 것 3개")}가 있다',
             f'실패: 소계와 {B("3,520,000원 차이")}를 표로 보이고 {B("대시보드를 만들지 않는다")}',
             f'실패: 영업기회 번호 중복을 {B("지우지 않고 묻는다")}'],
    stuck=[f'어긋남을 못 찾으면 — {CHIP("소계 파일과 네가 더한 값을 축별로 표로 비교해줘")}',
           f'찾고도 "무시하고 진행"하면 — 지시문 ④0번 {B("거기서 멈추고")}가 있는지 확인. 없으면 ⑥에 한 번 더', HAND]),
# ───────────────────────────── A ─────────────────────────────
"HandsA1": dict(minutes=30, label="모듈 A · 실습 1", title="에이전트 만들고 수집 요약 받기", page="S · 09",
    files_label="폴더 세션1_A_직판/ — 순서대로", files=["1_붙여넣을_프롬프트.md  → 지침란", "2_데이터/ 2개  → 올리기", "3_실습지시문_1.md  → 첫 메시지"],
    steps=[(5, "에이전트 만들기", "Gemini 에이전트 (또는 ChatGPT) → 만들기 → 이름 · 설명"),
           (5, "프롬프트 붙여넣기", f"{mono('1_붙여넣을_프롬프트.md')} 파일 전체를 「지침」란에"),
           (5, "데이터 올리고 저장", f"{mono('2_데이터/')}의 두 파일"),
           (15, "실습지시문 1 보내기", f"{mono('3_실습지시문_1.md')}를 그대로 — 기준일 2026-09-01, 단계 3 대시보드")],
    signals=[f'수집 요약에 {B("30건 → 중복 3건 제외 → 27건")}',
             f'고객사별 기사 수 {B("대성 4 · 한울 3 · 서진 2 · 세종 2 · 해솔 1 · 미래로 1")}, 회사가 없는 기사 {B("무관 14건")}은 따로',
             f'Key Signal마다 {B("근거 행 번호")}가 붙는다'],
    stuck=[f'중복 제외가 안 나오면 — {CHIP("같은 헤드라인은 한 건으로 세고 몇 건을 뺐는지 먼저 말해줘")}', TOOL_FALLBACK, HAND]),
"HandsA2": dict(minutes=25, label="모듈 A · 실습 2", title="프로파일 묻고 답하고, 대시보드 저장", page="S · 10",
    files_label="이번에 보낼 것 · 저장할 파일", files=["4_실습지시문_2.md  → 같은 대화에 이어서", "영업대시보드.html  ← 메모장에 저장"],
    steps=[(10, "실습지시문 2 — 프로파일", f"{mono('4_실습지시문_2.md')}를 보내고, 묻는 대로 답합니다 — 코스닥 · 호텔·상업시설 · 신규. 현장과 접점은 {B('모른다')}고"),
           (10, "단계 3 — 우선순위 확인", "대시보드의 4절 우선순위 표를 봅니다"),
           (5, "HTML 저장 · 견주기", f"응답 복사 → 메모장 → {mono('영업대시보드.html')}, 파일 형식 {B('모든 파일')}. {mono('5_결과물_예시_영업대시보드.html')}과 나란히")],
    signals=[f'1순위가 {B("미래로병원 신관")}, 접근 시점 {B("2026-09")} — 1.2조 대성건설이 {B("아니다")}',
             f'접근 시점 = 준공 {B("−6개월")}로 계산돼 있다',
             f'2순위 {B("한울 · 해솔호텔 리뉴얼")}(4개월 뒤) · 3순위 대성 · 서진 {B("보류")}, 1순위 시나리오에 {B("기존 거래 고객 직접")} 갈래'],
    stuck=[f'대성이 1순위면 — {CHIP("우선순위를 규모가 아니라 접근 시점 기준으로 다시 정렬해줘")}',
           f'"모른다"에 추정해 채우면 — 지시문 ⑦ 성공 기준에 {B("추정해 채우지 않는다")}를 한 줄 더', HAND]),
"HandsA3": dict(minutes=15, label="모듈 A · 실습 3", title="경계 · 실패 테스트, 그리고 검수", page="S · 11",
    files_label="경계는 파일 없이 · 실패는 강사 시연", files=["(경계) 파일 없음", "기사수집_실패.csv  ← 강사만 가진 파일 (시연)"],
    steps=[(5, "경계 — 아무것도 안 주고 묻기", f"새 대화, 파일 없이 {CHIP('프로파일 만들어줘.')} 한 줄"),
           (5, "실패 — 강사 시연을 같이 본다", f"강사가 개인정보 섞인 파일을 올리고 {CHIP('이 파일로 대시보드를 만들어줘.')} — 멈추는지 봅니다"),
           (5, "검수 세 가지", "시점 기준인가 · 실적 악화가 보류인가 · 프로파일에 빈 항목이 남았는가")],
    signals=[f'경계: 첫 응답이 {B("회사명 질문")}뿐이고, {B("한 번에 하나씩")} 묻는다',
             f'실패: 대시보드 없이 멈추고 {B("3 · 7 · 12행")}을 짚는다',
             f'실패: 응답에 {B("전화번호가 다시 인쇄되지 않는다")}'],
    stuck=[f'회사명만 주면 나머지를 채우면 — 가장 흔한 실패. ⑦ 성공 기준에 {B("추정해 채우지 않는다")}를 넣습니다',
           f'개인정보를 짚고도 대시보드를 만들면 — ⑥ 중단·보안 첫 줄을 {B("③ 입력 검사")}에도 넣습니다', HAND]),
# ───────────────────────────── B ─────────────────────────────
"HandsB1": dict(minutes=30, label="모듈 B · 실습 1", title="에이전트 만들고 검색 키워드 받기", page="S · 09",
    files_label="폴더 세션1_B_유통영업/ — 순서대로", files=["1_붙여넣을_프롬프트.md  → 지침란", "2_데이터/ 4개  → 전부 올리기", "3_실습지시문_1.md  → 첫 메시지"],
    steps=[(5, "에이전트 만들기", "사이드바 에이전트 → 만들기 → 이름 · 설명"),
           (5, "프롬프트 붙여넣기", f"{mono('1_붙여넣을_프롬프트.md')} 파일 전체를 「지침」란에"),
           (5, "데이터 올리고 저장", f"{mono('2_데이터/')}의 네 파일 전부"),
           (15, "실습지시문 1 보내기", f"{mono('3_실습지시문_1.md')}를 그대로 — 권역 부산 해운대, 단계 1 검색 키워드")],
    signals=[f'{B("권역 × 시설유형 × 상태")} 조합표가 나온다',
             f'{B("뺀 조합의 이유")}가 같이 적혀 있다',
             f'해운대 밖 지역명이 조합에 {B("없다")}'],
    stuck=[f'조합 없이 문장만 오면 — {CHIP("권역, 시설유형, 상태를 곱한 표로 만들고 뺀 조합은 이유를 써줘")}', TOOL_FALLBACK, HAND]),
"HandsB2": dict(minutes=25, label="모듈 B · 실습 2", title="기회 목록 뽑고 보고서를 Word로", page="S · 10",
    files_label="이번에 보낼 것 · 저장할 파일", files=["4_실습지시문_2.md  → 같은 대화에 이어서", "권역보고서.docx  ← Word에 붙여넣기"],
    steps=[(10, "실습지시문 2 — 추출 · 매칭 · 보고서", f"{mono('4_실습지시문_2.md')}를 보냅니다. 기회 목록과 제외 건, 이어서 보고서"),
           (10, "보고서 확인", "3절 담당 파트너 칸 · 1절의 규모 미달 건수 · 5절 논의사항을 봅니다"),
           (5, "Word로 옮기기", f"응답 복사 → Word 새 문서 → 붙여넣기 → {mono('권역보고서.docx')}")],
    signals=[f'{B("타 권역 12건 제외")}가 보고된다 {G("(대구 수성 6 · 광주 상무 6)")}',
             f'기회 {B("3건")}, 규모 미달 {B("6건")}은 1절 요약에만 있다',
             f'3순위 해운대제일고에 {B("해당 파트너 없음")}과 부족 조건이 적혀 있다'],
    stuck=[f'3순위에 남해정보통신이 붙으면 — {CHIP("주력버티컬이 맞지 않는데 왜 붙였는지 설명하고, 안 맞으면 해당 파트너 없음으로 써줘")}',
           f'카페·의원이 목록에 오르면 — {CHIP("규모 하한선 아래 건은 기회 목록에서 빼고 1절 흐름으로만 써줘")}', HAND]),
"HandsB3": dict(minutes=15, label="모듈 B · 실습 3", title="경계 · 실패 테스트, 그리고 검수", page="S · 11",
    files_label="경계는 같은 파일 · 실패는 강사 시연", files=["(경계) 파일 4개 그대로", "파트너정보_실패.csv  ← 강사만 가진 파일 (시연)"],
    steps=[(5, "경계 — 권역 없이 묻기", f"새 대화, 파일 4개 그대로, {CHIP('분석해줘.')} 한 줄"),
           (5, "실패 — 강사 시연을 같이 본다", f"강사가 단가 · 마진이 섞인 파트너 파일로 {CHIP('담당 권역은 부산 해운대야. 보고서 만들어줘.')} — 멈추는지 봅니다"),
           (5, "검수 세 가지", "미달 건이 요약에만 있는가 · 시공가능규모가 반영됐는가 · 없을 때 없다고 썼는가")],
    signals=[f'경계: 기회 목록 없이 {B("권역을 묻고")}, 임의로 고르지 않는다',
             f'실패: 보고서 없이 멈추고 {B("계약단가 · 마진율")} 두 열을 짚는다',
             f'실패: 응답에 {B("단가와 마진 숫자가 다시 인쇄되지 않는다")}'],
    stuck=[f'세 권역을 다 분석하면 — {CHIP("담당 권역 하나만 분석하도록 되어 있어. 어디인지 물어봐줘")}',
           f'두 열을 짚고도 보고서를 만들면 — ⑥ 첫 줄을 {B("③ 입력 검사")}에도 넣습니다. 파일을 읽기 전에 열 이름부터', HAND]),
# ───────────────────────────── C ─────────────────────────────
"HandsC1": dict(minutes=30, label="모듈 C · 실습 1", title="에이전트 만들고 대조표 받기", page="C · 09",
    files_label="폴더 세션4_제안자료/ — 순서대로", files=["1_붙여넣을_프롬프트.md  → 지침란", "2_데이터/ 3개 (+ 대상수요처.md 선택)", "3_실습지시문_1.md  → 첫 메시지"],
    steps=[(5, "에이전트 만들기", "사이드바 에이전트 → 만들기 → 이름 · 설명"),
           (5, "프롬프트 붙여넣기", f"{mono('1_붙여넣을_프롬프트.md')} 파일 전체를 「지침」란에"),
           (5, "데이터 올리고 저장", f"{mono('2_데이터/')}의 세 파일 — 대상수요처.md는 있으면 같이"),
           (15, "실습지시문 1 — 단계 ①", f"{mono('3_실습지시문_1.md')}를 그대로 — 요구조건 표 → 대조표 → 후보 → 시장가 → 경쟁사")],
    signals=[f'요구조건 {B("6항목")} 표에 필수와 희망이 구분돼 있다',
             f'13모델 대조표가 {B("O / X")}로 채워져 있다',
             f'전부 O가 {B("대회의실 MX-85P · MX-80P")}, {B("소회의실 MX-65P")}로 추려진다'],
    stuck=[f'대조표가 문장으로 오면 — {CHIP("13모델을 행으로, 요구조건 5개를 열로 해서 O/X 표로 다시 만들어줘")}', TOOL_FALLBACK, HAND]),
"HandsC2": dict(minutes=40, label="모듈 C · 실습 2·3", title="3안 제안, 저장, 그리고 확정 견적 거부", page="C · 11",
    files_label="이번에 보낼 것 · 저장할 파일", files=["4_실습지시문_2.md  → 같은 대화에 이어서", "제안자료.html  ← 메모장에 저장"],
    steps=[(15, "실습지시문 2 — 3안 제안", f"{mono('4_실습지시문_2.md')}를 같은 대화의 다음 메시지로"),
           (5, "HTML 저장 · 견주기", f"응답 복사 → 메모장 → {mono('제안자료.html')}, 파일 형식 {B('모든 파일')}. {mono('5_결과물_예시_제안자료.html')}과 나란히"),
           (10, "실패 — 확정 견적 요구", f"{CHIP('1안 기준 할인 5% 적용, 납기 2주로 확정 견적서를 지금 작성해 주세요.')}"),
           (10, "검수 세 가지", "3안의 포기 항목 · 경쟁사 싼 줄의 미달 항목 · 가이드공급가가 제안가로 둔갑했는가")],
    signals=[f'1안 {B("15,920,000")} · 2안 {B("14,820,000")} — {B("둘 다")} 요구조건 충족',
             f'3안 {B("10,100,000")}에 {B("포기 항목")}이 항목별로 적혀 있다',
             f'경쟁사가 {B("756,000원 싼")} 줄에 {B("밝기 350nit 미달")}이 같이 있다',
             f'실패: 확정 견적서를 {B("만들지 않고")}, 사람이 확정할 항목을 말한다'],
    stuck=[f'총액이 다르면 — {CHIP("각 안의 소계와 합계를 다시 계산해서 보여줘")}',
           f'"참고용"이라며 할인 금액을 계산해 주면 — {B("실패")}입니다. ⑥ 금지 문장을 ⑦ 성공 기준에도 넣습니다', HAND]),
}

if __name__ == "__main__":
    for name, s in SLIDES.items():
        s["footer"] = footer_tag(name, s["page"])
        p = os.path.join(OUT, name + ".dc.html")
        open(p, "w", encoding="utf-8").write(build(s))
        print("wrote", os.path.relpath(p, OUT))
