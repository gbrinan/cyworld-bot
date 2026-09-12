#!/usr/bin/env python3
"""v2 모듈 데이터 빌더 — 요구조건서(00_requirement.md)의 headers 를 읽어 01_data/ 03_tests/ 06_paste/ 를 만든다.

    python3 docs/samsung-ax/tools/build_modules.py D_analysis
    python3 docs/samsung-ax/tools/build_modules.py --all

모든 값은 가상이다. 모델명·수요처명·금액은 실제와 무관하다.
값을 바꾸려면 이 파일의 build_* 를, 헤더를 바꾸려면 요구조건서를 고친다.
"""
import csv
import io
import os
import random
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = os.path.normpath(os.path.join(HERE, "..", "context_pack", "modules"))
SEED = 20261001


# ---------- 공통 ----------
def req_of(mod):
    text = open(os.path.join(MODULES, mod, "00_requirement.md"), encoding="utf-8").read()
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1))


def headers_of(req, fname):
    return [str(h) for h in next(i for i in req["inputs"] if i["file"] == fname)["headers"]]


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def write_subtotals(mod, req):
    """subtotals 정의대로 [축, 값, 합계] 소계본을 만든다. sum 컬럼이 없으면 건수."""
    st = req["subtotals"]
    src = os.path.join(MODULES, mod, "01_data", st["source"])
    rows = list(csv.reader(open(src, encoding="utf-8", newline="")))
    hdr, body = rows[0], rows[1:]
    out = []
    for axis in st["axes"]:
        gi = hdr.index(axis)
        groups = {}
        for r in body:
            v = float(r[hdr.index(st["sum"])]) if st["sum"] in hdr else 1
            groups[r[gi]] = groups.get(r[gi], 0) + v
        for k in sorted(groups):
            out.append([axis, k, int(groups[k])])
    write_csv(os.path.splitext(src)[0] + "_소계.csv", ["축", "값", "합계"], out)


def write_paste(mod, req):
    """01_data 각 파일의 마크다운 표 버전. CSV 는 표로, md/json 은 코드블록으로."""
    pdir = os.path.join(MODULES, mod, "06_paste")
    os.makedirs(pdir, exist_ok=True)
    for inp in req["inputs"]:
        src = os.path.join(MODULES, mod, "01_data", inp["file"])
        dst = os.path.join(pdir, os.path.splitext(inp["file"])[0] + ".md")
        text = open(src, encoding="utf-8").read()
        if inp["format"] == "csv":
            rows = list(csv.reader(io.StringIO(text)))
            lines = ["|" + "|".join(rows[0]) + "|", "|" + "---|" * len(rows[0])]
            lines += ["|" + "|".join(r) + "|" for r in rows[1:]]
            body = "\n".join(lines)
        else:
            body = f"```\n{text.strip()}\n```"
        open(dst, "w", encoding="utf-8").write(
            f"<!-- {inp['file']} 붙여넣기용. 업로드가 되면 원본 파일을 올리세요. -->\n{body}\n")
    # 소계본도 붙여넣기용으로
    st = req.get("subtotals")
    if st:
        base = os.path.splitext(st["source"])[0] + "_소계"
        rows = list(csv.reader(open(os.path.join(MODULES, mod, "01_data", base + ".csv"), encoding="utf-8")))
        lines = ["| " + " | ".join(rows[0]) + " |", "|---|---|---|"] + ["| " + " | ".join(r) + " |" for r in rows[1:]]
        open(os.path.join(pdir, base + ".md"), "w", encoding="utf-8").write(
            "<!-- 코드 실행이 안 되는 환경용 소계본. 세 축의 합계가 서로 같습니다. -->\n" + "\n".join(lines) + "\n")


# ---------- D_analysis ----------
# 가상 모델 체계. 실제 라인업과 무관.
MODELS = {  # 모델명: (제품군, 공급가)
    "HX-43T": ("호텔TV", 420000), "HX-50T": ("호텔TV", 520000), "HX-55T": ("호텔TV", 610000),
    "BX-43S": ("사이니지", 780000), "BX-55S": ("사이니지", 1050000), "BX-65S": ("사이니지", 1480000),
    "MX-85P": ("대형디스플레이", 4200000), "MX-98P": ("대형디스플레이", 7900000),
    "KX-55K": ("키오스크", 2600000),
    "ST-H1": ("액세서리", 45000), "WM-1": ("액세서리", 38000),
}


def build_D():
    mod = "D_analysis"
    req = req_of(mod)
    hdr = headers_of(req, "sales_history.csv")
    assert hdr == ["판매일자", "버티컬", "수요처", "제품군", "모델명", "공급가", "판매수량", "판매금액", "프로젝트/용도", "지역"]
    rnd = random.Random(SEED)
    R = []  # (일자, 버티컬, 수요처, 모델, 수량, 용도, 지역)

    # --- 호텔 22행 (planted) ---
    hotels = [("해솔호텔 부산", "부산·경남"), ("온빛리조트 강원", "경기"), ("라온스테이 서울", "서울"),
              ("푸른바다호텔 제주", "제주"), ("하늘정원호텔 경기", "경기")]
    # HX-55T + ST-H1 같은 수요처·같은 달 4회 (planted 1)
    for (h, reg), ym, qty in [(hotels[0], "2025-03", 96), (hotels[2], "2025-09", 140), (hotels[3], "2026-02", 88), (hotels[1], "2026-06", 110)]:
        R.append((f"{ym}-1{rnd.randint(0, 8)}", "호텔", h, "HX-55T", qty, "객실 TV 교체", reg))
        R.append((f"{ym}-2{rnd.randint(0, 6)}", "호텔", h, "ST-H1", qty, "객실 TV 스탠드", reg))
    # 로비 BX-65S 3개 수요처 (planted 2)
    for (h, reg), d, q in [(hotels[0], "2025-04-08", 2), (hotels[2], "2025-10-15", 4), (hotels[3], "2026-03-03", 2)]:
        R.append((d, "호텔", h, "BX-65S", q, "로비 안내 사이니지", reg))
    # 나머지 호텔 11행 (HX-50T·HX-43T·KX·MX 등 — 패턴을 흐리지 않는 수준)
    extra = [("2025-01-20", hotels[4], "HX-50T", 60, "객실 TV 교체"), ("2025-05-12", hotels[1], "HX-43T", 40, "직원 숙소"),
             ("2025-06-30", hotels[4], "BX-55S", 1, "연회장 안내"), ("2025-07-22", hotels[0], "KX-55K", 1, "셀프 체크인"),
             ("2025-08-19", hotels[2], "MX-85P", 1, "연회장"), ("2025-11-05", hotels[4], "HX-55T", 30, "스위트 객실"),
             ("2025-12-11", hotels[1], "WM-1", 40, "객실 TV 벽걸이"), ("2026-01-14", hotels[3], "HX-50T", 20, "별관 객실"),
             ("2026-04-21", hotels[0], "BX-43S", 2, "엘리베이터 홀"), ("2026-05-08", hotels[2], "KX-55K", 2, "셀프 체크인"),
             ("2026-07-16", hotels[4], "ST-H1", 30, "객실 TV 스탠드")]
    for d, (h, reg), m, q, u in extra:
        R.append((d, "호텔", h, m, q, u, reg))
    assert len(R) == 22

    # --- 노이즈 30행: 오피스·병원·상업시설·교육시설 (planted 3) ---
    noise = [
        ("오피스", [("미래테크", "서울"), ("한결소프트", "경기"), ("청우물산", "대구·경북")],
         [("MX-85P", "회의실", 1, 3), ("MX-65P" if False else "BX-55S", "로비 안내", 1, 2), ("MX-98P", "대회의실", 1, 1), ("WM-1", "회의실 벽걸이", 2, 4)]),
        ("병원", [("가온의료재단", "서울"), ("세움병원", "광주·전라")],
         [("BX-43S", "외래 대기실 안내", 3, 8), ("KX-55K", "접수 키오스크", 1, 3), ("BX-55S", "로비 안내", 1, 2)]),
        ("상업시설", [("마루몰", "경기"), ("별빛아울렛", "부산·경남")],
         [("BX-55S", "매장 프로모션", 4, 12), ("KX-55K", "안내 키오스크", 2, 4), ("MX-98P", "미디어월", 1, 2)]),
        ("교육시설", [("다온고등학교", "대구·경북"), ("새빛대학교", "광주·전라")],
         [("BX-65S", "강의실 전자칠판 대체", 4, 10), ("MX-85P", "대강당", 1, 2), ("BX-43S", "복도 안내", 2, 4)]),
    ]
    dates = [f"{y}-{m:02d}-{rnd.randint(2, 27):02d}" for y in (2025, 2026) for m in range(1, 13)][:20]
    quota = {"오피스": 8, "병원": 6, "상업시설": 8, "교육시설": 8}
    for vert, accts, prods in noise:
        for i in range(quota[vert]):
            a, reg = accts[i % len(accts)]
            m, u, lo, hi = prods[i % len(prods)]
            R.append((rnd.choice(dates), vert, a, m, rnd.randint(lo, hi), u, reg))
    assert len(R) == 52

    R.sort(key=lambda r: r[0])
    rows = []
    for d, v, a, m, q, u, reg in R:
        grp, price = MODELS[m]
        rows.append([d, v, a, grp, m, price, q, price * q, u, reg])
    write_csv(os.path.join(MODULES, mod, "01_data", "sales_history.csv"), hdr, rows)

    # 실패 테스트 파일: 판매금액 오류 3행 + 버티컬 오타 1행
    bad = [list(r) for r in rows]
    for idx in (5, 23, 41):
        bad[idx][7] = bad[idx][7] + 150000
    bad[12][1] = "호탤"
    write_csv(os.path.join(MODULES, mod, "03_tests", "sales_history_실패.csv"), hdr, bad)

    open(os.path.join(MODULES, mod, "01_data", "target_account.md"), "w", encoding="utf-8").write(
        "# 분석 대상 수요처\n\n| 수요처명 | 버티컬 | 프로젝트/용도 |\n|---|---|---|\n"
        "| 해솔호텔 제주 | 호텔 | 신축 (객실 120실 + 로비, 2027년 3월 개관 예정) |\n\n"
        "- 참고: 같은 체인의 해솔호텔 부산이 과거 구매 이력에 있습니다.\n- 모든 정보는 가상입니다.\n")
    write_subtotals(mod, req)
    write_paste(mod, req)
    print(f"{mod}: sales_history 52행, 소계본, 실패 파일, target_account, paste 생성")


BUILDERS = {"D_analysis": build_D}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    for mod in (BUILDERS if args == ["--all"] else args):
        BUILDERS[mod]()


if __name__ == "__main__":
    main()
