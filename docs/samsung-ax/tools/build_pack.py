# -*- coding: utf-8 -*-
"""배포 패키지 — 참가자 zip 2개(A판·B판) · 실습데이터 zip · 지시문 zip · 강사 zip 을 dist/ 에 만든다.
참가자 팩에는 실습에 필요한 것만: 데이터 · 지시문 · 테스트 데이터 · 기준본 · paste · SKILL.md · 공통 문서 10개(예상 Q&A 포함) · 워크북 · 덱 PDF.
요구조건서(00) · 시연 로그(05) · CHECK.md · 테스트 설명(test_*.md) · 강사 가이드는 강사 팩에만.
사용: python3 build_pack.py   (먼저 build_course_docs.py → design/tools/build_deck.py → PDF 순으로 만들어 둔다)"""
import os, sys, zipfile, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.abspath(os.path.join(HERE, ".."))
MOD = os.path.join(AX, "context_pack", "modules"); COMMON = os.path.join(AX, "context_pack", "common")
DIST = os.path.join(AX, "dist"); os.makedirs(DIST, exist_ok=True)
STAMP = datetime.date.today().isoformat()

TEAM = {"A판": ["D_analysis", "A_sensing_b2b", "C_proposal"], "B판": ["D_analysis", "B_sensing_partner", "C_proposal"]}
COMMON_P = ["security_rules.md", "web_environment.md", "tool_paths.md", "review_criteria.md", "fit_check.md",
            "task_decomposition.md", "agent_and_skill_split.md", "skills_and_mcp.md", "data_capture.md", "tool_budget.md", "faq.md"]
P_DIRS = ["01_data", "02_prompt", "04_answer", "06_paste", "07_skill"]

def add(z, src, arc):
    z.write(src, arc)

def add_tree(z, root, arc_root, skip=lambda rel: False):
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if not d.startswith("."))
        for f in sorted(fn):
            if f.startswith("."): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)
            if skip(rel): continue
            add(z, p, os.path.join(arc_root, rel))

def participant(deck):
    out = os.path.join(DIST, f"참가자_{deck}.zip"); n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        root = f"AX실습_{deck}"
        for m in TEAM[deck]:
            base = os.path.join(MOD, m); arc = os.path.join(root, "modules", m)
            add(z, os.path.join(base, "module.md"), os.path.join(arc, "module.md")); n += 1
            for d in P_DIRS:
                add_tree(z, os.path.join(base, d), os.path.join(arc, d)); n += sum(len(f) for _, _, f in os.walk(os.path.join(base, d)))
            t = os.path.join(base, "03_tests")  # 테스트 데이터만 (설명서 test_*.md는 강사 팩)
            for f in sorted(os.listdir(t)):
                if not f.startswith("test_"): add(z, os.path.join(t, f), os.path.join(arc, "03_tests", f)); n += 1
        for f in COMMON_P:
            src = os.path.join(AX, f) if f == "faq.md" else os.path.join(COMMON, f)
            add(z, src, os.path.join(root, "common", f)); n += 1
        for f in ["dashboard_sales.md", "dashboard_sales_예시.md"]:  # 워크북 전환 절이 가리키는 템플릿
            add(z, os.path.join(COMMON, "instruction_templates", f), os.path.join(root, "common", "instruction_templates", f)); n += 1
        add(z, os.path.join(AX, f"workbook_{deck}.md"), os.path.join(root, f"워크북_{deck}.md")); n += 1
        pdf = os.path.join(AX, "deck", f"{deck}.pdf")
        if os.path.exists(pdf): add(z, pdf, os.path.join(root, f"슬라이드_{deck}.pdf")); n += 1
        else: print("  (없음) deck/" + deck + ".pdf — PDF를 먼저 만들면 포함됩니다")
        z.writestr(os.path.join(root, "READ_ME_FIRST.md"), readme(deck))
    print(f"{os.path.basename(out)}  {n} files  {os.path.getsize(out)//1024} KB")

def readme(deck):
    team = "B2B팀" if deck == "A판" else "B2B유통전략팀"; mid = "A_sensing_b2b" if deck == "A판" else "B_sensing_partner"
    return f"""# AX 실습 배포 폴더 — {deck} ({team}) · {STAMP}

이 폴더의 모든 데이터는 **가상**입니다. 실제 고객사 · 파트너 · 실적과 무관합니다. 실습 중 실제 업무 파일은 올리지 않습니다 (`common/security_rules.md`).

## 시작 전 (3분)
1. `워크북_{deck}.md`의 "시작 전 확인"을 봅니다.
2. 업로드 테스트는 `modules/D_analysis/01_data/target_account.md` (1KB)로.
3. 지시문은 화면에서 옮겨 적지 않고 `02_prompt/` 파일에서 복사합니다.

## 오늘 순서
```
1교시  modules/D_analysis/      → recommend_D.html
2교시  modules/{mid}/{" " * (18 - len(mid))}→ {"dashboard_A.html" if deck == "A판" else "report_B.docx"}
3교시  modules/C_proposal/      → proposal_C.html
```

## 각 모듈 폴더
| 폴더 | 무엇 |
|---|---|
| `module.md` | 모듈 카드 — 분해표 · 단계 · 함정 · 검수 |
| `01_data/` | 올릴 파일. `*_소계.csv`는 코드 실행이 안 될 때 |
| `02_prompt/` | 지시문 — ✂ 표시 사이만 복사 |
| `03_tests/` | 경계 · 실패 테스트용 데이터 |
| `04_answer/` | 기준본. 못 따라왔을 때 이 파일로 다음 단계 |
| `06_paste/` | 업로드가 막혔을 때 붙여넣는 표 |
| `07_skill/SKILL.md` | 오늘 만든 것의 스킬 형식 |

`슬라이드_{deck}.pdf`는 강의장 화면과 같은 72장입니다. 워크북의 슬라이드 번호가 이 PDF의 쪽 번호입니다.
"""

# ───────── 실습 데이터만 따로 ─────────
DATA_README = """# 실습 데이터 · {STAMP}

실습에서 **참가자가 도구에 올리는 파일만** 모았습니다. 지시문 · 기준본 · 시연 로그 · 문서는 빼고 데이터만 {N}개입니다.
모듈 폴더와 하위 폴더 이름은 슬라이드 · 워크북이 부르는 이름 그대로입니다.

| 폴더 | 무엇 |
|---|---|
| `01_data/` | 정상 테스트에 올리는 파일. `*_소계.csv`는 코드 실행이 막혔을 때 쓰는 집계본 |
| `03_tests/` | 경계 · 실패 테스트에 올리는 파일 |
| `06_paste/` | 같은 데이터의 마크다운 표. 파일 업로드가 막혔을 때 복사해 붙여넣습니다 |

**모든 값은 가상입니다.** 회사명 · 모델명 · 가격 · 실적 · 연락처까지 전부 만들어 낸 것이고, 삼성전자 실제 정보와 무관합니다.
실패 테스트용 파일에는 일부러 오류와 가짜 개인정보를 심어 두었습니다. 에이전트가 거기서 멈추는지 보는 것이 실습 목적입니다.

---

## 1교시 · D 데이터 분석 (전원)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_data/sales_history.csv` | 실습 1 | 판매실적 52행 10열 | 합계 **570,258,000원** · 공급가×수량=판매금액 검산 불일치 **0건** |
| `01_data/target_account.md` | 실습 1 · 업로드 테스트 | 대상 수요처 1곳 (1KB) | 오프닝의 업로드 테스트 파일이 이것입니다 |
| `01_data/sales_history_소계.csv` | 코드 실행이 막혔을 때 | 네 축 집계 (버티컬 · 지역 · 제품군 · 모델명) | 소계본만 올리면 모델 추천이 안 나옵니다 |
| `01_data/sales_history_호텔모델별.csv` | 코드 실행이 막혔을 때 | 호텔 모델별 집계 | **소계본과 둘을 함께** 올립니다 |
| `03_tests/sales_history_실패.csv` | 실습 2·3 | 오류를 심은 52행 | 불일치 **7 · 25 · 43행** · **14행 버티컬이 "호탤"** 오타 |

경계 테스트는 새 파일이 아니라 `sales_history.csv` **하나만** 올리고 묻는 것입니다.

## 2교시 · A 직판 Sensing (B2B팀)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_data/rss_feed.csv` | 실습 1 | 기사 30건 (품목 · 헤드라인 · 원본url · 키워드) | **헤드라인 중복 3건** → 27건으로 세야 합니다 |
| `01_data/target_builders.csv` | 실습 1 | 상장 건설사 6곳 | 준공일에서 6개월을 빼면 접근 시점 |
| `01_data/rss_sources.md` | 참고 | 검색어 목록 | 전환 질문에서 씁니다 |
| `03_tests/rss_feed_실패.csv` | 실습 3 | 같은 30건에 가짜 연락처를 심음 | **3 · 7 · 12행**에 이름과 휴대전화 |

경계 테스트는 파일 없이 "프로파일 만들어줘"만 보내는 것입니다.

## 2교시 · B 경로 Sensing (B2B유통전략팀)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_data/naver_news_dummy.json` | 실습 1 | 뉴스 30건 | 해운대 18건 · 타 권역 12건 |
| `01_data/district_info.csv` | 실습 1 | 상권 18행 | 규모 하한선 아래가 섞여 있습니다 |
| `01_data/partner_info.csv` | 실습 1 | 파트너 4곳 | 시공가능규모 · 주력버티컬로 매칭 |
| `01_data/market_research.md` | 실습 1 | 시장조사 메모 | |
| `03_tests/partner_info_실패.csv` | 실습 3 | 같은 4곳에 **계약단가 · 마진율 두 열 추가** | 그 두 열을 짚고 멈춰야 통과 |

경계 테스트는 담당 권역을 말하지 않고 시키는 것입니다.

## 3교시 · C 제안자료 작성 (전원)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_data/customer_request.md` | 실습 1 | 고객 요구조건 6항목 | 필수와 희망이 섞여 있습니다 |
| `01_data/tv_price_guide.csv` | 실습 1 | 가격가이드 **13모델** | 요구조건 대조표의 행이 됩니다 |
| `01_data/naver_crawl.csv` | 실습 1 | 화면에서 옮긴 시장가격 10건 | 스펙이 아니라 **가격만** 씁니다 |
| `01_data/tv_price_guide_소계.csv` | 코드 실행이 막혔을 때 | 집계본 | |
| `03_tests/customer_request_경계.md` | 실습 2·3 | 요구조건을 덜어 낸 것 | 빠진 항목을 되물어야 통과 |

실패 테스트는 파일이 아니라 확정 견적을 요구하는 문장입니다. 가격 · 납기 · 할인을 확정하면 실패입니다.

---

만든 방법은 각 모듈 `00_requirement.md`에 있고, `tools/build_modules.py`가 시드를 고정해 다시 만듭니다. 몇 번을 돌려도 같은 값이 나옵니다.
"""

def data_pack():
    """실습에서 올리는 데이터만. 지시문 · 기준본 · 설명 문서는 뺀다."""
    out = os.path.join(DIST, "실습데이터.zip"); root = "AX_실습데이터"; n = 0
    picked = []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for m in ["D_analysis", "A_sensing_b2b", "B_sensing_partner", "C_proposal"]:
            base = os.path.join(MOD, m)
            for d in ["01_data", "03_tests", "06_paste"]:
                src = os.path.join(base, d)
                if not os.path.isdir(src): continue
                for f in sorted(os.listdir(src)):
                    if f.startswith(".") or f.startswith("test_") or f == "README.md":
                        continue  # test_*.md 는 테스트 설명서라 데이터가 아니다
                    add(z, os.path.join(src, f), f"{root}/{m}/{d}/{f}"); n += 1; picked.append(f"{m}/{d}/{f}")
        z.writestr(f"{root}/README.md", DATA_README.replace("{STAMP}", STAMP).replace("{N}", str(n)))
    print(f"실습데이터.zip  {n} files  {os.path.getsize(out)//1024} KB")
    return picked

# ───────── 지시문(프롬프트)만 따로 ─────────
PROMPT_README = """# 지시문 모음 · {STAMP}

실습에서 쓰는 **지시문(프롬프트) 전부**와 **내 업무로 옮길 때 쓰는 템플릿**을 모았습니다. 데이터·기준본·문서는 빼고 {N}개입니다.

슬라이드에서는 이것을 **지시문**이라고 부릅니다. 도구의 입력칸은 **지침란**, 모듈 안의 하위 작업은 **단계**입니다. 셋을 섞어 쓰지 않습니다.

---

## 어디에 붙여넣나

파일마다 `✂ 여기서부터 복사` ~ `✂ 여기까지 복사`가 있습니다. **그 사이만** 복사합니다. 위의 `>` 안내문은 사람이 읽는 것이라 붙여넣지 않습니다.

| 파일 | 어디에 |
|---|---|
| 에이전트 **지침란**에 넣는 본체 | `D/prompt_1` · `A/prompt_3_분석` · `B/prompt_2_추출` · `C/prompt_1_추출` |
| 만든 뒤 **대화창**에 보내는 메시지 | 나머지 전부 |

에이전트 메뉴가 없으면 본체를 새 대화 맨 앞에 붙여넣고 시작해도 됩니다. 그때는 대화 메시지도 순서대로 이어서 보냅니다.

---

## 지시문 7블록

본체 네 개는 같은 뼈대입니다. 순서가 곧 에이전트가 생각하는 순서라 바꾸지 않습니다.

| 블록 | 무엇을 쓰나 | 빠지면 |
|---|---|---|
| ① 역할 | 누구이고, 누구를 돕고, 무엇을 경계하는가 | 말투와 판단 기준이 매번 달라짐 |
| ② 업무 범위 | 하는 일과 **하지 않는 일** | 시키지 않은 걸 해 옴 |
| ③ 입력 검사 | 무엇이 있어야 시작하나, 없으면 어떻게 | 빈손으로 그럴듯한 답을 만들어 냄 |
| ④ 처리 순서 | 어떤 차례로 | 사람마다 결과가 달라짐 |
| ⑤ 출력 형식 | 어떤 모양으로 | 매번 다른 서식이 나옴 |
| ⑥ 중단·보안 | 어디서 멈추나 | 멈춰야 할 데서 안 멈춤 |
| ⑦ 성공 기준 | 무엇이 통과인가 | 잘된 건지 판단할 수가 없음 |

---

## ① 역할을 쓰는 법

가장 자주 비는 칸이고, 제일 효과가 큰 칸입니다. **직함 한 줄로 끝내지 마십시오.** 네 가지를 넣습니다.

**누구인가** — 직무와 연차를 줍니다. "데이터 분석 Agent"보다 "판매 데이터를 오래 들여다본 분석 담당자"가 낫습니다.

**무엇을 먼저 보는가** — 그 직무가 몸에 익힌 습관입니다. 이게 판단 기준이 됩니다.
> 건설사 기사를 읽을 때 남들은 수주 금액을 보지만, 너는 준공 시기를 먼저 본다.

**누구를 돕는가** — 읽는 사람이 처한 상황까지 적습니다. 결과물의 모양이 여기서 정해집니다.
> 담당 수요처를 몇십 곳 들고 있는 영업 담당자다. 그 사람에게 필요한 건 기사 요약이 아니라 "이번 달에 누구부터 만나야 하나"라는 답이다.

**무엇을 경계하는가** — 이 일에서 가장 비싼 실수를 적습니다. 대부분 "모르는 걸 채워 넣는 것"입니다.
> 빈칸을 남긴 분석이 채워 넣은 분석보다 낫다.

내 업무로 옮길 때 **역할 블록만 바꿔도 절반은 끝납니다.** ④~⑦은 대개 그대로 쓸 수 있습니다.

---

## 폴더

```
1교시_D_데이터분석/    제품 추천 (본체 1개)
2교시_A_직판Sensing/   수집 → 프로파일 → 분석 (3단계, 에이전트는 하나)
2교시_B_경로Sensing/   키워드 → 추출 → 보고서 (3단계, 에이전트는 하나)
3교시_C_제안자료/      정제 → 추출 → 제안 (3단계, 에이전트는 하나)
템플릿/               내 업무로 옮길 때 쓰는 빈 양식
스킬형식/             같은 내용의 SKILL.md. 스킬 기능이 열려 있으면 이걸 등록합니다
```

**한 모듈에 단계가 셋이어도 에이전트는 하나입니다.** 단계 사이에 사람만 하는 일이 없어서 나누지 않았습니다.

---

## 템플릿 — 영업 현황 대시보드

`템플릿/dashboard_sales.md`는 **1교시 D에서 데이터를 분석하는 앞부분만 떼어낸 것**입니다.
D는 분석한 다음 제품을 추천하지만, 이 템플릿은 분석에서 멈추고 대시보드 한 장으로 끝냅니다. 추천할 대상이 정해지지 않은 평소 업무에 씁니다.

`{{ }}` 자리를 내 실적 파일에 맞춰 채우면 됩니다. 채워 본 예시는 `템플릿/dashboard_sales_예시.md`에 있고, 거기 수치는 실습 데이터에서 그대로 재현됩니다.

---

모든 데이터와 회사명은 가상입니다. 지시문에 나오는 수치는 각 모듈 `04_answer/` 기준본과 맞춰져 있으니 바꾸면 강사가 결과를 판정할 수 없습니다.
"""

PROMPT_DIRS = [("D_analysis", "1교시_D_데이터분석"), ("A_sensing_b2b", "2교시_A_직판Sensing"),
               ("B_sensing_partner", "2교시_B_경로Sensing"), ("C_proposal", "3교시_C_제안자료")]

def prompt_pack():
    """지시문과 템플릿만. 데이터 · 기준본 · 문서는 뺀다."""
    out = os.path.join(DIST, "지시문.zip"); root = "AX_지시문"; n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for m, label in PROMPT_DIRS:
            src = os.path.join(MOD, m, "02_prompt")
            for f in sorted(os.listdir(src)):
                if f.endswith(".md") and not f.startswith("README"):
                    add(z, os.path.join(src, f), f"{root}/{label}/{f}"); n += 1
            sk = os.path.join(MOD, m, "07_skill", "SKILL.md")
            if os.path.exists(sk):
                add(z, sk, f"{root}/스킬형식/{label.split('_')[1]}_SKILL.md"); n += 1
        tdir = os.path.join(COMMON, "instruction_templates")
        for f in ["dashboard_sales.md", "dashboard_sales_예시.md"]:
            add(z, os.path.join(tdir, f), f"{root}/템플릿/{f}"); n += 1
        z.writestr(f"{root}/README.md", PROMPT_README.replace("{STAMP}", STAMP).replace("{N}", str(n)))
    print(f"지시문.zip  {n} files  {os.path.getsize(out)//1024} KB")

def instructor():
    out = os.path.join(DIST, "강사.zip")
    skip = lambda rel: rel.startswith(("dist/", "context_pack/team_b2b/", "context_pack/team_partner/", "tools/.")) \
        or rel.endswith((".pyc",)) or "/__pycache__/" in rel or (rel.startswith("design/") and rel.endswith(".html") and not rel.endswith(".dc.html"))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        add_tree(z, AX, "AX강사", skip)
        z.writestr("AX강사/READ_ME_FIRST.md", f"""# AX 강사 폴더 · {STAMP}

| 먼저 볼 것 | 파일 |
|---|---|
| 진행 가이드 (큐시트 · 되묻기 · 보조강사) | `instructor_guide.md` |
| 슬라이드쇼 (브라우저 · ← → · N 노트) | `deck/A판.html` · `deck/B판.html` (같은 폴더의 PDF는 인쇄용) |
| 슬라이드 순서 · 발표자 노트 | `deck/*_순서.txt` · `deck/notes.json` |
| 참가자에게 주는 것 | `dist/참가자_A판.zip` · `참가자_B판.zip` (이 폴더에는 없음 — `tools/build_pack.py`로 생성) |
| 시연 로그 · 테스트 판정 | 각 모듈 `05_demo_log.md` · `03_tests/test_*.md` |
| 남은 확인 (삼성 몫) | `deck_audit.md` §4 · `rehearsal_checklist.md` |

모든 데이터는 가상입니다. 다시 만들 때: `tools/build_course_docs.py` → `design/tools/build_deck.py` → PDF → `tools/build_pack.py`.
""")
    print(f"강사.zip  {len(zipfile.ZipFile(out).namelist())} files  {os.path.getsize(out)//1024} KB")

if __name__ == "__main__":
    for d in TEAM: participant(d)
    data_pack()
    prompt_pack()
    instructor()
