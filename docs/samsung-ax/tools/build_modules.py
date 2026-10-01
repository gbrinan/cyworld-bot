#!/usr/bin/env python3
"""v2 모듈 데이터 빌더 — 요구조건서(00_요구조건서.md)의 headers 를 읽어 01_데이터/ 03_테스트/ 06_붙여넣기/ 를 만든다.

    python3 docs/samsung-ax/tools/build_modules.py D_analysis
    python3 docs/samsung-ax/tools/build_modules.py --all

모든 값은 가상이다. 모델명·수요처명·금액은 실제와 무관하다.
값을 바꾸려면 이 파일의 build_* 를, 헤더를 바꾸려면 요구조건서를 고친다.
"""
import csv
import io
import json
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
    text = open(os.path.join(MODULES, mod, "00_요구조건서.md"), encoding="utf-8").read()
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
    src = os.path.join(MODULES, mod, "01_데이터", st["source"])
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
    """01_데이터 각 파일의 마크다운 표 버전. CSV 는 표로, md/json 은 코드블록으로."""
    pdir = os.path.join(MODULES, mod, "06_붙여넣기")
    os.makedirs(pdir, exist_ok=True)
    for inp in req["inputs"]:
        src = os.path.join(MODULES, mod, "01_데이터", inp["file"])
        dst = os.path.join(pdir, os.path.splitext(inp["file"])[0] + ".md")
        text = open(src, encoding="utf-8").read()
        if inp["format"] == "csv":
            rows = list(csv.reader(io.StringIO(text)))
            lines = ["|" + "|".join(rows[0]) + "|", "|" + "---|" * len(rows[0])]
            lines += ["|" + "|".join(r) + "|" for r in rows[1:]]
            body = "\n".join(lines)
        elif inp["format"] == "json":
            # 붙여넣기용은 한 줄씩 압축한다. 들여쓴 JSON은 6KB를 넘긴다.
            doc = json.loads(text)
            head = {k: v for k, v in doc.items() if k != "items"}
            lines = [json.dumps(head, ensure_ascii=False)[:-1] + ', "items": [']
            # 붙여넣기용은 link(포털 주소)를 뺀다. originallink와 중복이고 6KB를 넘긴다.
            slim = [{k: v for k, v in it.items() if k != "link"} for it in doc["items"]]
            lines += [" " + json.dumps(it, ensure_ascii=False) + ("," if i < len(slim) - 1 else "")
                      for i, it in enumerate(slim)]
            lines.append("]}")
            body = "```json\n" + "\n".join(lines) + "\n```"
        else:
            body = f"```\n{text.strip()}\n```"
        open(dst, "w", encoding="utf-8").write(
            f"<!-- {inp['file']} 붙여넣기용. 업로드가 되면 원본 파일을 올리세요."
            + (" link 필드는 originallink와 중복이라 뺐습니다. -->" if inp["format"] == "json" else " -->")
            + f"\n{body}\n")
    # 소계본도 붙여넣기용으로
    st = req.get("subtotals")
    if st:
        base = os.path.splitext(st["source"])[0] + "_소계"
        rows = list(csv.reader(open(os.path.join(MODULES, mod, "01_데이터", base + ".csv"), encoding="utf-8")))
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
    """D는 삼성이 공유한 매출 16열 헤더로 바뀌어, 생성기가 tools/build_session2_sample.py 로 옮겨 갔다.
    옛 10열(판매일자·버티컬·공급가 …) 생성 코드는 새 헤더에 쓸 데가 없어 지웠다."""
    print("D_analysis: 건너뜀 — tools/build_session2_sample.py 로 만듭니다.")




# ---------- C_proposal ----------
# 가격가이드 12모델. 가상 라인업 (MX 회의실 / BX 사이니지 / HX 호텔TV / KX 키오스크).
GUIDE = [
    ("MX-98P", "대형디스플레이", 98, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 7900000, 1),
    ("MX-85P", "대형디스플레이", 85, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 4200000, 1),
    ("MX-80P", "대형디스플레이", 80, "4K", 500, "무선화면공유·HDMI 3", "벽걸이", 3650000, 1),
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
    hdr = headers_of(req, "가격가이드.csv")
    write_csv(os.path.join(MODULES, mod, "01_데이터", "가격가이드.csv"), hdr,
              [[m, g, f"{s}인치", r, f"{b}nit", fn, ins, p, q] for m, g, s, r, b, fn, ins, p, q in GUIDE])
    write_csv(os.path.join(MODULES, mod, "01_데이터", "시장가격.csv"),
              headers_of(req, "시장가격.csv"), [list(r) for r in CRAWL])
    open(os.path.join(MODULES, mod, "01_데이터", "고객요구조건.md"), "w", encoding="utf-8").write(
        """# 고객 요구조건 — 미래로병원 신관 회의공간 (가상)

> **세션2에서 넘어온 수요처입니다.** 수요처코드 `1000425` · 미래로병원.
> 매출 데이터에서 고른 것은 "누구를 고를 것인가"까지이고, 아래 요구조건은 **영업담당이 현장에서 받아 온 것**입니다.
> 매출 헤더에는 요구조건 · 설치 환경 · 경쟁 상황이 없습니다.

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
    src = open(os.path.join(MODULES, mod, "01_데이터", "고객요구조건.md"), encoding="utf-8").read()
    open(os.path.join(MODULES, mod, "03_테스트", "고객요구조건_경계.md"), "w", encoding="utf-8").write(
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
    ("호텔TV", "한울종합건설 시공 해솔호텔 2027년 3월 재개관", "a106", "준공,호텔"),
    ("사이니지", "한울종합건설 객실 300실 규모 확정", "a107", "리뉴얼,호텔"),
    ("업계일반", "서진리테일 신규 출점 계획 전면 보류", "a108", "실적,악화"),
    ("업계일반", "서진리테일 상반기 영업손실 확대", "a109", "실적,악화"),
]
BUILDERS_A_NOISE = [
    ("업계일반", "건설경기 하반기 회복 전망 엇갈려", "b201", "동향"),
    ("업계일반", "건자재 가격 3분기 연속 상승", "b202", "동향"),
    ("디스플레이", "국내 사이니지 시장 연 7% 성장", "b203", "동향,시장"),
    ("키오스크", "무인 주문기 도입 매장 증가", "b204", "동향,키오스크"),
    ("호텔TV", "호텔 객실 IPTV 교체 주기 도래", "b205", "동향,호텔"),
    ("업계일반", "세종교육재단 신관 설계 공모 연기", "b206", "교육,연기"),
    ("업계일반", "해솔호텔 별관 로비 준공", "b207", "준공,호텔"),
    ("디스플레이", "경쟁사 신형 패널 출시 예고", "b208", "경쟁"),
    ("사이니지", "옥외광고 규제 개정안 논의", "b209", "규제"),
    ("업계일반", "건설사 ESG 공시 의무화 시행", "b210", "규제,공시"),
    ("업계일반", "미래로병원 신관 증축 설계 착수", "b211", "증축,병원"),
    ("키오스크", "공항 셀프체크인 확대 검토", "b212", "동향,키오스크"),
    ("디스플레이", "회의실 디스플레이 교체 수요 증가", "b213", "동향,오피스"),
    ("업계일반", "중대재해법 건설현장 점검 강화", "b214", "규제"),
    ("호텔TV", "지방 관광호텔 가동률 회복세", "b215", "동향,호텔"),
    ("업계일반", "건설업 인력난 심화 보도", "b216", "동향"),
    ("사이니지", "지하철 역사 안내판 교체 사업", "b217", "수주,공공"),
    ("업계일반", "세종교육재단 이사진 개편", "b218", "인사"),
]
DUP_IDX = [0, 4, 12]   # 이 세 건은 헤드라인이 한 번 더 실린다 (중복 제거 대상)


def build_A():
    mod = "A_sensing_b2b"
    req = req_of(mod)
    hdr = headers_of(req, "기사수집.csv")
    rows = [[p, h, f"https://news.example.kr/{u}", k] for p, h, u, k in BUILDERS_A_SIGNAL]
    rows += [[p, h, f"https://news.example.kr/{u}", k] for p, h, u, k in BUILDERS_A_NOISE]
    for i in DUP_IDX:                      # 같은 헤드라인, 다른 매체 url
        p, h, u, k = BUILDERS_A_NOISE[i]
        rows.append([p, h, f"https://press.example.kr/{u}r", k])
    assert len(rows) == 30, len(rows)
    write_csv(os.path.join(MODULES, mod, "01_데이터", "기사수집.csv"), hdr, rows)

    bad = [list(r) for r in rows]
    bad[1][1] = "대성건설 오피스동 준공 (담당 김O수 부장 010-1234-5678)"
    bad[5][1] = "해솔호텔 재개관, 이O영 상무 010-9876-5432 문의"
    bad[10][1] = "건자재 가격 상승, 박O호 팀장 010-2222-3333"
    write_csv(os.path.join(MODULES, mod, "03_테스트", "기사수집_실패.csv"), hdr, bad)

    # 세션1·2·3이 같은 고객사 6곳을 돈다 (삼성 메일 "고객사 숫자는 일관성 있게 6개로 유지").
    # 건설사만이 아니라 파일 이름은 대상고객사.csv 다.
    write_csv(os.path.join(MODULES, mod, "01_데이터", "대상고객사.csv"),
              headers_of(req, "대상고객사.csv"),
              [["대성건설", "건설", "코스피", "물류·오피스", "신규", "B2B 1팀"],
               ["한울종합건설", "건설", "코스닥", "호텔·상업시설", "신규", "B2B 1팀"],
               ["해솔호텔", "호텔", "비상장", "객실·로비", "기존", "B2B 1팀"],
               ["미래로병원", "병원", "비상장", "진료·대기공간", "기존", "B2B 2팀"],
               ["세종교육재단", "교육", "비상장", "강의실·행정", "신규", "B2B 2팀"],
               ["서진리테일", "유통", "코스닥", "매장·백오피스", "기존", "B2B 2팀"]])

    open(os.path.join(MODULES, mod, "01_데이터", "검색어목록.md"), "w", encoding="utf-8").write(
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
| 5 | `서진리테일 출점` | `.../rss/search?q=서진리테일+출점&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
| 6 | `미래로병원 증축` | `.../rss/search?q=미래로병원+증축&hl=ko&gl=KR&ceid=KR:ko` | 주 1회 |
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
    print(f"{mod}: 기사수집 30행(신호 9·노이즈 18·중복 3), 실패 파일, 고객사 6곳, 검색어 8개, 소계본, paste 생성")



# ---------- B_sensing_partner ----------
# 규모 하한: 객실 50실 또는 연면적 3,000㎡. 아래 값은 전부 가상이다.
DISTRICT = [
    ("부산 해운대", "해운대구 우동", "호텔", "해솔호텔", "리뉴얼", "2027-03", "객실 200실"),
    ("부산 해운대", "해운대구 중동", "호텔", "마린그랜드호텔", "리뉴얼", "2027-06", "객실 150실"),
    ("부산 해운대", "해운대구 좌동", "교육시설", "해운대제일고", "신축", "2027-09", "연면적 8,400㎡"),
    ("부산 해운대", "해운대구 우동", "상업시설", "우동 카페 A", "개점", "2026-10", "연면적 120㎡"),
    ("부산 해운대", "해운대구 센텀", "상업시설", "센텀 카페 B", "개점", "2026-11", "연면적 90㎡"),
    ("부산 해운대", "해운대구 좌동", "상업시설", "좌동 카페 C", "개점", "2026-12", "연면적 150㎡"),
    ("부산 해운대", "해운대구 중동", "병원", "해운대연합의원", "이전", "2026-11", "연면적 280㎡"),
    ("부산 해운대", "해운대구 센텀", "병원", "센텀피부과", "개점", "2027-01", "연면적 200㎡"),
    ("부산 해운대", "해운대구 좌동", "교육시설", "해운대수학학원", "개점", "2026-10", "연면적 340㎡"),
    ("대구 수성", "수성구 범어동", "오피스", "범어오피스타워", "신축", "2028-03", "연면적 42,000㎡"),
    ("대구 수성", "수성구 만촌동", "상업시설", "만촌복합몰", "리뉴얼", "2027-05", "연면적 18,000㎡"),
    ("대구 수성", "수성구 황금동", "병원", "수성요양병원", "증축", "2027-04", "병상 120"),
    ("대구 수성", "수성구 지산동", "상업시설", "지산 카페 D", "개점", "2026-10", "연면적 110㎡"),
    ("대구 수성", "수성구 두산동", "호텔", "수성레이크호텔", "신축", "2028-06", "객실 180실"),
    ("광주 상무", "서구 치평동", "오피스", "상무비즈센터", "신축", "2027-11", "연면적 26,000㎡"),
    ("광주 상무", "서구 쌍촌동", "교육시설", "상무국제학교", "신축", "2028-02", "연면적 12,000㎡"),
    ("광주 상무", "서구 화정동", "병원", "상무재활병원", "개점", "2027-07", "병상 90"),
    ("광주 상무", "서구 치평동", "상업시설", "상무 카페 E", "개점", "2026-11", "연면적 130㎡"),
]
NEWS = [  # (제목, 요약, 날짜, url키)
    ("해솔호텔 전면 리뉴얼 착공", "객실 200실 규모로 2027년 3월 재개관 예정", "2026-08-21", "n301"),
    ("해솔호텔 리뉴얼 설계 확정", "객실동과 로비를 함께 손본다", "2026-08-28", "n302"),
    ("우동 일대 호텔 리뉴얼 잇따라", "해솔호텔을 시작으로", "2026-09-02", "n303"),
    ("마린그랜드호텔 리뉴얼 추진", "객실 150실, 2027년 6월 재개관 목표", "2026-08-19", "n304"),
    ("마린그랜드호텔 시공사 선정", "중동 일대 숙박시설 정비 흐름", "2026-09-01", "n305"),
    ("중동 숙박시설 리뉴얼 확대", "마린그랜드호텔 포함 3곳", "2026-09-05", "n306"),
    ("해운대제일고 신축 착공", "2027년 9월 개교 목표, 연면적 8,400㎡", "2026-08-25", "n307"),
    ("좌동 학교 신설 부지 조성 완료", "해운대제일고 부지", "2026-09-03", "n308"),
    ("우동 카페거리에 신규 매장", "연면적 120㎡ 규모", "2026-09-04", "n309"),
    ("센텀 신규 카페 개점 준비", "11월 오픈 예정", "2026-09-06", "n310"),
    ("좌동 상권에 카페 추가 개점", "12월 오픈", "2026-09-07", "n311"),
    ("해운대연합의원 이전 개원", "중동으로 이전, 11월", "2026-08-30", "n312"),
    ("센텀피부과 신규 개원 예정", "2027년 1월", "2026-09-02", "n313"),
    ("해운대 학원가 신규 입점", "좌동 수학학원 10월 개원", "2026-09-05", "n314"),
    ("해운대 상권 유동인구 회복세", "전년 대비 8% 증가", "2026-08-27", "n315"),
    ("해운대구 신규 개점 증가", "올해 상반기 전년 대비 22% 늘어", "2026-09-01", "n316"),
    ("부산 숙박업 가동률 상승", "해운대 권역 중심", "2026-08-29", "n317"),
    ("해운대 공실률 하락 지속", "3분기 연속", "2026-09-08", "n318"),
    ("범어오피스타워 신축 인가", "연면적 42,000㎡, 2028년 준공", "2026-08-20", "n401"),
    ("만촌복합몰 리뉴얼 발주", "2027년 5월 완료 목표", "2026-08-22", "n402"),
    ("수성요양병원 증축 승인", "병상 120 규모", "2026-08-26", "n403"),
    ("지산동 카페 신규 개점", "10월 오픈", "2026-09-03", "n404"),
    ("수성레이크호텔 신축 추진", "객실 180실, 2028년 6월", "2026-09-04", "n405"),
    ("대구 수성구 상권 확장", "범어·만촌 중심", "2026-09-06", "n406"),
    ("상무비즈센터 신축 착공", "연면적 26,000㎡", "2026-08-24", "n501"),
    ("상무국제학교 설립 인가", "2028년 2월 개교", "2026-08-31", "n502"),
    ("상무재활병원 개원 예정", "2027년 7월", "2026-09-02", "n503"),
    ("치평동 카페 신규 개점", "11월", "2026-09-05", "n504"),
    ("광주 상무지구 오피스 수요 증가", "공실률 하락", "2026-09-07", "n505"),
    ("호남권 신축 인허가 증가", "전년 대비 14%", "2026-09-08", "n506"),
]


def build_B():
    mod = "B_sensing_partner"
    req = req_of(mod)
    write_csv(os.path.join(MODULES, mod, "01_데이터", "상권정보.csv"),
              headers_of(req, "상권정보.csv"), [list(r) for r in DISTRICT])
    write_csv(os.path.join(MODULES, mod, "01_데이터", "파트너정보.csv"),
              headers_of(req, "파트너정보.csv"),
              [["남해정보통신", "부산·경남", "호텔", "A", "객실 200실"],
               ["동백시스템", "부산·경남", "상업시설", "B", "연면적 5,000㎡"],
               ["가야네트웍스", "대구·경북", "오피스", "B", "연면적 10,000㎡"],
               ["빛고을솔루션", "광주·전라", "교육시설", "C", "연면적 3,000㎡"]])
    items = [{"title": t, "originallink": f"https://news.example.kr/{u}",
              "link": f"https://n.ex.kr/{u}", "description": d,
              "pubDate": p} for t, d, p, u in NEWS]
    doc = {"lastBuildDate": "2026-09-09", "total": len(items), "start": 1,
           "display": len(items), "items": items}
    os.makedirs(os.path.join(MODULES, mod, "01_데이터"), exist_ok=True)
    with open(os.path.join(MODULES, mod, "01_데이터", "뉴스수집.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    open(os.path.join(MODULES, mod, "01_데이터", "시장조사.md"), "w", encoding="utf-8").write(
        """# 시장조사 자료 (권역 지표)

기사만으로는 상권 규모와 흐름이 안 나옵니다. 기회 목록에는 안 올라가지만 **권역시장 요약**의 근거가 됩니다.

| 권역 | 지표 | 값 | 출처 | 조사시점 |
|---|---|---|---|---|
| 부산 해운대 | 유동인구 전년 대비 | +8% | 상권정보 시스템(가상) | 2026-08 |
| 부산 해운대 | 공실률 | 6.2% (3분기 연속 하락) | 상권정보 시스템(가상) | 2026-08 |
| 부산 해운대 | 신규 개점 수 (상반기) | 전년 대비 +22% | 구청 인허가 통계(가상) | 2026-07 |
| 부산 해운대 | 숙박업 가동률 | 71% (전년 64%) | 관광 통계(가상) | 2026-08 |
| 부산 해운대 | 숙박시설 리뉴얼 건수 | 3건 (전년 1건) | 상권정보 시스템(가상) | 2026-08 |
| 대구 수성 | 공실률 | 9.1% | 상권정보 시스템(가상) | 2026-08 |
| 광주 상무 | 공실률 | 8.4% (하락) | 상권정보 시스템(가상) | 2026-08 |
| 전국 | 상업시설 신규 개점 | 전년 대비 +11% | 업계 자료(가상) | 2026-07 |

**모든 수치는 가상입니다.**
""")
    bad = [["파트너사", "담당권역", "주력버티컬", "최근분기실적등급", "시공가능규모", "계약단가", "마진율"],
           ["남해정보통신", "부산·경남", "호텔", "A", "객실 200실", "1,240,000", "18%"],
           ["동백시스템", "부산·경남", "상업시설", "B", "연면적 5,000㎡", "980,000", "15%"],
           ["가야네트웍스", "대구·경북", "오피스", "B", "연면적 10,000㎡", "1,050,000", "16%"],
           ["빛고을솔루션", "광주·전라", "교육시설", "C", "연면적 3,000㎡", "870,000", "12%"]]
    write_csv(os.path.join(MODULES, mod, "03_테스트", "파트너정보_실패.csv"), bad[0], bad[1:])
    write_subtotals(mod, req)
    write_paste(mod, req)
    print(f"{mod}: 뉴스 30건(해운대 18·타권역 12), 상권 18행, 파트너 4곳, 시장조사 8행, 실패 파일, 소계본, paste 생성")



# ---------- E_supplier (템플릿 검증용 예제) ----------
# 공급사명·단가·이력은 전부 가상이다.
SUPPLIERS = ["대광상사", "성진물산", "동진테크", "신우산업", "제일전자", "한백금속"]
# 요청 품목: 알루미늄 프로파일. (규격, 단가, 최소주문수량, 납기일수, 결제조건, 견적일)
PROFILE = {
    "대광상사":  ("6063-T5 2.0mm", 9800, 1000, 25, "현금 30일", "2026-09-01"),
    "성진물산":  ("6063-T5 2.0mm", 10400, 500, 15, "현금 30일", "2026-09-03"),
    "동진테크":  ("6063-T5 2.2mm", 9950, 3000, 18, "현금 60일", "2026-09-02"),
    "신우산업":  ("6063-T5 1.8mm", 9600, 1000, 12, "현금 30일", "2026-09-04"),
    "제일전자":  ("6063-T5 2.0mm", 10100, 1000, 20, "현금 30일", "2026-05-15"),
    "한백금속":  ("6063-T5 2.0mm", 11200, 500, 10, "현금 30일", "2026-09-05"),
}
# 노이즈 3품목
OTHERS = [
    ("스테인리스 볼트 M8", "STS304 M8x30", 320, 5000, 12, "현금 30일"),
    ("실리콘 개스킷", "두께 3mm 내열 200도", 1450, 2000, 14, "현금 30일"),
    ("전원 케이블 3C", "3C x 2.5SQ", 2800, 1000, 16, "현금 60일"),
]
HISTORY = {"대광상사": (71, 3, 36), "성진물산": (96, 0, 48), "동진테크": (88, 1, 24),
           "신우산업": (93, 2, 12), "제일전자": (82, 1, 60), "한백금속": (97, 0, 18)}


def build_E():
    mod = "E_supplier"
    req = req_of(mod)
    rnd = random.Random(SEED)
    rows = []
    for s in SUPPLIERS:
        spec, price, moq, lead, pay, qdate = PROFILE[s]
        rows.append([s, "알루미늄 프로파일", spec, price, moq, lead, pay, qdate])
    for item, spec, base, moq, lead, pay in OTHERS:
        for s in SUPPLIERS:
            rows.append([s, item, spec, base + rnd.randrange(-40, 60, 10), moq,
                         lead + rnd.randint(-2, 4), pay,
                         f"2026-09-0{rnd.randint(1, 5)}"])
    assert len(rows) == 24, len(rows)
    write_csv(os.path.join(MODULES, mod, "01_데이터", "견적서.csv"), headers_of(req, "견적서.csv"), rows)
    write_csv(os.path.join(MODULES, mod, "01_데이터", "공급사이력.csv"),
              headers_of(req, "공급사이력.csv"),
              [[s, f"{HISTORY[s][0]}%", HISTORY[s][1], HISTORY[s][2]] for s in SUPPLIERS])
    open(os.path.join(MODULES, mod, "01_데이터", "구매요청.md"), "w", encoding="utf-8").write(
        """# 구매 요청서 — 2026-09-12

| 항목 | 내용 |
|---|---|
| 품목 | 알루미늄 프로파일 |
| 필요수량 | **2,000개** |
| 희망납기일수 | **20일 이내** |
| 예산 | **24,000,000원** |
| 필수규격 | 6063-T5, **두께 2.0mm 이상** |

- 견적 유효기간은 사내 기준 **90일**입니다. 오늘(2026-09-12) 기준 2026-06-14 이전 견적은 재견적을 받습니다.
- 모든 값은 가상입니다.
""")
    # 경계 테스트용: 필수규격 줄 삭제
    src = open(os.path.join(MODULES, mod, "01_데이터", "구매요청.md"), encoding="utf-8").read()
    open(os.path.join(MODULES, mod, "03_테스트", "구매요청_경계.md"), "w", encoding="utf-8").write(
        "\n".join(l for l in src.split("\n") if "필수규격" not in l))
    write_subtotals(mod, req)
    write_paste(mod, req)
    print(f"{mod}: 견적 24행(요청 품목 6 · 노이즈 18), 이력 6곳, 구매 요청, 경계 파일, 소계본, paste 생성")


BUILDERS = {"D_analysis": build_D, "C_proposal": build_C,
            "A_sensing_b2b": build_A, "B_sensing_partner": build_B,
            "E_supplier": build_E}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    for mod in (BUILDERS if args == ["--all"] else args):
        BUILDERS[mod]()


if __name__ == "__main__":
    main()
