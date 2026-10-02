# -*- coding: utf-8 -*-
"""덱과 같은 데이터에서 참가자 워크북(A판·B판) · 강사 진행 가이드 · 슬라이드 노트를 만든다.
사용: python3 build_course_docs.py   (docs/samsung-ax 에서 실행하지 않아도 됨 — 경로는 파일 기준)"""
import os, re, sys, json, html as H
HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.abspath(os.path.join(HERE, ".."))
DESIGN = os.path.join(AX, "design"); MOD = os.path.join(AX, "context_pack", "modules")
sys.path.insert(0, os.path.join(DESIGN, "tools"))
import gen_handson  # noqa: E402  — 실습 슬라이드의 원본 데이터

# ───────── 강의 순서 (덱 순서) ─────────
ORDER = {
 "A판": ["Main","DeckO2","DeckO3","DeckO4","DeckO5","DeckO6","DeckO7","DeckO8",
         "DeckW1","Design6","DeckW3","DeckW4","DeckW5","Tags4","DeckW7","AgentSkill","DeckW9",
         "DeckM1","DeckM2","DeckM5","Blocks7","DeckM8",
         "DeckA1","DeckA2","DeckA3","DeckA4","DeckA5","DeckA6","DeckA7","DeckA8","HandsA1","HandsA2","DeckM4","Tests3","DeckM10","DeckM11","HandsA3","DeckA12",
         "DeckD1","DeckD2","DeckD3","DeckD4","DeckD5","DeckD6","DeckD7","DeckD8","HandsD1","DeckD10","HandsD2","DeckD12",
         "DeckM3","DeckM6",
         "DeckC1","DeckC2","DeckC3","DeckC4","DeckC5","DeckC6","DeckC7","DeckC8","HandsC1","DeckC10","HandsC2",
         "DeckK1","DeckK2","DeckK3","DeckK4","DeckK5","DeckK6","DeckZ1","DeckZ2","DeckZ3"],
}
ORDER["B판"] = [n.replace("DeckA","DeckB").replace("HandsA","HandsB") for n in ORDER["A판"]]
# 세션 시작 장 — 삼성 일정표의 세션 번호 그대로 (1-based 슬라이드 번호 → 세션 이름)
def _breaks(deck):
    names = ORDER[deck]; L = "A" if deck == "A판" else "B"
    first = {"Main": "세션0 · 오프닝", "Deck"+L+"1": ("세션1-1 · 직판 Sensing" if L == "A" else "세션1-2 · 경로 Sensing"),
             "DeckD1": "세션2-1 · 대시보드", "DeckD10": "세션2-2 · 데이터 분석 (같은 대화)", "DeckM3": "세션3 · 제안자료"}
    return {names.index(k) + 1: v for k, v in first.items()}
SESSION_BREAKS = {d: _breaks(d) for d in ORDER}

def strip(s):
    s = re.sub(r"<br\s*/?>", " ", s); s = re.sub(r"<[^>]+>", "", s); s = H.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def artboard_meta(name):
    s = open(os.path.join(DESIGN, name + ".dc.html"), encoding="utf-8").read()
    m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", s, re.S); title = strip(m.group(1)) if m else name
    lab = re.search(r'letter-spacing: 0\.(?:18|22)em;[^>]*>(.*?)</div>', s, re.S); label = strip(lab.group(1)) if lab else ""
    cap = re.search(r'<div style="font-size: 12px; color: #(?:6b6660|8fa4d8);">(.*?)</div>', s, re.S); caption = strip(cap.group(1)) if cap else ""
    bands = [strip(b) for b in re.findall(r'background: #111821; color: #fbfaf7;[^>]*>(.*?)</div>\s*</div>', s, re.S)]
    band = bands[0] if bands else ""
    return dict(name=name, title=title, label=label, caption=caption, band=band)

def notes_for(name, meta):
    """발표자 노트 — 슬라이드가 말하는 한두 줄 + 실습 장은 되묻기까지"""
    lines = []
    if meta["caption"]: lines.append(meta["caption"])
    if meta["band"]: lines.append(meta["band"])
    if name in gen_handson.SLIDES:
        s = gen_handson.SLIDES[name]
        lines.append("파일: " + " · ".join(s["files"]))
        lines.append("신호: " + " / ".join(strip(x) for x in s["signals"]))
        lines.append("되묻기: " + " / ".join(strip(x) for x in s["stuck"][:2]))
    return lines

# ───────── 슬라이드 색인 · 노트 ─────────
INDEX = {}; NOTES = {}
for deck, names in ORDER.items():
    INDEX[deck] = [dict(n=i+1, **artboard_meta(nm)) for i, nm in enumerate(names)]
    NOTES[deck] = {i+1: notes_for(nm, INDEX[deck][i]) for i, nm in enumerate(names)}
json.dump({d: {str(k): v for k, v in NOTES[d].items()} for d in NOTES}, open(os.path.join(AX, "deck", "notes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for deck in ORDER:
    with open(os.path.join(AX, "deck", f"{deck}_순서.txt"), "w", encoding="utf-8") as f:
        for it in INDEX[deck]:
            brk = SESSION_BREAKS[deck].get(it["n"]); 
            if brk: f.write(f"── {brk} ──\n")
            f.write(f'{it["n"]:02d} {it["name"]:12s} {it["label"]} · {it["title"]}\n')

def num(deck, name):
    for it in INDEX[deck]:
        if it["name"] == name: return it["n"]
    return None
def rng(deck, a, b): return f"{num(deck,a)}~{num(deck,b)}"

# ───────── 모듈 카드에서 검수 3항목 · 전환 질문 ─────────
def card(mod):
    s = open(os.path.join(MOD, mod, "모듈카드.md"), encoding="utf-8").read()
    rev = re.search(r"## 8\. 검수 5분\n(.*?)\n\n## 9", s, re.S); rev = re.sub(r"`[^`]*` 중 (?:특히 |이 모듈에서 특히 )?볼 것[.:]? ?", "", rev.group(1).strip()) if rev else ""
    q = re.search(r"내 업무로 전환 질문: \"(.*?)\"", s); q = q.group(1) if q else ""
    return rev, q
TEAM = {"A판": ("B2B팀", "A", "직판 Sensing", "A_sensing_b2b", "영업대시보드.html"), "B판": ("B2B유통전략팀", "B", "경로 Sensing", "B_sensing_partner", "권역보고서.docx")}

def hands_md(name, n):
    s = gen_handson.SLIDES[name]
    out = [f'## {s["label"].split("·", 1)[-1].strip()} — {strip(s["title"])} ({s["minutes"]}분) · 슬라이드 {n}', "",
           f'**{s["files_label"]}**', "```"] + s["files"] + ["```", "", "**할 일** — 끝나는 시각 `__ : __`", ""]
    for m, t, d in s["steps"]: out.append(f"- **{m}분 · {strip(t)}** — {strip(d)}")
    out += ["", "**이게 나오면 된 것**", ""]
    for x in s["signals"]: out.append(f"- [ ] {strip(x)}")
    out += ["", "**막혔을 때**", ""]
    for i, x in enumerate(s["stuck"]): out.append(f"{i+1}. {strip(x)}")
    out += ["", "> 문장은 화면에서 옮겨 적지 않습니다. `AX_실습파일` 폴더의 파일에서 복사합니다.", ""]
    return "\n".join(out)

CLOSING = open(os.path.join(AX, "workbook.md"), encoding="utf-8").read()
CLOSING = CLOSING[CLOSING.index("# 오늘 마무리 — 내 업무로 전환하기"):]
# 참조 파일 예시는 그 판에 실제로 배포되는 파일만 든다 (다른 팀 파일을 대면 참가자가 폴더에서 못 찾는다)
CLOSING = CLOSING.replace("| 팀 프로필 | team_profile.md | |", "| 참조 파일 (팀 것) | {REF_FILES} | |")
# 꼬리표는 덱과 같이 글자 라벨로 (이모지는 인쇄·확대에서 깨짐)
for _a, _b in [("> 꼬리표: 🔒 사람만 · ✍️ AI 초안 · ⚙️ AI 반복 · 🔌 밖에서 가져옴", "> 꼬리표 4종: [사람만] · [AI 초안] · [AI 반복] · [밖에서 가져옴] — 슬라이드의 선 아이콘과 같은 순서"),
               ("| 🔒 | ✍️ | ⚙️ | 🔌 |", "| 사람만 | AI 초안 | AI 반복 | 밖에서 |"), ("경계 (🔒)     : ____번", "경계 (사람만) : ____번"), ("입력 (🔌)     : ____번", "입력 (밖에서) : ____번"),
               ("| 꼬리표가 전부 ✍️ |", "| 꼬리표가 전부 [AI 초안] |"), ("| 🔒이 하나도 없음 |", "| [사람만]이 하나도 없음 |")]:
    assert _a in CLOSING, _a; CLOSING = CLOSING.replace(_a, _b)
CLOSING = CLOSING.replace("바꾸지 않아도 되는 것** — 지시문 7블록 구조, 테스트 3종 방식, 검수 기준, 파일로 인계하는 방식", "바꾸지 않아도 되는 것** — 지시문 7블록 구조, 테스트 3종 방식, 검수 기준 6항목, 파일로 인계하는 방식, 사람 승인 지점이 지시문에 있다는 것")

def workbook(deck):
    team, L, sensing, smod, sfile = TEAM[deck]
    D_rev, D_q = card("D_analysis"); S_rev, S_q = card(smod); C_rev, C_q = card("C_proposal")
    HS = "HandsA" if L == "A" else "HandsB"
    w = [f"# 참가자 실습 워크북 — {deck} ({team})", "",
         "이름 ______________  날짜 __________  옆자리 짝 ______________", "",
         "> 슬라이드 번호는 강의장 화면 우하단의 `n / 72`와 같습니다. 파일 이름은 화면에 뜬 철자 그대로 씁니다.", "", "---", "",
         "## 시작 전 확인 (3분)", "", "```",
         "□ 포털에서 ChatGPT / Gemini에 접속됐다",
         "□ 탭을 두 개 열었다 (① AI 창  ② 메모장)",
         "□ 오늘 쓸 폴더를 만들었다 → 바탕화면/AX실습_______________/",
         "□ AX_실습파일 폴더를 열었다 — 세션 폴더마다 프롬프트 · 데이터 · 실습지시문 (세션2는 한 대화에 프롬프트 2개 · 실습지시문 4개)",
         f"□ 업로드 테스트 — {'세션1_A_직판/2_데이터/대상고객사.xlsx' if L == 'A' else '세션1_B_유통영업/2_데이터/시장조사.md'} (작은 파일)를 먼저 올려 봤다",
         "□ 실제 업무 파일은 올리지 않는다 (실습 파일 폴더의 가상 데이터만)",
         "□ 지시문은 메모장에 먼저 — 세션이 끊기면 채팅창의 지시문은 사라진다", "```", "",
         "**업로드가 안 되면** — 손을 듭니다. 강사가 붙여넣기용 표를 나눠 주면 복사해 붙여넣습니다. 채팅창에 먼저 한 줄: \"아래는 첨부 자료입니다. 이 데이터로만 작업하세요.\"", "",
         "**결과를 저장하는 법** — AI 출력을 복사 → 메모장 → 파일 이름 정해 저장(HTML은 파일 형식 **모든 파일**) → 다음 모듈에 업로드. AI에게 \"파일로 만들어줘\"라고 하지 않습니다.", "",
         "**오늘 만드는 것** — 에이전트 셋, 파일 셋", "", "```",
         f"세션{'1-1' if L == 'A' else '1-2'}  {L} {sensing:8s} → {sfile}",
         f"세션2    D 대시보드 → 분석  → 대시보드.html · 리뷰 + 대상수요처.md (한 대화)",
         f"세션3    C 제안자료 작성    → 제안자료.html", "```", "",
         "세 세션이 **같은 고객 6곳**을 돕니다 — 세션1에서 기사로 본 회사의 매출을 세션2에서 보고(같은 대화에서 대시보드 → 분석), 거기서 고른 한 곳에 세션3에서 제안합니다. 실패 테스트용 함정 파일은 참가자 폴더에 없고 **강사가 시연**합니다.", "", "---", "",
         f"# 세션0 — 오프닝 · 일 보는 법 · 방법론 (슬라이드 {rng(deck,'Main','DeckM8')})", "",
         "실습 없이 듣는 시간입니다. 분해표 → 단계 → 에이전트가 나오는 순서(슬라이드 " + rng(deck,"DeckW1","DeckW9") + ")를 여기서 한 번 보고, 세 세션에서 세 번 반복합니다. 끝의 방법론 5장(슬라이드 " + rng(deck,"DeckM1","DeckM8") + ")은 왜 팀마다 따로 만들지 않는가부터 — 여기서 두 팀이 갈립니다.", "", "---", "",
         f"# 세션{'1-1' if L == 'A' else '1-2'} — 모듈 {L} {sensing} (슬라이드 {rng(deck,'Deck'+L+'1','Deck'+L+'12')})", "",
         f"**이 모듈의 함정 넷** (슬라이드 {num(deck,'Deck'+L+'6')}) — 결과에서 확인합니다.", "",
         hands_md(HS+"1", num(deck,HS+"1")), hands_md(HS+"2", num(deck,HS+"2")),
         "**실습 2와 3 사이 — 방법론 4장** (슬라이드 " + rng(deck,"DeckM4","DeckM11") + "): 51:49 · 테스트 3종 · 사람이 하는 일 · 완주 기준. 경계·실패를 왜 돌리는지 듣고 돌립니다.", "",
         hands_md(HS+"3", num(deck,HS+"3")),
         "## 검수 5분", "", S_rev, "", "검수 6항목 전체는 강사 자료 `common/review_criteria.md`. **1·3·4번은 안전 항목** — 하나라도 걸리면 결과물을 쓰지 않고 지시문을 고칩니다.", "",
         f"## 내 업무로 전환 (5분) · 슬라이드 {num(deck,'Deck'+L+'12')}", "", f"**{S_q}**", "", "_____________________________________________________________", "",
         "**가져갈 템플릿** — " + ("담당 고객사를 접근 시점 순으로 세운 목록이 필요하면 `common/instruction_templates/dashboard_customer.md`" if L == "A" else "담당 구역의 기회와 담당 배정을 한 장으로 보려면 `common/instruction_templates/dashboard_territory.md`") + "를 쓰십시오. 채워 본 예시가 같은 폴더에 있습니다.", "",
         "**스킬로 뗄 것 / 에이전트에 둘 것** — 누가 써도 같은 것은 스킬, 우리 팀 것은 에이전트. 슬라이드 " + str(num(deck,'Deck'+L+'12')) + "의 두 칸을 내 업무로 채워 봅니다.", "",
         "| 스킬로 뗄 것 (절차 · 양식 · 금지 · 검수) | 에이전트에 둘 것 (참조 파일 · 용어 · 주기) |", "|---|---|", "| | |", "", "---", "",
         f"# 세션2-1 — 대시보드 · 모듈 D 실습 1 (슬라이드 {rng(deck,'DeckD1','HandsD1')})", "",
         "세션1과 같은 이름이 나옵니다 — 수요처 6곳은 **1-1 직판의 담당 고객사**, 판매처 3곳(남해정보통신 · 동백시스템 · 가야네트웍스)은 **1-2 유통의 파트너사**입니다. 화면은 비개발자가 쓰도록 조건 칸 넷과 누르는 표만 둡니다.", "",
         "**이 모듈의 함정 셋** (슬라이드 " + str(num(deck,"DeckD6")) + ") — 결과에서 확인합니다: 9월은 24일까지라 8월 전체와 견주면 −40%로 보인다(같은 날짜까지 자르면 +2.8%) / 전년비 −46.9%의 116%가 미래로병원 한 곳 — 작년 일회성(기저효과) / 단가 열이 없어 검산식을 못 세운다", "",
         hands_md("HandsD1", num(deck,"HandsD1")),
         "---", "", f"# 세션2-2 — 데이터 분석 · 모듈 D 실습 2·3 (슬라이드 {rng(deck,'DeckD10','DeckD12')})", "",
         "**대시보드를 만든 대화를 닫지 않고 이어 갑니다.** `세션2-2_데이터분석/1_이어서_보낼_프롬프트.md`를 같은 대화에 메시지로 보냅니다 — 새 에이전트도, 파일 재업로드도 없습니다. 먼저 슬라이드 " + str(num(deck,"DeckD10")) + " — 화면은 '어디서'까지, 작년 쪽 큰 건을 보는 이유(기저효과).", "",
         hands_md("HandsD2", num(deck,"HandsD2")),
         "## 검수 5분", "", D_rev, "", "검수 6항목 전체는 강사 자료 `common/review_criteria.md`. **1·3·4번은 안전 항목** — 하나라도 걸리면 결과물을 쓰지 않고 지시문을 고칩니다.", "",
         f"## 내 업무로 전환 (5분) · 슬라이드 {num(deck,'DeckD12')}", "", f"**{D_q}**", "", "_____________________________________________________________", "",
         "**인계 (필수)**: 마지막 응답 맨 아래 인계본을 복사해 메모장에 `대상수요처.md`로 저장합니다. **세션3 C 모듈의 필수 입력**입니다. 견줄 예시는 `세션2-2_데이터분석/5_결과물_예시_대상수요처.md`.", "",
         "**가져갈 템플릿** — 내 팀 매출 파일로 같은 화면을 만들려면 `common/instruction_templates/dashboard_sales.md`를 쓰십시오. `{{ }}` 자리를 내 파일에 맞춰 채우면 됩니다. 채워 본 예시는 같은 폴더의 `dashboard_sales_예시.md`에 있습니다.", "", "---", "",
         f"# 세션3 — 모듈 C 제안자료 작성 (슬라이드 {rng(deck,'DeckM3','HandsC2')})", "",
         "앞 20분에 방법론 2장(슬라이드 " + rng(deck,"DeckM3","DeckM6") + ") — 일반 대화와 업무 에이전트의 차이 · IPO 명세 6칸. 세션2에서 저장한 `대상수요처.md`를 **반드시 같이 올립니다.** 저장을 못 했으면 그냥 시작합니다 — 에이전트가 올려 달라고 하고, 없다고 하면 몇 가지를 물어서 채웁니다.", "",
         f"**이 모듈의 함정 넷** (슬라이드 {num(deck,'DeckC8')}) · **절대 쓰면 안 되는 것** (슬라이드 {num(deck,'DeckC10')}) — 가격 · 납기 · 할인은 확정 문구 금지.", "",
         hands_md("HandsC1", num(deck,"HandsC1")), hands_md("HandsC2", num(deck,"HandsC2")),
         "## 검수 5분", "", C_rev, "",
         f"## 내 업무로 전환", "", f"**{C_q}**", "", "_____________________________________________________________", "",
         "**가져갈 템플릿** — 요구조건 대조표와 안 3개 비교를 한 장으로 만들려면 `common/instruction_templates/dashboard_proposal.md`를 쓰십시오. 채워 본 예시가 같은 폴더에 있습니다.", "", "---", "",
         f"# Skill과 MCP · 클로징 (슬라이드 {rng(deck,'DeckK1','DeckZ3')})", "",
         "오늘 만든 것에는 이름이 있습니다 — **Agent Skill** = 지시문 7블록 + 참조 파일 + 정답 예시. 각 세션의 `1_붙여넣을_프롬프트.md`를 스킬 형식으로 옮긴 `07_스킬/SKILL.md`(강사 자료)가 그 실물입니다. 스킬 기능이 열려 있으면 등록하고, 아니면 메모장 보관이 그대로 답입니다.", "", "---", "",
         CLOSING.replace("{REF_FILES}", "대상수요처.md · 대상고객사.xlsx" if deck == "A판" else "대상수요처.md · 파트너정보.xlsx")]
    return "\n".join(w)

# ───────── 강사 진행 가이드 ─────────
def stuck_lines(name):
    return [strip(x) for x in gen_handson.SLIDES[name]["stuck"][:2]]
def guide():
    v1 = open(os.path.join(AX, "instructor_guide.md"), encoding="utf-8").read()
    def sect(hdr_start, hdr_end):
        a = v1.index(hdr_start); b = v1.index(hdr_end) if hdr_end else len(v1); return re.sub(r"\n---\s*$", "", v1[a:b].rstrip()) + "\n"
    cache = os.path.join(HERE, ".instructor_guide_v1.md")
    if "(v2 · 72장 덱 기준)" in v1 or not v1.strip():  # 이미 v2면 v1 원문은 캐시에서
        v1 = open(cache, encoding="utf-8").read()
    elif "## 0. 진행 원칙" in v1:
        open(cache, "w", encoding="utf-8").write(v1)
    assert "## 0. 진행 원칙" in v1, "v1 원문을 찾지 못함 (instructor_guide.md 또는 tools/.instructor_guide_v1.md)"
    principles = sect("## 0. 진행 원칙", "## 1. 하루 운영표")
    principles = principles.replace("`handoff/` 정답 파일로", "각 모듈 `04_기준본/` 기준본으로").replace("IPO가 채워졌는지", "분해표와 파일이 준비됐는지")
    assist = sect("## 4. 보조강사 운영", "## 5. 진도 관리").replace("`handoff/` 안내", "`04_기준본/` 안내").replace("짝 시연 | 짝이 안 맞는 참가자 매칭", "실습 2 · 3 | 새 대화를 여는 것을 어려워하는 참가자 확인")
    situations = sect("## 6. 자주 나오는 상황 대응", "## 7. 모듈 종료 체크리스트").replace("`handoff/`", "`04_기준본/`").replace("`paste/`", "`06_붙여넣기/`").replace("④에서 숫자가 매번 다름", "D에서 합계가 매번 다름").replace("메모장에 보관한 `agent*_prompt.md`를 다시 붙여넣게 함. 안 만들어 뒀으면 지금 만들게 함", "메모장에 보관한 지시문을 다시 붙여넣게 함. 안 만들어 뒀으면 `02_지시문/`에서 다시 복사하게 함").replace("소계본(`*_소계.csv`)으로 교체", "소계본 + 호텔모델별 집계본 둘로 교체 (소계본만 올리면 추천이 안 나옵니다)")
    checklist = sect("## 7. 모듈 종료 체크리스트", None).replace("handoff 위치를 안다", "04_기준본 위치를 안다")
    def cue(deck):
        L = "A" if deck == "A판" else "B"; HS = "Hands" + L
        rows = [
          ("세션0 · 오프닝", [
            ("0~10", "오프닝", rng(deck,"Main","DeckO8"), "표지 · 4개 체인 · 흐름 · 준비 · 결과 남기기 · 에이전트 만드는 곳 · HTML · 지시문 메모장", "업로드 테스트 (작은 파일)"),
            ("10~40", "일 보는 법", rng(deck,"DeckW1","DeckW9"), "설계 6단계를 분해표로 실연. 틈(W5)과 묶기(W7)에서 멈춰 질문", "task_decomposition.md"),
            ("40~60", "방법론 5장", rng(deck,"DeckM1","DeckM8"), "M1에서 팀이 갈리는 이유 → 컨텍스트 → RACS · 7블록 → 나쁜 문장 vs 좋은 문장", "—")]),
          (f"세션{'1-1' if L == 'A' else '1-2'} · {L}", [
            ("0~20", "분해표 + 입력", rng(deck,"Deck"+L+"1","Deck"+L+"8"), "분해표 → 단계 셋 → 입력 → 팀 전용 2장 → 함정 → 도구", "모듈카드.md §1~5"),
            ("20~35", "시연", "—", "Gemini 에이전트 수동 빌드 + ChatGPT [예약] 3분" if L == "A" else "ChatGPT 에이전트 + 파일 4개, 첫 메시지에 권역", "05_시연로그.md"),
            ("35~65", "실습 1", str(num(deck,HS+"1")), "에이전트 만들기 + 실습지시문 1", "세션1 폴더 1_ · 2_ · 3_"),
            ("65~90", "실습 2", str(num(deck,HS+"2")), "단계 2 · 3 + 저장 (HTML)" if L == "A" else "단계 2 · 3 + 저장 (Word)", "web_environment.md 3 · 4장"),
            ("90~95", "방법론 4장", rng(deck,"DeckM4","DeckM11"), "51:49 → 테스트 3종 → 사람이 하는 일 → 완주 기준. 실습 3의 경계 · 실패를 예고", "—"),
            ("95~110", "실습 3", str(num(deck,HS+"3")), "경계는 참가자가 · 실패는 강사 시연 + 검수 3", "강사 묶음 03_테스트/"),
            ("110~115", "전환", str(num(deck,"Deck"+L+"12")), "스킬로 뗄 것 / 에이전트에 둘 것 두 칸", "workbook"),
            ("115~120", "버퍼", "—", "04_기준본/로 진입", "04_기준본/")]),
          ("세션2 · D (전반 대시보드 0~65 · 후반 데이터 분석 65~120 · 한 대화)", [
            ("0~20", "분해표 + 입력", rng(deck,"DeckD1","DeckD8"), "분해표 → 결과물 → 입력 16열 → 0번 숫자 확인 → 함정 셋 → 두 갈래 → 대조할 숫자", "모듈카드.md §1~5"),
            ("20~35", "시연", "—", "강사가 D 에이전트를 만들어 정상 테스트 한 번. 0번 확인이 먼저 나오고, 조건 칸 · 표의 줄 누르기를 보여 줌", "05_시연로그.md"),
            ("35~65", "실습 1", str(num(deck,"HandsD1")), "띄워 두고 순회. 기준본 대시보드.html과 1번 네 칸을 견주게", "세션2-1_대시보드/ 1_ ~ 5_"),
            ("65~70", "'어디서'까지만", str(num(deck,"DeckD10")), "작년 쪽 큰 건 4건 → 빼면 −1.9%. 리뷰에서 가설로. 대화를 닫지 말 것", "—"),
            ("70~110", "실습 2·3", str(num(deck,"HandsD2")), "같은 대화에 2-2의 1_ 프롬프트 → 3_ 리뷰 → 4_ 인계본 저장 · 실패는 강사 시연(강사 묶음의 매출데이터_함정.csv) · 검수 3", "세션2-2_데이터분석/"),
            ("110~115", "전환", str(num(deck,"DeckD12")), "내 매출 파일의 16개 열 — 워크북에 적게. 대상수요처.md 저장 확인 (세션3 필수 입력)", "workbook"),
            ("115~120", "버퍼", "—", "못 따라온 참가자는 04_기준본/대시보드.html을 열어 다음으로", "04_기준본/")]),
          ("세션3 · C", [
            ("0~20", "방법론 2장 + 분해표", rng(deck,"DeckM3","DeckC8"), "M3 · M6 → 분해표(90분 단계에 색) → 결과물 → 입력 → 밖의 데이터 → 어디서 무엇을 → 셋인 이유 → 함정", "모듈카드.md §1~5"),
            ("20~35", "시연", "—", "단계 ⓪ 정제(화면 복사 → 4열)를 실제 사이트 화면으로 3분, 이어서 단계 ①", "data_capture.md"),
            ("35~65", "실습 1", str(num(deck,"HandsC1")), "에이전트 만들기 + 대상수요처.md 포함 4개 올리기 + 단계 ① 대조표. 인계본 없는 참가자는 에이전트 질문에 답하게", "세션3 폴더 1_ ~ 3_ + 내 대상수요처.md"),
            ("65~70", "절대 쓰면 안 되는 것", str(num(deck,"DeckC10")), "확정 문구 금지 — 실습 2·3의 실패 테스트 예고", "—"),
            ("70~105", "실습 2·3", str(num(deck,"HandsC2")), "단계 ② 3안 → 저장 → 확정 견적 요구 → 검수 3", "지시문_2_제안.md"),
            ("105~120", "Skill + 클로징", rng(deck,"DeckK1","DeckZ3"), "이름이 있다 → SKILL.md → 5패턴 → CANNOT 7 → 다음 단계 → 옮기려면 → 다섯 원칙 → 7일", "07_스킬/SKILL.md · workbook 마무리")]),
        ]
        out = []
        for title, rs in rows:
            out += [f"### {title}", "", "| 분 | 구간 | 슬라이드 | 강사가 하는 것 | 파일 |", "|---|---|---|---|---|"]
            for r in rs: out.append("| " + " | ".join(r) + " |")
            out.append("")
        return "\n".join(out)
    def notes():
        out = []
        for mod, L, tests in [("A_sensing_b2b","A",["HandsA1","HandsA2","HandsA3"]), ("B_sensing_partner","B",["HandsB1","HandsB2","HandsB3"]), ("D_analysis","D",["HandsD1","HandsD2"]), ("C_proposal","C",["HandsC1","HandsC2"])]:
            rev, q = card(mod)
            out += [f"### 모듈 {L}", "", "**되묻기 — 답을 주지 않습니다**", ""]
            for t in tests:
                s = gen_handson.SLIDES[t]
                for line in stuck_lines(t): out.append(f"- ({s['label'].split('·', 1)[-1].strip()}) {line}")
            out += ["", f"**검수 5분에서 볼 것** — {rev}", "", f"**전환 질문** — {q}", "",
                    f"자세한 되묻기와 부분 통과 판정은 `modules/{mod}/03_테스트/테스트_*.md`의 \"안 되면\" · \"부분 통과와 실패\" 표.", ""]
        return "\n".join(out)
    g = ["# 강사용 진행 가이드 (v2 · 72장 덱 기준)", "",
         "> 대상: 사내강사(양성 후보 17명) 및 보조강사 · 범위: 강사 담당 6시간 · 덱은 `deck/A판.html` · `B판.html` (슬라이드 번호는 그 화면의 `n / 72`)",
         "> ①「AI Agent와 정보보안의 이해」와 ⑤「결과 발표 및 공유」는 삼성 자체 운영입니다.", "", "---", "",
         principles, "---", "",
         "## 1. 하루 운영표 — 수업 순서는 삼성 일정표의 세션 번호 그대로", "",
         "| 세션 | 모듈 | 누가 | 실습 | 산출물 |", "|---|---|---|---|---|",
         "| 0 | 오프닝 · 일 보는 법 · 방법론 5장 | 전원 | — | — |",
         "| 1-1 / 1-2 | A 직판 Sensing / B 경로 Sensing — 방법론 4장이 실습 2와 3 사이에 | B2B팀은 A · 유통전략팀은 B | 70분 | `영업대시보드.html` / `권역보고서.docx` |",
         "| 2 | D 대시보드 → 데이터 분석 — 세션1의 고객 6곳 매출, **한 대화로 이어서** · 실패는 강사 시연 | 전원 | 30분 + 40분 | `대시보드.html` · `리뷰.md` · `대상수요처.md` |",
         "| 3 | C 제안자료 작성 — 방법론 2장이 앞에, Skill · 클로징이 뒤에 | 전원 | 70분 | `제안자료.html` |", "",
         "한 고객이 세 세션을 이어서 돕니다 — **세션1**(A 직판) 기사로 보면 1순위 미래로병원 신관(2027-03 준공 → 접근 지금) · 2순위 한울종합건설 · 해솔호텔 리뉴얼(4개월 뒤) · 3순위 대성건설 / **세션1-2**(B 유통) 해운대 1순위 마린그랜드 · 2순위 해솔호텔, 파트너 남해정보통신 → **세션2-1** 월말 대시보드에서 \"매출이 왜 빠졌어?\" — 미래로병원이 눈에 띄게 빠짐 → **세션2-2**(같은 대화) 기저효과(작년 노트북 일괄 교체)를 빼도 −65%이고 파트너 동백시스템 경로도 −30.9%, 해솔호텔은 +36.3%로 순항 → 기사로는 1순위 기회인데 매출은 급감하는 미래로병원을 골라 `대상수요처.md`로 저장 → **세션3** 마침 들어온 미래로병원 신관 회의공간 요구조건으로 제안 — PC에서 빠진 매출을 디스플레이로 만회. **함정 · 실패 테스트 파일은 참가자 묶음에서 빼고 강사 묶음에만 둡니다** — 실습 3의 실패 테스트는 강사가 화면으로 시연합니다.", "",
         "**시작 전 5분 (세션0 앞)** — 배포 폴더를 열었는지 · 탭 두 개(AI 창 + 메모장) · 저장 폴더 · **업로드 테스트는 첫 모듈의 작은 파일로**(A판 `대상고객사.xlsx` · B판 `시장조사.md`) · 실제 업무 파일 금지 · 지시문은 메모장에 먼저. 안 되는 참가자는 전원 `06_붙여넣기/` 경로로.", "",
         "**세션0 길이**는 지금 60분으로 잡았습니다. 삼성 일정표가 확정되면 큐시트의 세션0 칸만 고칩니다.", "", "---", "",
         "## 2. 세션별 큐시트 — A판 (B2B팀)", "", cue("A판"), "## 2b. 세션별 큐시트 — B판 (유통전략팀) — 세션1만 다릅니다", "", "### 세션1-2 · B\n\n" + cue("B판").split("### 세션1-2 · B\n\n")[1].split("### 세션2")[0], "---", "",
         "## 3. 모듈별 진행 노트", "", notes(), "---", "",
         assist, "---", "",
         "## 5. 진도 관리", "",
         "| 라인 | 조건 | 못 넘겼을 때 |", "|---|---|---|",
         "| 최소 완주 | 에이전트 하나 + 정상 테스트 1건이 기준본과 같음 + 결과 파일 저장 | 다음 모듈은 `04_기준본/` 기준본으로 시작 |",
         "| 확장 | 경계 · 실패까지 셋 통과 + 고친 문장을 반영한 v1 + 전환 표 | — |", "",
         "모듈 종료 10분 전에 **손을 들게 해서 최소 완주 인원을 셉니다.** 절반이 안 되면 전환을 5분으로 줄이고 실습에 시간을 더 줍니다.", "", "---", "",
         situations, "---", "", checklist]
    return "\n".join(g)

if __name__ == "__main__":
    for deck in ORDER:
        open(os.path.join(AX, f"workbook_{deck}.md"), "w", encoding="utf-8").write(workbook(deck)); print("workbook", deck)
    text = guide()  # 먼저 읽고 나서 쓴다 (open("w")가 먼저 평가되면 원문이 지워짐)
    open(os.path.join(AX, "instructor_guide.md"), "w", encoding="utf-8").write(text); print("instructor_guide v2")
    print("notes.json", sum(len(v) for v in NOTES.values()), "slides")
