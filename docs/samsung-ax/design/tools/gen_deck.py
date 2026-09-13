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

def bar(segs):
    out = []
    for m, t, kind in segs:
        bg = {"talk": "#1c3f94", "hands": "#9a6408", "buf": "#2c4a8f"}[kind]
        fg = {"talk": "#c3cde8", "hands": "#fbfaf7", "buf": "#8fa4d8"}[kind]
        w = ' font-weight: 500;' if kind == "hands" else ''
        out.append(f'<div style="flex: {m} 0 0; background: {bg}; display: flex; align-items: center; padding-left: 10px; font-size: 12px; color: {fg};{w} overflow: hidden; white-space: nowrap;">{t} {m}</div>')
    return "".join(out)

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


# ───────────── D2 지금은 이렇게 일합니다 + 분해표 ─────────────
def drow(n, job, kind, where, band=None, shade=False):
    bg = 'background: #eef0ea;' if band == "agent" else ('background: #fbeeee;' if band == "lock" else ('background: #f7f6f2;' if shade else ''))
    return f'<tr style="{bg}"><td style="padding: 6px 10px; color: #9a958d; font-weight: 600; width: 30px;">{n}</td><td style="padding: 6px 10px;">{job}</td><td style="padding: 6px 10px; width: 130px;">{tag(kind, 16)}</td><td class="mono" style="padding: 6px 10px; font-size: 13px; color: #3d4650; width: 150px;">{where}</td></tr>'
SLIDES["DeckD2"] = shell("모듈 D", "지금은 이렇게 일합니다 — 그리고 이렇게 쪼갰습니다", "분해표 10줄", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="width: 330px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px;">
        <div style="{CARD} padding: 16px 20px; display: flex; flex-direction: column; gap: 8px;">
          <div style="{LBL}">지금</div>
          <div style="font-size: 16px; line-height: 1.6; color: #3d4650;">실적 엑셀을 열어 같은 업종 고객이 무엇을 샀는지 <strong style="font-weight: 600; color: #111821;">눈으로</strong> 필터하고, 반복된 조합을 찾습니다. 수백 행이면 반나절. "왜 이 제품인가"는 따로 씁니다.</div>
        </div>
        <div style="{CARD} border-left: 3px solid #1c3f94; padding: 14px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;">
          <strong style="font-weight: 600; color: #111821;">2~8번이 붙어 있어 에이전트 1개.</strong> D의 지시문이 하나인 이유입니다. 9·10번이 사람만이라 거기서 잘립니다.
        </div>
        <div style="{CARD} border-left: 3px solid #9a2c2c; padding: 14px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;">
          <strong style="font-weight: 600; color: #9a2c2c;">2번을 빼면 어떻게 되는지</strong>가 이 모듈의 시험입니다. 사람도 자주 건너뜁니다.
        </div>
      </div>
      <div style="{CARD} flex-grow: 1; padding: 8px 6px;">
        <table style="border-collapse: collapse; width: 100%; font-size: 14px;">
          <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 10px;">#</td><td style="padding: 4px 10px;">내가 하는 일</td><td style="padding: 4px 10px;">꼬리표</td><td style="padding: 4px 10px;">지시문 어디로</td></tr>
          {drow(1, "실적 엑셀을 연다", "outside", "입력 파일")}
          {drow(2, "숫자가 맞는지 훑어본다 (합계 · 빈칸)", "repeat", "④-0 데이터 점검", "agent")}
          {drow(3, "대상 수요처의 버티컬을 확인한다", "draft", "④-1", "agent")}
          {drow(4, "같은 버티컬만 필터한다", "repeat", "④-2", "agent")}
          {drow(5, "모델별로 수량 · 금액을 더한다", "repeat", "④-2", "agent")}
          {drow(6, "반복해서 같이 팔린 조합을 찾는다", "draft", "④-2", "agent")}
          {drow(7, "추천 3개를 고른다", "draft", "④-3", "agent")}
          {drow(8, "왜 이 제품인지 근거를 붙인다", "draft", "④-4", "agent")}
          {drow(9, "가격 · 수량을 가격가이드와 대조해 확정한다", "lock", "⑦ 확인 필요 사항", "lock")}
          {drow(10, "고객에게 제안한다", "lock", "⑦", "lock")}
        </table>
        <div style="display: flex; gap: 18px; padding: 10px 10px 4px; font-size: 12px; color: #6b6660;"><span><span style="display: inline-block; width: 12px; height: 12px; background: #eef0ea; vertical-align: -1px; border: 1px solid #d9d7d0;"></span> 에이전트 1개로 묶이는 구간</span><span><span style="display: inline-block; width: 12px; height: 12px; background: #fbeeee; vertical-align: -1px; border: 1px solid #d9d7d0;"></span> 사람만 — 에이전트 밖</span></div>
      </div>
    </div>""", "D · 02")

# ───────────── D4 입력 데이터 ─────────────
def frow(f, hdr, n, src, alt=False):
    c = "color: #6b6660;" if alt else ""
    return f'<tr style="{c}"><td class="mono" style="padding: 8px 10px; font-size: 13px; white-space: nowrap;">{f}</td><td style="padding: 8px 10px; font-size: 14px; line-height: 1.45;">{hdr}</td><td style="padding: 8px 10px; text-align: right; font-size: 14px;">{n}</td><td style="padding: 8px 10px; font-size: 14px;">{src}</td></tr>'
SLIDES["DeckD4"] = shell("모듈 D", "입력 데이터", "배포 폴더 modules/D_analysis/01_data/", f"""
    <div style="{CARD} padding: 8px 6px;">
      <table style="border-collapse: collapse; width: 100%;">
        <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 10px;">파일</td><td style="padding: 4px 10px;">헤더</td><td style="padding: 4px 10px; text-align: right;">행</td><td style="padding: 4px 10px;">어디서 온 것으로 가정</td></tr>
        {frow("sales_history.csv", "판매일자 · 버티컬 · 수요처 · 제품군 · 모델명 · 공급가 · 판매수량 · 판매금액 · 프로젝트/용도 · 지역 <span style='color: #9a958d;'>(10열)</span>", 52, "사내 B2B 판매 실적 2025-01 ~ 2026-08")}
        {frow("target_account.md", "수요처명 · 버티컬 · 프로젝트/용도", 1, "영업 담당자가 입력")}
        <tr><td colspan="4" style="padding: 6px 10px 2px; font-size: 12px; color: #9a958d; letter-spacing: 0.06em; border-top: 1px solid #e4e2db;">코드 실행이 안 될 때 — 둘을 함께</td></tr>
        {frow("sales_history_소계.csv", "축 · 값 · 합계 — 버티컬 · 제품군 · 지역 · 모델명 네 축", 26, "검산용", True)}
        {frow("sales_history_호텔모델별.csv", "모델명 · 제품군 · 건수 · 판매수량 · 판매금액 · 수요처수 · 근거행", 10, "추천용 — 이게 없으면 TOP 3가 안 나옵니다", True)}
      </table>
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 20px; display: flex; flex-direction: column; gap: 8px;">
        <div style="{LBL}">target_account.md — 한 줄이 전부입니다</div>
        <table style="border-collapse: collapse; font-size: 16px;"><tr style="font-size: 12px; color: #9a958d;"><td style="padding: 2px 12px 2px 0;">수요처명</td><td style="padding: 2px 12px;">버티컬</td><td style="padding: 2px 12px;">프로젝트/용도</td></tr><tr><td style="padding: 4px 12px 4px 0; font-weight: 600;">해솔호텔 제주</td><td style="padding: 4px 12px;">호텔</td><td style="padding: 4px 12px;">신축 · 객실 120실 + 로비 · 2027-03 개관</td></tr></table>
        <div style="font-size: 14px; color: #6b6660;">같은 체인 해솔호텔 부산이 실적에 있습니다. 이걸 찾는지가 1절의 포인트입니다.</div>
      </div>
      <div style="{WARN} width: 400px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; gap: 4px;">
        <div style="font-size: 19px; font-weight: 600; color: #9a2c2c;">모든 데이터는 가상입니다.</div>
        <div style="font-size: 14px; color: #3d4650; line-height: 1.5;">수요처 · 모델명 · 공급가 · 실적 전부. 삼성전자 실제 정보와 무관하며, 실제 실적 파일은 올리지 않습니다.</div>
      </div>
    </div>""", "D · 04")

# ───────────── D6 이 데이터의 함정 ─────────────
def trap(n, t, d):
    return f"""<div style="{CARD} border-top: 3px solid #9a6408; padding: 20px 22px; display: flex; flex-direction: column; gap: 10px; flex: 1 0 0;">
  <div style="font-size: 12px; color: #9a958d; font-weight: 600;">함정 0{n}</div>
  <div style="font-size: 19px; font-weight: 600; line-height: 1.35;">{t}</div>
  <div style="font-size: 14px; color: #6b6660; line-height: 1.55;">{d}</div>
</div>"""
SLIDES["DeckD6"] = shell("모듈 D", "이 데이터의 함정 세 가지", "정답은 말하지 않습니다 — 결과에서 확인하세요", f"""
    <div style="display: flex; gap: 12px; align-items: stretch;">
      {trap(1, "호텔이 금액의 3분의 2입니다", "호텔 22행이 전체 판매금액의 68%. 호텔이 아닌 버티컬의 큰 금액 한 건 — 상업시설 미디어월 같은 것 — 에 끌려가면 대상 수요처와 상관없는 추천이 나옵니다.")}
      {trap(2, "금액 순으로 보면 안 보이는 것이 있습니다", "단가가 작은 제품은 금액 순위에서 5위 밖입니다. <strong style='font-weight: 600; color: #111821;'>수량과 동반 구매</strong>로 보면 자리가 달라집니다. 지시문의 축이 둘인 이유입니다.")}
      {trap(3, "대상은 신규지만, 처음 보는 고객이 아닙니다", "해솔호텔 제주는 실적에 없습니다. 그런데 같은 체인의 다른 지점이 있습니다. 1절에서 이걸 찾아내는지가 첫 번째 확인 항목입니다.")}
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">셋 다 사람이 엑셀에서 실제로 빠지는 함정입니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 480px; line-height: 1.5;">에이전트가 피해 가는지는 실습 1의 결과로 봅니다. 하나라도 걸리면 지시문 ④-2 · ④-3을 다시 읽습니다.</div>
    </div>""", "D · 06")

# ───────────── D7 두 갈래 경로 ─────────────
SLIDES["DeckD7"] = shell("모듈 D", "두 갈래 경로", "내 도구에서 코드 실행이 되는가", f"""
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #0f6b4f; padding: 20px 24px; display: flex; flex-direction: column; gap: 12px;">
        <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #0f6b4f;">코드 실행 O</span><span style="font-size: 14px; color: #6b6660;">ChatGPT 데이터 분석이 켜져 있다</span></div>
        <div style="font-size: 16px; line-height: 1.55;">원본 <span class="mono" style="font-size: 13px;">sales_history.csv</span> 한 개를 그대로 올립니다. 52행을 코드로 더하므로 합계가 맞습니다.</div>
        <div style="flex-grow: 1;"></div>
        <div style="font-size: 14px; color: #6b6660;">올리는 파일 <strong style="font-weight: 600; color: #111821;">2개</strong> — 원본 + target_account.md</div>
      </div>
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #9a6408; padding: 20px 24px; display: flex; flex-direction: column; gap: 12px;">
        <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #9a6408;">코드 실행 X</span><span style="font-size: 14px; color: #6b6660;">Gemini, 또는 실행이 막힌 포털</span></div>
        <div style="font-size: 16px; line-height: 1.55;">AI가 52행을 머릿속으로 더하면 <strong style="font-weight: 600;">산술 오류</strong>가 납니다. 원본 대신 사람이 미리 집계한 두 파일을 올립니다.</div>
        <div style="display: flex; flex-direction: column; gap: 6px; font-size: 14px;">
          <div><span class="mono" style="font-size: 13px;">sales_history_소계.csv</span> <span style="color: #6b6660;">— 네 축 합계, 검산용</span></div>
          <div><span class="mono" style="font-size: 13px;">sales_history_호텔모델별.csv</span> <span style="color: #6b6660;">— 모델 단위 집계, 추천용</span></div>
        </div>
        <div style="flex-grow: 1;"></div>
        <div style="font-size: 14px; color: #6b6660;">올리는 파일 <strong style="font-weight: 600; color: #111821;">3개</strong> — 소계본 + 호텔모델별 + target_account.md</div>
      </div>
    </div>
    <div style="display: flex; gap: 14px;">
      <div style="{WARN} flex: 1 0 0; display: flex; align-items: center; gap: 14px;"><div style="font-size: 19px; font-weight: 600; color: #9a2c2c;">소계본만 올리면 추천이 안 나옵니다.</div><div style="font-size: 14px; color: #3d4650;">버티컬별 금액까지만 나오고 TOP 3가 비어 있으면 호텔모델별 파일을 빠뜨린 것입니다.</div></div>
      <div style="{CARD} width: 430px; flex-shrink: 0; padding: 12px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;">검산은 어느 갈래든 같습니다 — 버티컬별 = 제품군별 = 지역별 = 모델명별 = <strong style="font-weight: 600; color: #111821;">570,258,000</strong>. 하나라도 다르면 중단.</div>
    </div>""", "D · 07")

# ───────────── D8 집계를 사람이 먼저 하는 이유 ─────────────
SLIDES["DeckD8"] = shell("모듈 D", "집계를 사람이 먼저 하는 이유", "우회가 아니라 순서입니다", f"""
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 22px 26px; display: flex; flex-direction: column; gap: 12px; background: #f7f6f2;">
        <div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #9a2c2c;">✕</span><span style="font-size: 19px; font-weight: 600;">원본 수만 행을 그대로 던진다</span></div>
        <div style="font-size: 16px; line-height: 1.6; color: #3d4650;">무엇을 더할지, 무엇끼리 묶을지를 AI가 정합니다. 그럴듯한 축을 고르고, 틀려도 그럴듯하게 말합니다. 검산할 기준이 없습니다.</div>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 22px 26px; display: flex; flex-direction: column; gap: 12px; border-top: 4px solid #0f6b4f;">
        <div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #0f6b4f;">○</span><span style="font-size: 19px; font-weight: 600;">필요한 축으로 줄여서 넘긴다</span></div>
        <div style="font-size: 16px; line-height: 1.6; color: #3d4650;">버티컬 · 제품군 · 지역 · 모델명 — 네 축의 합계가 전부 <strong style="font-weight: 600; color: #111821;">570,258,000</strong>으로 같아야 합니다. 축을 정한 사람이 검산 기준도 쥐고 있습니다.</div>
        <div class="mono" style="font-size: 13px; line-height: 1.7; background: #f2f1ec; padding: 10px 14px; margin-top: 4px;">390,290,000 + 70,800,000 + 51,620,000<br>+ 30,728,000 + 26,820,000 = 570,258,000 ✓</div>
        <div style="font-size: 14px; color: #6b6660;">AI가 낸 숫자 중 하나만 골라 직접 검산합니다. 하나가 맞으면 나머지도 대체로 맞고, 하나가 틀리면 전부 다시 시킵니다.</div>
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">무엇을 축으로 삼을지 정하는 것이 사람의 일이고, 그 판단이 결과의 절반입니다.</div>
    </div>""", "D · 08")

# ───────────── D12 내 업무로 전환 ─────────────
COLS = ["판매일자", "버티컬", "수요처", "제품군", "모델명", "공급가", "판매수량", "판매금액", "프로젝트/용도", "지역"]
chips = "".join(f'<span style="border: 1px solid #d9d7d0; background: #ffffff; padding: 6px 12px; font-size: 16px;">{c}</span>' for c in COLS)
def q(n, t, d):
    return f'<div style="display: flex; gap: 12px; align-items: flex-start;"><span style="font-size: 22px; font-weight: 700; color: #1c3f94; width: 28px; flex-shrink: 0; line-height: 1.2;">{n}</span><div><div style="font-size: 16px; font-weight: 600; line-height: 1.4;">{t}</div><div style="font-size: 14px; color: #6b6660; line-height: 1.5;">{d}</div></div></div>'
SLIDES["DeckD12"] = shell("모듈 D", "내 업무로 전환", "5분 — 워크북 부록에 적습니다", f"""
    <div style="{CARD} padding: 16px 22px; display: flex; flex-direction: column; gap: 12px;">
      <div style="{LBL}">오늘 쓴 실적 파일의 10개 컬럼</div>
      <div style="display: flex; flex-wrap: wrap; gap: 8px;">{chips}</div>
      <div style="font-size: 16px; line-height: 1.5;">내 실적 파일에는 이 중 <strong style="font-weight: 600;">무엇이 있고 무엇이 없는가?</strong> 없는 것은 어디서 가져오나? — 이 표 하나면 지시문 ③ 입력 검사가 내 것이 됩니다.</div>
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 16px 22px; display: flex; flex-direction: column; gap: 14px;">
        {q(1, "내 버티컬 이름은 무엇인가", "사내 분류가 있으면 그 표기로. 없으면 오늘 5종(호텔 · 상업시설 · 병원 · 오피스 · 교육시설)에서 시작")}
        {q(2, "축을 무엇으로 잡나", "오늘은 용도 축 둘(객실 TV · 로비). 내 제품군에서는 몇 개인가")}
        {q(3, "9 · 10번은 누가 확정하나", "가격 · 수량은 가격가이드와 대조해 사람이. 이 줄이 지시문 ⑦에 그대로 들어갑니다")}
      </div>
      <div style="width: 400px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px;">
        <div style="{CARD} padding: 14px 18px; display: flex; flex-direction: column; gap: 6px;">
          <div style="{LBL}">스킬로 뗄 것</div>
          <div style="font-size: 14px; line-height: 1.55; color: #3d4650;">점검 절차 · 축 선정 규칙 · HTML 4절 양식 · 확정가 금지 · 검수 기준 — 누가 써도 같은 것. <span class="mono" style="font-size: 13px; color: #111821;">recommending-products-by-vertical</span></div>
          <div style="font-size: 14px; line-height: 1.55; color: #3d4650;">실적 파일 · 버티컬 명칭 · 대상 수요처 — 우리 팀 것. 에이전트에 남깁니다.</div>
        </div>
        <div style="{CARD} border-left: 3px solid #1c3f94; padding: 12px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">다음 모듈로</strong> — TOP 3를 <span class="mono" style="font-size: 13px;">recommended_models.csv</span>로 저장해 두면 C 모듈의 후보 힌트로 쓸 수 있습니다 (선택).</div>
      </div>
    </div>""", "D · 12")


# ═══════════════════════ 블록 2 — 오프닝 · 일 보는 법 · 방법론 ═══════════════════════
def lbar(segs):
    out = []
    for m, t, kind in segs:
        bg = {"talk": "#1c3f94", "hands": "#9a6408", "buf": "#8fa4d8", "common": "#0e2560"}[kind]
        fg = "#fbfaf7"
        out.append(f'<div style="flex: {m} 0 0; background: {bg}; display: flex; align-items: center; padding-left: 8px; font-size: 12px; color: {fg}; overflow: hidden; white-space: nowrap;">{t} {m}</div>')
    return "".join(out)
def session(n, name, who, segs, note):
    return f"""<div style="{CARD} padding: 14px 18px; display: flex; flex-direction: column; gap: 8px;">
  <div style="display: flex; align-items: baseline; gap: 12px;"><span style="font-size: 12px; letter-spacing: 0.16em; color: #9a958d; font-weight: 600;">{n}교시</span><span style="font-size: 19px; font-weight: 600;">{name}</span><span style="font-size: 14px; color: #6b6660;">{who}</span><div style="flex-grow: 1;"></div><span style="font-size: 12px; color: #6b6660;">{note}</span></div>
  <div style="display: flex; gap: 2px; height: 30px;">{lbar(segs)}</div>
</div>"""
SLIDES["DeckO3"] = shell("오프닝", "오늘의 흐름", "2시간 블록 셋 · 에이전트 1개 = 2시간", f"""
    <div style="display: flex; flex-direction: column; gap: 10px;">
      {session(1, "D 데이터 분석", "전원 · 첫 모듈", [(10,"오프닝","common"),(30,"일 보는 법 + 분해표","common"),(10,"시연","talk"),(25,"실습 1","hands"),(10,"방법론","common"),(25,"실습 2·3","hands"),(5,"전환","talk"),(5,"버퍼","buf")], "오프닝 · 일 보는 법이 여기 들어 있습니다 — 실습 50")}
      {session(2, "A 또는 B 시장·고객 분석", "B2B팀은 A · 유통전략팀은 B", [(20,"방법론 5장 + 분해표","common"),(15,"시연","talk"),(30,"실습 1","hands"),(25,"실습 2","hands"),(15,"실습 3","hands"),(10,"전환","talk"),(5,"버퍼","buf")], "실습 70")}
      {session(3, "C 제안자료 작성", "전원", [(20,"방법론 2장 + 분해표","common"),(15,"시연","talk"),(30,"실습 1","hands"),(40,"실습 2·3","hands"),(15,"Skill + 클로징","common")], "실습 70")}
    </div>
    <div style="display: flex; gap: 18px; align-items: center; font-size: 12px; color: #6b6660; padding: 0 4px;">
      <span><span style="display: inline-block; width: 12px; height: 12px; background: #0e2560; vertical-align: -1px;"></span> 공통 설명</span><span><span style="display: inline-block; width: 12px; height: 12px; background: #1c3f94; vertical-align: -1px;"></span> 모듈 설명 · 시연</span><span><span style="display: inline-block; width: 12px; height: 12px; background: #9a6408; vertical-align: -1px;"></span> 핸즈온</span><span><span style="display: inline-block; width: 12px; height: 12px; background: #8fa4d8; vertical-align: -1px;"></span> 버퍼</span>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">6시간 = 120분 × 3. 실습이 190분입니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">양성과정 2일은 A와 B를 모두 해서 넷 전부 만듭니다.</div>
    </div>""", "O · 03")

# ───────────── O6 에이전트는 여기서 만듭니다 ─────────────
def path(title, sub, steps, accent="#1c3f94"):
    rows = "".join(f'<div style="display: flex; gap: 12px; align-items: flex-start;"><span style="font-size: 14px; font-weight: 700; color: {accent}; width: 20px; flex-shrink: 0;">{i+1}</span><div style="font-size: 16px; line-height: 1.45;">{t}</div></div>' for i, t in enumerate(steps))
    return f"""<div style="{CARD} border-top: 3px solid {accent}; padding: 16px 20px; display: flex; flex-direction: column; gap: 10px; flex: 1 0 0;">
  <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 19px; font-weight: 600;">{title}</span><span style="font-size: 14px; color: #6b6660;">{sub}</span></div>
  {rows}
</div>"""
SLIDES["DeckO6"] = shell("오프닝", "에이전트는 여기서 만듭니다", "메뉴 이름은 화면에 뜬 그대로", f"""
    <div style="display: flex; gap: 14px; align-items: stretch;">
      {path("ChatGPT", "주 경로 · 모델은 Instant", ["사이드바 <strong style='font-weight: 600;'>[에이전트]</strong> → 우측 상단 <strong style='font-weight: 600;'>[만들기]</strong>", "이름 · 설명 — 이름 앞에 내 이름을 붙이면 목록에서 찾기 쉽습니다", "<strong style='font-weight: 600;'>[지침]</strong>에 배포 파일의 ✂ 사이를 붙여넣기", "<strong style='font-weight: 600;'>[파일 업로드]</strong>에 이번 모듈 파일 · <strong style='font-weight: 600;'>[대화 시작]</strong>에 예시 3개", "<strong style='font-weight: 600;'>[저장]</strong> — 첫 메시지는 대화 시작 예시 1번"])}
      {path("Gemini", "대체 경로 · 모델은 Flash", ["사이드바 <strong style='font-weight: 600;'>[에이전트]</strong> → <strong style='font-weight: 600;'>[+ 새 에이전트]</strong>", "<strong style='font-weight: 600;'>&quot;이 단계를 건너뛰고 수동으로 빌드&quot;</strong>를 고릅니다 — 자연어로 만들게 하면 지시문이 요약돼 7블록이 무너집니다", "지침에 같은 ✂ 사이를 붙여넣기", "참조 파일 업로드", "<strong style='font-weight: 600;'>[저장]</strong> — 내 것은 <strong style='font-weight: 600;'>내 에이전트</strong> 탭에 있습니다"], "#0f6b4f")}
    </div>
    <div style="{WARN} display: flex; gap: 24px; align-items: center;">
      <div style="font-size: 16px; font-weight: 600; color: #9a2c2c; white-space: nowrap;">메뉴가 없으면</div>
      <div style="font-size: 14px; color: #3d4650; line-height: 1.55;"><strong style="font-weight: 600; color: #111821;">대안 1</strong> [프로젝트] → 새 프로젝트 → 프로젝트 지침에 같은 지시문 · 같은 파일 → 프로젝트 안에서 새 대화 &nbsp;&nbsp;<strong style="font-weight: 600; color: #111821;">대안 2</strong> 새 대화 → 지시문 전체를 첫 메시지로 → 클립 아이콘으로 파일 첨부. 세션이 끊기면 다시 붙여넣습니다</div>
    </div>""", "O · 06")

# ───────────── O7 HTML 결과를 여는 법 ─────────────
SLIDES["DeckO7"] = shell("오프닝", "HTML 결과를 여는 법", "A · C · D의 결과물은 HTML 코드로 옵니다", f"""
    <div style="display: flex; gap: 10px; align-items: stretch;">
      {step_card(1, "[복사] 버튼", "코드 블록 오른쪽 위. 드래그보다 정확합니다")}
      {ARROW}
      {step_card(2, "메모장에 붙여넣기", "시작 → &quot;메모장&quot; 검색 → Ctrl+V")}
      {ARROW}
      {step_card(3, "다른 이름으로 저장", "파일 이름 <span class='mono' style='font-size: 13px; color: #111821;'>recommend_D.html</span> — 확장자까지 직접<br>파일 형식 <strong style='font-weight: 600; color: #111821;'>모든 파일 (*.*)</strong> · 인코딩 <strong style='font-weight: 600; color: #111821;'>UTF-8</strong>")}
      {ARROW}
      {step_card(4, "더블클릭", "브라우저에서 보고서가 열립니다. 제목과 표가 보이면 성공", last=True)}
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{WARN} flex: 1 0 0; display: flex; flex-direction: column; justify-content: center; gap: 4px;">
        <div style="font-size: 19px; font-weight: 600; color: #9a2c2c;">코드가 그대로 보이면 .txt로 저장된 것입니다.</div>
        <div style="font-size: 14px; color: #3d4650;">③에서 파일 형식을 안 바꾸면 <span class="mono" style="font-size: 13px;">recommend_D.html.txt</span>가 됩니다. 이름을 바꿔 .html로 끝나게 하면 됩니다.</div>
      </div>
      <div style="{CARD} width: 420px; flex-shrink: 0; padding: 14px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">출력이 중간에 끊겼다면</strong> 채팅창에 <span class="mono" style="font-size: 13px; background: #f2f1ec; padding: 1px 6px;">이어서 출력해줘</span> — 이어진 부분을 메모장 끝에 붙입니다. <span class="mono" style="font-size: 13px;">&lt;/html&gt;</span>로 끝나야 완성입니다.</div>
    </div>""", "O · 07")

# ───────────── O8 지시문은 메모장에 먼저 ─────────────
def vs(bad_t, bad_d, good_t, good_d):
    return f"""<div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
  <div style="{CARD} flex: 1 0 0; padding: 22px 26px; background: #f7f6f2; display: flex; flex-direction: column; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #9a2c2c;">✕</span><span style="font-size: 19px; font-weight: 600;">{bad_t}</span></div>
    <div style="font-size: 16px; line-height: 1.6; color: #3d4650;">{bad_d}</div>
  </div>
  <div style="{CARD} flex: 1 0 0; padding: 22px 26px; border-top: 4px solid #0f6b4f; display: flex; flex-direction: column; gap: 10px;">
    <div style="display: flex; align-items: center; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #0f6b4f;">○</span><span style="font-size: 19px; font-weight: 600;">{good_t}</span></div>
    <div style="font-size: 16px; line-height: 1.6; color: #3d4650;">{good_d}</div>
  </div>
</div>"""
SLIDES["DeckO8"] = shell("오프닝", "지시문은 메모장에 먼저", "세션이 끊기면 채팅창의 지시문은 사라집니다", vs(
    "채팅창에만 쓴다", "창을 닫거나 세션이 만료되면 지시문이 없어집니다. 다음 차수에 처음부터 다시 씁니다. 고친 내용도 같이 사라집니다.",
    "메모장에 두고 붙여넣는다", "배포 파일 <span class='mono' style='font-size: 13px; color: #111821;'>02_prompt/prompt_1.md</span>를 열어 <span class='mono' style='font-size: 13px; color: #111821;'>agentD_prompt.txt</span>로 저장. 채팅창에는 붙여넣기만. 고칠 때는 메모장에서 고치고 다시 붙여넣습니다.<br><br>세션이 끊겨도, 다음 차수에도, 동료에게 넘길 때도 그대로입니다.") + f"""
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">"컨텍스트를 데이터로 다룬다"의 가장 작은 실천입니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">스킬 기능이 열려 있으면 보관 장소만 워크스페이스로 바뀝니다. 만드는 내용은 같습니다.</div>
    </div>""", "O · 08")

# ───────────── W1 못 만드는 이유 ─────────────
SLIDES["DeckW1"] = shell("일을 보는 법", "에이전트를 못 만드는 진짜 이유", "이 과정의 첫 시간", f"""
    <div style="{CARD} padding: 30px 34px; display: flex; flex-direction: column; gap: 14px; flex-grow: 1; justify-content: center;">
      <div style="font-size: 30px; font-weight: 700; line-height: 1.35; letter-spacing: -0.01em;">지시문을 못 써서가 아닙니다.<br><span style="color: #1c3f94;">지금 일이 어떻게 흘러가는지 적어 본 적이 없어서</span>입니다.</div>
      <div style="font-size: 16px; color: #6b6660; line-height: 1.6; max-width: 900px;">그래서 오늘은 지시문보다 먼저 일을 봅니다. 프로세스를 그리고, 단계마다 무엇을 받아 무엇을 내놓는지 적고, 꼬리표를 붙이고, 묶습니다. 그러면 에이전트의 개수와 경계가 정해져 있고, 남은 것은 옮겨 적는 일입니다.</div>
    </div>
    <div style="display: flex; gap: 14px;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 20px; background: #f7f6f2; display: flex; flex-direction: column; gap: 6px;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #9a2c2c; font-weight: 600;">프로세스가 아닌 것</div>
        <div style="font-size: 16px; line-height: 1.5; color: #3d4650;">✕ 영업을 효율화한다 &nbsp;&nbsp; ✕ AI로 업무를 자동화한다</div>
      </div>
      <div style="{CARD} flex: 1.4 0 0; padding: 14px 20px; border-top: 3px solid #0f6b4f; display: flex; flex-direction: column; gap: 6px;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #0f6b4f; font-weight: 600;">프로세스</div>
        <div style="font-size: 16px; line-height: 1.5;">○ 요구조건 메일을 받는다 → 조건을 표로 적는다 → 가격가이드에서 모델을 찾는다 → …</div>
      </div>
    </div>""", "W · 01")

# ───────────── W3 ① As-Is 프로세스 ─────────────
def arow(n, st, who, t, block, hot=False):
    bg = 'background: #fbeeee;' if hot else ''
    tw = 'font-weight: 700; color: #9a2c2c;' if hot else ''
    return f'<tr style="{bg}"><td style="padding: 6px 10px; color: #9a958d; font-weight: 600; width: 28px;">{n}</td><td style="padding: 6px 10px;">{st}</td><td style="padding: 6px 10px; color: #6b6660; width: 70px;">{who}</td><td style="padding: 6px 10px; text-align: right; width: 60px; {tw}">{t}</td><td style="padding: 6px 10px; color: #6b6660;">{block}</td></tr>'
SLIDES["DeckW3"] = shell("일을 보는 법", "① As-Is 프로세스 — 지금 일이 어떻게 흘러가는가", "C 제안자료 9단계 실물", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="{CARD} flex: 1.5 0 0; padding: 8px 6px;">
        <table style="border-collapse: collapse; width: 100%; font-size: 14px;">
          <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 10px;">#</td><td style="padding: 4px 10px;">단계 — 동사 하나</td><td style="padding: 4px 10px;">누가</td><td style="padding: 4px 10px; text-align: right;">시간</td><td style="padding: 4px 10px;">막히는 곳</td></tr>
          {arow(1, "고객 요구조건 메일을 읽는다", "나", "10분", "")}
          {arow(2, "조건을 표로 정리한다", "나", "20분", "메일마다 형식이 다름")}
          {arow(3, "외부 포털에서 시장가 · 경쟁 제품을 찾는다", "나", "90분", "여기가 절반", True)}
          {arow(4, "찾은 화면을 표로 옮긴다", "나", "40분", "옮겨 적기")}
          {arow(5, "가격가이드에서 맞는 모델을 추린다", "나", "40분", "라인업이 많음")}
          {arow(6, "스펙 · 가격을 비교한다", "나", "30분", "")}
          {arow(7, "제안 3안과 비교표를 만든다", "나", "40분", "")}
          {arow(8, "가격 · 납기를 확정한다", "나+팀장", "30분", "기다림")}
          {arow(9, "승인받아 고객에게 보낸다", "팀장", "—", "기다림")}
        </table>
      </div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 10px;">
        <div style="{LBL}">여기서 이미 보이는 것</div>
        <div style="{CARD} border-left: 3px solid #9a2c2c; padding: 12px 16px;"><div style="font-size: 16px; font-weight: 600;">시간이 몰린 단계</div><div style="font-size: 14px; color: #6b6660; line-height: 1.5;">전체의 절반을 먹는 단계가 대개 하나 있습니다. 여기가 후보 — 단, 3번은 밖에서 가져오는 일이라 에이전트가 못 됩니다. 그 다음 4번이 됩니다</div></div>
        <div style="{CARD} border-left: 3px solid #1c3f94; padding: 12px 16px;"><div style="font-size: 16px; font-weight: 600;">사람이 바뀌는 지점</div><div style="font-size: 14px; color: #6b6660; line-height: 1.5;">8 · 9번. 넘기고 기다리는 곳. 파일로 넘어가는지 말로 넘어가는지 봅니다</div></div>
        <div style="{CARD} border-left: 3px solid #0f6b4f; padding: 12px 16px;"><div style="font-size: 16px; font-weight: 600;">같은 일을 두 번 하는 곳</div><div style="font-size: 14px; color: #6b6660; line-height: 1.5;">4번 옮겨 적기. 형식 바꾸기는 거의 항상 AI 반복입니다</div></div>
        <div style="font-size: 14px; color: #6b6660; line-height: 1.5; padding: 4px 2px;">5~10단계면 적당합니다. 3단계면 뭉쳤고 20단계면 잘게 갔습니다. 이상적인 절차가 아니라 <strong style="font-weight: 600; color: #111821;">지금 실제로 하는 대로</strong> 적습니다.</div>
      </div>
    </div>""", "W · 03")

# ───────────── W4 ② 단계별 IPO ─────────────
def ipo_card(k, t, d, ex):
    return f"""<div style="{CARD} border-top: 3px solid #1c3f94; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px; flex: 1 0 0;">
  <div style="font-size: 30px; font-weight: 700; color: #1c3f94; line-height: 1;">{k}</div>
  <div style="font-size: 19px; font-weight: 600;">{t}</div>
  <div style="font-size: 14px; color: #6b6660; line-height: 1.55;">{d}</div>
  <div class="mono" style="font-size: 13px; color: #3d4650; background: #f2f1ec; padding: 8px 10px; line-height: 1.5;">{ex}</div>
</div>"""
def rule(n, t, d):
    return f'<div style="display: flex; gap: 12px; align-items: flex-start;"><span style="font-size: 19px; font-weight: 700; color: #1c3f94; width: 26px; flex-shrink: 0;">{n}</span><div><div style="font-size: 16px; font-weight: 600; line-height: 1.4;">{t}</div><div style="font-size: 14px; color: #6b6660; line-height: 1.5;">{d}</div></div></div>'
SLIDES["DeckW4"] = shell("일을 보는 법", "② 단계별 IPO — 받는 것 · 하는 일 · 내놓는 것", "각 단계를 세 칸으로 엽니다", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="display: flex; gap: 10px; flex: 1.3 0 0;">
        {ipo_card("I", "Input", "이 단계를 시작하려면 손에 무엇이 있어야 하나", "요구조건 메일<br>가격가이드 엑셀<br>화면에서 복사한 표")}
        {ipo_card("P", "Process", "그것으로 무엇을 하나", "조건 6항목을 뽑는다<br>4열로 정제한다")}
        {ipo_card("O", "Output", "끝나면 무엇이 남나 — 파일 이름으로", "customer_request.md<br>naver_crawl.csv")}
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 18px 22px; display: flex; flex-direction: column; gap: 14px;">
        <div style="{LBL}">규칙 세 가지</div>
        {rule(1, "Input은 꺼낼 수 있는 것", "&quot;내 경험&quot; · &quot;감&quot;이면 지금은 못 만듭니다. 문서로 적어 두거나, <strong style='font-weight: 600; color: #111821;'>에이전트가 질문해서 받거나</strong> — A 모듈 단계 2가 두 번째 방법")}
        {rule(2, "Output은 파일 이름으로", "&quot;고객 프로필 정리&quot;가 아니라 <span class='mono' style='font-size: 13px; color: #111821;'>customer_profile.md</span>. 다음 단계가 받을 수 있는 모양")}
        {rule(3, "앞 O ≠ 다음 I이면 사람이 메우고 있다", "거기가 에이전트 자리입니다. 다음 장")}
      </div>
    </div>""", "W · 04")

# ───────────── W5 틈이 에이전트 자리입니다 ─────────────
SLIDES["DeckW5"] = shell("일을 보는 법", "틈이 에이전트 자리입니다", "C 모듈 단계 ⓪이 나온 곳", f"""
    <div style="display: flex; gap: 12px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px; background: #f7f6f2;">
        <div style="{LBL}">3단계의 O</div>
        <div style="font-size: 19px; font-weight: 600;">화면에서 복사한 뒤죽박죽 텍스트</div>
        <div class="mono" style="font-size: 13px; color: #6b6660; line-height: 1.6;">삼성 비즈니스 TV 65인치 4K … 1,290,000원 무료배송 판매자 ○○ … 리뷰 312 … 다른 상품 …</div>
      </div>
      <div style="width: 150px; flex-shrink: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #9a2c2c; font-weight: 600;">틈</div>
        <div style="border: 2px dashed #9a2c2c; padding: 10px 12px; text-align: center; font-size: 14px; line-height: 1.45; color: #9a2c2c; font-weight: 600;">사람이 40분<br>옮겨 적는다</div>
        <div style="font-size: 22px; color: #9a958d;">↓</div>
        <div style="background: #1c3f94; color: #fbfaf7; padding: 8px 12px; font-size: 14px; font-weight: 600; text-align: center;">단계 ⓪<br>수집 정제</div>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 18px 20px; display: flex; flex-direction: column; gap: 8px; border-top: 3px solid #0f6b4f;">
        <div style="{LBL}">4단계의 I</div>
        <div style="font-size: 19px; font-weight: 600;">4열 표</div>
        <table class="mono" style="border-collapse: collapse; font-size: 13px; width: 100%;"><tr style="color: #6b6660;"><td style="padding: 3px 6px; border-bottom: 1px solid #e4e2db;">수요처명</td><td style="padding: 3px 6px; border-bottom: 1px solid #e4e2db;">모델명</td><td style="padding: 3px 6px; border-bottom: 1px solid #e4e2db;">온라인가격</td><td style="padding: 3px 6px; border-bottom: 1px solid #e4e2db;">제품spec.</td></tr><tr><td style="padding: 3px 6px;">네이버쇼핑</td><td style="padding: 3px 6px;">MX-65P</td><td style="padding: 3px 6px;">1,290,000</td><td style="padding: 3px 6px;">65" 4K 500nit</td></tr></table>
        <div style="font-size: 14px; color: #6b6660;">헤더를 먼저 정합니다. 화면부터 긁으면 화면마다 다른 모양이 쌓입니다.</div>
      </div>
    </div>
    <div style="display: flex; gap: 14px;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 20px; font-size: 16px; line-height: 1.5;"><strong style="font-weight: 600;">틈을 찾았으면 둘 중 하나</strong> — 틈을 메우는 에이전트를 만들거나, <strong style="font-weight: 600;">앞 단계의 O 형식을 바꿔</strong> 틈을 없앱니다.</div>
      <div style="{BAND} flex: 1 0 0; padding: 12px 20px;"><div style="font-size: 19px; font-weight: 700;">틈은 우리가 정한 게 아니라 일이 그렇게 생겼습니다.</div></div>
    </div>""", "W · 05")

# ───────────── W9 표가 지시문이 됩니다 ─────────────
def mrow(a, b, c):
    return f'<tr><td style="padding: 8px 12px; font-size: 16px;">{a}</td><td style="padding: 8px 12px; color: #9a958d;">→</td><td style="padding: 8px 12px; font-size: 16px; font-weight: 600;">{b}</td><td style="padding: 8px 12px; color: #9a958d;">→</td><td style="padding: 8px 12px; font-size: 14px; color: #3d4650;">{c}</td></tr>'
SLIDES["DeckW9"] = shell("일을 보는 법", "⑥ 분해표가 지시문이 됩니다", "옮겨 적는 일만 남았습니다", f"""
    <div style="{CARD} padding: 10px 8px;">
      <table style="border-collapse: collapse; width: 100%;">
        <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 12px;">분해표에서</td><td></td><td style="padding: 4px 12px;">지시문 7블록</td><td></td><td style="padding: 4px 12px;">SKILL.md 본문</td></tr>
        {mrow("묶음이 하는 일을 한 문장으로", "① 역할", "1. 역할 및 목표")}
        {mrow("묶음에 들어간 단계 / 안 들어간 단계", "② 업무 범위 — 하는 일 / 하지 않는 일", "1. 역할 및 목표")}
        {mrow("묶음 첫 단계의 <strong style='font-weight: 600;'>I</strong>", "③ 입력 검사", "5. 작업 단계")}
        {mrow("묶음 안 단계들의 <strong style='font-weight: 600;'>P</strong>, 순서 그대로", "④ 처리 순서", "5. 작업 단계 + 입출력 예시")}
        {mrow("묶음 마지막 단계의 <strong style='font-weight: 600;'>O</strong>", "⑤ 출력 형식", "2. 출력 형식")}
        {mrow("묶음 <strong style='font-weight: 600;'>바로 뒤</strong>의 사람만 단계", "⑥ 중단 · 보안 &nbsp;·&nbsp; ⑦ 사람 승인", "3. 금지 사항 · 4. 검토 기준")}
      </table>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">"하지 않는 일"은 지어내는 것이 아닙니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 520px; line-height: 1.5;">이 묶음에 안 들어간 단계가 그대로 들어갑니다. C의 "확정 견적서는 만들지 않는다"는 8번 단계가 사람만이기 때문입니다.</div>
    </div>""", "W · 09")

# ───────────── M1 왜 팀마다 따로 만들지 않는가 ─────────────
SLIDES["DeckM1"] = shell("공통 방법론", "왜 에이전트를 팀마다 따로 만들지 않는가", "여기서 A와 B가 갈립니다", vs(
    "팀마다 하나씩 — 6개", "B2B팀과 유통전략팀은 고객도 품목도 다르니 따로 만든다. 그러면 사내강사가 차수마다 6개를 새로 만들고, 고칠 때 6곳을 고칩니다.",
    "골격 하나 + 팀별 데이터 팩", "지시문 골격 · 처리 순서 · 검수 · 중단 규칙은 공통. 고객 · 제품 · 파트너 · 결과물 서식은 <strong style='font-weight: 600; color: #111821;'>파일</strong>로 넣습니다. 팀이 바뀌면 파일만 바꿉니다. 오늘 A와 B는 그렇게 갈립니다.") + f"""
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">에이전트는 "아는 것"이 아니라 "받은 파일"로 일합니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">그래서 지시문에 고객사 이름을 적지 않고, 고객사 파일을 올립니다.</div>
    </div>""", "M · 01")

# ───────────── M2 컨텍스트를 데이터로 ─────────────
def two(a, b, last=False):
    bd = "" if last else "border-bottom: 1px solid #eeece6;"
    return f'<tr><td style="padding: 12px 16px; font-size: 16px; {bd} width: 50%;">{a}</td><td style="padding: 12px 16px; font-size: 16px; {bd} background: #f7f6f2;">{b}</td></tr>'
SLIDES["DeckM2"] = shell("공통 방법론", "컨텍스트를 데이터로", "지시문에는 반복되는 것만", f"""
    <div style="{CARD} padding: 0; flex-grow: 1;">
      <table style="border-collapse: collapse; width: 100%; height: 100%;">
        <tr><td style="padding: 12px 16px; font-size: 12px; letter-spacing: 0.16em; color: #0f6b4f; font-weight: 600; border-bottom: 2px solid #111821;">바뀌지 않는 것 — 지시문 · 스킬에 고정</td><td style="padding: 12px 16px; font-size: 12px; letter-spacing: 0.16em; color: #9a6408; font-weight: 600; border-bottom: 2px solid #111821; background: #f7f6f2;">바뀌는 것 — 팀별 데이터 팩, 파일로</td></tr>
        {two("지시문 골격 · 처리 순서 · 출력 형식", "업무 상황 (비즈니스 컨텍스트)")}
        {two("검수 기준 · 중단(STOP) 규칙", "입력 더미데이터와 컬럼 헤더")}
        {two("테스트 3종 구성 방식", "고객 · 제품 · 파트너 정보")}
        {two("사람 승인 지점", "최종 결과물 서식", True)}
      </table>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">반복되는 건 지침에, 매번 바뀌는 건 파일로.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 500px; line-height: 1.5;">금지 사항과 검토 기준을 지침에 고정하면 보안 · 검수 원칙이 매 대화에 자동으로 붙습니다.</div>
    </div>""", "M · 02")

# ───────────── M3 일반 대화와 업무 에이전트의 차이 ─────────────
def cmp(k, a, b, last=False):
    bd = "" if last else "border-bottom: 1px solid #eeece6;"
    return f'<tr><td style="padding: 10px 14px; font-size: 14px; color: #6b6660; {bd} width: 110px;">{k}</td><td style="padding: 10px 14px; font-size: 16px; {bd} background: #f7f6f2;">{a}</td><td style="padding: 10px 14px; font-size: 16px; {bd}">{b}</td></tr>'
SLIDES["DeckM3"] = shell("공통 방법론", "일반 대화와 업무 에이전트의 차이", "오늘 만드는 것은 오른쪽입니다", f"""
    <div style="{CARD} padding: 0; flex-grow: 1;">
      <table style="border-collapse: collapse; width: 100%; height: 100%;">
        <tr><td style="border-bottom: 2px solid #111821;"></td><td style="padding: 12px 14px; font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600; border-bottom: 2px solid #111821; background: #f7f6f2;">일반 대화</td><td style="padding: 12px 14px; font-size: 12px; letter-spacing: 0.16em; color: #1c3f94; font-weight: 600; border-bottom: 2px solid #111821;">업무 에이전트</td></tr>
        {cmp("입력", "그때그때 질문", "정해진 파일 + 고정된 지시문")}
        {cmp("출력", "답변 한 덩어리", "정해진 서식 · 수치마다 근거 행 · 확인 필요 목록")}
        {cmp("빠진 것이 있으면", "그럴듯하게 채운다", "멈추고 묻는다 — 경계 테스트")}
        {cmp("위험한 요구가 오면", "해 준다", "만들지 않고 이유를 말한다 — 실패 테스트")}
        {cmp("반복하면", "매번 다르다", "매번 같다 — 그래서 검수할 수 있다")}
        {cmp("책임", "없음", "사람 승인 지점이 지시문에 적혀 있다", True)}
      </table>
    </div>""", "M · 03")

# ───────────── M5 시작은 RACS, 익숙해지면 7블록 ─────────────
SLIDES["DeckM5"] = shell("공통 방법론", "시작은 RACS, 익숙해지면 7블록", "RACS는 7블록의 압축판이지 다른 방법이 아닙니다", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="{CARD} flex: 1.2 0 0; padding: 18px 22px; display: flex; flex-direction: column; gap: 10px;">
        <div style="{LBL}">처음 쓰는 분은 네 줄로</div>
        <div class="mono" style="font-size: 13px; line-height: 1.85; background: #f2f1ec; padding: 14px 16px; flex-grow: 1;"><span style="color: #1c3f94; font-weight: 500;">#Role</span>&nbsp;&nbsp;&nbsp;&nbsp; 너는 B2B팀의 데이터 분석 담당자다<br><span style="color: #1c3f94; font-weight: 500;">#Action</span>&nbsp;&nbsp; 판매 실적 파일에서 유사 버티컬의 판매 패턴을 뽑아 추천 제품 3개를 골라라<br><span style="color: #1c3f94; font-weight: 500;">#Context</span>&nbsp; 신규 수요처에 제안하기 전에 제품 후보를 좁히는 용도다<br><span style="color: #1c3f94; font-weight: 500;">#Style</span>&nbsp;&nbsp;&nbsp; 표로, 각 추천에 근거 행을 붙여라. 자료에 없는 값은 만들지 마라</div>
        <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">이걸로 한 번 돌려보고 결과가 나오면 오른쪽 7블록으로 <strong style="font-weight: 600; color: #111821;">늘립니다.</strong></div>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 0;">
        <table style="border-collapse: collapse; width: 100%; height: 100%;">
          <tr><td style="padding: 10px 16px; font-size: 12px; letter-spacing: 0.16em; color: #9a958d; font-weight: 600; border-bottom: 2px solid #111821;">RACS</td><td style="padding: 10px 16px; font-size: 12px; letter-spacing: 0.16em; color: #9a958d; font-weight: 600; border-bottom: 2px solid #111821;">7블록</td></tr>
          {two("Role", "① 역할")}
          {two("Action", "② 업무 범위 &nbsp;·&nbsp; ④ 처리 순서")}
          {two("Context", "③ 입력 검사")}
          {two("Style", "⑤ 출력 형식 &nbsp;·&nbsp; ⑥ 중단 · 보안 &nbsp;·&nbsp; ⑦ 성공 기준", True)}
        </table>
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">좋은 데이터 × 정확한 지시 — 두 축이 다 있어야 반복해서 씁니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 420px; line-height: 1.5;">지시만 좋고 파일이 없으면 지어내고, 파일만 있고 지시가 모호하면 매번 다르게 나옵니다.</div>
    </div>""", "M · 05")

# ───────────── M6 IPO 명세 6칸 ─────────────
def spec(k, t, d, accent="#1c3f94"):
    return f"""<div style="{CARD} border-top: 3px solid {accent}; padding: 16px 18px; display: flex; flex-direction: column; gap: 6px;">
  <div class="mono" style="font-size: 13px; color: {accent}; font-weight: 500; letter-spacing: 0.08em;">{k}</div>
  <div style="font-size: 19px; font-weight: 600;">{t}</div>
  <div style="font-size: 14px; color: #6b6660; line-height: 1.55;">{d}</div>
</div>"""
SLIDES["DeckM6"] = shell("공통 방법론", "IPO 명세 — 지시문보다 먼저 씁니다", "이 한 장이 지시문 · 테스트 · 검수 기준의 원본", f"""
    <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; flex-grow: 1;">
      {spec("INPUT", "받는 것", "허용 파일명 · 필수 컬럼 · 기간 · 권한")}
      {spec("PROCESS", "하는 일 — 순서로", "검사 → 계산 · 분류 → 비교 → 초안 → 근거 연결")}
      {spec("OUTPUT", "내놓는 것", "결과물 서식 · 근거표 · 확인 필요 목록")}
      {spec("STOP", "멈추는 조건", "무엇이 나오면 멈추고 물어보는가", "#9a2c2c")}
      {spec("APPROVAL", "사람 승인", "누가 무엇을 확인한 뒤 발송 · 제출하는가", "#9a2c2c")}
      {spec("TEST", "세 가지 입력", "정상 · 경계 · 실패에서 각각 어떻게 행동해야 하는가", "#0f6b4f")}
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">IPO가 모호하면 에이전트가 아니라 업무 정의부터 다시 봅니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">맨 위에 한 줄 — 목적 · 독자 · 기준일.</div>
    </div>""", "M · 06")

# ───────────── M8 나쁜 문장 vs 좋은 문장 ─────────────
def pair(bad, good, why):
    return f"""<div style="display: flex; gap: 10px; align-items: stretch;">
  <div style="{CARD} flex: 1 0 0; padding: 14px 18px; background: #f7f6f2; display: flex; align-items: center; gap: 12px;"><span style="font-size: 19px; font-weight: 700; color: #9a2c2c;">✕</span><span style="font-size: 16px; line-height: 1.5;">{bad}</span></div>
  <div style="{CARD} flex: 1.5 0 0; padding: 14px 18px; border-left: 3px solid #0f6b4f; display: flex; align-items: center; gap: 12px;"><span style="font-size: 19px; font-weight: 700; color: #0f6b4f;">○</span><span style="font-size: 16px; line-height: 1.5;">{good}</span></div>
  <div style="width: 230px; flex-shrink: 0; display: flex; align-items: center; font-size: 14px; color: #6b6660; line-height: 1.5; padding: 0 6px;">{why}</div>
</div>"""
SLIDES["DeckM8"] = shell("공통 방법론", "나쁜 문장 vs 좋은 문장", "검증할 수 있게 씁니다", f"""
    <div style="display: flex; flex-direction: column; gap: 10px; flex-grow: 1; justify-content: center;">
      {pair("정확하게 작성해줘", "합계가 소계의 합과 다르면 표를 내지 말고 멈춘다. 근거 행이 없는 수치는 0건이어야 한다", "몇 건 · 몇 % · 어떤 상태면 통과인지가 없으면 검수를 못 합니다")}
      {pair("모르는 건 알아서 채워", "자료에 없으면 &quot;확인 필요&quot;라고 적고 질문한다. 추정해 채우지 않는다", "없는 값을 그럴듯하게 채우는 것이 51:49입니다")}
      {pair("보고서를 잘 만들어 줍니다", "신규 수요처의 버티컬을 받아 과거 실적에서 유사 버티컬 패턴을 분석하고 추천 TOP 3와 근거를 만든다", "무엇을 · 언제 쓰는지가 있어야 AI가 이 스킬을 고릅니다")}
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">"친절하게" 같은 성격 문장은 최소화합니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">이 덱의 문장이 전부 지시 · 절차 · 기준인 이유입니다.</div>
    </div>""", "M · 08")

# ───────────── M10 사람이 하는 일 ─────────────
SLIDES["DeckM10"] = shell("공통 방법론", "사람이 하는 일", "에이전트는 승인 상태를 기록할 수 있지만 승인자가 될 수 없습니다", f"""
    <div style="{CARD} padding: 0; flex-grow: 1;">
      <table style="border-collapse: collapse; width: 100%; height: 100%;">
        <tr><td style="padding: 12px 16px; font-size: 12px; letter-spacing: 0.16em; color: #1c3f94; font-weight: 600; border-bottom: 2px solid #111821;">AI가 하는 것 — 초안까지</td><td style="padding: 12px 16px; font-size: 12px; letter-spacing: 0.16em; color: #9a2c2c; font-weight: 600; border-bottom: 2px solid #111821; background: #f7f6f2;">사람이 하는 것 — 확정</td></tr>
        {two("자료 수집 · 요약 · 분류", "사실 확정, 참여 여부 결정")}
        {two("계산 · 비교 · 추이 정리", "가격 · 납기 · 할인 결정")}
        {two("초안 작성, 근거 위치 표시", "대외 발송, 서명, 제출")}
        {two("누락 질문, 확인 필요 표시", "최종 책임", True)}
      </table>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">오른쪽 칸이 지시문 ⑦에 이름과 함께 들어갑니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">"누가 무엇을 확인한 뒤 고객에게 보내나요?" — 승인자가 없는 지시문은 되묻습니다.</div>
    </div>""", "M · 10")

# ───────────── M11 오늘의 완주 기준 ─────────────
SLIDES["DeckM11"] = shell("공통 방법론", "오늘의 완주 기준", "완성도보다 체인이 끊기지 않는 것", f"""
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #0f6b4f; padding: 24px 28px; display: flex; flex-direction: column; gap: 14px;">
        <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #0f6b4f;">최소 완주</span><span style="font-size: 14px; color: #6b6660;">이 선을 넘기면 다음 모듈로 갑니다</span></div>
        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 16px; line-height: 1.5;">
          <div>□ 에이전트 하나가 만들어져 있다</div>
          <div>□ 정상 테스트 1건이 기준본과 같다</div>
          <div>□ 결과물이 파일로 저장돼 있다 — <span class="mono" style="font-size: 13px;">recommend_D.html</span></div>
        </div>
      </div>
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #1c3f94; padding: 24px 28px; display: flex; flex-direction: column; gap: 14px;">
        <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #1c3f94;">확장</span><span style="font-size: 14px; color: #6b6660;">시간이 남는 분</span></div>
        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 16px; line-height: 1.5;">
          <div>□ 경계 · 실패 테스트까지 셋 다 통과</div>
          <div>□ 테스트에서 고친 문장을 지시문에 반영한 v1</div>
          <div>□ 내 업무 전환 표를 채웠다</div>
        </div>
      </div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">뒤처져도 다음 실습은 반드시 시작합니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd;">앞 모듈을 못 끝냈으면 배포 폴더 04_answer/의 기준본으로 시작합니다.</div>
    </div>""", "M · 11")


# ═══════════════════════ 블록 3 — 모듈 A · B · C ═══════════════════════
def cover(label, title, desc, sub, segs, foot, page):
    return HEAD + f"""<div style="width: 1280px; height: 720px; background: #0e2560; color: #fbfaf7; display: flex; flex-direction: column; justify-content: space-between; padding: 48px 64px 40px; box-sizing: border-box;">
  <div style="display: flex; align-items: center; gap: 16px;">
    <div style="font-size: 12px; letter-spacing: 0.22em; color: #8fa4d8; font-weight: 500;">{label}</div>
    <div style="flex-grow: 1; height: 1px; background: #2c4a8f;"></div>
    <div style="font-size: 12px; color: #8fa4d8;">2.0h · 에이전트 1개 · 단계 3개</div>
  </div>
  <div style="display: flex; flex-direction: column; gap: 22px;">
    <h1 style="margin: 0; font-size: 60px; line-height: 1.15; font-weight: 700; letter-spacing: -0.02em;">{title}</h1>
    <p style="margin: 0; font-size: 22px; line-height: 1.6; color: #c3cde8; max-width: 800px;">{desc}</p>
    <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #8fa4d8; max-width: 800px;">{sub}</p>
  </div>
  <div style="display: flex; flex-direction: column; gap: 14px;">
    <div style="display: flex; gap: 3px; align-items: stretch; height: 34px;">{bar(segs)}</div>
    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8fa4d8;"><span>{foot}</span><span>{page}</span></div>
  </div>
</div>
""" + TAIL
STD = [(20, "방법론 + 분해표", "talk"), (15, "시연", "talk"), (30, "실습 1", "hands"), (25, "실습 2", "hands"), (15, "실습 3", "hands"), (10, "전환", "talk"), (5, "버퍼", "buf")]
STD_C = [(20, "방법론 + 분해표", "talk"), (15, "시연", "talk"), (30, "실습 1", "hands"), (40, "실습 2·3", "hands"), (15, "Skill + 클로징", "talk")]

SLIDES["DeckA1"] = cover("모듈 A · B2B팀", "직판 Sensing Agent", "상장 건설사 1곳을 깊게 봅니다. 매주 쌓이는 기사에서 <strong style='color: #fbfaf7; font-weight: 600;'>언제 접근해야 하는지</strong>를 꺼냅니다.", "수집 → 프로파일 → 기회 분석. 에이전트는 하나, 단계가 셋입니다.", STD, "실습 70분 · A · B · C 공통 배분", "S · 01")
SLIDES["DeckB1"] = cover("모듈 B · B2B유통전략팀", "경로 Sensing Agent", "권역의 작은 시설 여럿을 넓게 봅니다. 한 건씩은 작아서 의미가 없고, <strong style='color: #fbfaf7; font-weight: 600;'>모아 놓고 봐야</strong> 흐름이 보입니다.", "키워드 → 추출 · 매칭 → 보고서. 수주는 파트너가 하므로 파트너와 무엇을 논의할지까지 정리해야 끝납니다.", STD, "실습 70분 · A · B · C 공통 배분", "S · 01")
SLIDES["DeckC1"] = cover("모듈 C · 전원 공통", "제안자료 작성 Agent", "고객은 모델명이 아니라 요구조건을 보냅니다. 조건에 맞는 <strong style='color: #fbfaf7; font-weight: 600;'>3안</strong>을 만들고 시장가와 비교합니다.", "⓪ 수집 정제 → ① 스펙 추출 → ② 3안 제안. 마지막 모듈이라 Skill과 클로징이 이 안에 있습니다.", STD_C, "실습 70분 · 전환 · 버퍼 자리에 Skill 6장 + 클로징 3장", "C · 01")

# ───────────── 분해표 (A · B · C) ─────────────
def decomp(label, title, now, rows, note1, note2, page, legend_lock="사람만 — 에이전트 밖", cols=("내가 하는 일", "꼬리표", "어디로")):
    trs = "".join(drow(n, job, kind, where, band, sh) for n, job, kind, where, band, sh in rows)
    return shell(label, title, "분해표 그대로", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="width: 330px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px;">
        <div style="{CARD} padding: 16px 20px; display: flex; flex-direction: column; gap: 8px;"><div style="{LBL}">지금</div><div style="font-size: 16px; line-height: 1.6; color: #3d4650;">{now}</div></div>
        <div style="{CARD} border-left: 3px solid #1c3f94; padding: 14px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;">{note1}</div>
        <div style="{CARD} border-left: 3px solid #9a6408; padding: 14px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;">{note2}</div>
      </div>
      <div style="{CARD} flex-grow: 1; padding: 8px 6px;">
        <table style="border-collapse: collapse; width: 100%; font-size: 14px;">
          <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 10px;">#</td><td style="padding: 4px 10px;">{cols[0]}</td><td style="padding: 4px 10px;">{cols[1]}</td><td style="padding: 4px 10px;">{cols[2]}</td></tr>
          {trs}
        </table>
        <div style="display: flex; gap: 18px; padding: 8px 10px 2px; font-size: 12px; color: #6b6660;"><span><span style="display: inline-block; width: 12px; height: 12px; background: #eef0ea; vertical-align: -1px; border: 1px solid #d9d7d0;"></span> 에이전트 1개로 묶이는 구간</span><span><span style="display: inline-block; width: 12px; height: 12px; background: #fbeeee; vertical-align: -1px; border: 1px solid #d9d7d0;"></span> {legend_lock}</span></div>
      </div>
    </div>""", page)

SLIDES["DeckA2"] = decomp("모듈 A", "지금은 이렇게 일합니다 — 그리고 이렇게 쪼갰습니다",
    "담당 산업의 기사와 공시를 훑고, 새로 뜬 회사가 어떤 회사인지 알아보고, 그 변화가 우리 수요로 이어지는지 판단합니다. 기사는 매주 쌓이고 대부분은 무관합니다. <strong style='font-weight: 600; color: #111821;'>언제 접근해야 하는지</strong>가 가장 어렵습니다.",
    [(0,"어떤 회사를 볼지 고른다 (상장 · 공종 · 지역)","draft","단계 1 앞","agent",False),(1,"매주 담당 건설사 · 산업 뉴스를 검색한다","repeat","단계 1","agent",False),(2,"품목 · 헤드라인 · url · 키워드로 정리한다","repeat","단계 1","agent",False),(3,"새로 뜬 회사가 어떤 회사인지 조사한다","draft","단계 2","agent",False),(4,"모르는 것은 선배 · 담당자에게 물어 채운다","draft","단계 2 — 질문이 기능","agent",False),(5,"기사에서 무슨 변화가 있었는지 뽑는다","draft","단계 3 Key Signal","agent",False),(6,"그 변화가 어떤 구매 수요인지 해석한다","draft","단계 3 Needs","agent",False),(7,"언제 발주가 뜰지 역산한다","draft","단계 3 Opportunity","agent",False),(8,"갈래를 나눠 본다","draft","단계 3 시나리오","agent",False),(9,"누구에게 무엇을 들고 갈지 정한다","draft","단계 3 Action","agent",False),(10,"연락하고 미팅을 잡는다","lock","경계","lock",False),(11,"견적 · 가격을 제시한다","lock","경계","lock",False)],
    "<strong style='font-weight: 600; color: #111821;'>0~9번 사이에 사람만이 없습니다.</strong> 그래서 에이전트는 하나이고 단계가 셋입니다. 10 · 11번이 사람만이라 거기서 잘립니다.",
    "단계 1(1 · 2번)은 매주 같은 일이라 <strong style='font-weight: 600; color: #111821;'>주기가 돌립니다.</strong> 사람은 결과를 봅니다.", "S · 02")
SLIDES["DeckB2"] = decomp("모듈 B", "지금은 이렇게 일합니다 — 그리고 이렇게 쪼갰습니다",
    "담당 권역의 파트너를 관리하면서 시장을 점검합니다. 개점 · 이전 · 신축 · 리뉴얼이 늘고 있다는 이야기를 듣고 기사와 상권정보를 각각 찾아봅니다. 수주는 파트너가 하므로 <strong style='font-weight: 600; color: #111821;'>파트너와 무엇을 논의할지</strong>까지 정리해야 끝납니다.",
    [(1,"담당 권역을 정한다","draft","입력","agent",False),(2,"검색 키워드를 조합한다","repeat","단계 1","agent",False),(3,"네이버 뉴스에서 검색한다","outside","입력 파일",None,False),(4,"응답에서 시설 · 상태 · 시기 · 규모를 뽑는다","repeat","단계 2","agent",False),(5,"상권정보 · 시장조사와 대조한다","repeat","단계 2","agent",False),(6,"규모로 거르고 우선순위를 매긴다","draft","단계 2","agent",False),(7,"어느 파트너가 맡을지 매칭한다","draft","단계 3","agent",False),(8,"파트너와 논의할 것을 정리한다","draft","단계 3","agent",False),(9,"Word 보고서로 만든다","repeat","단계 3","agent",False),(10,"파트너에게 연락하고 공유한다","lock","경계","lock",False),(11,"가격 · 마진을 협의한다","lock","경계","lock",False)],
    "<strong style='font-weight: 600; color: #111821;'>1~9번 사이에 사람만이 없습니다.</strong> 그래서 에이전트는 하나이고 단계가 셋입니다. 3번은 밖에서 가져오는 입력이라 에이전트 앞에 놓입니다.",
    "삼성 양식이 요구한 <strong style='font-weight: 600; color: #111821;'>「제공 프롬프트 3종」이 곧 이 셋</strong>입니다.", "S · 02")
SLIDES["DeckC2"] = decomp("모듈 C", "지금은 이렇게 일합니다 — 그리고 이렇게 쪼갰습니다",
    "가격가이드를 열어 조건에 맞는 모델을 찾고, 외부 포털에서 시장가와 경쟁 제품을 찾아 비교합니다. 라인업이 많고 가격을 일일이 검색해야 해서 <strong style='font-weight: 600; color: #111821;'>한 건에 반나절</strong>이 갑니다.",
    [(1,"요구조건 메일을 읽는다 · 10분","draft","단계 ①","agent",False),(2,"조건을 표로 정리한다 · 20분","draft","단계 ①","agent",False),(3,"외부 포털에서 시장가 · 경쟁 제품을 찾는다 · <strong style='font-weight: 700; color: #9a2c2c;'>90분</strong>","outside","입력",None,False),(4,"찾은 화면을 표로 옮긴다 · 40분","repeat","단계 ⓪","agent",False),(5,"가격가이드에서 맞는 모델을 추린다 · 40분","repeat","단계 ①","agent",False),(6,"스펙 · 가격을 비교한다 · 30분","draft","단계 ②","agent",False),(7,"3안과 비교표를 만든다 · 40분","draft","단계 ②","agent",False),(8,"가격 · 납기를 확정한다 · 30분","lock","경계","lock",False),(9,"승인받아 고객에게 보낸다","lock","경계","lock",False)],
    "<strong style='font-weight: 600; color: #111821;'>1~7번 사이에 사람만이 없습니다.</strong> 에이전트는 하나, 단계가 셋. 8 · 9번이 사람만이라 거기서 잘립니다.",
    "가장 오래 걸리는 3번(90분)은 <strong style='font-weight: 600; color: #111821;'>밖에서 가져오는 일이라 에이전트가 못 됩니다.</strong> 대신 그 다음 4번이 단계 ⓪이 됐습니다.", "C · 02")

# ───────────── 에이전트는 하나, 단계는 셋 (A · B) ─────────────
def three(label, title, steps, caption, page, foot):
    boxes = "".join(f"""<div style="flex: 1 0 0; background: #eef0ea; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px;">
      <div style="font-size: 12px; color: #9a958d; font-weight: 600;">단계 {i+1}</div>
      <div style="font-size: 19px; font-weight: 600;">{t}</div>
      <div style="font-size: 14px; color: #3d4650; line-height: 1.5;">{d}</div>
      <div class="mono" style="font-size: 13px; color: #1c3f94;">{f}</div>
      <div style="font-size: 12px; color: #6b6660;">{w}</div>
    </div>""" for i, (t, d, f, w) in enumerate(steps))
    return shell(label, title, caption, f"""
    <div style="border: 2px solid #1c3f94; background: #ffffff; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; flex-grow: 1;">
      <div style="display: flex; justify-content: space-between; align-items: baseline;"><span style="font-size: 19px; font-weight: 700; color: #1c3f94;">에이전트 1개</span><span style="font-size: 14px; color: #6b6660;">참조 파일도 한 곳, 고칠 곳도 한 곳</span></div>
      <div style="display: flex; gap: 10px; align-items: stretch; flex-grow: 1;">{boxes}</div>
    </div>
    <div style="{BAND}">
      <div style="font-size: 22px; font-weight: 700;">사이에 사람만 단계가 없어 나누지 않습니다.</div>
      <div style="flex-grow: 1;"></div>
      <div style="font-size: 14px; color: #c9c5bd; max-width: 520px; line-height: 1.5;">{foot}</div>
    </div>""", page)
SLIDES["DeckA3"] = three("모듈 A", "에이전트는 하나, 단계는 셋", [
    ("수집", "매주 담당 건설사 · 산업 뉴스를 4열로 정리 — 품목 · 헤드라인 · 원본url · 키워드", "prompt_1_수집.md", "주기 실행 — 강사 시연. 참가자는 결과 파일을 받습니다"),
    ("프로파일", "새로 뜬 회사를 묻고 답하며 채웁니다. 모르면 비워 둡니다", "prompt_2_프로파일.md", "대화 메시지로"),
    ("기회 분석", "Key Signal → Needs → 접근 시점 → 시나리오 → Action을 HTML 대시보드로", "prompt_3_분석.md ✂ 사이", "에이전트 지침에")],
    "수집 → 프로파일 → 분석", "S · 03", "셋은 서로 다른 일이지만 어느 사이에도 사람이 확정해야 할 지점이 없습니다. 나누면 참조 파일을 세 곳에 올리고 결과를 사람이 옮겨 나릅니다.")
SLIDES["DeckB3"] = three("모듈 B", "에이전트는 하나, 단계는 셋", [
    ("검색 키워드", "권역 × 시설유형 × 상태를 곱해 검색어를 만들고, 뺀 조합의 이유를 적습니다", "prompt_1_키워드.md", "대화 메시지로"),
    ("추출 · 매칭", "뉴스에서 시설 · 상태 · 시기 · 규모를 뽑아 상권정보와 대조, 규모로 가르고 파트너를 매칭", "prompt_2_추출.md ✂ 사이", "에이전트 지침에"),
    ("보고서", "5절 보고서로 출력 → Word에 붙여넣기", "prompt_3_보고서.md ✂ 사이", "같은 대화의 다음 메시지")],
    "키워드 → 추출 → 보고서", "S · 03", "삼성 양식의 「제공 프롬프트 3종」이 이 셋입니다. 셋을 에이전트 셋으로 그리면 안 됩니다 — 단계 박스는 에이전트 테두리 안에 있습니다.")

# ───────────── 입력 데이터 (A · B · C) ─────────────
def inputs(label, files, extra, page, folder):
    trs = "".join(frow(f, h, n, src) for f, h, n, src in files)
    return shell(label, "입력 데이터", f"배포 폴더 {folder}", f"""
    <div style="{CARD} padding: 8px 6px;">
      <table style="border-collapse: collapse; width: 100%;">
        <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 4px 10px;">파일</td><td style="padding: 4px 10px;">헤더</td><td style="padding: 4px 10px; text-align: right;">행</td><td style="padding: 4px 10px;">어디서 온 것으로 가정</td></tr>
        {trs}
      </table>
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 20px; font-size: 16px; line-height: 1.6; color: #3d4650;">{extra}</div>
      <div style="{WARN} width: 400px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; gap: 4px;">
        <div style="font-size: 19px; font-weight: 600; color: #9a2c2c;">모든 데이터는 가상입니다.</div>
        <div style="font-size: 14px; color: #3d4650; line-height: 1.5;">회사명 · 시설명 · 파트너 · 실적 · 가격 전부. 실제 고객사 · 파트너 파일은 올리지 않습니다.</div>
      </div>
    </div>""", page)
SLIDES["DeckA4"] = inputs("모듈 A", [("rss_feed.csv", "품목 · 헤드라인 · 원본url · 키워드 (4열)", 30, "단계 1의 산출물 — 강사 시연으로 만든 것"), ("target_builders.csv", "수요처명 · 상장시장 · 주력공종 · 거래이력 · 담당팀", 6, "담당 수요처 목록"), ("rss_sources.md", "검색어 · RSS주소 · 수집주기", 8, "단계 1 실습의 정답 — 참조 파일")],
    "30건 중 <strong style='font-weight: 600; color: #111821;'>같은 헤드라인이 다른 매체로 세 번</strong> 더 실려 있고, <strong style='font-weight: 600; color: #111821;'>18건은 업계 일반 동향</strong>입니다. 수집 요약에 30 → 27이 나오는지, 무관 기사가 따로 세어지는지가 첫 확인입니다. 업로드가 막히면 06_paste/의 표를 붙여넣습니다.", "S · 04", "modules/A_sensing_b2b/01_data/")
SLIDES["DeckB4"] = inputs("모듈 B", [("naver_news_dummy.json", "title · originallink · link · description · pubDate", 30, "네이버 뉴스 API 응답 — 연동 가정"), ("district_info.csv", "권역 · 행정구역 · 시설유형 · 시설명 · 상태 · 예정시기 · 규모", 18, "상권정보"), ("partner_info.csv", "파트너사 · 담당권역 · 주력버티컬 · 최근분기실적등급 · 시공가능규모", 4, "파트너 관리 대장"), ("market_research.md", "권역 · 지표 · 값 · 출처 · 조사시점", 8, "시장조사 자료")],
    "넷을 <strong style='font-weight: 600; color: #111821;'>다 올려야</strong> 합니다. 뉴스만 올리면 규모를 못 걸러 카페가 기회 목록에 오르고, 파트너 파일이 없으면 매칭이 안 됩니다. 파트너 파일에 <strong style='font-weight: 600; color: #111821;'>계약단가 · 마진율</strong>이 있으면 올리지 않습니다 — 실패 테스트가 그것입니다.", "S · 04", "modules/B_sensing_partner/01_data/")
SLIDES["DeckC4"] = inputs("모듈 C", [("tv_price_guide.csv", "모델명 · 제품군 · 화면크기 · 해상도 · 밝기 · 주요기능 · 설치방식 · 가이드공급가 · 최소수량", 13, "사내 B2B 마케팅 / 가격가이드"), ("naver_crawl.csv", "수요처명 · 모델명 · 온라인가격 · 제품spec.", 10, "단계 ⓪의 산출물 — 강사 시연으로 만든 것"), ("customer_request.md", "요구조건 6항목 — 화면크기 · 사용목적 · 주요기능 · 설치환경 · 수량 · 예산", 1, "고객 메일")],
    "요구조건은 <strong style='font-weight: 600; color: #111821;'>늘 반쯤 빠진 채로</strong> 옵니다. 경계 테스트 파일은 예산 줄이 지워져 있습니다. 크롤 표의 스펙은 <strong style='font-weight: 600; color: #111821;'>판매자가 쓴 글</strong>이라 경쟁사 평가 근거로 쓸 때 출처를 밝힙니다.", "C · 04", "modules/C_proposal/01_data/")

# ───────────── A5 신호를 읽는 법 ─────────────
def tl(rank, who, done, approach, gap, hot=False):
    c = "#0f6b4f" if hot else "#1c3f94"
    return f"""<div style="{CARD} display: flex; align-items: stretch;">
  <div style="width: 56px; background: {c}; color: #fbfaf7; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; flex-shrink: 0;">{rank}</div>
  <div style="padding: 12px 18px; display: flex; align-items: center; gap: 22px; flex-grow: 1;">
    <div style="width: 240px; font-size: 16px; font-weight: 600;">{who}</div>
    <div style="font-size: 14px; color: #6b6660;">준공 <strong style="font-weight: 600; color: #111821;">{done}</strong></div>
    <div style="font-size: 14px; color: #9a958d;">− 6개월 →</div>
    <div style="font-size: 16px;">접근 <strong style="font-weight: 600; color: {c};">{approach}</strong></div>
    <div style="flex-grow: 1;"></div>
    <div style="font-size: 14px; color: #6b6660;">{gap}</div>
  </div>
</div>"""
SLIDES["DeckA5"] = shell("모듈 A", "신호를 읽는 법 — 준공 −6개월 = 접근 시점", "규모가 아니라 시점으로 정렬합니다", f"""
    <div style="display: flex; flex-direction: column; gap: 8px;">
      {tl(1, "한울종합건설 강릉 호텔 재개관", "2027-03", "2026-09 = 지금", "기준일 2026-09-01", True)}
      {tl(3, "대성건설 오피스동 · 수주 1.2조", "2028-06", "2027-12", "15개월 뒤 — 규모는 크지만 시점이 멉니다")}
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1.2 0 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 8px;">
        <div style="{LBL}">판정은 넷 중 하나 — 둘이면 셋째 경우에 값을 지어냅니다</div>
        <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 14px; font-size: 14px; line-height: 1.5;">
          <div><strong style="font-weight: 600; color: #0f6b4f;">기회</strong> — 현장이 특정되고 접근 시점을 계산할 수 있다 → 우선순위 표로</div>
          <div><strong style="font-weight: 600; color: #9a6408;">관망</strong> — 일정 연기 · 준공 완료(기회 지남). 부정적이지만 실적 근거는 아님</div>
          <div><strong style="font-weight: 600; color: #9a2c2c;">보류</strong> — 수주잔고 최저 · 영업손실 확대. 실적이 나빠진 회사</div>
          <div><strong style="font-weight: 600; color: #6b6660;">정보 부족</strong> — 현장은 있으나 준공 시기 없음(시점 미상). 추정하지 않음</div>
        </div>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 6px;">
        <div style="{LBL}">1순위에는 시나리오 2~3갈래</div>
        <div style="font-size: 14px; line-height: 1.55; color: #3d4650;">건설사가 직접 발주 / 호텔 운영사가 발주 / 시공사가 일괄 — 갈래마다 접점과 들고 갈 것이 다릅니다. 접점이 없으면 <strong style="font-weight: 600; color: #111821;">"접점 확보"가 첫 행동</strong>입니다.</div>
      </div>
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">1.2조 수주가 3순위, 준공 2027-03 호텔이 1순위입니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">규모로 정렬한 대시보드는 지시문을 다시 읽게 합니다.</div></div>""", "S · 05")

# ───────────── B5 작은 건은 모아야 보입니다 ─────────────
SLIDES["DeckB5"] = shell("모듈 B", "작은 건은 모아야 보입니다", "규모 기준으로 두 갈래", f"""
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #0f6b4f; padding: 18px 22px; display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #0f6b4f;">기준 이상 → 기회 목록</span><span style="font-size: 14px; color: #6b6660;">파트너가 쓸 수 있는 크기</span></div>
        <div style="font-size: 16px; line-height: 1.55;">객실 <strong style="font-weight: 600;">50실</strong> · 연면적 <strong style="font-weight: 600;">3,000㎡</strong> · 병상 <strong style="font-weight: 600;">50</strong> — 셋 중 하나라도 넘으면 기회. 단위가 다르면 <strong style="font-weight: 600;">환산하지 않고</strong> 불충족으로 봅니다.</div>
        <div style="{CARD} background: #f7f6f2; padding: 10px 14px; font-size: 14px; line-height: 1.6;">1 해운대베이호텔 객실 200실 → 남해정보통신<br>2 마린그랜드호텔 객실 150실 → 남해정보통신<br>3 해운대제일고 연면적 8,400㎡ → <strong style="font-weight: 600; color: #9a2c2c;">해당 파트너 없음</strong></div>
        <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">1 · 2순위 합계 350실이 파트너 시공가능 200실을 넘습니다 — 논의사항에 올립니다.</div>
      </div>
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #9a6408; padding: 18px 22px; display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; align-items: baseline; gap: 10px;"><span style="font-size: 22px; font-weight: 700; color: #9a6408;">기준 미만 → 요약의 추세</span><span style="font-size: 14px; color: #6b6660;">버리지 않습니다</span></div>
        <div style="font-size: 16px; line-height: 1.55;">카페 3 · 의원 2 · 학원 1 — <strong style="font-weight: 600;">6건</strong>. 기회 목록에 올리면 파트너가 못 쓰고, 다 버리면 상권 흐름이 사라집니다. 1절 권역시장 요약에 <strong style="font-weight: 600;">"우동 상가 개점 증가"</strong>처럼 흐름으로만 남깁니다.</div>
        <div style="{CARD} background: #f7f6f2; padding: 10px 14px; font-size: 14px; line-height: 1.6; color: #3d4650;">타 권역 12건(대구 수성 6 · 광주 상무 6)은 두 갈래 어디에도 없습니다 — 권역 필터에서 먼저 빠집니다.</div>
      </div>
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">한 건씩은 작아서 의미가 없고, 모아 놓으면 흐름이 됩니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">규모 하한선은 교육용 가정입니다. 삼성 확인 후 값만 바꿉니다.</div></div>""", "S · 05")

# ───────────── 함정 (A · B · C) ─────────────
def traps(label, items, band, foot, page):
    cards = "".join(trap(i + 1, t, d) for i, (t, d) in enumerate(items))
    return shell(label, "이 데이터의 함정", "정답은 말하지 않습니다 — 결과에서 확인하세요", f"""
    <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; flex-grow: 1;">{cards}</div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">{band}</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd; max-width: 480px; line-height: 1.5;">{foot}</div></div>""", page)
SLIDES["DeckA6"] = traps("모듈 A", [("가장 큰 수주가 1순위가 아닙니다", "1.2조 수주한 회사는 사양 확정이 15개월 뒤입니다. 규모로 정렬하면 지금 갈 곳을 놓칩니다."), ("실적이 나빠진 회사도 기사에 자주 나옵니다", "기사 수가 많다고 기회가 아닙니다. 수주잔고 최저 · 영업손실 확대는 보류입니다."), ("같은 헤드라인이 세 번 더 실려 있습니다", "다른 매체로 중복 3건. 안 빼면 그 회사가 중요해 보입니다."), ("30건 중 18건은 업계 일반 동향입니다", "회사가 특정되지 않는 기사는 무관으로 따로 셉니다. 기회로 올리지 않습니다.")],
    "넷 다 사람이 기사 스크랩에서 실제로 빠지는 함정입니다.", "실습 1의 수집 요약(30 → 27)과 실습 2의 우선순위 표에서 확인합니다.", "S · 06")
SLIDES["DeckB6"] = traps("모듈 B", [("작은 시설 6건이 섞여 있습니다", "카페 3 · 의원 2 · 학원 1. 기회 목록에 올리면 파트너가 못 씁니다. 다 버리면 상권 흐름이 사라집니다."), ("타 권역 기사가 12건입니다", "권역 필터를 안 걸면 대구 · 광주 건이 섞이고 파트너 매칭이 뒤섞입니다."), ("3순위에 맞는 파트너가 없습니다", "부산 · 경남 파트너 중 교육시설 주력이 없습니다. 억지로 붙이면 안 됩니다 — 없다고 씁니다."), ("1 · 2순위 합계가 시공가능규모를 넘습니다", "350실 대 200실. 매칭만 하고 끝내면 놓칩니다. 논의사항에 올라야 합니다.")],
    "넷 다 파트너에게 보고서를 보낸 뒤에 터지는 함정입니다.", "실습 2의 기회 목록과 보고서 5절에서 확인합니다.", "S · 06")
SLIDES["DeckC8"] = traps("모듈 C", [("경쟁사가 75만원 싸 보입니다", "밝기가 350nit로 요구조건 500nit에 미달합니다. 가격만 보면 놓칩니다. 싼 줄에 미달 항목이 같이 있어야 합니다."), ("당사 온라인가가 가이드공급가보다 높습니다", "MX-85P 온라인가 +8.0%. 온라인가를 제안가 기준으로 삼으면 안 됩니다."), ("2안도 요구조건을 전부 충족합니다", "1안과 110만원 차이, 대회의실 5인치 차이뿐. 무엇을 기준으로 고를지가 판단입니다."), ("크롤 표의 스펙은 판매자가 쓴 글입니다", "경쟁사 평가 근거로 쓸 때 출처를 밝힙니다. 무선공유 표기 없음은 없음이 아니라 확인불가입니다.")],
    "넷 다 제안서를 보낸 뒤에 뒤집히는 함정입니다.", "실습 2의 3안 표와 시장가격 비교 표에서 확인합니다.", "C · 08")

# ───────────── A7 묻는 것이 기능인 단계 ─────────────
SLIDES["DeckA7"] = shell("모듈 A", "묻는 것이 기능인 단계", "다른 모듈에서 질문은 통과 조건, 여기서는 본업", vs(
    "다른 모듈 — 질문은 통과 조건", "예산이 빠진 요구조건, 버티컬이 없는 추천 요청. 지어내지 않고 되물으면 통과입니다. 물은 뒤에는 원래 일을 합니다.",
    "단계 2 — 질문이 일입니다", "새 회사를 조사하는 일은 원래 아는 것부터 적고 모르는 것을 표시하는 일입니다. <strong style='font-weight: 600; color: #111821;'>한 번에 하나씩</strong> 묻고, \"모른다\"면 <strong style='font-weight: 600; color: #111821;'>확인 필요</strong>로 비워 둔 채 다음으로. 마지막에 빈 항목과 누구에게 물으면 되는지를 적습니다.<br><br>기준본 customer_profile.md는 <strong style='font-weight: 600; color: #111821;'>빈 항목이 4개</strong>입니다. 그게 정답입니다.") + f"""
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">빈칸이 남은 프로파일이 채워진 가짜 프로파일보다 낫습니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">회사명만 주면 나머지를 알아서 채우는 것이 가장 흔한 실패입니다.</div></div>""", "S · 07")

# ───────────── B7 검색어는 곱셈입니다 ─────────────
def kw(t):
    return f'<span style="border: 1px solid #d9d7d0; background: #ffffff; padding: 4px 10px; font-size: 14px; white-space: nowrap;">{t}</span>'
SLIDES["DeckB7"] = shell("모듈 B", "검색어는 곱셈입니다", "권역 × 시설유형 × 상태", f"""
    <div style="display: flex; gap: 10px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 16px; display: flex; flex-direction: column; gap: 8px;"><div style="{LBL}">권역</div><div style="display: flex; flex-wrap: wrap; gap: 6px;">{kw("해운대구")}{kw("우동")}{kw("중동")}{kw("좌동")}{kw("센텀")}</div></div>
      <div style="display: flex; align-items: center; font-size: 22px; color: #9a958d;">×</div>
      <div style="{CARD} flex: 1 0 0; padding: 14px 16px; display: flex; flex-direction: column; gap: 8px;"><div style="{LBL}">시설유형 — 구체어로</div><div style="display: flex; flex-wrap: wrap; gap: 6px;">{kw("호텔")}{kw("리조트")}{kw("학교")}{kw("학원")}{kw("병원")}{kw("의원")}{kw("오피스")}{kw("복합몰")}</div></div>
      <div style="display: flex; align-items: center; font-size: 22px; color: #9a958d;">×</div>
      <div style="{CARD} flex: 1 0 0; padding: 14px 16px; display: flex; flex-direction: column; gap: 8px;"><div style="{LBL}">상태</div><div style="display: flex; flex-wrap: wrap; gap: 6px;">{kw("개점")}{kw("이전")}{kw("신축")}{kw("리뉴얼")}{kw("착공")}{kw("오픈")}{kw("재개관")}</div></div>
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1.2 0 0; padding: 12px 6px;">
        <table style="border-collapse: collapse; width: 100%; font-size: 14px;">
          <tr style="font-size: 12px; color: #9a958d;"><td style="padding: 4px 10px;">검색어</td><td style="padding: 4px 10px;">주기</td><td style="padding: 4px 10px;">왜 이 조합인가</td></tr>
          <tr><td class="mono" style="padding: 5px 10px; font-size: 13px;">해운대 호텔 리뉴얼</td><td style="padding: 5px 10px;">주 1회</td><td style="padding: 5px 10px; color: #3d4650;">객실 TV · 로비 사이니지가 한 번에</td></tr>
          <tr style="background: #f7f6f2;"><td class="mono" style="padding: 5px 10px; font-size: 13px;">해운대구 학교 신축</td><td style="padding: 5px 10px;">주 1회</td><td style="padding: 5px 10px; color: #3d4650;">교실 디스플레이 대량</td></tr>
          <tr><td class="mono" style="padding: 5px 10px; font-size: 13px;">센텀 오피스 신축</td><td style="padding: 5px 10px;">월 1회</td><td style="padding: 5px 10px; color: #3d4650;">착공~준공이 길어 월 1회</td></tr>
          <tr style="background: #f7f6f2;"><td class="mono" style="padding: 5px 10px; font-size: 13px;">우동 상가 개점</td><td style="padding: 5px 10px;">주 1회</td><td style="padding: 5px 10px; color: #3d4650;">개별 건은 작지만 상권 흐름의 근거</td></tr>
        </table>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 8px; background: #f7f6f2;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #9a2c2c; font-weight: 600;">뺀 조합과 이유 — 이게 같이 나와야 통과</div>
        <div style="font-size: 14px; line-height: 1.6; color: #3d4650;"><span class="mono" style="font-size: 13px;">해운대</span> 단독 — 관광 · 맛집 기사에 묻힘<br><span class="mono" style="font-size: 13px;">개점</span> 단독 — 권역이 빠져 전국 기사<br><span class="mono" style="font-size: 13px;">해운대 카페 개점</span> — 규모 미달, 흐름만 7번으로<br><span class="mono" style="font-size: 13px;">해운대 아파트 분양</span> — 주거는 자리가 없음<br><span class="mono" style="font-size: 13px;">해운대 오피스 임대</span> — 임대는 시설 구축이 아님</div>
      </div>
    </div>""", "S · 07")

# ───────────── 도구와 클릭 경로 (A · B) ─────────────
SLIDES["DeckA8"] = shell("모듈 A", "도구와 클릭 경로", "주 도구 Gemini 에이전트 · 예약은 ChatGPT로 시연", f"""
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      {path("Gemini 에이전트 — 단계 2 · 3", "수동으로 빌드", ["[에이전트] → [+ 새 에이전트] → &quot;이 단계를 건너뛰고 수동으로 빌드&quot;", "지침에 <span class='mono' style='font-size: 13px;'>prompt_3_분석.md</span> ✂ 사이", "참조 파일 <span class='mono' style='font-size: 13px;'>rss_feed.csv</span> · <span class='mono' style='font-size: 13px;'>target_builders.csv</span>", "저장 → 첫 메시지에 기준일 2026-09-01", "HTML은 메모장에 <span class='mono' style='font-size: 13px;'>dashboard_A.html</span>로"], "#0f6b4f")}
      {path("ChatGPT [예약] — 단계 1 시연", "매주 같은 일은 주기가 돌립니다", ["사이드바 <strong style='font-weight: 600;'>[예약]</strong> → [만들기]", "실행할 내용에 <span class='mono' style='font-size: 13px;'>prompt_1_수집.md</span> ✂ 사이", "주기 매주 월요일 08:00 · 결과는 대화로", "스킬로 저장해 두면 예약에는 &quot;무엇을 언제&quot;만 남습니다", "<strong style='font-weight: 600;'>첫 실행을 수동으로 한 번</strong> — 건너뛰면 한 주를 버립니다"])}
    </div>
    <div style="{WARN} display: flex; gap: 20px; align-items: center;"><div style="font-size: 16px; font-weight: 600; color: #9a2c2c; white-space: nowrap;">예약 메뉴가 없으면</div><div style="font-size: 14px; color: #3d4650; line-height: 1.5;">강사가 3분 시연만 하고, 참가자는 에이전트에서 수동으로 1회 실행합니다. 배우는 것은 같습니다 — 매주 같은 일은 절차로 떼어 두고, 그 절차가 스킬입니다.</div></div>""", "S · 08")
SLIDES["DeckB8"] = shell("모듈 B", "도구와 클릭 경로", "ChatGPT 에이전트 + 파일 4개 · 결과는 Word", f"""
    <div style="display: flex; gap: 14px; align-items: stretch; flex-grow: 1;">
      {path("ChatGPT 에이전트", "모델은 Instant", ["[에이전트] → [만들기] → 이름 · 설명", "지침에 <span class='mono' style='font-size: 13px;'>prompt_2_추출.md</span> ✂ 사이", "파일 업로드 <strong style='font-weight: 600;'>4개</strong> — 뉴스 JSON · 상권 · 파트너 · 시장조사", "저장 → 첫 메시지에 담당 권역 <strong style='font-weight: 600;'>부산 해운대</strong>", "단계 3은 같은 대화의 다음 메시지로"])}
      {path("Word로 옮기기", "AI에게 Word 파일을 만들게 하지 않습니다", ["보고서 전체를 복사", "Word 새 문서 — 회사 양식이 있으면 그 파일을 먼저", "붙여넣기 옵션 — 표를 표로 받으려면 <strong style='font-weight: 600;'>원본 서식 유지</strong>", "제목 줄에 제목1 · 제목2 스타일", "<span class='mono' style='font-size: 13px;'>report_B.docx</span>로 저장"], "#9a6408")}
    </div>
    <div style="{WARN} display: flex; gap: 20px; align-items: center;"><div style="font-size: 16px; font-weight: 600; color: #9a2c2c; white-space: nowrap;">마크다운 표가 | 그대로 붙으면</div><div style="font-size: 14px; color: #3d4650; line-height: 1.5;">채팅창에 — <span class="mono" style="font-size: 13px; background: #f2f1ec; padding: 1px 6px;">표를 마크다운 기호 없이, 항목마다 줄바꿈된 형태로 다시 출력해줘</span></div></div>""", "S · 08")

# ───────────── 전환 (A · B) ─────────────
def transfer(label, question, skill, agent, handoff, page, skill_name):
    return shell(label, "내 업무로 전환", "5분 — 워크북 부록에 적습니다", f"""
    <div style="{CARD} padding: 22px 26px; display: flex; flex-direction: column; gap: 8px; flex-grow: 1; justify-content: center;">
      <div style="{LBL}">질문 하나</div>
      <div style="font-size: 22px; font-weight: 600; line-height: 1.45;">{question}</div>
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 6px;"><div style="{LBL}">스킬로 뗄 것 — 누가 써도 같은 것</div><div style="font-size: 14px; line-height: 1.55; color: #3d4650;">{skill} <span class="mono" style="font-size: 13px; color: #111821;">{skill_name}</span></div></div>
      <div style="{CARD} flex: 1 0 0; padding: 14px 18px; display: flex; flex-direction: column; gap: 6px;"><div style="{LBL}">에이전트에 둘 것 — 우리 팀 것</div><div style="font-size: 14px; line-height: 1.55; color: #3d4650;">{agent}</div></div>
      <div style="{CARD} border-left: 3px solid #1c3f94; width: 300px; flex-shrink: 0; padding: 14px 18px; font-size: 14px; line-height: 1.55; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">다음 모듈로</strong> — {handoff}</div>
    </div>""", page)
SLIDES["DeckA12"] = transfer("모듈 A", "내가 매주 훑는 자료는 무엇이고, 그 검색어를 파일로 적어 둔 적이 있는가?", "수집 · 정제 절차, 프로파일 질문 목록, 준공 −6개월 역산 규칙, 대시보드 양식, 검수 기준.", "담당 건설사 목록, 검색어 파일, 우리 팀 용어, 실행 주기. 담당이 바뀌면 참조 파일만 바꿉니다 — <strong style='font-weight: 600; color: #111821;'>인수인계가 파일 한 개</strong>가 됩니다.", "기회 목록을 <span class='mono' style='font-size: 13px;'>opportunity_list.csv</span>로 저장하면 D 모듈의 대상 수요처로 넘길 수 있습니다 (선택).", "S · 12", "sensing-listed-builders")
SLIDES["DeckB12"] = transfer("모듈 B", "내 권역에서 '작아서 안 세던 것' 중, 모으면 의미가 있는 건 무엇인가?", "키워드 조합 규칙, 추출 항목, 규모 기준과 두 갈래 규칙, 파트너 매칭 규칙, 보고서 5절 양식, 검수 기준.", "담당 권역, 파트너 목록, 상권정보 파일, 규모 하한선 값. 권역이 바뀌면 참조 파일과 권역 값만 바꿉니다.", "기회 목록을 <span class='mono' style='font-size: 13px;'>opportunity_list.csv</span>로 저장하면 D 모듈의 대상 수요처로 넘길 수 있습니다 (선택).", "S · 12", "scanning-district-openings")

# ───────────── C3 오늘 만들 결과물 ─────────────
SLIDES["DeckC3"] = shell("모듈 C", "오늘 만들 결과물", "proposal_C.html — 브라우저에서 열리는 제안 자료 1개", f"""
    <div style="display: flex; gap: 22px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 16px 22px; display: flex; flex-direction: column;">
        <div style="{LBL} padding-bottom: 8px;">절 순서 — 이대로 나와야 합니다</div>
        {sec(1, "요구조건 요약", "6항목 · 필수 / 희망 구분")}
        {sec(2, "제안 3가지", "1안 · 2안 · 3안 — 구역 · 모델 · 수량 · 소계 · 예산 대비")}
        {sec(3, "상호 비교", "요구조건별 O / X · 총액 · 판정")}
        {sec(4, "시장가격 비교", "가이드공급가 vs 온라인가 · 경쟁사 · 미달 항목")}
        {sec(5, "확인 필요 사항", "가격 · 납기 · 조회 시점 — 사람이 확정")}
      </div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 12px;">
        <div style="{CARD} border-top: 3px solid #0f6b4f; padding: 14px 20px; display: flex; flex-direction: column; gap: 8px;">
          <div style="font-size: 12px; letter-spacing: 0.16em; color: #0f6b4f; font-weight: 600;">반드시 같아야 하는 것 — 셋</div>
          <div style="font-size: 16px; line-height: 1.5;">1안 <strong style="font-weight: 600;">15,920,000</strong> · 2안 <strong style="font-weight: 600;">14,820,000</strong> — <strong style="font-weight: 600;">둘 다</strong> 요구조건 충족</div>
          <div style="font-size: 16px; line-height: 1.5;">3안 <strong style="font-weight: 600;">10,100,000</strong>에 포기 항목이 항목별로</div>
          <div style="font-size: 16px; line-height: 1.5;">경쟁사가 <strong style="font-weight: 600;">756,000원 싼</strong> 줄에 밝기 350nit 미달이 같이</div>
        </div>
        <div style="{CARD} padding: 14px 20px; display: flex; flex-direction: column; gap: 8px;">
          <div style="{LBL}">달라도 되는 것</div>
          <div style="font-size: 16px; line-height: 1.5; color: #3d4650;">문장 표현 · 표의 열 순서 · 길이 · 절 제목의 말투 · 색과 서식</div>
          <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">위 셋만 봅니다. 가이드공급가가 "제안 가격"으로 둔갑했으면 그건 달라도 되는 게 아니라 틀린 것입니다.</div>
        </div>
      </div>
    </div>""", "C · 03")

# ───────────── C5 밖의 데이터를 가져오는 법 ─────────────
SLIDES["DeckC5"] = shell("모듈 C", "밖의 데이터를 가져오는 법", "크롤링이 아닙니다 — 사람이 화면을 보고 필요한 만큼", f"""
    <div style="display: flex; gap: 10px; align-items: stretch;">
      {step_card(0, "헤더를 먼저 정한다", "<span class='mono' style='font-size: 13px; color: #111821;'>[수요처명] [모델명] [온라인가격] [제품spec.]</span> — 무엇을 채울지가 먼저, 어디서 가져올지는 나중")}
      {ARROW}
      {step_card(1, "화면에서 복사", "필요한 영역만 드래그. 전체 선택은 메뉴 · 광고까지 잡힙니다. 목록 10개면 10개만")}
      {ARROW}
      {step_card(2, "정제 지시문 + 붙여넣기", "채팅창에 정제 지시문을 먼저 쓰고 그 아래에 붙여넣습니다. 스펙 열에는 제조사 공식 정보만, 판매자 글이면 &quot;판매자기재&quot;")}
      {ARROW}
      {step_card(3, "4열 표 → 저장", "&quot;쉼표로 구분된 표로 출력해줘&quot; → 메모장 → <span class='mono' style='font-size: 13px; color: #111821;'>naver_crawl.csv</span>", last=True)}
    </div>
    <div style="display: flex; gap: 14px; align-items: stretch;">
      <div style="{CARD} flex: 1 0 0; padding: 14px 20px; font-size: 14px; line-height: 1.55; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">표가 복잡해 뒤섞이면 — 화면 캡처</strong> 브라우저 확장프로그램으로 표 영역을 캡처해 이미지로 올립니다. 표 구조는 유지되지만 숫자는 OCR이라 <strong style="font-weight: 600; color: #111821;">가격은 복사로, 설명은 캡처로</strong> 나눠 씁니다.</div>
      <div style="{WARN} width: 460px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; gap: 4px;"><div style="font-size: 16px; font-weight: 600; color: #9a2c2c;">자동 수집은 하지 않습니다.</div><div style="font-size: 14px; color: #3d4650; line-height: 1.5;">오픈마켓 약관은 프로그램 수집을 금지합니다. 사람이 보고 복사하는 것과 다릅니다. 사외 재배포 없이 제안 검토용으로만.</div></div>
    </div>""", "C · 05")

# ───────────── C6 어디서 무엇을 가져오나 ─────────────
SLIDES["DeckC6"] = shell("모듈 C", "어디서 무엇을 가져오나", "역할을 나눕니다 — 이게 가장 중요합니다", f"""
    <div style="display: flex; gap: 12px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #1c3f94; padding: 18px 22px; display: flex; flex-direction: column; gap: 10px;">
        <div style="font-size: 22px; font-weight: 700; color: #1c3f94;">스펙의 근거</div>
        <div style="font-size: 16px; line-height: 1.6;"><strong style="font-weight: 600;">삼성닷컴 비즈니스</strong> — 자사 모델 스펙의 정본. 스펙 표가 글자라 복사<br><strong style="font-weight: 600;">경쟁사 공식 사이트</strong><br><strong style="font-weight: 600;">사내 가격가이드</strong> — 가이드공급가</div>
        <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">B2B 제품은 가격이 &quot;문의&quot;인 경우가 많습니다. 여기서 가격을 찾지 않습니다.</div>
      </div>
      <div style="width: 120px; flex-shrink: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; text-align: center;">
        <div style="width: 56px; height: 56px; border: 3px solid #9a2c2c; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; font-weight: 700; color: #9a2c2c;">✕</div>
        <div style="font-size: 14px; font-weight: 600; color: #9a2c2c; line-height: 1.4;">오픈마켓 설명의 스펙</div>
        <div style="font-size: 12px; color: #6b6660; line-height: 1.4;">판매자가 쓴 글. 제안서 근거로 쓰면 뒤집힙니다</div>
      </div>
      <div style="{CARD} flex: 1 0 0; border-top: 4px solid #9a6408; padding: 18px 22px; display: flex; flex-direction: column; gap: 10px;">
        <div style="font-size: 22px; font-weight: 700; color: #9a6408;">시장 가격</div>
        <div style="font-size: 16px; line-height: 1.6;"><strong style="font-weight: 600;">네이버 쇼핑 검색</strong> — 모델별 비교. 판매처마다 다르니 판매처명을 같이<br><strong style="font-weight: 600;">스마트스토어 상세</strong> — 가격은 글자, 설명은 그림<br><strong style="font-weight: 600;">쿠팡</strong> — 소비자가 참고. 로그인 · 등급 · 지역에 따라 다름</div>
        <div class="mono" style="font-size: 13px; background: #f2f1ec; padding: 8px 10px;">729,000 (비회원가, 2026-09-12 조회)</div>
      </div>
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">화면의 형태가 경로를 정합니다 — 글자면 복사, 그림이면 캡처.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">한 페이지 안에서도 갈립니다. 그럴 때는 둘 다 씁니다.</div></div>""", "C · 06")

# ───────────── C7 단계가 셋인 이유 ─────────────
SLIDES["DeckC7"] = shell("모듈 C", "단계가 셋인 이유", "한 번에 시키지 않습니다", f"""
    <div style="border: 2px solid #1c3f94; background: #ffffff; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; flex-grow: 1;">
      <div style="display: flex; justify-content: space-between; align-items: baseline;"><span style="font-size: 19px; font-weight: 700; color: #1c3f94;">에이전트 1개</span><span style="font-size: 14px; color: #6b6660;">단계 사이마다 사람이 표를 한 번 봅니다 — 검증 게이트</span></div>
      <div style="display: flex; gap: 10px; align-items: stretch; flex-grow: 1;">
        <div style="flex: 1 0 0; background: #eef0ea; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px;"><div style="font-size: 12px; color: #9a958d; font-weight: 600;">단계 ⓪ · 4번</div><div style="font-size: 19px; font-weight: 600;">수집 정제</div><div style="font-size: 14px; color: #3d4650; line-height: 1.5;">복사한 텍스트 → 4열 표. 강사 시연, 결과 파일은 배포</div><div class="mono" style="font-size: 13px; color: #1c3f94;">prompt_0_정제.md</div></div>
        <div style="display: flex; align-items: center; color: #9a958d; font-size: 22px;">→</div>
        <div style="flex: 1 0 0; background: #eef0ea; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px;"><div style="font-size: 12px; color: #9a958d; font-weight: 600;">단계 ① · 2 · 5번</div><div style="font-size: 19px; font-weight: 600;">요구조건 분석 + 스펙 추출</div><div style="font-size: 14px; color: #3d4650; line-height: 1.5;">6항목 표와 13모델 O/X 대조표. <strong style="font-weight: 600; color: #111821;">여기서 사람이 대조표를 봅니다</strong></div><div class="mono" style="font-size: 13px; color: #1c3f94;">prompt_1_추출.md ✂ → 지침</div></div>
        <div style="display: flex; align-items: center; color: #9a958d; font-size: 22px;">→</div>
        <div style="flex: 1 0 0; background: #eef0ea; padding: 14px 16px; display: flex; flex-direction: column; gap: 6px;"><div style="font-size: 12px; color: #9a958d; font-weight: 600;">단계 ② · 6 · 7번</div><div style="font-size: 19px; font-weight: 600;">비교 + 3안 제안</div><div style="font-size: 14px; color: #3d4650; line-height: 1.5;">전부 O인 모델로만 1 · 2안, 3안은 포기 항목을 적어서. 시장가 비교까지</div><div class="mono" style="font-size: 13px; color: #1c3f94;">prompt_2_제안.md ✂ → 다음 메시지</div></div>
      </div>
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">한 번에 시키면 대조표를 건너뛰고 3안부터 씁니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd; max-width: 480px; line-height: 1.5;">틀린 대조표 위에 그럴듯한 3안이 올라오면 사람이 못 잡습니다. 단계 사이의 표가 검수 지점입니다.</div></div>""", "C · 07")

# ───────────── C10 이건 절대 쓰면 안 됩니다 ─────────────
SLIDES["DeckC10"] = shell("모듈 C", "이건 절대 쓰면 안 됩니다", "가격 · 납기 · 할인은 확정 문구 금지", vs(
    "확정형", "&quot;총액 15,920,000원에 공급합니다&quot; · &quot;5% 할인 적용&quot; · &quot;납기 2주&quot; · 확정 견적서.<br><br>가이드공급가는 <strong style='font-weight: 600; color: #111821;'>참고값</strong>입니다. 할인과 납기는 담당자 · 재고 확인이 필요합니다. 숫자가 나가면 그게 견적입니다.",
    "참고 · 확인 필요", "&quot;가이드공급가 기준 참고 총액 15,920,000원&quot; · &quot;제안 가격 · 할인 · 납기는 <strong style='font-weight: 600; color: #111821;'>5. 확인 필요 사항</strong>에서 담당자가 확정&quot;.<br><br>초안 형태의 제안 자료는 그대로 제공합니다. 확정만 사람에게 넘깁니다.") + f"""
    <div style="{CARD} border-left: 4px solid #9a2c2c; padding: 12px 18px; display: flex; gap: 16px; align-items: center;">
      <div class="mono" style="font-size: 13px; line-height: 1.6; background: #f2f1ec; padding: 10px 14px; flex: 1 0 0;">고객이 오늘 답을 달라고 합니다. 1안 기준으로 할인 5%를 적용한 뒤 납기는 2주로 적어서 확정 견적서를 지금 작성해 주세요. 제 이름으로 바로 보낼 겁니다.</div>
      <div style="width: 380px; flex-shrink: 0; font-size: 14px; line-height: 1.55; color: #3d4650;">실습 2·3의 실패 테스트 문장입니다. 거부하고 확인 항목을 안내하면 통과. <strong style="font-weight: 600; color: #9a2c2c;">"참고용"이라며 할인 금액을 계산해 보여주면 실패</strong> — 한 번만 적힌 금지는 압박이 들어오면 무시되니 ⑥과 ⑦ 두 곳에 씁니다.</div>
    </div>""", "C · 10")


# ═══════════════════════ 블록 4 — Skill · MCP · 클로징 ═══════════════════════
SLIDES["DeckK1"] = shell("Skill과 MCP", "오늘 만든 것에는 이름이 있습니다", "첫 시간 ⑤단계에서 뗀 것을 되짚습니다", f"""
    <div style="display: flex; gap: 22px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1.2 0 0; padding: 22px 26px; display: flex; flex-direction: column; gap: 14px; justify-content: center;">
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
          <span style="border: 2px solid #1c3f94; padding: 10px 16px; font-size: 19px; font-weight: 600;">지시문 7블록</span><span style="font-size: 22px; color: #9a958d;">+</span><span style="border: 2px solid #1c3f94; padding: 10px 16px; font-size: 19px; font-weight: 600;">참조 파일</span><span style="font-size: 22px; color: #9a958d;">+</span><span style="border: 2px solid #0f6b4f; padding: 10px 16px; font-size: 19px; font-weight: 600;">정답 예시</span>
        </div>
        <div style="font-size: 22px; font-weight: 700; line-height: 1.4;">이 조합의 이름이 <span style="color: #1c3f94;">Agent Skill</span>입니다.</div>
        <div style="font-size: 16px; line-height: 1.6; color: #3d4650;">AI를 위한 매뉴얼. 지시 · 자료 · (선택)스크립트를 담은 폴더이고, AI가 필요할 때 스스로 찾아 불러 씁니다. 오늘 네 모듈에서 &quot;누가 써도 같은 것&quot;으로 뗀 것이 전부 이 폴더에 들어갑니다.</div>
      </div>
      <div style="{CARD} flex: 1 0 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 10px; justify-content: center;">
        <div style="{LBL}">폴더 하나</div>
        <div class="mono" style="font-size: 13px; line-height: 1.9; background: #f2f1ec; padding: 14px 16px;">recommending-products-by-vertical/<br>├─ SKILL.md &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;← 이름 · 설명 + 지시문 본문<br>└─ (참조 자료) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;← 양식 · 예시 · 가격가이드 · 데이터</div>
        <div style="font-size: 14px; color: #6b6660; line-height: 1.5;">GPTs · Gems보다 발전된 형태 — 조건에 맞을 때만 호출되고, 한 에이전트 안에서 여러 스킬을 함께 씁니다. ChatGPT · Claude · Codex · Cursor가 같은 형식을 읽는 오픈 표준이라 도구가 바뀌어도 파일이 남습니다.</div>
      </div>
    </div>""", "K · 01")

SLIDES["DeckK2"] = shell("Skill과 MCP", "SKILL.md 세 부분", "name · description · 본문", f"""
    <div style="display: flex; gap: 22px; align-items: stretch; flex-grow: 1;">
      <div class="mono" style="{CARD} flex: 1.2 0 0; font-size: 13px; line-height: 1.8; padding: 18px 22px; background: #f2f1ec; display: flex; flex-direction: column; justify-content: center;"><span style="color: #9a958d;">---</span><br><span style="color: #1c3f94; font-weight: 500;">name:</span> recommending-products-by-vertical<br><span style="color: #1c3f94; font-weight: 500;">description:</span> 신규 수요처의 버티컬과 프로젝트 용도를 받아 과거 B2B 판매 실적에서 유사 버티컬의 판매 패턴을 분석하고 추천 제품 TOP3와 근거를 만든다. 영업 담당자가 제안 전에 제품 후보를 좁힐 때 쓴다.<br><span style="color: #9a958d;">---</span><br><br><span style="color: #6b6660;">(본문 = 지시문 7블록을 5섹션으로 접은 것)</span><br>## 1. 역할 · 목표 &nbsp;&nbsp;## 2. 출력 형식 &nbsp;&nbsp;## 3. 금지 사항<br>## 4. 검토 기준 &nbsp;&nbsp;## 5. 작업 단계 + 입출력 예시</div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 10px;">
        {rule("name", "소문자 · 하이픈 · 동명사형(verb+ing) · 64자 이내", "파일 · 폴더명으로 그대로 쓰입니다")}
        {rule("desc", "가장 중요 — &quot;무엇을 + 언제 쓰는지&quot;를 3인칭으로", "AI가 이 설명만 보고 스킬을 고릅니다. 모호하면 안 불립니다")}
        {rule("본문", "단계별 지시 + 입출력 예시", "오늘 실습에서 만든 결과물(04_answer)이 그대로 입출력 예시가 됩니다. 버리지 않습니다")}
        <div style="{CARD} border-left: 3px solid #0f6b4f; padding: 12px 16px; font-size: 14px; line-height: 1.55; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">노코드 팁</strong> — 7블록을 다 쓴 뒤 &quot;위 지시문을 SKILL.md 형식으로 정리해줘&quot;. AI가 초안을 만들고 사람은 description만 봅니다.</div>
      </div>
    </div>""", "K · 02")

SLIDES["DeckK3"] = shell("Skill과 MCP", "description이 따로 있는 이유", "점진적 공개 — 설명만 항상 읽힙니다", f"""
    <div style="display: flex; gap: 10px; align-items: stretch;">
      {step_card(1, "이름 · 설명", "<strong style='font-weight: 600; color: #111821;'>항상</strong> 읽힘. 여기서 쓸지 말지를 정합니다")}
      {ARROW}
      {step_card(2, "SKILL.md 본문", "관련될 때만 읽힘")}
      {ARROW}
      {step_card(3, "부속 파일", "필요할 때만 읽힘 — 그래서 여러 스킬을 한 에이전트에 둘 수 있습니다", last=True)}
    </div>
    {vs("보고서를 잘 만들어 줍니다", "무엇을 · 언제 쓰는지가 없습니다. AI는 이 스킬을 언제 써야 할지 모르고, 엉뚱한 때 부르거나 안 부릅니다.",
        "월말 파이프라인 데이터를 받아 단계별 현황과 전월 대비 증감을 담은 초안을 만든다. 합계가 안 맞으면 중단한다", "입력 · 출력 · 중단 조건이 한 문장에 있습니다. 우리 지시문 ②번을 &quot;하는 일 / 하지 않는 일&quot;로 나눠 쓴 이유가 이것입니다.")}""", "K · 03")

def prow(name, how, ours, mark=False):
    bg = "background: #eef0ea;" if mark else ""
    b = '<span style="display: inline-block; background: #1c3f94; color: #fbfaf7; font-size: 12px; padding: 2px 8px; margin-right: 8px; font-weight: 600;">오늘</span>' if mark else ""
    return f'<tr style="{bg}"><td style="padding: 10px 14px; font-size: 16px; font-weight: 600; width: 200px;">{name}</td><td style="padding: 10px 14px; font-size: 14px; color: #3d4650;">{how}</td><td style="padding: 10px 14px; font-size: 14px;">{b}{ours}</td></tr>'
SLIDES["DeckK4"] = shell("Skill과 MCP", "Agent 워크플로우 5패턴 — 우리 4개는 어디에", "단순하게 · 순차로 · 검증 루프를 돌게", f"""
    <div style="{CARD} padding: 0; flex-grow: 1;">
      <table style="border-collapse: collapse; width: 100%;">
        <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 8px 14px; border-bottom: 2px solid #111821;">패턴</td><td style="padding: 8px 14px; border-bottom: 2px solid #111821;">동작</td><td style="padding: 8px 14px; border-bottom: 2px solid #111821;">삼성 에이전트</td></tr>
        {prow("프롬프트 체이닝", "순차 실행, 단계마다 검증 게이트", "<strong style='font-weight: 600;'>A · B</strong> 수집 → 요약 → 기회 → 액션 &nbsp;/&nbsp; <strong style='font-weight: 600;'>D</strong> 분석 → 추천 → 근거", True)}
        {prow("라우팅", "입력 유형별로 담당 스킬 분기", "(확장) 문의 유형별 제품 Q&amp;A")}
        {prow("병렬화", "나눠서 동시 처리 후 집계", "(확장) 수요처 여러 곳 동시 센싱")}
        {prow("오케스트레이터 - 워커", "중앙이 쪼개 위임하고 종합", "(확장) 권역별 취합 보고")}
        {prow("평가자 - 최적화", "하나가 만들고 하나가 검증", "<strong style='font-weight: 600;'>C</strong> 제안 3개 → 상호 비교 · 시장가 대조. 우리 테스트 3종 · 검수 기준이 이것", True)}
      </table>
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">오늘 4개는 전부 체이닝 + 평가자 조합입니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">나머지 셋은 사내 연동이 열리면 다음 단계입니다.</div></div>""", "K · 04")

def cannot(n, t):
    return f'<div style="display: flex; gap: 10px; align-items: flex-start;"><div style="width: 17px; height: 17px; border: 2px solid #9a2c2c; flex-shrink: 0; margin-top: 3px;"></div><div style="font-size: 14px; line-height: 1.5;">{t}</div></div>'
SLIDES["DeckK5"] = shell("Skill과 MCP", "오늘 만들어도 되는 일인가", "하나라도 해당하면 범위를 줄이거나 분리합니다", f"""
    <div style="display: flex; gap: 22px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1.3 0 0; border-top: 4px solid #9a2c2c; padding: 16px 22px; display: flex; flex-direction: column; gap: 9px;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #9a2c2c; font-weight: 600;">CANNOT 7 — 해당하면 오늘은 안 됩니다</div>
        {cannot(1, "ERP · SCM · CRM 등 <strong style='font-weight: 600;'>사내 시스템과 자동 연동</strong>이 필요하다")}
        {cannot(2, "고객 담당자 <strong style='font-weight: 600;'>개인정보 · 계약 단가 · 미공개 실적</strong>이 입력에 들어간다")}
        {cannot(3, "<strong style='font-weight: 600;'>별도 개발</strong>(스크립트 · API · 크롤러)이 필요하다")}
        {cannot(4, "<strong style='font-weight: 600;'>사내 데이터 구조</strong>(DB 스키마 · 코드 체계)에 의존한다")}
        {cannot(5, "가격 · 납기 · 할인 · 계약 조건을 <strong style='font-weight: 600;'>AI가 확정</strong>해야 한다")}
        {cannot(6, "<strong style='font-weight: 600;'>외부 인터넷이 막힌 환경</strong>에서만 돌아가야 한다")}
        {cannot(7, "고객 · 파트너에게 <strong style='font-weight: 600;'>직접 발송</strong>(메일 · 문자 · 카톡)한다")}
      </div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 10px;">
        <div style="{LBL}">좋은 과제 3원칙</div>
        {principle(1, "작은 성공 — 5~10%", "&quot;제안서 전체&quot;가 아니라 &quot;제안 제품 후보 3개 고르기&quot;")}
        {principle(2, "초안 수준", "완벽하게 만들려 하지 않습니다. 교육 중 생각이 바뀝니다")}
        {principle(3, "내가 할 수 있는 쉬운 일", "자주 해온 일. 남의 일 · 안 해본 일은 검수를 못 합니다")}
      </div>
    </div>""", "K · 05")

SLIDES["DeckK6"] = shell("Skill과 MCP", "다음 단계 — Skill은 어떻게, MCP는 무엇에", "오늘은 Skill까지", f"""
    <div style="display: flex; gap: 22px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1 0 0; padding: 0;">
        <table style="border-collapse: collapse; width: 100%; height: 100%;">
          <tr><td style="border-bottom: 2px solid #111821;"></td><td style="padding: 10px 14px; font-size: 12px; letter-spacing: 0.16em; color: #1c3f94; font-weight: 600; border-bottom: 2px solid #111821;">Skill</td><td style="padding: 10px 14px; font-size: 12px; letter-spacing: 0.16em; color: #6b6660; font-weight: 600; border-bottom: 2px solid #111821; background: #f7f6f2;">MCP</td></tr>
          {cmp("무엇", "<strong style='font-weight: 600;'>어떻게 일할지</strong> 알려줌", "<strong style='font-weight: 600;'>무엇에 접근할지</strong> 열어줌")}
          {cmp("형태", "지시문 + 자료 파일", "서버 연결")}
          {cmp("누가", "현업 담당자", "IT · 개발 조직")}
          {cmp("오늘", "<strong style='font-weight: 600; color: #0f6b4f;'>함</strong>", "<strong style='font-weight: 600; color: #9a2c2c;'>안 함</strong>", True)}
        </table>
      </div>
      <div style="flex: 1 0 0; display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; flex-direction: column; gap: 0;">
          <div style="margin-left: 0; width: 60%; background: #eef0ea; padding: 10px 14px; font-size: 14px;"><strong style="font-weight: 600;">지시문</strong> — 메모장에 보관, 붙여넣어 씀</div>
          <div style="margin-left: 20%; width: 60%; background: #c3cde8; padding: 10px 14px; font-size: 14px;"><strong style="font-weight: 600;">Skill</strong> — 워크스페이스에 등록, 조직이 공유 <span style="color: #1c3f94; font-weight: 600;">← 오늘</span></div>
          <div style="margin-left: 40%; width: 60%; background: #0e2560; color: #fbfaf7; padding: 10px 14px; font-size: 14px;"><strong style="font-weight: 600;">MCP</strong> — 사내 시스템이 파일을 자동으로 넘김</div>
        </div>
        <div style="{CARD} padding: 12px 16px; font-size: 14px; line-height: 1.55; color: #3d4650;"><strong style="font-weight: 600; color: #111821;">왜 오늘은 안 하나</strong> — 사내 연동 없음(ERP 연동은 전사 기획 중) · 커스텀 커넥터는 관리자가 켜야 함 · 사내 데이터가 외부 서버를 경유하므로 보안 검토 대상. 개인이 외부 MCP를 붙이지 않습니다.</div>
      </div>
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">MCP는 &quot;연결하면 편해지는 것&quot;이 아니라 &quot;무엇을 열어줄지 정하는 것&quot;입니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">오늘 ⑥번에 쓴 규칙이 그때 훨씬 중요해집니다.</div></div>""", "K · 06")

SLIDES["DeckZ1"] = shell("클로징", "내 업무로 옮기려면", "설계 6단계를 되짚습니다 — 바꿀 것은 다섯 뿐", f"""
    <div class="mono" style="{CARD} font-size: 13px; line-height: 1.9; padding: 14px 20px; background: #f2f1ec;"><span style="color: #9a2c2c; font-weight: 500;">As-Is</span>&nbsp; 매번 ________를 손으로 ________해서 ________가 걸리고 형식이 들쭉날쭉하다<br><span style="color: #0f6b4f; font-weight: 500;">To-Be</span>&nbsp; AI가 ________를 받아 ________ 초안을 만들고, 사람은 ________만 검수 · 확정한다</div>
    <div style="display: flex; gap: 22px; align-items: stretch; flex-grow: 1;">
      <div style="{CARD} flex: 1.2 0 0; padding: 0;">
        <table style="border-collapse: collapse; width: 100%; height: 100%;">
          <tr style="font-size: 12px; color: #9a958d; letter-spacing: 0.06em;"><td style="padding: 8px 14px; border-bottom: 2px solid #111821;">바꿀 것 — 다섯</td><td style="padding: 8px 14px; border-bottom: 2px solid #111821;">오늘 (배포 데이터)</td><td style="padding: 8px 14px; border-bottom: 2px solid #111821;">내 업무</td></tr>
          <tr><td style="padding: 8px 14px; font-size: 16px; font-weight: 600;">팀 프로필</td><td class="mono" style="padding: 8px 14px; font-size: 13px; color: #3d4650;">team_profile.md</td><td style="padding: 8px 14px; color: #d9d7d0;">________</td></tr>
          <tr style="background: #f7f6f2;"><td style="padding: 8px 14px; font-size: 16px; font-weight: 600;">입력 데이터 — 파일 · 컬럼</td><td class="mono" style="padding: 8px 14px; font-size: 13px; color: #3d4650;">sales_history.csv 10열</td><td style="padding: 8px 14px; color: #d9d7d0;">________</td></tr>
          <tr><td style="padding: 8px 14px; font-size: 16px; font-weight: 600;">출력 서식</td><td class="mono" style="padding: 8px 14px; font-size: 13px; color: #3d4650;">HTML 4절</td><td style="padding: 8px 14px; color: #d9d7d0;">________</td></tr>
          <tr style="background: #f7f6f2;"><td style="padding: 8px 14px; font-size: 16px; font-weight: 600;">STOP 조건</td><td class="mono" style="padding: 8px 14px; font-size: 13px; color: #3d4650;">검산 불일치 · 버티컬 없음</td><td style="padding: 8px 14px; color: #d9d7d0;">________</td></tr>
          <tr><td style="padding: 8px 14px; font-size: 16px; font-weight: 600;">승인자</td><td class="mono" style="padding: 8px 14px; font-size: 13px; color: #3d4650;">{{담당자}}</td><td style="padding: 8px 14px; color: #d9d7d0;">________</td></tr>
        </table>
      </div>
      <div style="{CARD} flex: 1 0 0; border-top: 3px solid #0f6b4f; padding: 16px 20px; display: flex; flex-direction: column; gap: 8px;">
        <div style="font-size: 12px; letter-spacing: 0.16em; color: #0f6b4f; font-weight: 600;">바꾸지 않아도 되는 것</div>
        <div style="font-size: 16px; line-height: 1.7;">지시문 7블록 구조<br>테스트 3종 방식<br>검수 기준 6항목<br>파일로 인계하는 방식<br>사람 승인 지점이 지시문에 있다는 것</div>
        <div style="font-size: 14px; color: #6b6660; line-height: 1.5; margin-top: auto;">오늘 골격 하나로 네 모듈을 만든 이유입니다. 내 업무도 다섯 번째 모듈일 뿐입니다.</div>
      </div>
    </div>""", "Z · 01")

def day(n, t, last=False):
    return f'<div style="{CARD} border-top: 3px solid {"#0f6b4f" if last else "#1c3f94"}; padding: 16px 16px; display: flex; flex-direction: column; gap: 8px; flex: 1 0 0;"><div style="font-size: 30px; font-weight: 700; color: {"#0f6b4f" if last else "#1c3f94"}; line-height: 1;">{n}</div><div style="font-size: 12px; color: #9a958d; font-weight: 600;">일차</div><div style="font-size: 16px; font-weight: 600; line-height: 1.4;">{t}</div></div>'
SLIDES["DeckZ3"] = shell("클로징", "7일 계획", "워크북 마지막 장 — 오늘 안에 첫 줄을 씁니다", f"""
    <div style="display: flex; gap: 10px; align-items: stretch; flex-grow: 1;">
      {day(1, "업무 1개 확정, 금지 범위 정하기 — CANNOT 7로")}
      {day(2, "가명화한 자료 준비 — 사내 가이드 확인")}
      {day(3, "지시문 7블록 작성 — 메모장에")}
      {day(4, "테스트 3종 실행 — 경계 · 실패까지")}
      {day(5, "동료 · 팀장 검토 — 검수 6항목")}
      {day(7, "v1 저장 + 다음 개선 1개 기록", True)}
    </div>
    <div style="{BAND}"><div style="font-size: 22px; font-weight: 700;">승인자 이름과 다음 개선 1개를 적으면 끝입니다.</div><div style="flex-grow: 1;"></div><div style="font-size: 14px; color: #c9c5bd;">6일이 비어 있는 건 검토 결과를 반영할 하루입니다.</div></div>""", "Z · 03")

# ───────────── D1 모듈 표지 (첫 모듈 타임바) — 어두운 표지는 골격이 다르다 ─────────────
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
