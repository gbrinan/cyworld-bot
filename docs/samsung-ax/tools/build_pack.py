# -*- coding: utf-8 -*-
"""배포 패키지 — 참가자 zip 2개(A판·B판)와 강사 zip 1개를 dist/ 에 만든다.
참가자 팩에는 실습에 필요한 것만: 데이터 · 지시문 · 테스트 데이터 · 기준본 · paste · SKILL.md · 공통 문서 8개 · 워크북 · 덱 PDF.
요구조건서(00) · 시연 로그(05) · CHECK.md · 테스트 설명(test_*.md) · 강사 가이드는 강사 팩에만.
사용: python3 build_pack.py   (먼저 build_course_docs.py → design/tools/build_deck.py → PDF 순으로 만들어 둔다)"""
import os, sys, zipfile, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.abspath(os.path.join(HERE, ".."))
MOD = os.path.join(AX, "context_pack", "modules"); COMMON = os.path.join(AX, "context_pack", "common")
DIST = os.path.join(AX, "dist"); os.makedirs(DIST, exist_ok=True)
STAMP = datetime.date.today().isoformat()

TEAM = {"A판": ["D_analysis", "A_sensing_b2b", "C_proposal"], "B판": ["D_analysis", "B_sensing_partner", "C_proposal"]}
COMMON_P = ["security_rules.md", "web_environment.md", "tool_paths.md", "review_criteria.md", "fit_check.md",
            "task_decomposition.md", "agent_and_skill_split.md", "skills_and_mcp.md", "data_capture.md"]
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
        for f in COMMON_P: add(z, os.path.join(COMMON, f), os.path.join(root, "common", f)); n += 1
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
    instructor()
