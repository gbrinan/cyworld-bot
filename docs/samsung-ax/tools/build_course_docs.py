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
         "DeckD1","DeckD2","DeckD3","DeckD4","DeckD5","DeckD6","DeckD7","DeckD8","HandsD1","DeckD10","DeckM4","Tests3","DeckM10","DeckM11","HandsD2","DeckD12",
         "DeckM1","DeckM2","DeckM5","Blocks7","DeckM8",
         "DeckA1","DeckA2","DeckA3","DeckA4","DeckA5","DeckA6","DeckA7","DeckA8","HandsA1","HandsA2","HandsA3","DeckA12",
         "DeckM3","DeckM6",
         "DeckC1","DeckC2","DeckC3","DeckC4","DeckC5","DeckC6","DeckC7","DeckC8","HandsC1","DeckC10","HandsC2",
         "DeckK1","DeckK2","DeckK3","DeckK4","DeckK5","DeckK6","DeckZ1","DeckZ2","DeckZ3"],
}
ORDER["B판"] = [n.replace("DeckA","DeckB").replace("HandsA","HandsB") for n in ORDER["A판"]]
SESSION_BREAKS = {"A판": {34: "2교시", 52: "3교시"}, "B판": {34: "2교시", 52: "3교시"}}  # 1-based slide index where a session starts

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
            if it["n"] == 1: f.write("── 1교시 ──\n")
            if brk: f.write(f"── {brk} ──\n")
            f.write(f'{it["n"]:02d} {it["name"]:12s} {it["label"]} · {it["title"]}\n')

def num(deck, name):
    for it in INDEX[deck]:
        if it["name"] == name: return it["n"]
    return None
def rng(deck, a, b): return f"{num(deck,a)}~{num(deck,b)}"

# ───────── 모듈 카드에서 검수 3항목 · 전환 질문 ─────────
def card(mod):
    s = open(os.path.join(MOD, mod, "module.md"), encoding="utf-8").read()
    rev = re.search(r"## 8\. 검수 5분\n(.*?)\n\n## 9", s, re.S); rev = re.sub(r"`[^`]*` 중 (?:특히 |이 모듈에서 특히 )?볼 것[.:]? ?", "", rev.group(1).strip()) if rev else ""
    q = re.search(r"내 업무로 전환 질문: \"(.*?)\"", s); q = q.group(1) if q else ""
    return rev, q
TEAM = {"A판": ("B2B팀", "A", "직판 Sensing", "A_sensing_b2b", "dashboard_A.html"), "B판": ("B2B유통전략팀", "B", "경로 Sensing", "B_sensing_partner", "report_B.docx")}

def hands_md(name, n):
    s = gen_handson.SLIDES[name]
    out = [f'## {s["label"].split("·", 1)[-1].strip()} — {strip(s["title"])} ({s["minutes"]}분) · 슬라이드 {n}', "",
           f'**{s["files_label"]}**', "```"] + s["files"] + ["```", "", "**할 일** — 끝나는 시각 `__ : __`", ""]
    for m, t, d in s["steps"]: out.append(f"- **{m}분 · {strip(t)}** — {strip(d)}")
    out += ["", "**이게 나오면 된 것**", ""]
    for x in s["signals"]: out.append(f"- [ ] {strip(x)}")
    out += ["", "**막혔을 때**", ""]
    for i, x in enumerate(s["stuck"]): out.append(f"{i+1}. {strip(x)}")
    out += ["", "> 지시문은 화면에서 옮겨 적지 않습니다. 배포 폴더의 파일에서 복사합니다.", ""]
    return "\n".join(out)

CLOSING = open(os.path.join(AX, "workbook.md"), encoding="utf-8").read()
CLOSING = CLOSING[CLOSING.index("# 오늘 마무리 — 내 업무로 전환하기"):]
CLOSING = CLOSING.replace("| 팀 프로필 | team_profile.md | |", "| 참조 파일 (팀 것) | target_account.md · target_builders.csv · partner_info.csv | |")
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
         "□ 배포 폴더의 modules/D_analysis/ 를 열었다",
         "□ 업로드 테스트 — target_account.md (1KB)를 먼저 올려 봤다",
         "□ 실제 업무 파일은 올리지 않는다 (배포 폴더의 가상 데이터만)",
         "□ 지시문은 메모장에 먼저 — 세션이 끊기면 채팅창의 지시문은 사라진다", "```", "",
         "**업로드가 안 되면** — `06_paste/`의 마크다운 표를 복사해 붙여넣습니다. 채팅창에 먼저 한 줄: \"아래는 첨부 자료입니다. 이 데이터로만 작업하세요.\"", "",
         "**결과를 저장하는 법** — AI 출력을 복사 → 메모장 → 파일 이름 정해 저장(HTML은 파일 형식 **모든 파일**) → 다음 모듈에 업로드. AI에게 \"파일로 만들어줘\"라고 하지 않습니다.", "",
         "**오늘 만드는 것** — 에이전트 셋, 파일 셋", "", "```",
         f"1교시  D 데이터 분석      → recommend_D.html",
         f"2교시  {L} {sensing:8s} → {sfile}",
         f"3교시  C 제안자료 작성    → proposal_C.html", "```", "", "---", "",
         f"# 1교시 — 모듈 D 데이터 분석 (슬라이드 {rng(deck,'DeckD1','DeckD12')})", "",
         "첫 모듈이라 앞 40분은 **일을 보는 법**(슬라이드 " + rng(deck,"DeckW1","DeckW9") + ")입니다. 분해표 → 단계 → 에이전트가 나오는 순서를 여기서 한 번 보고, 세 모듈에서 세 번 반복합니다.", "",
         "**이 모듈의 함정 셋** (슬라이드 " + str(num(deck,"DeckD6")) + ") — 결과에서 확인합니다: 호텔이 금액의 3분의 2 / 금액 순으로는 안 보이는 것 / 신규지만 같은 체인의 다른 지점", "",
         hands_md("HandsD1", num(deck,"HandsD1")),
         "**실습 1과 2·3 사이 — 방법론 4장** (슬라이드 " + rng(deck,"DeckM4","DeckM11") + "): 51:49 · 테스트 3종 · 사람이 하는 일 · 완주 기준. 경계·실패를 왜 돌리는지 듣고 돌립니다.", "",
         hands_md("HandsD2", num(deck,"HandsD2")),
         "## 검수 5분", "", D_rev, "", "검수 6항목 전체는 배포 폴더 `common/review_criteria.md`. **1·3·4번은 안전 항목** — 하나라도 걸리면 결과물을 쓰지 않고 지시문을 고칩니다.", "",
         f"## 내 업무로 전환 (5분) · 슬라이드 {num(deck,'DeckD12')}", "", f"**{D_q}**", "", "_____________________________________________________________", "",
         "인계(선택): TOP 3를 `recommended_models.csv`로 저장해 두면 C 모듈의 후보 힌트로 쓸 수 있습니다.", "", "---", "",
         f"# 2교시 — 모듈 {L} {sensing} (슬라이드 {rng(deck,'Deck'+L+'1','Deck'+L+'12')})", "",
         "앞 20분에 방법론 5장(슬라이드 " + rng(deck,"DeckM1","DeckM8") + ") — 왜 팀마다 따로 만들지 않는가부터. 여기서 두 팀이 갈립니다.", "",
         f"**이 모듈의 함정 넷** (슬라이드 {num(deck,'Deck'+L+'6')}) — 결과에서 확인합니다.", "",
         hands_md(HS+"1", num(deck,HS+"1")), hands_md(HS+"2", num(deck,HS+"2")), hands_md(HS+"3", num(deck,HS+"3")),
         "## 검수 5분", "", S_rev, "",
         f"## 내 업무로 전환 (10분) · 슬라이드 {num(deck,'Deck'+L+'12')}", "", f"**{S_q}**", "", "_____________________________________________________________", "",
         "**스킬로 뗄 것 / 에이전트에 둘 것** — 누가 써도 같은 것은 스킬, 우리 팀 것은 에이전트. 슬라이드 " + str(num(deck,'Deck'+L+'12')) + "의 두 칸을 내 업무로 채워 봅니다.", "",
         "| 스킬로 뗄 것 (절차 · 양식 · 금지 · 검수) | 에이전트에 둘 것 (참조 파일 · 용어 · 주기) |", "|---|---|", "| | |", "", "---", "",
         f"# 3교시 — 모듈 C 제안자료 작성 (슬라이드 {rng(deck,'DeckC1','HandsC2')})", "",
         "앞 20분에 방법론 2장(슬라이드 " + rng(deck,"DeckM3","DeckM6") + ") — 일반 대화와 업무 에이전트의 차이 · IPO 명세 6칸.", "",
         f"**이 모듈의 함정 넷** (슬라이드 {num(deck,'DeckC8')}) · **절대 쓰면 안 되는 것** (슬라이드 {num(deck,'DeckC10')}) — 가격 · 납기 · 할인은 확정 문구 금지.", "",
         hands_md("HandsC1", num(deck,"HandsC1")), hands_md("HandsC2", num(deck,"HandsC2")),
         "## 검수 5분", "", C_rev, "",
         f"## 내 업무로 전환", "", f"**{C_q}**", "", "_____________________________________________________________", "", "---", "",
         f"# Skill과 MCP · 클로징 (슬라이드 {rng(deck,'DeckK1','DeckZ3')})", "",
         "오늘 만든 것에는 이름이 있습니다 — **Agent Skill** = 지시문 7블록 + 참조 파일 + 정답 예시. 각 모듈 배포 폴더의 `07_skill/SKILL.md`가 그 실물입니다. 스킬 기능이 열려 있으면 등록하고, 아니면 메모장 보관이 그대로 답입니다.", "", "---", "",
         CLOSING]
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
    principles = principles.replace("`handoff/` 정답 파일로", "각 모듈 `04_answer/` 기준본으로").replace("IPO가 채워졌는지", "분해표와 파일이 준비됐는지")
    assist = sect("## 4. 보조강사 운영", "## 5. 진도 관리").replace("`handoff/` 안내", "`04_answer/` 안내").replace("짝 시연 | 짝이 안 맞는 참가자 매칭", "실습 2 · 3 | 새 대화를 여는 것을 어려워하는 참가자 확인")
    situations = sect("## 6. 자주 나오는 상황 대응", "## 7. 모듈 종료 체크리스트").replace("`handoff/`", "`04_answer/`").replace("`paste/`", "`06_paste/`").replace("④에서 숫자가 매번 다름", "D에서 합계가 매번 다름").replace("소계본(`*_소계.csv`)으로 교체", "소계본 + 호텔모델별 집계본 둘로 교체 (소계본만 올리면 추천이 안 나옵니다)")
    checklist = sect("## 7. 모듈 종료 체크리스트", None).replace("handoff 위치를 안다", "04_answer 위치를 안다")
    def cue(deck):
        L = "A" if deck == "A판" else "B"; HS = "Hands" + L
        rows = [
          ("1교시 · D", [
            ("0~10", "오프닝", rng(deck,"Main","DeckO8"), "표지 · 4개 체인 · 타임라인 · 준비 · 결과 남기기 · 에이전트 만드는 곳 · HTML · 지시문 메모장", "업로드 테스트 target_account.md"),
            ("10~40", "일 보는 법 + D 분해표", rng(deck,"DeckW1","DeckD8"), "설계 6단계를 D 분해표로 실연. 틈(W5)과 묶기(W7)에서 멈춰 질문", "module.md §1"),
            ("40~50", "시연", "—", "강사가 D 에이전트를 만들어 정상 테스트 한 번. 0번 점검이 먼저 나오는 화면을 보여 줌", "05_demo_log.md"),
            ("50~75", "실습 1", str(num(deck,"HandsD1")), "띄워 두고 순회. 종료 시각을 칸에 적음", "01_data/ · 02_prompt/prompt_1.md"),
            ("75~85", "방법론 4장", rng(deck,"DeckD10","DeckM11"), "근거 붙은 추천 → 51:49 → 테스트 3종 → 사람이 하는 일 → 완주 기준", "—"),
            ("85~110", "실습 2·3", str(num(deck,"HandsD2")), "경계(파일 하나) · 실패(03_tests/sales_history_실패.csv) · 검수 3", "03_tests/"),
            ("110~115", "전환", str(num(deck,"DeckD12")), "내 실적 파일의 10개 컬럼 — 워크북에 적게", "workbook"),
            ("115~120", "버퍼", "—", "못 따라온 참가자는 04_answer/recommend_D.html을 열어 다음으로", "04_answer/")]),
          (f"2교시 · {L}", [
            ("0~20", "방법론 5장 + 분해표", rng(deck,"DeckM1","Deck"+L+"8"), "M1에서 팀이 갈리는 이유 → 분해표 → 단계 셋 → 입력 → 팀 전용 2장 → 함정 → 도구", "module.md §1~5"),
            ("20~35", "시연", "—", "Gemini 에이전트 수동 빌드 + ChatGPT [예약] 3분" if L == "A" else "ChatGPT 에이전트 + 파일 4개, 첫 메시지에 권역", "05_demo_log.md"),
            ("35~65", "실습 1", str(num(deck,HS+"1")), "에이전트 만들기 + 첫 응답", "01_data/ · 02_prompt/"),
            ("65~90", "실습 2", str(num(deck,HS+"2")), "단계 2 · 3 + 저장 (HTML)" if L == "A" else "단계 2 · 3 + 저장 (Word)", "web_environment.md 3 · 4장"),
            ("90~105", "실습 3", str(num(deck,HS+"3")), "경계 · 실패 + 검수 3", "03_tests/"),
            ("105~115", "전환", str(num(deck,"Deck"+L+"12")), "스킬로 뗄 것 / 에이전트에 둘 것 두 칸", "workbook"),
            ("115~120", "버퍼", "—", "04_answer/로 진입", "04_answer/")]),
          ("3교시 · C", [
            ("0~20", "방법론 2장 + 분해표", rng(deck,"DeckM3","DeckC8"), "M3 · M6 → 분해표(90분 단계에 색) → 결과물 → 입력 → 밖의 데이터 → 어디서 무엇을 → 셋인 이유 → 함정", "module.md §1~5"),
            ("20~35", "시연", "—", "단계 ⓪ 정제(화면 복사 → 4열)를 실제 사이트 화면으로 3분, 이어서 단계 ①", "data_capture.md"),
            ("35~65", "실습 1", str(num(deck,"HandsC1")), "에이전트 만들기 + 단계 ① 대조표", "01_data/ · prompt_1_추출.md"),
            ("65~70", "절대 쓰면 안 되는 것", str(num(deck,"DeckC10")), "확정 문구 금지 — 실습 2·3의 실패 테스트 예고", "—"),
            ("70~105", "실습 2·3", str(num(deck,"HandsC2")), "단계 ② 3안 → 저장 → 확정 견적 요구 → 검수 3", "prompt_2_제안.md"),
            ("105~120", "Skill + 클로징", rng(deck,"DeckK1","DeckZ3"), "이름이 있다 → SKILL.md → 5패턴 → CANNOT 7 → 다음 단계 → 옮기려면 → 다섯 원칙 → 7일", "07_skill/SKILL.md · workbook 마무리")]),
        ]
        out = []
        for title, rs in rows:
            out += [f"### {title}", "", "| 분 | 구간 | 슬라이드 | 강사가 하는 것 | 파일 |", "|---|---|---|---|---|"]
            for r in rs: out.append("| " + " | ".join(r) + " |")
            out.append("")
        return "\n".join(out)
    def notes():
        out = []
        for mod, L, tests in [("D_analysis","D",["HandsD1","HandsD2"]), ("A_sensing_b2b","A",["HandsA1","HandsA2","HandsA3"]), ("B_sensing_partner","B",["HandsB1","HandsB2","HandsB3"]), ("C_proposal","C",["HandsC1","HandsC2"])]:
            rev, q = card(mod)
            out += [f"### 모듈 {L}", "", "**되묻기 — 답을 주지 않습니다**", ""]
            for t in tests:
                s = gen_handson.SLIDES[t]
                for line in stuck_lines(t): out.append(f"- ({s['label'].split('·', 1)[-1].strip()}) {line}")
            out += ["", f"**검수 5분에서 볼 것** — {rev}", "", f"**전환 질문** — {q}", "",
                    f"자세한 되묻기와 부분 통과 판정은 `modules/{mod}/03_tests/test_*.md`의 \"안 되면\" · \"부분 통과와 실패\" 표.", ""]
        return "\n".join(out)
    g = ["# 강사용 진행 가이드 (v2 · 72장 덱 기준)", "",
         "> 대상: 사내강사(양성 후보 17명) 및 보조강사 · 범위: 강사 담당 6시간 · 덱은 `deck/A판.html` · `B판.html` (슬라이드 번호는 그 화면의 `n / 72`)",
         "> ①「AI Agent와 정보보안의 이해」와 ⑤「결과 발표 및 공유」는 삼성 자체 운영입니다.", "", "---", "",
         principles, "---", "",
         "## 1. 하루 운영표 — 수업 순서는 D → A 또는 B → C", "",
         "| 교시 | 모듈 | 누가 | 실습 | 산출물 |", "|---|---|---|---|---|",
         "| 1 | D 데이터 분석 — **첫 모듈.** 오프닝 · 일 보는 법 · 방법론 4장이 이 안에 | 전원 | 50분 | `recommend_D.html` |",
         "| 2 | A 직판 Sensing / B 경로 Sensing — 방법론 5장이 앞에 | B2B팀은 A · 유통전략팀은 B | 70분 | `dashboard_A.html` / `report_B.docx` |",
         "| 3 | C 제안자료 작성 — 방법론 2장이 앞에, Skill · 클로징이 뒤에 | 전원 | 70분 | `proposal_C.html` |", "",
         "삼성 양식 번호 ②③④는 수업 순서가 아닙니다. 정본은 `slides_outline.md`의 6시간 배치표.", "",
         "**시작 전 5분 (1교시 앞)** — 배포 폴더를 열었는지 · 탭 두 개(AI 창 + 메모장) · 저장 폴더 · **업로드 테스트는 `target_account.md`(1KB)로** · 실제 업무 파일 금지 · 지시문은 메모장에 먼저. 안 되는 참가자는 전원 `06_paste/` 경로로.", "",
         "**삼성이 오프닝 10분을 자기 시간으로 받아 주면** D 실습 1을 35분으로 늘립니다. 그 확인 전까지는 아래 큐시트가 기준입니다.", "", "---", "",
         "## 2. 교시별 큐시트 — A판 (B2B팀)", "", cue("A판"), "## 2b. 교시별 큐시트 — B판 (유통전략팀) — 2교시만 다릅니다", "", "### 2교시 · B\n\n" + cue("B판").split("### 2교시 · B\n\n")[1].split("### 3교시")[0], "---", "",
         "## 3. 모듈별 진행 노트", "", notes(), "---", "",
         assist, "---", "",
         "## 5. 진도 관리", "",
         "| 라인 | 조건 | 못 넘겼을 때 |", "|---|---|---|",
         "| 최소 완주 | 에이전트 하나 + 정상 테스트 1건이 기준본과 같음 + 결과 파일 저장 | 다음 모듈은 `04_answer/` 기준본으로 시작 |",
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
