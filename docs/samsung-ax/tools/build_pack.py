# -*- coding: utf-8 -*-
"""배포 패키지 — 참가자 실습 파일 묶음 하나(AX_실습파일: 세션1 A·B / 세션2 / 세션3 / 세션4, 함정 데이터 제외) · 강사 zip 을 dist/ 에 만든다.
참가자 팩에는 실습에 필요한 것만: 데이터 · 지시문 · 테스트 데이터 · 기준본 · paste · SKILL.md · 공통 문서 10개(예상 Q&A 포함) · 워크북 · 덱 PDF.
요구조건서(00) · 시연 로그(05) · 완성판정.md · 테스트 설명(테스트_*.md) · 강사 가이드는 강사 팩에만.
사용: python3 build_pack.py   (먼저 build_course_docs.py → design/tools/build_deck.py → PDF 순으로 만들어 둔다)"""
import os, sys, zipfile, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.abspath(os.path.join(HERE, ".."))
MOD = os.path.join(AX, "context_pack", "modules"); COMMON = os.path.join(AX, "context_pack", "common")
DIST = os.path.join(AX, "dist"); os.makedirs(DIST, exist_ok=True)
STAMP = datetime.date.today().isoformat()

TEAM = {"A판": ["D_analysis", "A_sensing_b2b", "C_proposal"], "B판": ["D_analysis", "B_sensing_partner", "C_proposal"]}
COMMON_P = ["security_rules.md", "web_environment.md", "tool_paths.md", "review_criteria.md", "fit_check.md",
            "task_decomposition.md", "agent_and_skill_split.md", "skills_and_mcp.md", "data_capture.md", "tool_budget.md", "faq.md"]
P_DIRS = ["01_데이터", "02_지시문", "04_기준본", "06_붙여넣기", "07_스킬"]
TEMPLATES = ["dashboard_sales.md", "dashboard_sales_예시.md", "dashboard_customer.md", "dashboard_customer_예시.md",
             "dashboard_territory.md", "dashboard_territory_예시.md", "dashboard_proposal.md", "dashboard_proposal_예시.md"]

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
            add(z, os.path.join(base, "모듈카드.md"), os.path.join(arc, "모듈카드.md")); n += 1
            for d in P_DIRS:
                # 어느 폴더에 있든 '테스트_' 로 시작하는 파일은 강사용이다 (기준본 폴더에도 들어간다)
                add_tree(z, os.path.join(base, d), os.path.join(arc, d),
                         skip=lambda rel: os.path.basename(rel).startswith("테스트_"))
                n += sum(1 for _, _, fs in os.walk(os.path.join(base, d))
                         for f in fs if not f.startswith("테스트_"))
            t = os.path.join(base, "03_테스트")  # 테스트 데이터만 (설명서 테스트_*.md는 강사 팩)
            for f in sorted(os.listdir(t)):
                if not f.startswith("테스트_"): add(z, os.path.join(t, f), os.path.join(arc, "03_테스트", f)); n += 1
        for f in COMMON_P:
            src = os.path.join(AX, f) if f == "faq.md" else os.path.join(COMMON, f)
            add(z, src, os.path.join(root, "common", f)); n += 1
        for f in TEMPLATES:  # 워크북 전환 절이 가리키는 템플릿
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
2. 업로드 테스트는 `modules/D_analysis/01_데이터/매출데이터_소계.csv` (1KB)로.
3. 지시문은 화면에서 옮겨 적지 않고 `02_지시문/` 파일에서 복사합니다.

## 오늘 순서
```
1교시  modules/D_analysis/      → 대시보드.html + 리뷰.md
2교시  modules/{mid}/{" " * (18 - len(mid))}→ {"영업대시보드.html" if deck == "A판" else "권역보고서.docx"}
3교시  modules/C_proposal/      → 제안자료.html
```

## 각 모듈 폴더
| 폴더 | 무엇 |
|---|---|
| `모듈카드.md` | 모듈 카드 — 분해표 · 단계 · 함정 · 검수 |
| `01_데이터/` | 올릴 파일. `*_소계.csv`는 코드 실행이 안 될 때 |
| `02_지시문/` | 지시문 — ✂ 표시 사이만 복사 |
| `03_테스트/` | 경계 · 실패 테스트용 데이터 |
| `04_기준본/` | 기준본. 못 따라왔을 때 이 파일로 다음 단계 |
| `06_붙여넣기/` | 업로드가 막혔을 때 붙여넣는 표 |
| `07_스킬/SKILL.md` | 오늘 만든 것의 스킬 형식 |

`슬라이드_{deck}.pdf`는 강의장 화면과 같은 72장입니다. 워크북의 슬라이드 번호가 이 PDF의 쪽 번호입니다.
"""

# ───────── 실습 데이터만 따로 ─────────
DATA_README = """# 실습 데이터 · {STAMP}

실습에서 **참가자가 도구에 올리는 파일만** 모았습니다. 지시문 · 기준본 · 시연 로그 · 문서는 빼고 데이터만 {N}개입니다.
모듈 폴더와 하위 폴더 이름은 슬라이드 · 워크북이 부르는 이름 그대로입니다.

| 폴더 | 무엇 |
|---|---|
| `01_데이터/` | 정상 테스트에 올리는 파일. `*_소계.csv`는 코드 실행이 막혔을 때 쓰는 집계본 |
| `03_테스트/` | 경계 · 실패 테스트에 올리는 파일 |
| `06_붙여넣기/` | 같은 데이터의 마크다운 표. 파일 업로드가 막혔을 때 복사해 붙여넣습니다 |

**모든 값은 가상입니다.** 회사명 · 모델명 · 가격 · 실적 · 연락처까지 전부 만들어 낸 것이고, 삼성전자 실제 정보와 무관합니다.
실패 테스트용 파일에는 일부러 오류와 가짜 개인정보를 심어 두었습니다. 에이전트가 거기서 멈추는지 보는 것이 실습 목적입니다.

---

## 1교시 · D 데이터 분석 (전원)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_데이터/매출데이터.csv` | 실습 1·2 | 매출 1,093행 **16열** (삼성 공유 헤더 · 2025-01 ~ 2026-09-24 일 단위) | 합계 **8,623,580,000원** |
| `01_데이터/매출데이터_소계.csv` | 실습 1·2 · 업로드 테스트 | 다섯 축 집계 (품목구분 · 주문유형 · 수요처명 · 파트명 · 판매처명) | **검산 대조용.** 오프닝의 업로드 테스트 파일이 이것입니다 |
| `03_테스트/매출데이터_함정.csv` | 실습 3 | 어긋남을 심은 1,093행 | 소계와 **3,520,000원 차이** · 580행 표기 · 638행 날짜 형식 · 876행 번호 중복 · 934행 음수 · 994행 수량 0 |

**이 헤더에는 단가 열이 없습니다.** `단가 × 수량 = 금액` 검산을 세울 수 없어, **소계 파일 대조**가 그 자리를 대신합니다.
경계 테스트는 새 파일이 아니라 `매출데이터.csv` **하나만** 올리고(소계 없이) 묻는 것입니다.

## 2교시 · A 직판 Sensing (B2B팀)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_데이터/기사수집.csv` | 실습 1 | 기사 30건 (품목 · 헤드라인 · 원본url · 키워드) | **헤드라인 중복 3건** → 27건으로 세야 합니다 |
| `01_데이터/대상고객사.csv` | 실습 1 | 상장 건설사 6곳 | 준공일에서 6개월을 빼면 접근 시점 |
| `01_데이터/검색어목록.md` | 참고 | 검색어 목록 | 전환 질문에서 씁니다 |
| `03_테스트/기사수집_실패.csv` | 실습 3 | 같은 30건에 가짜 연락처를 심음 | **3 · 7 · 12행**에 이름과 휴대전화 |

경계 테스트는 파일 없이 "프로파일 만들어줘"만 보내는 것입니다.

## 2교시 · B 경로 Sensing (B2B유통전략팀)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_데이터/뉴스수집.json` | 실습 1 | 뉴스 30건 | 해운대 18건 · 타 권역 12건 |
| `01_데이터/상권정보.csv` | 실습 1 | 상권 18행 | 규모 하한선 아래가 섞여 있습니다 |
| `01_데이터/파트너정보.csv` | 실습 1 | 파트너 4곳 | 시공가능규모 · 주력버티컬로 매칭 |
| `01_데이터/시장조사.md` | 실습 1 | 시장조사 메모 | |
| `03_테스트/파트너정보_실패.csv` | 실습 3 | 같은 4곳에 **계약단가 · 마진율 두 열 추가** | 그 두 열을 짚고 멈춰야 통과 |

경계 테스트는 담당 권역을 말하지 않고 시키는 것입니다.

## 3교시 · C 제안자료 작성 (전원)

| 파일 | 언제 | 무엇 | 확인값 |
|---|---|---|---|
| `01_데이터/고객요구조건.md` | 실습 1 | 고객 요구조건 6항목 | 필수와 희망이 섞여 있습니다 |
| `01_데이터/가격가이드.csv` | 실습 1 | 가격가이드 **13모델** | 요구조건 대조표의 행이 됩니다 |
| `01_데이터/시장가격.csv` | 실습 1 | 화면에서 옮긴 시장가격 10건 | 스펙이 아니라 **가격만** 씁니다 |
| `01_데이터/가격가이드_소계.csv` | 코드 실행이 막혔을 때 | 집계본 | |
| `03_테스트/고객요구조건_경계.md` | 실습 2·3 | 요구조건을 덜어 낸 것 | 빠진 항목을 되물어야 통과 |

실패 테스트는 파일이 아니라 확정 견적을 요구하는 문장입니다. 가격 · 납기 · 할인을 확정하면 실패입니다.

---

만든 방법은 각 모듈 `00_요구조건서.md`에 있고, `tools/build_modules.py`가 시드를 고정해 다시 만듭니다. 몇 번을 돌려도 같은 값이 나옵니다.
"""

def data_pack():
    """실습에서 올리는 데이터만. 지시문 · 기준본 · 설명 문서는 뺀다."""
    out = os.path.join(DIST, "실습데이터.zip"); root = "AX_실습데이터"; n = 0
    picked = []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for m in ["D_analysis", "A_sensing_b2b", "B_sensing_partner", "C_proposal"]:
            base = os.path.join(MOD, m)
            for d in ["01_데이터", "03_테스트", "06_붙여넣기"]:
                src = os.path.join(base, d)
                if not os.path.isdir(src): continue
                for f in sorted(os.listdir(src)):
                    if f.startswith(".") or f.startswith("테스트_") or f == "README.md":
                        continue  # 테스트_*.md 는 테스트 설명서라 데이터가 아니다
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
| 에이전트 **지침란**에 넣는 본체 | `D/prompt_1` · `A/지시문_3_분석` · `B/지시문_2_추출` · `C/지시문_1_추출` |
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

## 템플릿 — 내 업무로 옮길 때

모듈마다 **분석하는 앞부분만 떼어낸 템플릿**이 하나씩 있습니다. 모듈은 끝까지 가지만(추천·Action Plan·제안서), 템플릿은 **화면 한 장**에서 멈춥니다. 평소 업무에 쓰기엔 그 길이가 맞습니다.

| 템플릿 | 어느 모듈에서 | 무엇을 내나 |
|---|---|---|
| `dashboard_sales.md` | 1교시 D | 우리 팀 실적을 축별로 쪼갠 현황 한 장 |
| `dashboard_customer.md` | 2교시 A | 담당 고객사를 접근 시점 순으로 세운 목록 |
| `dashboard_territory.md` | 2교시 B | 담당 구역의 기회와 담당 배정 |
| `dashboard_proposal.md` | 3교시 C | 요구조건 대조표와 안 3개 비교 |

`{{ }}` 자리를 내 데이터에 맞춰 채우면 됩니다. 템플릿마다 **채워 본 예시**가 `_예시.md`로 같이 있고, 거기 수치는 실습 데이터에서 그대로 재현됩니다.

**실습의 함정 파일은 템플릿에 들어 있지 않습니다.** `매출데이터_함정.csv`나 `기사수집_실패.csv`처럼 틀린 값과 가짜 개인정보를 일부러 심어 둔 파일은 교육용입니다.
내 업무 데이터에는 그런 게 없으니, 대신 각 템플릿의 **③ 입력 검사와 0번 점검이 진짜 오류를 잡습니다.** 실제 실적 파일에서도 검산은 생각보다 자주 깨집니다.

다만 C의 실패 테스트는 예외입니다. 그건 틀린 파일이 아니라 **"확정 견적서를 지금 만들어 달라"는 요구 문장**이고, 그 요청은 내 업무에서도 똑같이 들어옵니다. 그래서 `dashboard_proposal.md`의 ⑥ 중단 규칙은 그대로 두었습니다.

---

모든 데이터와 회사명은 가상입니다. 지시문에 나오는 수치는 각 모듈 `04_기준본/` 기준본과 맞춰져 있으니 바꾸면 강사가 결과를 판정할 수 없습니다.
"""

PROMPT_DIRS = [("D_analysis", "1교시_D_데이터분석"), ("A_sensing_b2b", "2교시_A_직판Sensing"),
               ("B_sensing_partner", "2교시_B_경로Sensing"), ("C_proposal", "3교시_C_제안자료")]

def prompt_pack():
    """지시문과 템플릿만. 데이터 · 기준본 · 문서는 뺀다."""
    out = os.path.join(DIST, "지시문.zip"); root = "AX_지시문"; n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for m, label in PROMPT_DIRS:
            src = os.path.join(MOD, m, "02_지시문")
            for f in sorted(os.listdir(src)):
                if f.endswith(".md") and not f.startswith("README"):
                    add(z, os.path.join(src, f), f"{root}/{label}/{f}"); n += 1
            sk = os.path.join(MOD, m, "07_스킬", "SKILL.md")
            if os.path.exists(sk):
                add(z, sk, f"{root}/스킬형식/{label.split('_')[1]}_SKILL.md"); n += 1
        tdir = os.path.join(COMMON, "instruction_templates")
        for f in TEMPLATES:
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
| 참가자에게 주는 것 | `dist/AX_실습파일.zip` — 세션1 A · B / 세션2 대시보드 / 세션3 데이터분석 / 세션4 제안자료. 함정 · 실패 데이터는 빠져 있고 이 강사 폴더의 각 모듈 `03_테스트/`에만 있습니다 |
| 참가자 묶음의 엑셀 파일 | 각 모듈 `01_데이터/`의 CSV를 그대로 xlsx로 바꾼 것 — 한글 CSV는 엑셀에서 깨져서. 기준본 · 붙여넣기용 표는 참가자 묶음에 없으니 강사가 나눠 줍니다 |
| 시연 로그 · 테스트 판정 | 각 모듈 `05_시연로그.md` · `03_테스트/테스트_*.md` |
| 남은 확인 (삼성 몫) | `deck_audit.md` §4 · `rehearsal_checklist.md` |

모든 데이터는 가상입니다. 다시 만들 때: `tools/build_course_docs.py` → `design/tools/build_deck.py` → PDF → `tools/build_pack.py`.
""")
    print(f"강사.zip  {len(zipfile.ZipFile(out).namelist())} files  {os.path.getsize(out)//1024} KB")

# ───────── 실습 파일 — 세션마다 세 가지만 (참가자 배포본) ─────────
# 세션 폴더 = 1_붙여넣을_프롬프트.md (지침란에 통째로) · 2_데이터/ (그 프롬프트가 쓰는 파일만) · 3_실습지시문_1.md → 4_실습지시문_2.md
# 원본은 context_pack/실습묶음/. 세션2 · 3 프롬프트는 D 모듈 지시문의 ✂ 사이를 그대로 옮긴다 (사본을 따로 두면 어긋난다).
# 함정 · 실패 테스트 데이터와 테스트 설명서는 넣지 않는다 — 강사 묶음에만 있다.
PRACTICE = "AX_실습파일"
SRC = os.path.join(AX, "context_pack", "실습묶음")
def _m(mod, *parts): return os.path.join(MOD, mod, *parts)
def _cut(path):
    import re
    t = open(path, encoding="utf-8").read()
    m = re.search(r"## ✂ 여기서부터 복사[^\n]*\n(.*?)\n## ✂ 여기까지 복사", t, re.S)
    assert m, path
    return m.group(1).strip() + "\n"
def sync_session_prompts():
    """세션2 · 3 통합 프롬프트를 D 지시문에서 다시 뽑아 실습묶음에 쓴다"""
    for sess, f in [("세션2_대시보드", "지시문_1_대시보드.md"), ("세션3_데이터분석", "지시문_2_분석.md")]:
        open(os.path.join(SRC, sess, "1_붙여넣을_프롬프트.md"), "w", encoding="utf-8").write(_cut(_m("D_analysis", "02_지시문", f)))
DATA = {
    "세션1_A_직판": [("A_sensing_b2b", "기사수집.csv"), ("A_sensing_b2b", "대상고객사.csv")],
    "세션1_B_유통영업": [("B_sensing_partner", f) for f in ["뉴스수집.json", "상권정보.csv", "파트너정보.csv", "시장조사.md"]],
    "세션2_대시보드": [("D_analysis", "매출데이터.csv"), ("D_analysis", "매출데이터_소계.csv")],
    "세션3_데이터분석": [("D_analysis", "매출데이터.csv"), ("D_analysis", "매출데이터_소계.csv")],
    "세션4_제안자료": [("C_proposal", f) for f in ["가격가이드.csv", "시장가격.csv", "고객요구조건.md"]],
}
CSV_NAMES = ["매출데이터_소계", "매출데이터", "기사수집", "대상고객사", "상권정보", "파트너정보", "가격가이드", "시장가격"]
def _xname(f):
    """참가자에게는 CSV 대신 xlsx — 한글 CSV는 엑셀에서 더블클릭하면 깨진다"""
    return f[:-4] + ".xlsx" if f.endswith(".csv") else f
def _xtext(t):
    for n in CSV_NAMES: t = t.replace(n + ".csv", n + ".xlsx")
    return t.replace("04_기준본/", "")
def csv_to_xlsx(src, dst):
    import csv, re, datetime
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    rows = list(csv.reader(open(src, encoding="utf-8-sig", newline="")))
    head, body = rows[0], rows[1:]
    kinds = []
    for j in range(len(head)):
        vals = [r[j] for r in body if j < len(r) and r[j] != ""]
        if vals and all(re.fullmatch(r"-?\d+", v) for v in vals) and not head[j].endswith("코드"): kinds.append("int")
        elif vals and all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) for v in vals): kinds.append("date")
        else: kinds.append("text")
    wb = Workbook(); ws = wb.active; ws.title = os.path.splitext(os.path.basename(dst))[0][:31]
    F = "맑은 고딕"
    ws.append(head)
    for c in ws[1]:
        c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1C3F94")
        c.alignment = Alignment(horizontal="center", vertical="center")
    for r in body:
        out = []
        for j, v in enumerate(r):
            k = kinds[j] if j < len(kinds) else "text"
            out.append(int(v) if k == "int" and v != "" else datetime.datetime.strptime(v, "%Y-%m-%d") if k == "date" and v != "" else v)
        ws.append(out)
    for j, k in enumerate(kinds, 1):
        col = get_column_letter(j)
        for (c,) in ws.iter_rows(min_row=2, min_col=j, max_col=j):
            c.font = Font(name=F)
            if k == "int": c.number_format = "#,##0"
            if k == "date": c.number_format = "yyyy-mm-dd"
        width = max(len(str(x)) + sum(1 for ch in str(x) if ord(ch) > 0x2E80) for x in [head[j-1]] + [r[j-1] for r in body[:300] if j-1 < len(r)])
        ws.column_dimensions[col].width = min(max(width + 2, 8), 60)
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    wb.save(dst)
    return len(body)

def practice_layout():
    """(묶음 안 경로, 원본 경로) 목록"""
    L = []
    for sess, files in DATA.items():
        L.append((f"{sess}/1_붙여넣을_프롬프트.md", os.path.join(SRC, sess, "1_붙여넣을_프롬프트.md")))
        for mod, f in files: L.append((f"{sess}/2_데이터/{_xname(f)}", _m(mod, "01_데이터", f)))
        L.append((f"{sess}/3_실습지시문_1.md", os.path.join(SRC, sess, "3_실습지시문_1.md")))
        L.append((f"{sess}/4_실습지시문_2.md", os.path.join(SRC, sess, "4_실습지시문_2.md")))
    # HTML로 나오는 세션은 기대 결과 화면을 같이 준다 — 내 결과와 나란히 열어 견준다
    for sess, mod, f in [("세션1_A_직판", "A_sensing_b2b", "영업대시보드.html"), ("세션2_대시보드", "D_analysis", "대시보드.html"), ("세션4_제안자료", "C_proposal", "제안자료.html")]:
        L.append((f"{sess}/5_결과물_예시_{f}", _m(mod, "04_기준본", f)))
    # 세션4 프롬프트가 선택 입력으로 받는 세션3 인계본
    L.append(("세션4_제안자료/2_데이터/대상수요처.md", _m("D_analysis", "04_기준본", "대상수요처.md")))
    L.append(("뉴스수집_예약/뉴스수집_예약_프롬프트.md", os.path.join(AX, "세션1_뉴스수집_제안", "지시문_뉴스수집.md")))
    return L

def practice_readme(L):
    return f"""# AX 실습 파일 · {STAMP}

**모든 데이터는 가상**이며 실제 고객사 · 파트너 · 매출과 무관합니다. 실습 중 실제 업무 파일은 올리지 않습니다.

| 폴더 | 누가 | 결과물 |
|---|---|---|
| `세션1_A_직판/` | B2B팀 | `영업대시보드.html` |
| `세션1_B_유통영업/` | B2B유통전략팀 | `권역보고서.docx` |
| `세션2_대시보드/` | 전원 | `대시보드.html` |
| `세션3_데이터분석/` | 전원 | 리뷰 한 장 + 넘길 수요처 |
| `세션4_제안자료/` | 전원 | `제안자료.html` |
| `뉴스수집_예약/` | 전원 · 세션1 마지막 10분 | 내 고객사 뉴스를 Gemini / ChatGPT에 예약 |

## 세션 폴더마다 하는 일 — 네 번

1. **`1_붙여넣을_프롬프트.md`** — 에이전트를 만들고 「지침」란에 **파일 전체**를 붙여넣습니다.
2. **`2_데이터/`** — 안의 파일을 **모두** 올리고 저장합니다. 그 프롬프트가 쓰는 파일만 들어 있습니다. 표 데이터는 **엑셀(.xlsx)**이라 더블클릭해도 한글이 깨지지 않습니다. 열어 보는 것은 괜찮지만 **고치거나 다른 이름으로 저장하지 마십시오** — 기대 결과가 달라집니다.
3. **`3_실습지시문_1.md`** — 대화창에 그대로 붙여넣어 보냅니다. 결과를 봅니다.
4. **`4_실습지시문_2.md`** — 같은 대화에 이어서 보냅니다.
5. **`5_결과물_예시_….html`** (세션1 A · 세션2 · 세션4) — 이렇게 나와야 한다는 기대 결과 화면입니다. 더블클릭해 열고 내 결과와 나란히 견줍니다. **먼저 열어 보지 말고, 내 결과가 나온 뒤에** 봅니다.

세션1 B(Word 보고서)와 세션3(리뷰 글)은 강사 화면의 기준본과 견줍니다. 확인할 항목과 막혔을 때 보낼 문장은 워크북 · 실습 슬라이드에 있습니다.
HTML로 나온 결과는 복사 → 메모장 → `이름.html`(파일 형식 **모든 파일**)로 저장해 더블클릭합니다.

## 이어지는 고객

다섯 폴더가 **같은 가상 고객 6곳**(해솔호텔 · 대성건설 · 한울종합건설 · 미래로병원 · 세종교육재단 · 서진리테일)을 돕니다.
세션1 기사 「미래로병원 신관 증축 설계 착수」 → 세션2 · 3 매출에서 미래로병원 급감 → 세션3에서 고른 수요처 → 세션4 신관 회의공간 제안.
세션4의 `2_데이터/대상수요처.md`는 세션3의 기준본입니다. 내가 세션3에서 만든 것이 있으면 그것으로 바꿔 올려도 됩니다.

## 이 묶음에 없는 것

함정 · 실패 테스트 데이터(일부러 틀리게 만든 파일 · 가짜 개인정보가 든 파일)는 넣지 않았습니다. 실패 테스트는 **강사가 화면으로 시연**합니다.
"""

def participant_all():
    sync_session_prompts()
    L = practice_layout()
    out_dir = os.path.join(DIST, PRACTICE)
    if os.path.exists(out_dir):
        import shutil; shutil.rmtree(out_dir)
    zp = os.path.join(DIST, f"{PRACTICE}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, src in L:
            assert os.path.exists(src), src
            dst = os.path.join(out_dir, arc); os.makedirs(os.path.dirname(dst), exist_ok=True)
            if src.endswith(".csv") and arc.endswith(".xlsx"):
                csv_to_xlsx(src, dst)
            elif src.endswith((".md", ".html")):
                open(dst, "w", encoding="utf-8").write(_xtext(open(src, encoding="utf-8").read()))
            else:
                with open(src, "rb") as a, open(dst, "wb") as b: b.write(a.read())
            z.write(dst, f"{PRACTICE}/{arc}")
        rd = practice_readme(L)
        z.writestr(f"{PRACTICE}/READ_ME_FIRST.md", rd)
        open(os.path.join(out_dir, "READ_ME_FIRST.md"), "w", encoding="utf-8").write(rd)
    assert not any(a.endswith(".csv") for a, _ in L), "참가자 묶음에 CSV가 남아 있음"
    bad = [a for a, _ in L if "/03_테스트/" in a or os.path.basename(a).startswith("테스트_") or "함정" in a or "_실패" in a or "_경계" in a]
    assert not bad, bad
    print(f"{PRACTICE}.zip  {len(L) + 1} files  {os.path.getsize(zp)//1024} KB · 함정 · 실패 데이터 0개")

if __name__ == "__main__":
    for old in ["참가자_A판.zip", "참가자_B판.zip", "실습데이터.zip", "지시문.zip"]:  # 세션 구성 묶음 하나로 바뀌었다
        if os.path.exists(os.path.join(DIST, old)): os.remove(os.path.join(DIST, old))
    participant_all()
    instructor()
