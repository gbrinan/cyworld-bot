# -*- coding: utf-8 -*-
"""전체 산출물을 폴더 하나(dist/AX_전체/)에 모으고 시작 페이지(index.html)를 붙인다.
마크다운은 옆에 같은 이름의 .html로 렌더링해 브라우저에서 바로 열린다. 마지막에 dist/AX_전체.zip.
사용: python3 build_bundle.py   (build_course_docs → build_deck → PDF → build_pack 다음에)"""
import os, re, shutil, zipfile, datetime, html as H
import markdown
HERE = os.path.dirname(os.path.abspath(__file__)); AX = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(AX, "dist", "AX_전체"); STAMP = datetime.date.today().isoformat()
if os.path.exists(OUT): shutil.rmtree(OUT)

FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">'
CSS = """
:root{--paper:#FBFAF7;--ink:#111821;--ink2:#4a4f57;--mute:#6b6660;--blue:#1C3F94;--deep:#0E2560;--amber:#9A6408;--red:#9A2C2C;--green:#0F6B4F;--card:#fff;--line:#E4E2DB;--panel:#EEF0EA;--rule:#D9D7D0;--code:#f3f2ee}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#15181d;--ink:#ece9e1;--ink2:#c2bfb6;--mute:#9b978f;--blue:#8fa4d8;--deep:#c9d3ee;--amber:#d6a54a;--red:#e88b8b;--green:#6fc2a0;--card:#1d2127;--line:#343941;--panel:#232830;--rule:#3a3f47;--code:#1a1e24}}
:root[data-theme="dark"]{--paper:#15181d;--ink:#ece9e1;--ink2:#c2bfb6;--mute:#9b978f;--blue:#8fa4d8;--deep:#c9d3ee;--amber:#d6a54a;--red:#e88b8b;--green:#6fc2a0;--card:#1d2127;--line:#343941;--panel:#232830;--rule:#3a3f47;--code:#1a1e24}
html{color-scheme:light dark}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans KR','Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic',sans-serif;font-size:16px;line-height:1.65;-webkit-font-smoothing:antialiased}
.wrap{max-width:860px;margin:0 auto;padding:40px 24px 80px}
.crumb{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin-bottom:18px}
.crumb a{color:var(--blue);text-decoration:none}
h1,h2,h3,h4{line-height:1.3;text-wrap:balance;margin:1.6em 0 .5em}
h1{font-size:28px;font-weight:700;margin-top:0;padding-bottom:12px;border-bottom:2px solid var(--ink)}
h2{font-size:21px;font-weight:700;padding-top:.4em;border-top:1px solid var(--rule)}
h3{font-size:18px;font-weight:600}
h4{font-size:16px;font-weight:600}
p,ul,ol{margin:.6em 0}
a{color:var(--blue)}
code{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:.88em;background:var(--code);padding:1px 5px;border-radius:3px}
pre{background:var(--code);border:1px solid var(--line);padding:14px 16px;overflow-x:auto;border-radius:4px;font-size:13.5px;line-height:1.55}
pre code{background:none;padding:0;font-size:inherit}
blockquote{margin:1em 0;padding:8px 18px;border-left:3px solid var(--blue);background:var(--panel);color:var(--ink2)}
blockquote p{margin:.3em 0}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:14.5px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:7px 10px;vertical-align:top;text-align:left}
th{background:var(--panel);font-weight:600}
hr{border:0;border-top:1px solid var(--rule);margin:2em 0}
img{max-width:100%}
strong{font-weight:700}
.foot{margin-top:60px;padding-top:14px;border-top:1px solid var(--rule);font-size:12px;color:var(--mute)}
"""
MD = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"], extension_configs={"toc": {"toc_depth": "2-3"}})

def md_to_html(src_path, rel_up):
    """rel_up: index.html 까지의 상대 경로 (예: '../../')"""
    text = open(src_path, encoding="utf-8").read()
    # 절 참조 링크: 같은 묶음 안의 .md 링크는 .html 로
    text = re.sub(r"\]\(([^)\s#]+?)\.md(#[^)]*)?\)", lambda m: f"]({m.group(1)}.html{m.group(2) or ''})", text)
    MD.reset(); body = MD.convert(text)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S); title = re.sub(r"<[^>]+>", "", m.group(1)) if m else os.path.basename(src_path)
    rel_src = os.path.relpath(src_path, AX)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title)}</title>{FONT}<style>{CSS}</style></head><body><div class="wrap">
<div class="crumb"><a href="{rel_up}index.html">AX 전체</a> · {H.escape(rel_src)} · <a href="{os.path.basename(src_path)}">.md 원본</a></div>
{body}
<div class="foot">삼성전자 B2B 영업 AX 과정 교안 · {STAMP} · 모든 데이터는 가상입니다</div>
</div></body></html>"""

INDEX_ROWS = []  # (section, [(href, label, note)])
def copy_tree(src, dst, rel_up, skip=lambda rel: False):
    """폴더를 복사하고 .md 옆에 .html 을 만든다. 만든 파일 목록을 돌려준다."""
    made = []
    for dp, dn, fn in os.walk(src):
        dn[:] = sorted(d for d in dn if not d.startswith(".") and d != "__pycache__")
        for f in sorted(fn):
            if f.startswith("."): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, src)
            if skip(rel): continue
            q = os.path.join(dst, rel); os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(p, q); made.append(q)
            if f.endswith(".md"):
                depth = rel.count(os.sep); up = rel_up + "../" * depth
                hq = q[:-3] + ".html"; open(hq, "w", encoding="utf-8").write(md_to_html(p, up)); made.append(hq)
    return made

def copy_files(files, dst, rel_up):
    os.makedirs(dst, exist_ok=True); made = []
    for src in files:
        q = os.path.join(dst, os.path.basename(src)); shutil.copy2(src, q); made.append(q)
        if src.endswith(".md"):
            hq = q[:-3] + ".html"; open(hq, "w", encoding="utf-8").write(md_to_html(src, rel_up)); made.append(hq)
    return made

os.makedirs(OUT, exist_ok=True)
D = os.path.join(AX, "deck"); DIST = os.path.join(AX, "dist")
# 01 덱
copy_files([os.path.join(D, f) for f in ["A판.html", "B판.html", "A판.pdf", "B판.pdf", "A판_순서.txt", "B판_순서.txt", "notes.json"] if os.path.exists(os.path.join(D, f))], os.path.join(OUT, "01_덱"), "../")
# 02 강사 문서
copy_files([os.path.join(AX, f) for f in ["instructor_guide.md", "faq.md", "rehearsal_checklist.md", "deck_audit.md", "slides_outline.md", "design_handoff_package.md", "validation_log.md", "module_spec.md", "agent_structure_v2.md", "handoff_review.md", "README.md"]], os.path.join(OUT, "02_강사"), "../")
# 03 참가자
copy_files([os.path.join(AX, "workbook_A판.md"), os.path.join(AX, "workbook_B판.md")] + [os.path.join(DIST, z) for z in ["참가자_A판.zip", "참가자_B판.zip"] if os.path.exists(os.path.join(DIST, z))], os.path.join(OUT, "03_참가자"), "../")
# 04 모듈 + 공통
copy_tree(os.path.join(AX, "context_pack", "modules"), os.path.join(OUT, "04_모듈"), "../../")
copy_tree(os.path.join(AX, "context_pack", "common"), os.path.join(OUT, "04_모듈", "common"), "../../../")
# 05 디자인 (아트보드 · canvas.json · 생성기)
copy_tree(os.path.join(AX, "design"), os.path.join(OUT, "05_디자인"), "../../", skip=lambda rel: rel.endswith(".html") and not rel.endswith(".dc.html"))
# 06 도구
copy_tree(os.path.join(AX, "tools"), os.path.join(OUT, "06_도구"), "../../")

# ───────── index.html ─────────
def row(href, label, note=""): return f'<tr><td><a href="{href}">{H.escape(label)}</a></td><td>{note}</td></tr>'
def table(rows): return '<table class="files"><tbody>' + "".join(rows) + "</tbody></table>"
mods = [("D_analysis", "D 데이터 분석", "1교시 · 전원", "recommend_D.html"), ("A_sensing_b2b", "A 직판 Sensing", "2교시 · B2B팀", "dashboard_A.html"),
        ("B_sensing_partner", "B 경로 Sensing", "2교시 · 유통전략팀", "report_B.docx"), ("C_proposal", "C 제안자료 작성", "3교시 · 전원", "proposal_C.html")]
mod_rows = "".join(f'<tr><td><a href="04_모듈/{m}/module.html">{n}</a></td><td>{w}</td><td><a href="04_모듈/{m}/index.html">폴더</a> · <a href="04_모듈/{m}/00_requirement.html">요구조건서</a> · <a href="04_모듈/{m}/01_data/index.html">01_data</a> · <a href="04_모듈/{m}/02_prompt/index.html">02_prompt</a> · <a href="04_모듈/{m}/03_tests/index.html">03_tests</a> · <a href="04_모듈/{m}/04_answer/index.html">04_answer</a> · <a href="04_모듈/{m}/07_skill/SKILL.html">SKILL.md</a></td><td class="mono">{o}</td></tr>' for m, n, w, o in mods)
common = [("security_rules", "업로드 금지 목록 · 실습 대체 규칙"), ("web_environment", "웹 환경 — 결과 저장 · HTML 열기 · Word 만들기 · 붙여넣기 경로"), ("tool_paths", "도구 클릭 경로 — 에이전트 만들기 · 막혔을 때 3단"),
          ("task_decomposition", "일을 보는 법 — 설계 6단계 (과정의 첫 시간)"), ("agent_and_skill_split", "에이전트와 스킬 나누기"), ("methodology", "IPO · 7블록 · 테스트 3종 · 사람 승인"),
          ("review_criteria", "검수 6항목"), ("test_cases_guide", "테스트 3종 — 모듈별 입력과 기대 행동"), ("data_capture", "화면 데이터를 표로 가져오기 (C 모듈)"), ("skills_and_mcp", "Skill과 MCP"), ("fit_check", "CANNOT 7항목 · 업무 유형"), ("tool_budget", "실행 횟수 예산")]
common_rows = "".join(row(f"04_모듈/common/{k}.html", k + ".md", v) for k, v in common)
def dir_pages():
    """모든 하위 폴더에 index.html 목록 페이지 — 정적 서버에도 폴더가 열리게"""
    for dp, dn, fn in os.walk(OUT):
        if dp == OUT: continue
        rel = os.path.relpath(dp, OUT); up = "../" * (rel.count(os.sep) + 1)
        dn.sort(); items = []
        for d in dn: items.append(f'<tr><td><a href="{d}/index.html">{H.escape(d)}/</a></td><td></td></tr>')
        for f in sorted(fn):
            if f == "index.html": continue
            sz = os.path.getsize(os.path.join(dp, f)); label = f
            href = f[:-3] + ".html" if f.endswith(".md") and os.path.exists(os.path.join(dp, f[:-3] + ".html")) else f
            extra = f' · <a href="{H.escape(f)}">.md 원본</a>' if href != f else ""
            items.append(f'<tr><td><a href="{H.escape(href)}">{H.escape(label)}</a>{extra}</td><td class="mono">{sz:,} B</td></tr>')
        page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(rel)}</title>{FONT}<style>{CSS}table.files{{display:table}}table.files td{{border-left:0;border-right:0;border-top:0}}.mono{{font-family:'IBM Plex Mono',monospace;font-size:13px;color:var(--mute);white-space:nowrap}}</style></head><body><div class="wrap">
<div class="crumb"><a href="{up}index.html">AX 전체</a> · {H.escape(rel)}</div><h1>{H.escape(rel)}</h1>
<table class="files"><tbody>{"".join(items)}</tbody></table>
<div class="foot">모든 데이터는 가상입니다</div></div></body></html>"""
        open(os.path.join(dp, "index.html"), "w", encoding="utf-8").write(page)
dir_pages()
n_files = sum(len(f) for _, _, f in os.walk(OUT)) + 1  # + index.html
index = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>삼성 B2B 영업 AX 교안</title>{FONT}<style>{CSS}
.wrap{{max-width:960px}}
.eyebrow{{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);font-weight:600;margin-bottom:8px}}
h1{{font-size:32px;border:0;padding:0;margin-bottom:6px}}
.lede{{color:var(--ink2);max-width:62ch;margin:0 0 28px}}
.day{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:24px 0 8px}}
.day > div{{background:var(--card);border:1px solid var(--line);padding:14px 16px}}
.day b{{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--amber);margin-bottom:4px}}
.day strong{{font-size:18px;display:block;margin-bottom:4px}}
.day small{{color:var(--mute);display:block;font-size:13px}}
.day .mono{{font-family:'IBM Plex Mono',monospace;font-size:13px;color:var(--ink2)}}
@media (max-width:640px){{.day{{grid-template-columns:1fr}}}}
table.files{{font-size:15px;display:table}}
table.files td:first-child{{white-space:nowrap;width:34%}}
table.files td{{border-left:0;border-right:0;border-top:0}}
.mono{{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13.5px}}
.note{{background:var(--panel);border-left:3px solid var(--blue);padding:10px 16px;margin:14px 0;font-size:15px}}
.warn{{border-left:4px solid var(--red)}}
section{{margin-top:36px}}
</style></head><body><div class="wrap">
<div class="eyebrow">삼성전자 B2B 영업 AX 과정 · {STAMP}</div>
<h1>삼성 B2B 영업 AX 교안</h1>
<p class="lede">에이전트 4개 · 모듈당 2시간 · 강사 담당 6시간. 이 폴더 하나에 덱 · 강사 문서 · 참가자 자료 · 모듈 팩 · 디자인 원본 · 생성 도구가 전부 있습니다({n_files}개 파일). 마크다운은 옆의 같은 이름 .html로 바로 열립니다.</p>

<div class="day">
<div><b>1교시</b><strong>D 데이터 분석</strong><small>전원 · 오프닝 + 일 보는 법 + 방법론 4장이 이 안에</small><span class="mono">recommend_D.html</span></div>
<div><b>2교시</b><strong>A 또는 B Sensing</strong><small>B2B팀은 A(직판) · 유통전략팀은 B(경로) · 방법론 5장이 앞에</small><span class="mono">dashboard_A.html / report_B.docx</span></div>
<div><b>3교시</b><strong>C 제안자료 작성</strong><small>전원 · 방법론 2장이 앞에 · Skill + 클로징이 뒤에</small><span class="mono">proposal_C.html</span></div>
</div>
<div class="note warn">모든 데이터 · 고객사 · 파트너 · 모델명 · 가격은 <strong>가상</strong>입니다. 실습 중 실제 업무 파일은 올리지 않습니다.</div>

<section><h2>01 · 덱 — 강의 순서 72장 × 2판</h2>
<p>브라우저에서 열고 ← → 로 넘깁니다. <strong>N</strong> 키로 발표자 노트, 우하단에 <span class="mono">n / 72 · 교시 · 장 이름</span>. 워크북 · 강사 가이드의 슬라이드 번호가 이 번호입니다.</p>
{table([row("01_덱/A판.html", "A판.html", "B2B팀 — D · A · C"), row("01_덱/B판.html", "B판.html", "B2B유통전략팀 — D · B · C"),
        row("01_덱/A판.pdf", "A판.pdf", "인쇄용 72쪽"), row("01_덱/B판.pdf", "B판.pdf", "인쇄용 72쪽"),
        row("01_덱/A판_순서.txt", "A판_순서.txt · B판_순서.txt", "강의 순서의 정본 — 교시 구분선 포함"), row("01_덱/notes.json", "notes.json", "발표자 노트 원본")])}
<div class="note">캔버스(Claude Design): <a href="https://claude.ai/code/artifact/084d98a0-07fa-4d9a-921c-e80d408e9ca4">artifact 084d98a0 · Version 8</a> — 아트보드 88장. 원본은 05_디자인.</div>
</section>

<section><h2>02 · 강사 문서</h2>
{table([row("02_강사/instructor_guide.html", "instructor_guide", "진행 가이드 v2 — 교시별 큐시트 · 되묻기 · 보조강사 운영 · 상황 대응"),
        row("02_강사/faq.html", "faq", "예상 Q&A — 웹 환경 · 도구 제약 · 보안 · 실습 · 설계 · 현업 적용 · 사내강사"),
        row("02_강사/rehearsal_checklist.html", "rehearsal_checklist", "환경 리허설 점검표 + 삼성 확인 요청 7가지 — 실행은 삼성 계정 필요"),
        row("02_강사/deck_audit.html", "deck_audit", "덱 28항목 점검 기록 · §4 남은 것(삼성 몫)"),
        row("02_강사/slides_outline.html", "slides_outline", "슬라이드 72장 설계서 · 6시간 배치표"),
        row("02_강사/design_handoff_package.html", "design_handoff_package", "Claude Design 핸드오프 최종본 — 프롬프트 · 디자인 시스템 · 수치 · 검수"),
        row("02_강사/validation_log.html", "validation_log", "블라인드 검증 기록 · 얻은 규칙 12가지"),
        row("02_강사/module_spec.html", "module_spec", "모듈 방식 — 요구조건서 1장 → 7단계 빌드 → CHECK"),
        row("02_강사/agent_structure_v2.html", "agent_structure_v2", "에이전트 구조 (9/7 시나리오 + 9/12 재설계)"),
        row("02_강사/README.html", "README", "폴더 안내 · 상태 표")])}
</section>

<section><h2>03 · 참가자 자료</h2>
{table([row("03_참가자/workbook_A판.html", "workbook_A판", "B2B팀 워크북 — 실습 슬라이드와 같은 파일 이름 · 신호 · 막혔을 때"),
        row("03_참가자/workbook_B판.html", "workbook_B판", "유통전략팀 워크북"),
        row("03_참가자/참가자_A판.zip", "참가자_A판.zip", "배포용 — 데이터 · 지시문 · 테스트 · 기준본 · paste · SKILL.md · 공통 문서 · 워크북 · PDF (zip은 폴더판 · AX_전체.zip 안에만)"),
        row("03_참가자/참가자_B판.zip", "참가자_B판.zip", "배포용 (B판) — zip은 폴더판에만")])}
</section>

<section><h2>04 · 모듈 팩 — 에이전트 하나 = 폴더 하나</h2>
<table class="files"><thead><tr><th>모듈</th><th>언제 · 누가</th><th>폴더</th><th>산출물</th></tr></thead><tbody>{mod_rows}</tbody></table>
<p>각 폴더: <span class="mono">00_requirement.md</span>(요구조건서 · 원본) · <span class="mono">module.md</span>(모듈 카드 9절 = 슬라이드 정본) · 01_data · 02_prompt · 03_tests · 04_answer · 05_demo_log · 06_paste · 07_skill · CHECK.md.
새 모듈을 만드는 법은 <a href="04_모듈/TEMPLATE.html">TEMPLATE.md</a>, 검증 예제는 <a href="04_모듈/E_supplier/module.html">E_supplier</a>.</p>
<h3>공통 문서 (common/)</h3>
{table([common_rows])}
</section>

<section><h2>05 · 디자인 원본</h2>
<p><a href="05_디자인/index.html">아트보드 88장</a>(<span class="mono">*.dc.html</span>)과 배치(<span class="mono">canvas.json</span>). 규칙은 <a href="05_디자인/README.html">README</a>. 생성기 <span class="mono">tools/gen_deck.py</span> · <span class="mono">gen_handson.py</span> · <span class="mono">build_deck.py</span>.</p>
</section>

<section><h2>06 · <a href="06_도구/index.html">도구</a> — 다시 만드는 순서</h2>
<pre>python3 tools/build_modules.py --all       # 모듈 데이터 · 소계본 · paste
python3 tools/check_module.py --all        # 모듈 자동 검사
python3 tools/build_course_docs.py         # 순서 · 노트 · 워크북 · 강사 가이드
python3 design/tools/build_deck.py         # A판 · B판 슬라이드쇼
chrome --headless=new --print-to-pdf=…     # PDF
python3 tools/build_pack.py                # 참가자 · 강사 zip
python3 tools/build_bundle.py              # 이 폴더</pre>
</section>

<section><h2>남은 것 — 삼성 · 강사 몫</h2>
<ul><li>도구 화면 캡처 5장 (O6 · O7 · D7 · A8 · B8) — 리허설 점검표 확인 요청 1~4번 답에 따라</li>
<li>CI 컬러 토큰 2개 · 로고</li><li>오프닝 10분 귀속 확인 — 받아주면 D 실습 1을 35분으로</li>
<li>90분 축약 16장 확정</li><li>14px 표(분해표 · 비교표) 뒷줄 판독 리허설</li></ul>
</section>
<div class="foot">저장소 docs/samsung-ax · 브랜치 claude/agent-curriculum-planning-ftcw7s · 모든 데이터는 가상입니다</div>
</div></body></html>"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index)

zp = os.path.join(DIST, "AX_전체.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, dn, fn in os.walk(OUT):
        for f in sorted(fn):
            p = os.path.join(dp, f); z.write(p, os.path.relpath(p, DIST))
print("AX_전체/", n_files, "files;", os.path.basename(zp), os.path.getsize(zp) // 1024 // 1024, "MB")
