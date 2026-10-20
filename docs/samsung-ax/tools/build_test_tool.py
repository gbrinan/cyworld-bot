# -*- coding: utf-8 -*-
"""실습 검수 도구 — HTML 한 파일에 지침 · 실습프롬프트 · 데이터 · 기대값을 모두 넣는다.
단계마다: 복사 → GPT에서 실행 → 응답 붙여넣기 → 기대 숫자 자동 대조 → 판정 → 보고서 내보내기.
먼저 tools/build_pack.py 로 dist/AX_실습파일 을 만든 뒤 실행한다."""
import os, json, base64, html
AX = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(AX, "dist", "AX_실습파일")
OUT = os.path.join(AX, "dist", "AX_실습검수도구.html")
def rd(rel): return open(os.path.join(P, rel), encoding="utf-8").read()
def b64(rel): return base64.b64encode(open(os.path.join(P, rel), "rb").read()).decode()
MIME = {".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".md": "text/markdown", ".json": "application/json", ".html": "text/html"}
files = {}
for root, _, fs in os.walk(P):
    for f in fs:
        rel = os.path.relpath(os.path.join(root, f), P)
        files[rel] = {"mime": MIME.get(os.path.splitext(f)[1], "application/octet-stream"), "b64": b64(rel)}
        if f.endswith(".md"): files[rel]["text"] = rd(rel)

S, D, A, C = "2. 시장Sensing", "3-1. 대시보드", "3-2. 데이터 분석", "4. 제안자료"
# (단계 제목, 어디서, [(종류, 파일)], 기대 결과, 자동 확인 숫자/문구, 수동만?)
#   종류: 지침 = 에이전트 지침란 · 첨부 = 대화창에 첨부 · 보내기 = 메시지로 보내기
STEPS = [
 ("시장Sensing — 수집 요약", "새 에이전트", [("지침", f"{S}/2_뉴스분석 Agent_지침.md"), ("첨부", f"{S}/기사수집.xlsx"), ("첨부", f"{S}/대상고객사.xlsx"), ("보내기", f"{S}/3_뉴스분석 Agent_실습프롬프트1.md")],
  "원본 30 → 중복 3 제외 → 27건, 무관 14건", ["30", "27", "14"], False),
 ("시장Sensing — 우선순위", "같은 대화", [("보내기", f"{S}/4_뉴스분석 Agent_실습프롬프트2.md")],
  "1순위 미래로병원 신관(2027-03 → 접근 2026-09 지금) · 2순위 한울·해솔(2027-07) · 3순위 대성(2028-06) · 서진리테일 보류", ["미래로병원", "2026-09", "2027-07", "2028-06", "보류"], False),
 ("용어 — 회사명 추상화", "앞 응답 전체", [], "응답에 '경쟁사' · LG · 애플 · 로보락이 없고 '타사' · X사 · A사 · R사로 쓴다", ["!경쟁사", "!LG", "!애플", "!로보락"], False),
 ("3-1 첫 응답 — 설정 확인", "새 에이전트", [("지침", f"{D}/2_대시보드 Agent_지침.md"), ("첨부", f"{D}/매출데이터.xlsx"), ("첨부", f"{D}/매출데이터_소계.xlsx"), ("보내기", f"{D}/2_대시보드 Agent_실습프롬프트.md")],
  "대시보드를 만들지 않고 0번 점검(1,093행 · 8,623,580,000원 · 5축 일치) + 시뮬레이션 설정 표 10항목(가격보상 · 탄력성 · 공헌이익 등) + '이 샘플값으로 만들까요?'", ["1,093", "8,623,580,000", "가격보상", "탄력성", "공헌이익", "만들까요"], False),
 ("3-1 대시보드 생성", "같은 대화", [("보내기", f"{D}/3_대시보드 Agent_설정확인_실습프롬프트.md")],
  "1번: 9월 1~24일 267백만 · 지난달 같은 날짜 +2.8% · 작년 같은 달 −46.9%", ["267", "2.8%", "46.9%"], False),
 ("대시보드 7번 목표 대비", "생성된 HTML", [],
  "누계 목표 4,287.7백만 · 실적 3,780.6백만 · 달성률 88.2%, 유통 → 품목 → 모델 순, '샘플값(가정)'", ["4,287", "3,780", "88.2%", "가정"], False),
 ("대시보드 8번 시뮬레이션", "생성된 HTML", [],
  "기준 204,100,000 · 증분 24,492,000 · 가격보상 비용 11,429,600 · 판촉비 6,857,760 · 공헌이익 −13,878,800 · 손익분기 없음", ["204,100,000", "24,492,000", "11,429,600", "6,857,760", "13,878,800"], False),
 ("8번 슬라이더 10%", "브라우저에서 조작", [], "증분 39,799,500 · 공헌이익 −24,543,025 로 바뀜", ["39,799,500", "24,543,025"], True),
 ("'가정' 표시", "생성된 HTML", [], "목표 · 시뮬레이션 값 옆에 '가정'과 '어떻게 정했나'", ["가정", "어떻게"], True),
 ("현황파악 1 — 구간 비교", "같은 대화", [("보내기", f"{D}/4_대시보드 Agent_현황파악1_구간비교_실습프롬프트.md")],
  "8월 전체 445 → 267 −40.0% · 8월 1~24일 260 → 267 +2.8% · 작년 9월 1~24일 503 → 267 −46.9%", ["445", "260", "503", "40.0%", "46.9%"], False),
 ("현황파악 2 — 매출 증감", "같은 대화", [("보내기", f"{D}/5_대시보드 Agent_현황파악2_매출증감_실습프롬프트.md")],
  "감소 1위 미래로병원 −274,970,000원(−275백만), 작년 큰 거래에 노트북 일괄 교체 4건", ["미래로병원", "275", "노트북"], False),
 ("현황파악 3 — 늘어난 곳", "같은 대화", [("보내기", f"{D}/6_대시보드 Agent_현황파악3_주요항목_실습프롬프트.md")],
  "늘어난 수요처 해솔호텔 · 대성건설 · 한울종합건설", ["해솔호텔", "대성건설", "한울종합건설"], False),
 ("3-2 가설 검증 보고서", "새 에이전트", [("지침", f"{A}/2_데이터 분석 Agent_지침.md"), ("첨부", f"{D}/매출데이터.xlsx"), ("첨부", f"{D}/매출데이터_소계.xlsx"), ("보내기", f"{A}/3_데이터 분석 Agent_가설확인과분석보고서_실습프롬프트.md")],
  "가설 1 맞음 · 2 부분 · 3 틀림(일회성 빼도 −65.2%, 최근 석 달 −50.7%), 요약 3,615 → 3,781 (+4.6%)", ["맞음", "부분", "틀림", "65", "50.7", "3,615", "3,781"], False),
 ("「가정한 값」 표", "보고서", [], "목표 · 시뮬레이션 값을 썼다면 '가정' 표시와 무엇을 · 어떻게 · 왜 · 바뀌면", ["가정"], True),
 ("인계본 저장", "보고서 맨 아래", [], "미래로병원 (1000425) — 메모장에 대상수요처.md로 저장", ["미래로병원", "1000425"], False),
 ("대시보드 고치기와 공지", "3-1 대시보드 대화로 돌아가서", [("보내기", f"{A}/4_대시보드 Agent_대시보드고치기와공지_실습프롬프트.md")],
  "🚩 + '큰 건 빼고 보기'(9월 전년비 −46.9% → −1.9%) · 이탈 경보 미래로병원만 빨강(−50.7%) · 공지 5줄, 마지막 줄 빈칸", ["1.9%", "50.7%", "미래로병원"], False),
 ("제안자료 단계 ①", "새 에이전트", [("지침", f"{C}/2_제안자료 Agent_지침.md"), ("첨부", f"{C}/가격가이드.xlsx"), ("첨부", f"{C}/시장가격.xlsx"), ("첨부", f"{C}/고객요구조건.md"), ("첨부", f"{A}/결과물_예시_대상수요처.md"), ("보내기", f"{C}/3_제안자료 Agent_실습프롬프트1.md")],
  "요구조건 6항목 · 13모델 O/X · 후보 대회의실 MX-85P · MX-80P / 소회의실 MX-65P (대상수요처.md는 내가 저장한 것 또는 예시)", ["MX-85P", "MX-80P", "MX-65P"], False),
 ("인계본 없이 시작", "새 대화(같은 지침)", [("보내기", f"{C}/3_제안자료 Agent_실습프롬프트1.md")],
  "대상수요처.md를 올려 달라고 묻고, 없다고 하면 하나씩 물어서 채움", ["대상수요처"], False),
 ("제안자료 단계 ② 3안", "단계 ① 대화에 이어서", [("보내기", f"{C}/4_제안자료 Agent_실습프롬프트2.md")],
  "1안 15,920,000 · 2안 14,820,000 · 3안 10,100,000, 타사 756,000원 싼 줄에 350nit 미달, 맨 뒤 부록 O/X 대조표", ["15,920,000", "14,820,000", "10,100,000", "756,000", "부록", "!경쟁사"], False),
 ("대응 보고서", "새 대화", [("보내기", f"{C}/5_대응보고서_실습프롬프트.md")],
  "가격보상 0% · 5% · 10% 비교 표, '이 가정에서는', 확정 가격 · 할인율 없음 (프롬프트 아래에 8번 결과를 붙여넣기)", ["0%", "5%", "10%", "가정"], False),
 ("PPT 차트", "제안자료 대화에 이어서", [("보내기", f"{C}/6_PPT차트만들기_실습프롬프트.md")],
  ".pptx 2장(또는 차트 이미지 2개), 막대 숫자 = 표 숫자(1안 15,920,000 · 2안 14,820,000 · 3안 10,100,000)", ["15,920,000", "14,820,000", "10,100,000"], False),
 ("IT 법령 변화", "새 대화 · 웹 검색 켜기", [("보내기", f"{C}/7_IT법령변화_실습프롬프트.md")],
  "항목마다 출처 URL(http…), 없으면 '확인 필요', 단정 없음", ["http", "확인 필요"], False),
]
def signed(expect, checks):
    """기대 결과에 음수로 나오는 숫자 · 비율은 검사값에도 '-'를 붙인다 (− 와 - 는 같은 부호)"""
    e = expect.replace("−", "-")
    return [c if c.startswith(("!", "-")) or ("-" + c) not in e else "-" + c for c in checks]
steps = [dict(n=i + 1, title=t, where=w, items=it, expect=e, checks=signed(e, c), manual=m) for i, (t, w, it, e, c, m) in enumerate(STEPS)]
for s in steps:
    for _, f in s["items"]: assert f in files, f

GPT_ALL = open(os.path.join(AX, "GPT_테스트_실행프롬프트.md"), encoding="utf-8").read()
GPT_ALL = GPT_ALL.split("## ✂ 여기서부터 복사")[1].split("## ✂ 여기까지 복사")[0].strip()
CHECK_MD = open(os.path.join(AX, "GPT_테스트_체크리스트.md"), encoding="utf-8").read()
ZIP = base64.b64encode(open(os.path.join(AX, "dist", "AX_실습파일.zip"), "rb").read()).decode()

# ───────── 안전장치 — 하나라도 걸리면 기존 HTML을 건드리지 않고 멈춘다 ─────────
import re, subprocess, shutil, tempfile, sys
bad = []
def neg(t): return t.replace("−", "-")
CK = neg(CHECK_MD)
for s in steps:
    e = neg(s["expect"])
    for c in s["checks"]:
        if c.startswith("!"): continue
        # ① 검사값이 그 단계 기대 결과 안에 있다 (부호 포함)
        if c not in e: bad.append(f"{s['n']}단계 검사값 '{c}'가 기대 결과에 없음")
        # ② 기대 결과에서 음수인데 검사값에 부호가 빠지지 않았다
        elif not c.startswith("-") and ("-" + c) in e: bad.append(f"{s['n']}단계 '{c}'는 기대 결과에서 음수 — 부호 누락")
        # ③ 숫자 검사값은 GPT_테스트_체크리스트.md에도 같은 값으로 있다 (두 문서가 어긋나지 않게)
        if re.search(r"\d", c) and c.lstrip("-") not in CK and c.lstrip("-").replace(",", "") not in CK.replace(",", ""):
            bad.append(f"{s['n']}단계 '{c}'가 체크리스트에 없음")
    if not s["checks"]: bad.append(f"{s['n']}단계 검사값 없음")
page = open(os.path.join(AX, "tools", "test_tool_template.html"), encoding="utf-8").read()
if page.count("/*__DATA__*/null") != 1: bad.append("템플릿의 데이터 자리(/*__DATA__*/null)가 정확히 1개가 아님")
if bad: sys.exit("검수 도구를 만들지 않았습니다:\n  - " + "\n  - ".join(bad))

DATA = {"steps": steps, "files": files, "gptAll": GPT_ALL, "checkMd": CHECK_MD, "zip": ZIP}
page = page.replace("/*__DATA__*/null", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/"))
tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); tmp.write(page); tmp.close()
# ④ 스크립트 문법 · ⑤ 브라우저에서 실제로 눌러 보는 점검 (node · playwright가 있을 때)
CHK = os.path.join(AX, "tools", "check_test_tool.js")
if shutil.which("node"):
    js = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
    js.write(re.findall(r"<script>(.*?)</script>", page, re.S)[-1]); js.close()
    r = subprocess.run(["node", "--check", js.name], capture_output=True, text=True)
    if r.returncode: os.unlink(tmp.name); sys.exit("자바스크립트 문법 오류 — 만들지 않았습니다:\n" + r.stderr)
    r = subprocess.run(["node", CHK, tmp.name], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode == 2: print("  (브라우저 점검 건너뜀 — playwright 없음)")
    elif r.returncode: os.unlink(tmp.name); sys.exit("브라우저 점검 실패 — 만들지 않았습니다:\n" + r.stdout + r.stderr)
else:
    print("  (node 없음 — 문법 · 브라우저 점검 건너뜀)")
shutil.move(tmp.name, OUT)
print(f"{os.path.relpath(OUT, AX)}  {os.path.getsize(OUT) // 1024}KB · 단계 {len(steps)} · 파일 {len(files)} · 안전장치 통과")
