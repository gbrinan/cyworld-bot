#!/usr/bin/env python3
"""삼성전자 B2B AX 과정 실습용 더미 데이터 생성기.

모든 값은 가상입니다. 실제 고객사·파트너·실적과 무관합니다.
컬럼 헤더는 사전과제 '필요 엑셀 컬럼 헤더 구상'을 반영해 교체할 수 있습니다.

사용법:
    python3 docs/samsung-ax/tools/make_dummy_data.py
"""

import csv
import os
import random
from datetime import date, timedelta

SEED = 20261001
ROOT = os.path.join(os.path.dirname(__file__), "..", "context_pack")
BASE_MONTH = "2026-09"


def w(rel_path, header, rows):
    """CSV 한 장을 쓴다."""
    path = os.path.normpath(os.path.join(ROOT, rel_path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{path}  ({len(rows)}행)")


# --------------------------------------------------------------------------
# team_b2b — 수요처 AX전략 기반 NBM Lead 발굴
# --------------------------------------------------------------------------

B2B_ACCOUNTS = [
    # (코드, 고객사명, 업종, 임직원수, 지역, 담당경로)
    ("A001", "가온건설", "건설", 4200, "서울", "대기업"),
    ("A002", "한빛전자", "제조", 3100, "경기", "대기업"),
    ("A003", "너울금융지주", "금융", 2600, "서울", "대기업"),
    ("A004", "미르통신", "통신", 5400, "서울", "대기업"),
    ("A005", "새벽유통", "유통", 1800, "경기", "대기업"),
    ("A006", "다솜서비스", "서비스", 950, "부산", "대기업"),
    ("A007", "온누리개발", "건설", 2200, "인천", "대기업"),
    ("A008", "빛솔제약", "제조", 1400, "충북", "대기업"),
    ("A009", "터울에너지", "제조", 3600, "울산", "대기업"),
    ("A010", "하람물산", "유통", 1100, "대구", "대기업"),
    ("A011", "가람시청", "관공서", 800, "경기", "공공"),
    ("A012", "누리고등학교", "초중고", 120, "서울", "공공"),
    ("A013", "슬기대학교", "대학", 1600, "대전", "공공"),
    ("A014", "여울구청", "관공서", 640, "서울", "공공"),
    ("A015", "아름중학교", "초중고", 90, "경기", "공공"),
]

B2B_ITEMS = ["SAC", "모바일", "IT제품", "DID", "가전"]

NEWS_SIGNALS = [
    ("신사옥·증축", "신사옥 착공 발표", "SAC"),
    ("설비투자", "생산라인 증설 투자 공시", "SAC"),
    ("조직개편", "디지털혁신팀 신설", "IT제품"),
    ("스마트오피스", "스마트오피스 전환 추진", "모바일"),
    ("공공입찰", "노후 냉난방 교체 공고", "SAC"),
    ("업무환경", "임직원 모바일 업무환경 개편", "모바일"),
    ("친환경", "에너지 효율 설비 교체 검토", "SAC"),
    ("매장확대", "신규 지점 개설 계획", "DID"),
]

MEDIA = ["산업일보", "건설경제", "디지털타임즈", "지역뉴스", "공공조달공고", "IR 자료"]


def build_b2b():
    rnd = random.Random(SEED)

    # --- ② Sensing: 업종 뉴스·투자 동향 ---
    news = []
    d0 = date(2026, 7, 1)
    for i in range(48):
        acc = rnd.choice(B2B_ACCOUNTS)
        sig, title, item = rnd.choice(NEWS_SIGNALS)
        day = d0 + timedelta(days=rnd.randint(0, 75))
        news.append([
            f"N{i+1:03d}",
            day.isoformat(),
            rnd.choice(MEDIA),
            acc[2],
            acc[1],
            sig,
            f"{acc[1]}, {title}",
            item,
            rnd.choice(["높음", "보통", "낮음"]),
        ])
    news.sort(key=lambda r: r[1])
    w("team_b2b/agent02_sensing/data/industry_news.csv",
      ["출처ID", "보도일", "매체", "업종", "고객사명", "신호유형", "요약", "관련품목군", "신뢰도"],
      news)

    # --- ② Sensing: 고객사 마스터 ---
    accounts = []
    for code, name, ind, emp, region, route in B2B_ACCOUNTS:
        last = date(2026, rnd.randint(1, 8), rnd.randint(1, 28))
        accounts.append([
            code, name, ind, emp, region, route,
            rnd.choice(B2B_ITEMS),
            last.isoformat(),
            rnd.choice(["신규", "기존", "휴면"]),
            f"담당자 {code[-1]}",  # 가명
        ])
    w("team_b2b/agent02_sensing/data/target_accounts.csv",
      ["고객사코드", "고객사명", "업종", "임직원수", "지역", "담당경로",
       "최근거래품목군", "최근거래일", "거래상태", "담당자(가명)"],
      accounts)

    # --- ③ Action: 제품 카탈로그 ---
    catalog = [
        ["P-SAC-01", "SAC", "시스템에어컨 4WAY 표준형", "냉방 15.5kW / 인버터", "사무동 층별 20대 구성", 3_200_000, "참고 단가"],
        ["P-SAC-02", "SAC", "시스템에어컨 고효율형", "냉방 22.4kW / 고효율 등급", "생산동 대공간 8대 구성", 4_800_000, "참고 단가"],
        ["P-SAC-03", "SAC", "중앙 제어 컨트롤러", "최대 128대 제어 / 원격 모니터링", "SAC 통합 관제", 1_500_000, "참고 단가"],
        ["P-MOB-01", "모바일", "업무용 스마트폰 표준형", "6.4인치 / 업무 보안 지원", "임직원 배포 100대", 850_000, "참고 단가"],
        ["P-MOB-02", "모바일", "업무용 태블릿", "11인치 / 현장 입력용", "현장직 배포 40대", 720_000, "참고 단가"],
        ["P-IT-01", "IT제품", "업무용 모니터 27형", "QHD / 높이조절", "사무 좌석 200석", 340_000, "참고 단가"],
        ["P-IT-02", "IT제품", "노트북 업무형", "14인치 / 경량", "이동 근무 60대", 1_450_000, "참고 단가"],
        ["P-DID-01", "DID", "디지털 사이니지 55형", "밝기 500nit / 24시간 구동", "로비·매장 12대", 1_900_000, "참고 단가"],
    ]
    w("team_b2b/agent03_action/data/product_catalog.csv",
      ["품목코드", "품목군", "모델명", "주요사양", "제안구성(예시)", "참고단가(원)", "비고"],
      catalog)

    # --- ④ Analysis: Lead/BO 파이프라인 ---
    stages = ["Lead", "BO", "제안", "협상", "수주", "실주"]
    pipeline = []
    for i in range(66):
        acc = rnd.choice(B2B_ACCOUNTS)
        stage = rnd.choices(stages, weights=[26, 22, 18, 14, 12, 8])[0]
        found = date(2026, rnd.randint(4, 9), rnd.randint(1, 28))
        scale = rnd.choice([30, 45, 60, 80, 120, 180, 240, 320])
        prob = {"Lead": 10, "BO": 25, "제안": 45, "협상": 65, "수주": 100, "실주": 0}[stage]
        pipeline.append([
            f"L{i+1:04d}", acc[0], acc[1], acc[2], acc[5],
            rnd.choice(B2B_ITEMS), stage, found.isoformat(),
            scale, prob,
            "Y" if stage == "수주" else "N",
            f"2026-{rnd.randint(9, 12):02d}",
        ])
    w("team_b2b/agent04_analysis/data/lead_bo_pipeline.csv",
      ["LeadID", "고객사코드", "고객사명", "업종", "담당경로", "품목군", "단계",
       "발굴일", "예상규모(백만원)", "확률(%)", "전환여부", "마감예정월"],
      pipeline)

    total = sum(int(r[8]) for r in pipeline)
    won = sum(int(r[8]) for r in pipeline if r[6] == "수주")
    summary = [
        [BASE_MONTH, "전체 파이프라인 금액(백만원)", total],
        [BASE_MONTH, "수주 금액(백만원)", won],
        [BASE_MONTH, "건수", len(pipeline)],
        [BASE_MONTH, "전월 파이프라인 금액(백만원)", int(total * 0.88)],
        [BASE_MONTH, "전월 수주 금액(백만원)", int(won * 0.79)],
    ]
    w("team_b2b/agent04_analysis/data/monthly_summary.csv",
      ["기준월", "항목", "값"], summary)

    # --- 테스트 케이스: 경계(합계 불일치) ---
    boundary = [list(r) for r in summary]
    boundary[0][2] = total - 140          # 표지 합계를 일부러 틀리게
    w("team_b2b/agent04_analysis/test_cases/monthly_summary_경계.csv",
      ["기준월", "항목", "값"], boundary)

    # --- 테스트 케이스: 실패(실명·연락처 포함) ---
    fail = [list(r) + ["", ""] for r in pipeline[:12]]
    real_names = ["김민준", "이서연", "박도윤", "최지우"]
    for idx, row in enumerate(fail):
        row[-2] = real_names[idx % len(real_names)] + " 부장"
        row[-1] = f"010-{rnd.randint(2000,9999)}-{rnd.randint(1000,9999)}"
    w("team_b2b/agent04_analysis/test_cases/lead_bo_pipeline_실패.csv",
      ["LeadID", "고객사코드", "고객사명", "업종", "담당경로", "품목군", "단계",
       "발굴일", "예상규모(백만원)", "확률(%)", "전환여부", "마감예정월",
       "고객담당자", "연락처"],
      fail)

    # --- 테스트 케이스: ② Sensing 실패용(실명 포함 뉴스) ---
    news_fail = [list(r) for r in news[:10]]
    for idx, row in enumerate(news_fail):
        row[6] = row[6] + f" (제보: {real_names[idx % len(real_names)]} 010-{rnd.randint(2000,9999)}-{rnd.randint(1000,9999)})"
    w("team_b2b/agent02_sensing/test_cases/industry_news_실패.csv",
      ["출처ID", "보도일", "매체", "업종", "고객사명", "신호유형", "요약", "관련품목군", "신뢰도"],
      news_fail)


# --------------------------------------------------------------------------
# team_partner — 사업자몰 라인업·맞춤 마케팅
# --------------------------------------------------------------------------

PARTNERS = [
    ("PT01", "새롬유통", "A", "서울"),
    ("PT02", "한결상사", "A", "경기"),
    ("PT03", "도담네트웍스", "B", "인천"),
    ("PT04", "빛가람오피스", "B", "광주"),
    ("PT05", "다온솔루션", "B", "부산"),
    ("PT06", "너나들이상사", "C", "대구"),
    ("PT07", "아라오피스", "C", "대전"),
    ("PT08", "은가람테크", "C", "경기"),
    ("PT09", "포근물산", "B", "서울"),
    ("PT10", "산들컴퍼니", "C", "충남"),
]

SMB_SECTORS = ["음식점", "미용", "학원", "의원", "소매점", "사무서비스", "숙박", "공방"]
PARTNER_ITEMS = ["SAC", "DMFP", "IT제품", "모바일"]


def build_partner():
    rnd = random.Random(SEED + 7)

    # --- ② Sensing: 소상공인 업종별 수요 ---
    demand = []
    for i, sector in enumerate(SMB_SECTORS):
        for month in ["2026-07", "2026-08", "2026-09"]:
            demand.append([
                f"D{i+1:02d}{month[-2:]}",
                month, sector,
                rnd.choice(["서울", "경기", "부산", "대구", "광주"]),
                rnd.randint(40, 320),
                rnd.choice(PARTNER_ITEMS),
                rnd.randint(80, 460) * 10_000,
                rnd.choice(["증가", "보합", "감소"]),
            ])
    w("team_partner/agent02_sensing/data/smb_demand.csv",
      ["출처ID", "기준월", "업종", "지역", "문의건수", "관심품목군", "평균구매액(원)", "전월대비"],
      demand)

    # --- ② Sensing: 경쟁사 라인업·가격·프로모션 ---
    comp = []
    for i in range(32):
        comp.append([
            f"C{i+1:03d}",
            date(2026, 9, rnd.randint(1, 3)).isoformat(),
            rnd.choice(["경쟁사 X", "경쟁사 Y", "경쟁사 Z"]),
            rnd.choice(PARTNER_ITEMS),
            f"모델-{rnd.randint(100, 999)}",
            rnd.randint(45, 320) * 10_000,
            rnd.choice(["무이자 12개월", "설치비 지원", "없음", "구독 첫달 면제", "사은품"]),
            rnd.choice(["온라인몰", "파트너몰", "직영"]),
        ])
    w("team_partner/agent02_sensing/data/competitor_lineup.csv",
      ["출처ID", "조사일", "경쟁사", "품목군", "모델명", "표시가(원)", "프로모션", "채널"],
      comp)

    # --- ③ Action: 사업자몰 라인업 ---
    catalog = [
        ["S-SAC-01", "SAC", "소형 상업용 에어컨", "냉방 7.2kW", "매장 1~2대", 1_450_000, "참고 단가"],
        ["S-SAC-02", "SAC", "천장형 카세트", "냉방 11.4kW", "중형 매장 3대", 2_300_000, "참고 단가"],
        ["S-DMFP-01", "DMFP", "복합기 컬러 A3", "35ppm / 양면", "월 과금 구독", 39_000, "월 구독료(참고)"],
        ["S-DMFP-02", "DMFP", "복합기 흑백 A4", "28ppm", "월 과금 구독", 24_000, "월 구독료(참고)"],
        ["S-IT-01", "IT제품", "업무용 모니터 24형", "FHD", "사무 4석", 210_000, "참고 단가"],
        ["S-IT-02", "IT제품", "노트북 사무형", "15인치", "소상공인 1~3대", 980_000, "참고 단가"],
        ["S-MOB-01", "모바일", "업무용 스마트폰 보급형", "6.1인치", "매장 2대", 540_000, "참고 단가"],
    ]
    w("team_partner/agent03_action/data/product_catalog.csv",
      ["품목코드", "품목군", "모델명", "주요사양", "제안구성(예시)", "참고단가(원)", "비고"],
      catalog)

    # --- ④ Analysis: 파트너별 매출·구독 ---
    sales = []
    for month in ["2026-07", "2026-08", "2026-09"]:
        for code, name, grade, region in PARTNERS:
            for item in ["SAC", "DMFP"]:
                base = {"A": 42_000, "B": 21_000, "C": 9_000}[grade]
                amount = int(base * rnd.uniform(0.7, 1.4))
                qty = max(1, amount // rnd.randint(600, 1400))
                subs = rnd.randint(3, 40) if item == "DMFP" else 0
                churn = rnd.randint(0, 5) if item == "DMFP" else 0
                sales.append([
                    month, code, name, grade, region, item,
                    amount, qty, subs, churn,
                ])
    w("team_partner/agent04_analysis/data/partner_sales.csv",
      ["기준월", "파트너코드", "파트너명", "등급", "지역", "품목군",
       "매출(천원)", "수량", "구독건수", "해지건수"],
      sales)

    # --- ④ Analysis: 온라인 가격·PSI ---
    psi = []
    for item in PARTNER_ITEMS:
        for month in ["2026-07", "2026-08", "2026-09"]:
            p_in = rnd.randint(400, 1200)
            p_out = rnd.randint(350, 1150)
            psi.append([
                month, item,
                rnd.randint(45, 320) * 10_000,
                p_in, p_out, rnd.randint(120, 900),
            ])
    w("team_partner/agent04_analysis/data/online_price_psi.csv",
      ["기준월", "품목군", "온라인평균가(원)", "입고수량", "판매수량", "기말재고"],
      psi)

    cur = [r for r in sales if r[0] == BASE_MONTH]
    prev = [r for r in sales if r[0] == "2026-08"]
    total = sum(int(r[6]) for r in cur)
    subs = sum(int(r[8]) for r in cur)
    churn = sum(int(r[9]) for r in cur)
    summary = [
        [BASE_MONTH, "전체 매출(천원)", total],
        [BASE_MONTH, "구독 건수", subs],
        [BASE_MONTH, "해지 건수", churn],
        [BASE_MONTH, "파트너 수", len(PARTNERS)],
        ["2026-08", "전체 매출(천원)", sum(int(r[6]) for r in prev)],
    ]
    w("team_partner/agent04_analysis/data/monthly_summary.csv",
      ["기준월", "항목", "값"], summary)

    boundary = [list(r) for r in summary]
    boundary[0][2] = total + 3_600
    w("team_partner/agent04_analysis/test_cases/monthly_summary_경계.csv",
      ["기준월", "항목", "값"], boundary)

    real_names = ["정하늘", "윤서준", "강예린", "임도현"]
    fail = [list(r) + ["", ""] for r in cur[:12]]
    for idx, row in enumerate(fail):
        row[-2] = real_names[idx % len(real_names)] + " 대표"
        row[-1] = f"010-{rnd.randint(2000,9999)}-{rnd.randint(1000,9999)}"
    w("team_partner/agent04_analysis/test_cases/partner_sales_실패.csv",
      ["기준월", "파트너코드", "파트너명", "등급", "지역", "품목군",
       "매출(천원)", "수량", "구독건수", "해지건수", "파트너대표", "연락처"],
      fail)

    demand_fail = [list(r) for r in demand[:10]]
    for idx, row in enumerate(demand_fail):
        row[2] = row[2] + f" ({real_names[idx % len(real_names)]} 사장, 010-{rnd.randint(2000,9999)}-{rnd.randint(1000,9999)})"
    w("team_partner/agent02_sensing/test_cases/smb_demand_실패.csv",
      ["출처ID", "기준월", "업종", "지역", "문의건수", "관심품목군", "평균구매액(원)", "전월대비"],
      demand_fail)


if __name__ == "__main__":
    build_b2b()
    build_partner()
    print("\n모든 값은 가상입니다. 실제 고객사·파트너·실적과 무관합니다.")
