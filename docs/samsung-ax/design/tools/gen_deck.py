# -*- coding: utf-8 -*-
"""덱 슬라이드(실습 외)를 같은 헤더·푸터 골격으로 생성한다. 본문은 슬라이드마다 HTML로 쓴다.
사용: python3 gen_deck.py  (design/ 안에 Deck*.dc.html을 쓴다)"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..")

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
TAIL = "</x-dc>\n</body>\n</html>\n"

def grow(body):
    i = body.find('<div style="')
    return body[:i+12] + "flex-grow: 1; " + body[i+12:]

def shell(label, title, caption, body, page, badge=None):
    b = f'<div style="font-size: 12px; letter-spacing: 0.14em; padding: 4px 10px; background: #9a6408; color: #fbfaf7; font-weight: 600;">{badge}</div>' if badge else ""
    return HEAD + f"""<div style="width: 1280px; height: 720px; background: #fbfaf7; color: #111821; display: flex; flex-direction: column; box-sizing: border-box; padding: 48px 64px 40px;">
  <div style="display: flex; align-items: baseline; gap: 14px; border-bottom: 2px solid #111821; padding-bottom: 12px;">
    {b}<div style="font-size: 12px; letter-spacing: 0.18em; color: #1c3f94; font-weight: 600;">{label}</div>
    <h2 style="margin: 0; font-size: 30px; font-weight: 700; letter-spacing: -0.01em;">{title}</h2>
    <div style="flex-grow: 1;"></div>
    <div style="font-size: 12px; color: #6b6660;">{caption}</div>
  </div>
  <div style="flex-grow: 1; display: flex; flex-direction: column; padding-top: 24px; gap: 18px;">
{grow(body)}
  </div>
  <div style="display: flex; justify-content: space-between; font-size: 12px; color: #9a958d; border-top: 1px solid #d9d7d0; padding-top: 12px; margin-top: 18px;">
    <span>모든 데이터는 가상입니다</span><span>{page}</span>
  </div>
</div>
""" + TAIL

# 꼬리표 아이콘 (Tags4와 같은 선 아이콘)
def tag(kind, size=18):
    c = {"lock": "#9a2c2c", "draft": "#1c3f94", "repeat": "#0f6b4f", "outside": "#6b6660"}[kind]
    name = {"lock": "사람만", "draft": "AI 초안", "repeat": "AI 반복", "outside": "밖에서 가져옴"}[kind]
    path = {
        "lock": '<rect x="4" y="10.5" width="16" height="10" rx="1.6"></rect><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"></path>',
        "draft": '<path d="M16.5 4.5l3 3L8 19l-4 1 1-4z"></path><path d="M14.5 6.5l3 3"></path>',
        "repeat": '<circle cx="12" cy="12" r="3.2"></circle><path d="M12 3v2.4M12 18.6V21M3 12h2.4M18.6 12H21M5.6 5.6l1.7 1.7M16.7 16.7l1.7 1.7M18.4 5.6l-1.7 1.7M7.3 16.7l-1.7 1.7"></path>',
        "outside": '<path d="M9 3v5M15 3v5"></path><rect x="6.5" y="8" width="11" height="6" rx="1.4"></rect><path d="M12 14v3.5a3 3 0 0 0 3 3h2"></path>',
    }[kind]
    return (f'<span style="display: inline-flex; align-items: center; gap: 5px; color: {c}; font-size: 14px; font-weight: 600; white-space: nowrap;">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">{path}</svg>{name}</span>')

CARD = 'background: #ffffff; border: 1px solid #e4e2db;'
LBL = 'font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600;'
WARN = 'background: #ffffff; border: 1px solid #e4e2db; border-left: 4px solid #9a2c2c; padding: 14px 18px;'
BAND = 'display: flex; align-items: center; gap: 18px; padding: 18px 26px; background: #111821; color: #fbfaf7;'

SLIDES = {}

# ───────────── O2 오늘 에이전트 4개를 만듭니다 ─────────────
def agent_card(letter, name, team, skill, out, accent="#1c3f94"):
    return f"""<div style="{CARD} border-top: 3px solid {accent}; padding: 16px 18px; display: flex; flex-direction: column; gap: 8px; flex: 1 0 0;">
  <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: {accent};">{letter}</span><span style="font-size: 19px; font-weight: 600;">{name}</span></div>
  <div style="font-size: 14px; color: #6b6660;">{team}</div>
  <div style="font-size: 14px; line-height: 1.5; padding-top: 4px; border-top: 1px solid #e4e2db;">에이전트 <span style="color: #6b6660;">1개 · 2시간</span><br>스킬 <span class="mono" style="font-size: 13px;">{skill}</span></div>
  <div style="font-size: 14px; color: #6b6660;">결과물 <span class="mono" style="font-size: 13px; color: #111821;">{out}</span></div>
</div>"""
ARROW = '<div style="display: flex; align-items: center; color: #9a958d; font-size: 22px; padding: 0 4px;">→</div>'
SLIDES["DeckO2"] = shell("오프닝", "오늘 에이전트 4개를 만듭니다", "한 칸 = 2시간 = 에이전트 하나", f"""
    <div style="display: flex; gap: 12px; align-items: stretch;">
      <div style="display: flex; flex-direction: column; gap: 10px; flex: 1.1 0 0;">
        <div style="{LBL}">시장 · 고객 분석 — 팀별로 하나</div>
        {agent_card("A", "직판 Sensing", "B2B팀 · 상장 건설사 1곳을 깊게", "sensing-listed-builders", "dashboard_A.html")}
        {agent_card("B", "경로 Sensing", "B2B유통전략팀 · 권역의 작은 시설 여럿을 넓게", "scanning-district-openings", "report_B.docx")}
      </div>
      {ARROW}
      <div style="display: flex; flex-direction: column; gap: 10px; flex: 1 0 0;">
        <div style="{LBL}">데이터 분석 — 공통</div>
        {agent_card("D", "데이터 분석", "전원 · 과거 실적에서 추천 TOP 3", "recommending-products-by-vertical", "recommend_D.html", "#9a6408")}
      </div>
      {ARROW}
      <div style="display: flex; flex-direction: column; gap: 10px; flex: 1 0 0;">
        <div style="{LBL}">제안자료 작성 — 공통</div>
        {agent_card("C", "제안자료 작성", "전원 · 요구조건에 맞는 3안 + 시장가 비교", "proposing-display-options", "proposal_C.html")}
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">에이전트는 넷, 모듈당 하나.</div>
      <div style="font-size: 16px; color: #c9c5bd;">모듈 안에 단계가 셋이어도 에이전트는 하나입니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; text-align: right; line-height: 1.5;">본 과정 6시간은 셋 — 수업 순서 <strong style="color: #fbfaf7;">D → A 또는 B → C</strong><br>양성과정 2일은 넷 전부</div>
    </div>""", "O · 02")

# ───────────── O4 시작 전 준비 ─────────────
def prep(n, title, desc):
    return f"""<div style="{CARD} padding: 18px 22px; display: flex; gap: 16px; align-items: flex-start;">
  <div style="font-size: 30px; font-weight: 700; color: #1c3f94; line-height: 1; width: 40px; flex-shrink: 0;">{n}</div>
  <div style="display: flex; flex-direction: column; gap: 6px;"><div style="font-size: 19px; font-weight: 600;">{title}</div><div style="font-size: 14px; color: #6b6660; line-height: 1.55;">{desc}</div></div>
</div>"""
SLIDES["DeckO4"] = shell("오프닝", "시작 전 준비", "3분이면 됩니다", f"""
    <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px;">
      {prep(1, "탭 두 개", "AI 창(ChatGPT 또는 Gemini) 하나, <strong style='font-weight: 600; color: #111821;'>메모장</strong> 하나. 지시문은 메모장에 먼저 둡니다 — 세션이 끊기면 채팅창의 지시문은 사라집니다")}
      {prep(2, "저장 폴더", "<span class='mono' style='font-size: 13px; color: #111821;'>바탕화면/AX실습_내이름/</span> 하나를 만들어 둡니다. 모듈마다 결과 파일 하나가 여기 쌓입니다")}
      {prep(3, "업로드 테스트", "작은 파일로 먼저 — <span class='mono' style='font-size: 13px; color: #111821;'>target_account.md</span> (1KB). 큰 파일로 시도하다 실패하면 시간이 날아갑니다")}
      {prep(4, "이번 모듈 폴더 열어 두기", "배포 폴더의 <span class='mono' style='font-size: 13px; color: #111821;'>modules/D_analysis/</span>. 파일 이름은 화면에 뜬 것을 그대로 씁니다")}
    </div>
    <div style="{WARN} display: flex; align-items: center; gap: 16px;">
      <div style="font-size: 19px; font-weight: 600; color: #9a2c2c;">오늘 올리는 파일은 전부 가상 데이터입니다.</div>
      <div style="font-size: 16px; color: #3d4650;">실제 고객사명 · 계약 단가 · 실적 파일은 올리지 않습니다. 실습이 끝나도 같습니다.</div>
    </div>""", "O · 04")

# ───────────── O5 웹에서 결과를 남기는 법 ─────────────
def step_card(n, title, desc, last=False):
    return f"""<div style="{CARD} border-top: 3px solid {'#9a6408' if last else '#1c3f94'}; padding: 18px 18px 16px; display: flex; flex-direction: column; gap: 8px; flex: 1 0 0;">
  <div style="font-size: 12px; color: #9a958d; font-weight: 600;">0{n}</div>
  <div style="font-size: 19px; font-weight: 600; line-height: 1.35;">{title}</div>
  <div style="font-size: 14px; color: #6b6660; line-height: 1.55;">{desc}</div>
</div>"""
SLIDES["DeckO5"] = shell("오프닝", "웹에서 결과를 남기는 법", "모듈이 끝날 때마다 한 번", f"""
    <div style="display: flex; gap: 10px; align-items: stretch;">
      {step_card(1, "화면에서 복사", "결과 부분만 드래그해 복사합니다. Ctrl+A는 화면 전체가 잡힙니다")}
      {ARROW}
      {step_card(2, "메모장에 붙여넣기", "워드·한글도 됩니다. AI 창이 아니라 내 PC의 프로그램입니다")}
      {ARROW}
      {step_card(3, "이름 정해 저장", "모듈마다 파일 하나. 이름은 아래 표대로. HTML은 파일 형식을 <strong style='font-weight: 600; color: #111821;'>모든 파일</strong>로")}
      {ARROW}
      {step_card(4, "다음 모듈에 업로드", "폴더에서 바로 참조되지 않습니다. 다시 올려야 이어집니다", last=True)}
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} padding: 14px 20px; flex: 1 0 0; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px 16px; font-size: 14px; align-content: center;">
        <div style="color: #6b6660;">A 직판 Sensing</div><div style="color: #6b6660;">B 경로 Sensing</div><div style="color: #6b6660;">C 제안자료</div><div style="color: #6b6660;">D 데이터 분석</div>
        <div class="mono" style="font-size: 13px;">dashboard_A.html</div><div class="mono" style="font-size: 13px;">report_B.docx</div><div class="mono" style="font-size: 13px;">proposal_C.html</div><div class="mono" style="font-size: 13px;">recommend_D.html</div>
      </div>
      <div style="{WARN} width: 420px; flex-shrink: 0; display: flex; flex-direction: column; gap: 4px; justify-content: center;">
        <div style="font-size: 16px; font-weight: 600; color: #9a2c2c;">AI에게 "파일로 만들어줘"라고 하지 않습니다.</div>
        <div style="font-size: 14px; color: #3d4650; line-height: 1.5;">웹에서 AI가 만든 파일은 다운로드가 막히거나 깨집니다. 화면에 텍스트로 받고 사람이 저장합니다.</div>
      </div>
    </div>""", "O · 05")

# ───────────── W7 묶으면 에이전트가 나옵니다 ─────────────
def ipo_row(n, p, o, kind, shade=False):
    return f"""<tr style="{'background: #f7f6f2;' if shade else ''}"><td style="padding: 7px 10px; color: #9a958d; font-weight: 600; width: 34px;">{n}</td><td style="padding: 7px 10px;">{p}</td><td class="mono" style="padding: 7px 10px; font-size: 13px; color: #3d4650;">{o}</td><td style="padding: 7px 10px; width: 118px;">{tag(kind)}</td></tr>"""
SLIDES["DeckW7"] = shell("일을 보는 법", "④ 묶으면 에이전트가 나옵니다", "C 모듈 분해표 그대로", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="{CARD} flex: 1.15 0 0; display: flex; flex-direction: column;">
        <div style="padding: 12px 16px 8px; {LBL}">C 제안자료 — 단계별 IPO에 꼬리표를 붙인 것</div>
        <table style="border-collapse: collapse; font-size: 14px; width: 100%;">
          <tr style="color: #9a958d; font-size: 12px; letter-spacing: 0.08em;"><td style="padding: 4px 10px;">#</td><td style="padding: 4px 10px;">하는 일 (P)</td><td style="padding: 4px 10px;">내놓는 것 (O)</td><td style="padding: 4px 10px;">꼬리표</td></tr>
          {ipo_row(3, "사이트를 열어 본다", "복사한 텍스트", "outside")}
          {ipo_row(4, "4열로 정제한다", "naver_crawl.csv", "repeat", True)}
          {ipo_row("2·5", "조건을 뽑고 맞는 모델을 고른다", "후보 모델 목록", "draft")}
          {ipo_row("6·7", "비교하고 3안을 쓴다", "proposal_C.html", "draft", True)}
          {ipo_row("8·9", "가격·납기를 확정해 보낸다", "확정 견적", "lock")}
        </table>
      </div>
      <div style="display: flex; align-items: center; color: #9a958d; font-size: 22px;">→</div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 10px;">
        <div style="{LBL}">묶은 결과</div>
        <div style="{CARD} border-left: 3px solid #6b6660; padding: 10px 14px; font-size: 14px; display: flex; gap: 10px; align-items: center;"><span style="color: #9a958d; font-weight: 600;">3</span><span>입력 — 사람이 화면에서 가져와 올립니다</span></div>
        <div style="border: 2px solid #1c3f94; padding: 12px 14px; display: flex; flex-direction: column; gap: 8px; background: #ffffff;">
          <div style="display: flex; justify-content: space-between; align-items: baseline;"><span style="font-size: 16px; font-weight: 700; color: #1c3f94;">에이전트 1개</span><span style="font-size: 12px; color: #6b6660;">사이에 사람만 단계가 없습니다</span></div>
          <div style="display: flex; gap: 8px;">
            <div style="flex: 1 0 0; background: #eef0ea; padding: 10px 12px; font-size: 14px;"><div style="color: #9a958d; font-weight: 600; font-size: 12px;">4</div><strong style="font-weight: 600;">단계 ⓪</strong> 수집 정제</div>
            <div style="flex: 1 0 0; background: #eef0ea; padding: 10px 12px; font-size: 14px;"><div style="color: #9a958d; font-weight: 600; font-size: 12px;">2·5</div><strong style="font-weight: 600;">단계 ①</strong> 조건 분석 + 모델 추출</div>
            <div style="flex: 1 0 0; background: #eef0ea; padding: 10px 12px; font-size: 14px;"><div style="color: #9a958d; font-weight: 600; font-size: 12px;">6·7</div><strong style="font-weight: 600;">단계 ②</strong> 비교 + 3안</div>
          </div>
        </div>
        <div style="{WARN} font-size: 14px; display: flex; gap: 10px; align-items: center;"><span style="color: #9a958d; font-weight: 600;">8·9</span><span><strong style="font-weight: 600; color: #9a2c2c;">⑥ 중단 · ⑦ 승인</strong> — "확정 견적서는 만들지 않는다". 실패 테스트가 여기서 나왔습니다</span></div>
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">{'<span style="color: #e88b8b;">사람만</span>이 끼면 나눕니다. 없으면 단계로.'}</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">네 모듈 전부 에이전트 1개 + 단계 1~3개. 프롬프트가 셋인 건 우리가 정한 게 아니라 일이 그렇게 생겼습니다.</div>
    </div>""", "W · 07")

# ───────────── M4 그럴듯함 ≠ 정확함 ─────────────
SLIDES["DeckM4"] = shell("공통 방법론", "그럴듯함 ≠ 정확함", "왜 근거와 검수를 붙이는가", f"""
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 51 0 0; padding: 26px 30px; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #1c3f94;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600;">채택된 답</div>
        <div style="font-size: 30px; font-weight: 700; color: #1c3f94; line-height: 1;"><span style="font-size: 96px; letter-spacing: -0.03em;">51</span><span style="font-size: 30px;">%</span></div>
        <div style="font-size: 16px; line-height: 1.55; color: #3d4650;">확률이 조금 더 높았던 다음 말. <strong style="font-weight: 600; color: #111821;">100%처럼 말합니다.</strong></div>
      </div>
      <div style="{CARD} flex: 49 0 0; padding: 26px 30px; display: flex; flex-direction: column; justify-content: space-between; border-top: 4px solid #9a2c2c; background: #f7f6f2;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600;">조용히 버려진 것</div>
        <div style="font-size: 30px; font-weight: 700; color: #9a2c2c; line-height: 1;"><span style="font-size: 96px; letter-spacing: -0.03em;">49</span><span style="font-size: 30px;">%</span></div>
        <div style="font-size: 16px; line-height: 1.55; color: #3d4650;">예외 · 반대 근거 · "자료에 없음". <strong style="font-weight: 600; color: #111821;">말해 주지 않습니다.</strong></div>
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">그래서 수치마다 근거 행, 결과마다 사람 검수.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 460px; line-height: 1.5;">"자료에 없으면 확인 필요"라고 쓰게 허용하는 것이 첫 번째 규칙입니다. 채워 넣는 에이전트보다 빈칸을 남기는 에이전트가 낫습니다.</div>
    </div>""", "M · 04")

# ───────────── D3 오늘 만들 결과물 ─────────────
def sec(n, t, d):
    return f'<div style="display: flex; gap: 12px; align-items: baseline; padding: 8px 0; border-bottom: 1px solid #eeece6;"><span class="mono" style="font-size: 13px; color: #1c3f94; width: 18px; flex-shrink: 0;">{n}</span><span style="font-size: 16px; font-weight: 600; width: 150px; flex-shrink: 0;">{t}</span><span style="font-size: 14px; color: #6b6660;">{d}</span></div>'
SLIDES["DeckD3"] = shell("모듈 D", "오늘 만들 결과물", "recommend_D.html — 브라우저에서 열리는 보고서 1개", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 16px 22px; display: flex; flex-direction: column;">
        <div style="{LBL} padding-bottom: 8px;">절 순서 — 이대로 나와야 합니다</div>
        {sec(0, "데이터 점검", "합계 · 검산 · 빈칸. 보고서보다 먼저")}
        {sec(1, "대상 수요처 분석", "해솔호텔 제주 · 같은 체인 부산점의 이력")}
        {sec(2, "버티컬별 판매 Insight", "호텔 68.4% · 모델별 집계 · 반복 구매 패턴")}
        {sec(3, "추천 제품 TOP 3", "순위 · 용도 · 근거 행 번호 + 수치")}
        {sec(4, "영업 제안 Point", "수량 · 검증된 구성 · 확인 필요 사항")}
      </div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 12px;">
        <div style="{CARD} border-top: 3px solid #0f6b4f; padding: 14px 20px; display: flex; flex-direction: column; gap: 8px;">
          <div style="font-size: 12px; letter-spacing: 0.16em; color: #0f6b4f; font-weight: 600;">반드시 같아야 하는 것 — 셋</div>
          <div style="font-size: 16px; line-height: 1.5;">전체 합계 <strong style="font-weight: 600;">570,258,000원</strong> · 검산 불일치 0건</div>
          <div style="font-size: 16px; line-height: 1.5;">TOP 3 순서 <strong style="font-weight: 600;">HX-55T → BX-65S → ST-H1</strong> (HX-50T는 대안)</div>
          <div style="font-size: 16px; line-height: 1.5;">추천마다 근거 행 번호 — 예: <strong style="font-weight: 600;">6 · 22 · 30 · 47행</strong></div>
        </div>
        <div style="{CARD} padding: 14px 20px; display: flex; flex-direction: column; gap: 8px;">
          <div style="{LBL}">달라도 되는 것</div>
          <div style="font-size: 16px; line-height: 1.5; color: #3d4650;">문장 표현 · 표의 열 순서 · 길이 · 절 제목의 말투 · 색과 서식</div>
          <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">내 화면이 예시와 한 글자 달라도 손을 들 일이 아닙니다. 위 셋만 봅니다.</div>
        </div>
      </div>
    </div>""", "D · 03")

# ───────────── D5 0번 데이터 점검 ─────────────
def vrow(n, c, q, a, p, bold=False):
    w = "font-weight: 600;" if bold else ""
    return f'<tr style="{w}"><td style="padding: 6px 10px;">{n}</td><td style="padding: 6px 10px; text-align: right;">{c}</td><td style="padding: 6px 10px; text-align: right;">{q}</td><td style="padding: 6px 10px; text-align: right;">{a}</td><td style="padding: 6px 10px; text-align: right; color: {"#1c3f94" if bold else "#6b6660"};">{p}</td></tr>'
SLIDES["DeckD5"] = shell("모듈 D", "보고서보다 먼저 오는 것", "0번 데이터 점검", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 12px;">
        <div style="{CARD} padding: 20px 24px; display: flex; flex-direction: column; gap: 6px;">
          <div style="{LBL}">전체 판매금액 합계</div>
          <div style="font-size: 30px; font-weight: 700; color: #1c3f94; letter-spacing: -0.01em;"><span style="font-size: 54px;">570,258,000</span> 원</div>
          <div style="font-size: 14px; color: #6b6660;">52행 · 버티컬별 소계의 합과 같아야 합니다</div>
        </div>
        <div style="{CARD} padding: 14px 20px; display: flex; flex-direction: column; gap: 8px; font-size: 16px; line-height: 1.5;">
          <div>검산 <span class="mono" style="font-size: 13px;">공급가 × 판매수량 = 판매금액</span> — <strong style="font-weight: 600;">52행 모두 일치, 불일치 0건</strong></div>
          <div>필수 컬럼 10개 이상 없음 · 결측·중복 없음 · 버티컬 값 5종만</div>
        </div>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 12px 8px 8px;">
        <div style="{LBL} padding: 4px 10px 8px;">버티컬별 소계</div>
        <table style="border-collapse: collapse; width: 100%; font-size: 16px;">
          <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 10px;">버티컬</td><td style="padding: 4px 10px; text-align: right;">건수</td><td style="padding: 4px 10px; text-align: right;">수량</td><td style="padding: 4px 10px; text-align: right;">판매금액(원)</td><td style="padding: 4px 10px; text-align: right;">비율</td></tr>
          {vrow("호텔", 22, "1,103", "390,290,000", "68.4%", True)}
          {vrow("상업시설", 8, 39, "70,800,000", "12.4%")}
          {vrow("교육시설", 8, 29, "51,620,000", "9.1%")}
          {vrow("오피스", 8, 13, "30,728,000", "5.4%")}
          {vrow("병원", 6, 19, "26,820,000", "4.7%")}
          <tr style="border-top: 1px solid #d9d7d0; font-weight: 600;"><td style="padding: 8px 10px;">합계</td><td style="padding: 8px 10px; text-align: right;">52</td><td style="padding: 8px 10px; text-align: right;">1,203</td><td style="padding: 8px 10px; text-align: right;">570,258,000</td><td style="padding: 8px 10px; text-align: right;">100%</td></tr>
        </table>
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">점검이 먼저 나오지 않으면 그 뒤는 읽지 않습니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 440px; line-height: 1.5;">틀린 파일로 만든 추천은 근거가 통째로 틀립니다. 실패 테스트 파일의 450,000원 차이가 그걸 보여 줍니다.</div>
    </div>""", "D · 05")

# ───────────── D10 근거가 붙은 추천이란 ─────────────
def rec(rank, model, kind, use, evidence, rows, strength, accent="#1c3f94"):
    return f"""<div style="{CARD} display: flex; align-items: stretch; flex: 1 0 0;">
  <div style="width: 64px; background: {accent}; color: #fbfaf7; display: flex; align-items: center; justify-content: center; font-size: 30px; font-weight: 700; flex-shrink: 0;">{rank}</div>
  <div style="padding: 12px 18px; display: flex; flex-direction: column; gap: 4px; flex-grow: 1; justify-content: center;">
    <div style="display: flex; align-items: baseline; gap: 10px;"><span class="mono" style="font-size: 22px; font-weight: 500;">{model}</span><span style="font-size: 14px; color: #6b6660;">{kind} · {use}</span><div style="flex-grow: 1;"></div><span style="font-size: 12px; color: #9a958d;">{strength}</span></div>
    <div style="font-size: 16px; line-height: 1.5;">{evidence} <span class="mono" style="font-size: 13px; color: #1c3f94;">{rows}</span></div>
  </div>
</div>"""
SLIDES["DeckD10"] = shell("모듈 D", "근거가 붙은 추천이란", "기준본 recommend_D.html 3절 그대로", f"""
    <div style="display: flex; flex-direction: column; gap: 10px;">
      {rec(1, "HX-55T", "호텔TV", "객실 120실 — 축 A 1위", "호텔 5개 수요처 <strong style='font-weight: 600;'>464대 283,040,000원</strong>, 호텔 판매금액의 72.5%. 같은 체인 부산점도 96대", "6 · 22 · 25 · 30 · 47행", "강함 · 5개 수요처")}
      {rec(2, "BX-65S", "사이니지", "로비 안내 — 축 B 1위", "호텔 3개 수요처 <strong style='font-weight: 600;'>8대</strong>, 전부 로비 용도. 객실 TV 구매 다음 달에 추가", "8 · 24 · 32행", "보통 · 3개 수요처")}
      {rec(3, "ST-H1", "액세서리", "객실 TV 스탠드 — 조합 동반", "HX-55T 구매 5건 <strong style='font-weight: 600;'>전부 같은 수량으로 동반</strong>, 464대. 단독 판매 없음", "7 · 23 · 31 · 48 · 53행", "강함 · 5개 수요처", "#9a6408")}
    </div>
    <div style="display: flex; gap: 14px;">
      <div style="{CARD} flex: 1 0 0; padding: 12px 18px; font-size: 14px; line-height: 1.5; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">대안</strong> HX-50T — 축 A의 2위(3 · 29행). 한 축에서 1위 하나만 올립니다. <strong style="font-weight: 600; color: #111821;">축 밖</strong> KX-55K · MX-85P · BX-43S · BX-55S — 대상 용도(객실 TV · 로비)에 없음</div>
      <div style="{BAND} flex: 1 0 0; padding: 12px 20px;"><div style="font-size: 19px; font-weight: 700;">행 번호가 없으면 추천이 아니라 의견입니다.</div></div>
    </div>""", "D · 10")

# ───────────── Z2 다섯 가지 원칙 ─────────────
def principle(n, t, d):
    return f"""<div style="{CARD} border-top: 3px solid #1c3f94; padding: 18px 16px; display: flex; flex-direction: column; gap: 10px; flex: 1 0 0;">
  <div style="font-size: 12px; color: #9a958d; font-weight: 600;">0{n}</div>
  <div style="font-size: 19px; font-weight: 600; line-height: 1.3;">{t}</div>
  <div style="font-size: 14px; color: #6b6660; line-height: 1.55;">{d}</div>
</div>"""
SLIDES["DeckZ2"] = shell("클로징", "다섯 가지 원칙", "네 모듈에 전부 걸려 있던 것", f"""
    <div style="display: flex; gap: 10px; align-items: stretch;">
      {principle(1, "보안 최우선", "고객 실명 · 계약 단가 · 미공개 실적은 넣지 않습니다. 오늘 가상 데이터로 실습한 이유")}
      {principle(2, "Human-in-the-Loop", "AI는 초안 · 후보 · 표까지. 제안 여부 · 가격 · 발송은 사람")}
      {principle(3, "할루시네이션 관리", "&quot;자료에 없으면 확인 필요&quot;를 허용합니다. 수치마다 근거 행")}
      {principle(4, "작은 범위", "업무의 5~10%만. 제안서 전체가 아니라 제품 후보 3개")}
      {principle(5, "결과 검증", "금액 · 고객명 · 모델 코드 · 대외 문구는 반드시 사람이 확인")}
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">오늘 실패 테스트에서 멈춘 에이전트가 이 다섯을 지킨 에이전트입니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">내 업무로 옮길 때도 순서는 같습니다 — 범위를 작게, 데이터는 가상으로, 결과는 검수.</div>
    </div>""", "Z · 02")

# ───────────── D1 모듈 표지 (첫 모듈 타임바) — 어두운 표지는 골격이 다르다 ─────────────
def bar(segs):
    out = []
    for m, t, kind in segs:
        bg = {"talk": "#1c3f94", "hands": "#9a6408", "buf": "#2c4a8f"}[kind]
        fg = {"talk": "#c3cde8", "hands": "#fbfaf7", "buf": "#8fa4d8"}[kind]
        w = ' font-weight: 500;' if kind == "hands" else ''
        out.append(f'<div style="flex: {m} 0 0; background: {bg}; display: flex; align-items: center; padding-left: 10px; font-size: 12px; color: {fg};{w} overflow: hidden; white-space: nowrap;">{t} {m}</div>')
    return "".join(out)
SLIDES["DeckD1"] = HEAD + f"""<div style="width: 1280px; height: 720px; background: #0e2560; color: #fbfaf7; display: flex; flex-direction: column; justify-content: space-between; padding: 48px 64px 40px; box-sizing: border-box;">
  <div style="display: flex; align-items: center; gap: 16px;">
    <div style="font-size: 12px; letter-spacing: 0.22em; color: #8fa4d8; font-weight: 500;">모듈 D · 첫 모듈</div>
    <div style="flex-grow: 1; height: 1px; background: #2c4a8f;"></div>
    <div style="font-size: 12px; color: #8fa4d8;">2.0h · 에이전트 1개 · 단계 1개</div>
  </div>
  <div style="display: flex; flex-direction: column; gap: 22px;">
    <h1 style="margin: 0; font-size: 60px; line-height: 1.15; font-weight: 700; letter-spacing: -0.02em;">데이터 분석 Agent</h1>
    <p style="margin: 0; font-size: 22px; line-height: 1.6; color: #c3cde8; max-width: 760px;">과거 판매 실적에서 같은 버티컬(업종)의 구매 패턴을 찾아 <strong style="color: #fbfaf7; font-weight: 600;">근거가 붙은 추천 3건</strong>을 제시합니다.</p>
    <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #8fa4d8; max-width: 760px;">단계가 하나라 가장 먼저 만듭니다. 그래서 오프닝과 <strong style="color: #c3cde8; font-weight: 600;">일을 보는 법</strong>이 이 2시간 안에 들어 있습니다.</p>
  </div>
  <div style="display: flex; flex-direction: column; gap: 14px;">
    <div style="display: flex; gap: 3px; align-items: stretch; height: 34px;">
      {bar([(10, "오프닝", "talk"), (30, "일 보는 법 + 분해표", "talk"), (10, "시연", "talk"), (25, "실습 1", "hands"), (10, "방법론", "talk"), (25, "실습 2·3", "hands"), (5, "전환", "talk"), (5, "버퍼", "buf")])}
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8fa4d8;">
      <span>첫 모듈만 이 배분입니다 · A · B · C는 실습 70분</span>
      <span>D · 01</span>
    </div>
  </div>
</div>
""" + TAIL

if __name__ == "__main__":
    for name, src in SLIDES.items():
        open(os.path.join(OUT, name + ".dc.html"), "w", encoding="utf-8").write(src)
        print("wrote", name)
