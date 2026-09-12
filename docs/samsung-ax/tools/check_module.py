#!/usr/bin/env python3
"""모듈 완성 판정 — 자동 8항목 (module_spec.md 5장).

사용법:
    python3 docs/samsung-ax/tools/check_module.py D_analysis
    python3 docs/samsung-ax/tools/check_module.py --all

00_requirement.md 의 frontmatter 를 원본으로 삼아 모듈 폴더를 대조합니다.
종료 코드 0 = 자동 항목 전부 통과. 수동 4항목(#10~12)은 CHECK.md 에서 사람이 확인합니다.
"""
import csv
import io
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.normpath(os.path.join(HERE, "..", "context_pack", "modules"))

REQUIRED_FIELDS = ["module", "name", "source", "team", "tool", "inputs", "outputs",
                   "process", "planted", "tests", "forbidden", "agent_count", "skill", "steps"]
TEST_FILES = ["test_normal.md", "test_boundary.md", "test_failure.md"]
DEMO_SECTIONS = ["올린 파일", "붙여넣은 프롬프트", "첫 응답에서 확인할 것", "안 나오면 되묻는 문장"]
SKILL_SECTIONS = ["역할·목표", "출력 형식", "금지 사항", "검토 기준", "작업 단계"]
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")
PASTE_LIMIT = 6 * 1024
PHONE = re.compile(r"01[016789]-?\d{3,4}-?\d{4}")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def load_requirement(mod_dir):
    path = os.path.join(mod_dir, "00_requirement.md")
    if not os.path.exists(path):
        return None, "00_requirement.md 없음"
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, "frontmatter(--- ... ---) 없음"
    try:
        return yaml.safe_load(m.group(1)), None
    except yaml.YAMLError as e:
        return None, f"frontmatter YAML 오류: {e}"


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def to_num(s):
    try:
        return float(str(s).replace(",", ""))
    except ValueError:
        return None


def check(mod_id):
    mod_dir = os.path.join(MODULES, mod_id)
    results = []  # (번호, 통과여부, 메시지)

    def add(no, ok, msg):
        results.append((no, ok, msg))

    req, err = load_requirement(mod_dir)
    if req is None:
        add(1, False, err)
        return results
    missing = [f for f in REQUIRED_FIELDS if f not in req]
    add(1, not missing, "필수 필드 " + ("모두 있음" if not missing else "누락: " + ", ".join(missing)))

    # 2. 입력 파일 + 헤더
    data_dir = os.path.join(mod_dir, "01_data")
    probs = []
    for inp in req.get("inputs", []):
        p = os.path.join(data_dir, inp["file"])
        if not os.path.exists(p):
            probs.append(f"{inp['file']} 없음")
            continue
        if inp.get("format") == "csv":
            rows = read_csv(p)
            if not rows or rows[0] != [str(h) for h in inp["headers"]]:
                probs.append(f"{inp['file']} 헤더 불일치: {rows[0] if rows else '빈 파일'} != {inp['headers']}")
            elif inp.get("rows") and len(rows) - 1 != inp["rows"]:
                probs.append(f"{inp['file']} 행 수 {len(rows)-1} != {inp['rows']}")
        elif inp.get("format") == "json":
            try:
                doc = json.load(open(p, encoding="utf-8"))
                items = doc.get("items", doc if isinstance(doc, list) else [])
                if items and set(inp["headers"]) - set(items[0].keys()):
                    probs.append(f"{inp['file']} items 키 누락: {set(inp['headers']) - set(items[0].keys())}")
            except (json.JSONDecodeError, AttributeError) as e:
                probs.append(f"{inp['file']} JSON 오류: {e}")
    add(2, not probs, "입력 파일·헤더 " + ("일치" if not probs else "; ".join(probs)))

    # 3. 프롬프트
    pdir = os.path.join(mod_dir, "02_prompt")
    prompts = [f for f in os.listdir(pdir)] if os.path.isdir(pdir) else []
    prompts = [f for f in prompts if f.endswith(".md") and f != "README.md"]
    holes = []
    for f in prompts:
        n = open(os.path.join(pdir, f), encoding="utf-8").read().count("{{")
        if n:
            holes.append(f"{f}: {{{{ }}}} {n}개")
    if not prompts:
        add(3, False, "02_prompt/ 에 프롬프트 파일 없음")
    else:
        add(3, not holes, f"프롬프트 {len(prompts)}개, " + ("자리 0개" if not holes else "; ".join(holes)))

    # 4. 테스트 3파일
    tdir = os.path.join(mod_dir, "03_tests")
    miss = [f for f in TEST_FILES if not os.path.exists(os.path.join(tdir, f))]
    add(4, not miss, "테스트 3파일 " + ("있음" if not miss else "누락: " + ", ".join(miss)))

    # 5. 정답 파일
    adir = os.path.join(mod_dir, "04_answer")
    miss = [o["file"] for o in req.get("outputs", []) if not os.path.exists(os.path.join(adir, o["file"]))]
    add(5, not miss, "정답 파일 " + ("있음" if not miss else "누락: " + ", ".join(miss)))

    # 6. 시연 로그
    dpath = os.path.join(mod_dir, "05_demo_log.md")
    if not os.path.exists(dpath):
        add(6, False, "05_demo_log.md 없음")
    else:
        txt = open(dpath, encoding="utf-8").read()
        miss = [s for s in DEMO_SECTIONS if s not in txt]
        filled = "{모듈 ID}" not in txt and "{YYYY-MM-DD}" not in txt
        add(6, not miss and filled, "시연 로그 " + ("필수 절 있음" if not miss else "누락 절: " + ", ".join(miss))
            + ("" if filled else " / 템플릿 자리표시자 남음"))

    # 7. paste
    pastedir = os.path.join(mod_dir, "06_paste")
    probs = []
    for inp in req.get("inputs", []):
        base = os.path.splitext(inp["file"])[0] + ".md"
        p = os.path.join(pastedir, base)
        if not os.path.exists(p):
            probs.append(f"{base} 없음")
        elif os.path.getsize(p) > PASTE_LIMIT:
            probs.append(f"{base} {os.path.getsize(p)}B > 6KB")
    add(7, not probs, "paste " + ("모두 있음·6KB 이하" if not probs else "; ".join(probs)))

    # 8. 소계본 검산
    st = req.get("subtotals")
    if not st:
        add(8, True, "subtotals 정의 없음 (검산 생략)")
    else:
        src = os.path.join(data_dir, st["source"])
        sub = os.path.join(data_dir, os.path.splitext(st["source"])[0] + "_소계.csv")
        if not (os.path.exists(src) and os.path.exists(sub)) or not src.endswith(".csv"):
            add(8, False, "소계본 또는 원본 CSV 없음")
        else:
            rows = read_csv(src)
            hdr, body = rows[0], rows[1:]
            col = st["sum"]
            if col in hdr:
                total = sum(to_num(r[hdr.index(col)]) or 0 for r in body)
            else:  # 건수 기준
                total = float(len(body))
            srows = read_csv(sub)
            shdr = srows[0]
            probs = []
            try:
                ai, vi, si = shdr.index("축"), shdr.index("값"), shdr.index("합계")
            except ValueError:
                probs.append("소계본 헤더는 [축, 값, 합계] 여야 함")
            else:
                for axis in st["axes"]:
                    axis_sum = sum(to_num(r[si]) or 0 for r in srows[1:] if r[ai] == axis)
                    if abs(axis_sum - total) > 0.5:
                        probs.append(f"축 {axis}: 소계 {axis_sum:.0f} != 상세 {total:.0f}")
                    if col in hdr:
                        ci = hdr.index(col)
                        gi = hdr.index(axis)
                        for r in srows[1:]:
                            if r[ai] != axis:
                                continue
                            detail = sum(to_num(x[ci]) or 0 for x in body if x[gi] == r[vi])
                            if abs(detail - (to_num(r[si]) or 0)) > 0.5:
                                probs.append(f"{axis}={r[vi]}: 소계 {r[si]} != 상세 {detail:.0f}")
            add(8, not probs, "소계본 " + ("세 축 합계 일치" if not probs else "; ".join(probs[:5])))

    # 9. forbidden / 개인정보
    hits = []
    for root, _, files in os.walk(mod_dir):
        for f in files:
            if f == "00_requirement.md" or "실패" in f or f == "test_failure.md":
                continue
            p = os.path.join(root, f)
            try:
                txt = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            rel = os.path.relpath(p, mod_dir)
            for w in req.get("forbidden", []):
                if str(w) in txt:
                    hits.append(f"{rel}: '{w}'")
            if PHONE.search(txt):
                hits.append(f"{rel}: 전화번호 패턴")
            if EMAIL.search(txt) and "example" not in EMAIL.search(txt).group(0):
                hits.append(f"{rel}: 이메일 패턴")
    add(9, not hits, "금지 문자열 " + ("없음" if not hits else "; ".join(hits[:8])))

    # 10. SKILL.md
    spath = os.path.join(mod_dir, "07_skill", "SKILL.md")
    if not os.path.exists(spath):
        add(10, False, "07_skill/SKILL.md 없음")
    else:
        txt = open(spath, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
        probs = []
        if not m:
            probs.append("frontmatter 없음")
        else:
            try:
                fm = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError as e:
                fm, _ = {}, probs.append(f"frontmatter YAML 오류: {e}")
            nm = str(fm.get("name", ""))
            if not NAME_RE.match(nm):
                probs.append(f"name '{nm}' 이 소문자-하이픈 규칙에 안 맞음")
            elif nm != str(req.get("skill", {}).get("name", nm)):
                probs.append(f"name '{nm}' 이 요구조건서 skill.name 과 다름")
            desc = str(fm.get("description", ""))
            if len(desc) < 40:
                probs.append("description 이 40자 미만 (무엇을 하고 언제 쓰는지 3인칭으로)")
        miss = [s for s in SKILL_SECTIONS if s not in txt]
        if miss:
            probs.append("본문 절 누락: " + ", ".join(miss))
        ans = [o["file"] for o in req.get("outputs", [])]
        if not any(a in txt for a in ans):
            probs.append("입출력 예시에 정답 파일(" + " / ".join(ans) + ")이 인용되지 않음")
        add(10, not probs, "SKILL.md " + ("이상 없음" if not probs else "; ".join(probs)))

    # 11. 단계별 프롬프트가 steps 수와 맞는가
    step_files = [s.get("prompt") for s in req.get("steps", []) if s.get("prompt")]
    miss = [f for f in step_files if not os.path.exists(os.path.join(pdir, f))]
    add(11, not miss and len(step_files) == len(req.get("steps", [])),
        f"단계 {len(req.get('steps', []))}개 / 프롬프트 파일 " +
        ("모두 있음" if not miss else "누락: " + ", ".join(miss)))
    return results


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    ids = sorted(d for d in os.listdir(MODULES) if not d.startswith("_")) if args == ["--all"] else args
    exit_code = 0
    for mod in ids:
        res = check(mod)
        ok = all(r[1] for r in res)
        print(f"\n== {mod}  {'PASS' if ok else 'FAIL'} ({sum(r[1] for r in res)}/{len(res)} 자동 항목)")
        for no, passed, msg in res:
            print(f"  [{'o' if passed else 'x'}] #{no} {msg}")
        if not ok:
            exit_code = 1
    print("\n#12~14 는 수동 — CHECK.md 에서 확인자·날짜를 적습니다.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
