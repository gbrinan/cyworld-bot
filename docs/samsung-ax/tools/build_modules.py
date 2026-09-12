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
    # 코드 실행이 안 되는 환경용: 대상 버티컬(호텔) 모델별 집계.
    # 사람이 미리 집계해 주는 것이 실제 업무의 순서이기도 하다.
    agg = {}
    for i, r in enumerate(rows, start=2):
        if r[1] != "호텔":
            continue
        m = r[4]
        a = agg.setdefault(m, [r[3], 0, 0, 0, set(), []])
        a[1] += 1; a[2] += r[6]; a[3] += r[7]; a[4].add(r[2]); a[5].append(str(i))
    hdr2 = headers_of(req, "sales_history_호텔모델별.csv")
    write_csv(os.path.join(MODULES, mod, "01_data", "sales_history_호텔모델별.csv"), hdr2,
              [[m, v[0], v[1], v[2], v[3], len(v[4]), " ".join(v[5])]
               for m, v in sorted(agg.items(), key=lambda x: -x[1][3])])
    write_subtotals(mod, req)
    write_paste(mod, req)
    print(f"{mod}: sales_history 52행, 소계본, 실패 파일, target_account, paste 생성")



# ---------- C_proposal ----------
# 가격가이드 12모델. 가상 라인업 (MX 회의실 / BX 사이니지 / HX 호텔TV / KX 키오스크).
GUIDE = [
    ("MX-98P", "대형디스플레이", 98, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 7900000, 1),
    ("MX-85P", "대형디스플레이", 85, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 4200000, 1),
    ("MX-75P", "대형디스플레이", 75, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 2950000, 1),
    ("MX-65P", "대형디스플레이", 65, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 1880000, 1),
    ("BX-65S", "사이니지", 65, "4K", 400, "HDMI 2", "벽걸이/스탠드", 1480000, 2),
    ("BX-55S", "사이니지", 55, "4K", 400, "HDMI 2", "벽걸이/스탠드", 1050000, 2),
    ("BX-43S", "사이니지", 43, "FHD", 350, "HDMI 2", "벽걸이", 780000, 2),
    ("HX-55T", "호텔TV", 55, "4K", 300, "호텔모드", "벽걸이/스탠드", 610000, 10),
    ("HX-50T", "호텔TV", 50, "4K", 300, "호텔모드", "벽걸이/스탠드", 520000, 10),
    ("HX-43T", "호텔TV", 43, "FHD", 300, "호텔모드", "벽걸이/스탠드", 420000, 10),
    ("KX-55K", "키오스크", 55, "4K", 500, "터치·스탠드형", "스탠드", 2600000, 1),
    ("KX-43K", "키오스크", 43, "FHD", 450, "터치·스탠드형", "스탠드", 1950000, 1),
]
# 네이버 크롤 더미. 경쟁사 엘리온(EL)·노바뷰(NV)는 가상. 가격만 낮고 밝기가 요구에 미달한다.
CRAWL = [
    ("마켓원", "MX-85P", 4536000, "85인치 4K 밝기 500nit 무선화면공유 HDMI 3포트 벽걸이"),
    ("비즈샵", "MX-65P", 1955000, "65인치 4K 밝기 500nit 무선화면공유 HDMI 3포트"),
    ("오피스몰", "MX-75P", 3120000, "75인치 4K 밝기 500nit 무선화면공유"),
    ("마켓원", "BX-65S", 1420000, "65인치 4K 밝기 400nit HDMI 2포트"),
    ("비즈샵", "BX-55S", 1010000, "55인치 4K 밝기 400nit HDMI 2포트"),
    ("오피스몰", "KX-55K", 2780000, "55인치 4K 터치 스탠드형"),
    ("마켓원", "EL-8500", 3780000, "85인치 4K 밝기 350nit 화면공유 동글 별매"),
    ("오피스몰", "EL-6500", 1590000, "65인치 4K 밝기 350nit HDMI 2포트"),
    ("비즈샵", "NV-8600", 3650000, "86인치 4K 밝기 350nit HDMI 2포트"),
    ("마켓원", "NV-6500", 1520000, "65인치 4K 밝기 350nit"),
]


def build_C():
    mod = "C_proposal"
    req = req_of(mod)
    hdr = headers_of(req, "tv_price_guide.csv")
    write_csv(os.path.join(MODULES, mod, "01_data", "tv_price_guide.csv"), hdr,
              [[m, g, f"{s}인치", r, f"{b}nit", fn, ins, p, q] for m, g, s, r, b, fn, ins, p, q in GUIDE])
    write_csv(os.path.join(MODULES, mod, "01_data", "naver_crawl.csv"),
              headers_of(req, "naver_crawl.csv"), [list(r) for r in CRAWL])
    open(os.path.join(MODULES, mod, "01_data", "customer_request.md"), "w", encoding="utf-8").write(
        """# 고객 요구조건 — 한빛에스앤디 신규 사무공간 (가상)

| 항목 | 내용 |
|---|---|
| 화면크기 | 대회의실 80~90인치 / 소회의실 60~70인치 |
| 사용목적 | 회의실 화면 공유·발표. 상시 표출 아님 |
| 주요기능 | **무선 화면공유 필수**, HDMI 3포트 이상 |
| 설치환경 | 창측 회의실이라 주간 조도 높음. **밝기 500nit 이상**. 벽걸이 |
| 수량 | 회의실 6개 — 대회의실 2 · 소회의실 4 |
| 예산 | **2,000만원** (설치비 별도) |

- 납품 희망: 2026년 11월
- 모든 정보는 가상입니다.
""")
    # 경계 테스트용: 예산 줄 삭제
    src = open(os.path.join(MODULES, mod, "01_data", "customer_request.md"), encoding="utf-8").read()
    open(os.path.join(MODULES, mod, "03_tests", "customer_request_경계.md"), "w", encoding="utf-8").write(
        "\n".join(l for l in src.split("\n") if "예산" not in l))
    write_subtotals(mod, req)
    write_paste(mod, req)
    print(f"{mod}: 가격가이드 12모델, 크롤 10건, 요구조건, 경계 파일, 소계본, paste 생성")



# ---------- A_sensing_b2b ----------
# 가상 상장 건설사. 실제 기업과 무관하다.
BUILDERS_A_SIGNAL = [
    ("사이니지", "대성건설 물류복합 1.2조 수주", "a101", "수주,공시"),
    ("디스플레이", "대성건설 오피스동 2028년 6월 준공", "a102", "준공,오피스"),
    ("업계일반", "대성건설 유형자산취득 결정 공시", "a103", "투자,공시"),
    ("디스플레이", "대성건설 스마트오피스 설계 착수", "a104", "착공,오피스"),
    ("호텔TV", "한울종합건설 호텔 2곳 리뉴얼 착공", "a105", "착공,호텔"),
    ("호텔TV", "한울 강릉호텔 2027년 3월 재개관", "a106", "준공,호텔"),
    ("사이니지", "한울종합건설 객실 300실 규모 확정", "a107", "리뉴얼,호텔"),
    ("업계일반", "서진이엔씨 수주잔고 3년래 최저", "a108", "실적,악화"),
    ("업계일반", "서진이엔씨 상반기 영업손실 확대", "a109", "실적,악화"),
]
BUILDERS_A_NOISE = [
    ("업계일반", "건설경기 하반기 회복 전망 엇갈려", "b201", "동향"),
    ("업계일반", "건자재 가격 3분기 연속 상승", "b202", "동향"),
    ("디스플레이", "국내 사이니지 시장 연 7% 성장", "b203", "동향,시장"),
    ("키오스크", "무인 주문기 도입 매장 증가", "b204", "동향,키오스크"),
    ("호텔TV", "호텔 객실 IPTV 교체 주기 도래", "b205", "동향,호텔"),
    ("업계일반", "동보건설 주택 분양 일정 연기", "b206", "주택,연기"),
    ("업계일반", "광명종합건설 소규모 상가 준공", "b207", "준공,상업시설"),
    ("디스플레이", "경쟁사 신형 패널 출시 예고", "b208", "경쟁"),
    ("사이니지", "옥외광고 규제 개정안 논의", "b209", "규제"),
    ("업계일반", "건설사 ESG 공시 의무화 시행", "b210", "규제,공시"),
    ("업계일반", "세아이앤씨 병원 증축 설계 수주", "b211", "수주,병원"),
    ("키오스크", "공항 셀프체크인 확대 검토", "b212", "동향,키오스크"),
    ("디스플레이", "회의실 디스플레이 교체 수요 증가", "b213", "동향,오피스"),
    ("업계일반", "중대재해법 건설현장 점검 강화", "b214", "규제"),
    ("호텔TV", "지방 관광호텔 가동률 회복세", "b215", "동향,호텔"),
    ("업계일반", "건설업 인력난 심화 보도", "b216", "동향"),
    ("사이니지", "지하철 역사 안내판 교체 사업", "b217", "수주,공공"),
    ("업계일반", "동보건설 임원 인사 단행", "b218", "인사"),
]
DUP_IDX = [0, 4, 12]   # 이 세 건은 헤드라인이 한 번 더 실린다 (중복 제거 대상)


def build_A():
    mod = "A_sensing_b2b"
    req = req_of(mod)
    hdr = headers_of(req, "rss_feed.csv")
    rows = [[p, h, f"https://news.example.kr/{u}", k] for p, h, u, k in BUILDERS_A_SIGNAL]
    rows += [[p, h, f"https://news.example.kr/{u}", k] for p, h, u, k in BUILDERS_A_NOISE]
    for i in DUP_IDX:                      # 같은 헤드라인, 다른 매체 url
        p, h, u, k = BUILDERS_A_NOISE[i]
        rows.append([p, h, f"https://press.example.kr/{u}r", k])
    assert len(rows) == 30, len(rows)
    write_csv(os.path.join(MODULES, mod, "01_data", "rss_feed.csv"), hdr, rows)

    bad = [list(r) for r in rows]
    bad[1][1] = "대성건설 오피스동 준공 (담당 김O수 부장 010-1234-5678)"
    bad[5][1] = "한울 강릉호텔 재개관, 이O영 상무 010-9876-5432 문의"
    bad[10][1] = "건자재 가격 상승, 박O호 팀장 010-2222-3333"
    write_csv(os.path.join(MODULES, mod, "03_tests", "rss_feed_실패.csv"), hdr, bad)

    write_csv(os.path.join(MODULES, mod, "01_data", "target_builders.csv"),
              headers_of(req, "target_builders.csv"),
              [["대성건설", "코스피", "물류·오피스", "신규", "B2B 1팀"],
               ["한울종합건설", "코스닥", "호텔·상업시설", "신규", "B2B 1팀"],
               ["서진이엔씨", "코스피", "토목·플랜트", "기존", "B2B 2팀"],
               ["동보건설", "코스피", "주택", "기존", "B2B 2팀"],
               ["세아이앤씨", "코스닥", "병원·교육", "신규", "B2B 1팀"],
               ["광명종합건설", "코넥스", "상업시설", "신규", "B2B 1팀"]])

    open(os.path.join(MODULES, mod, "01_data", "rss_sources.md"), "w", encoding="utf-8").write(
        """# 수집 검색어와 RSS 주소 (단계 1의 정답)

구글 뉴스 RSS 주소 형식입니다. `q=` 뒤의 검색어만 바꿔 씁니다.

```
https://news.google.com/rss/search?q={검색어}&hl=ko&gl=KR&ceid=KR:ko
```

검색어는 **회사명 × 신호어**로 조합합니다. 신호어는 수주·착공·준공·투자·리뉴얼·오픈입니다.

| # | 검색어 | RSS 주소 | 수집주기 |
|---|---|---|---|
| 1 | `대성건설 수주` | `.../rss/search?q=대성건설+수주&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 2 | `대성건설 준공` | `.../rss/search?q=대성건설+준공&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 3 | `한울종합건설 착공` | `.../rss/search?q=한울종합건설+착공&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 4 | `한울종합건설 리뉴얼` | `.../rss/search?q=한울종합건설+리뉴얼&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 5 | `서진이엔씨 수주` | `.../rss/search?q=서진이엔씨+수주&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 6 | `세아이앤씨 병원 증축` | `.../rss/search?q=세아이앤씨+병원+증축&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 7 | `건설사 유형자산취득 공시` | `.../rss/search?q=건설사+유형자산취득+공시&hl=ko&gl=KR&ceid=KR:ko` | 월 1회 |
| 8 | `호텔 리뉴얼 착공` | `.../rss/search?q=호텔+리뉴얼+착공&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |

**넣지 않은 조합과 이유**

| 조합 | 왜 뺐나 |
|---|---|
| `건설` 단독 | 하루 수백 건. 담당 수요처와 무관한 것이 대부분 |
| `대성건설` 단독 | 인사·주가 기사가 섞임. 신호어를 붙여야 영업 신호만 남음 |
| `디스플레이 수주` | 우리 품목이지만 고객사 신호가 아님. 경쟁 동향은 별도 |

**모든 회사명은 가상입니다.**
""")
    write_subtotals(mod, req)
    write_paste(mod, req)
    print(f"{mod}: rss_feed 30행(신호 9·노이즈 18·중복 3), 실패 파일, 건설사 6곳, 검색어 8개, 소계본, paste 생성")


BUILDERS = {"D_analysis": build_D, "C_proposal": build_C, "A_sensing_b2b": build_A}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    for mod in (BUILDERS if args == ["--all"] else args):
        BUILDERS[mod]()


if __name__ == "__main__":
    main()
