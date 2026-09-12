---
module: D_analysis
name: recommending-products-by-vertical
source: 삼성 양식 3 「데이터 분석」 (2026-09-07 pptx)
team: common
tool:
  primary: ChatGPT 에이전트 (Instant) + 파일 업로드
  backup: Gemini 에이전트 (Flash) + 파일 업로드
inputs:
  - file: sales_history.csv
    format: csv
    headers: [판매일자, 버티컬, 수요처, 제품군, 모델명, 공급가, 판매수량, 판매금액, 프로젝트/용도, 지역]
    rows: 52
  - file: target_account.md
    format: md
    headers: [수요처명, 버티컬, 프로젝트/용도]
    rows: 1
outputs:
  - file: recommend_D.html
    format: html
    sections: [대상 수요처 분석, 버티컬별 판매 Insight, 추천 제품 TOP 3, 영업 제안 Point]
process:
  - "① 대상 수요처의 버티컬 특성을 분석한다"
  - "② 유사 버티컬의 과거 판매 데이터를 분석한다 (판매량·판매금액·반복 구매 패턴)"
  - "③ 제품을 추천한다 (TOP 3)"
  - "④ 왜 이 제품인가를 과거 실적 데이터로 설명한다"
verticals: [상업시설, 호텔, 병원, 오피스, 교육시설]
planted:
  - "호텔: HX-55T(객실 TV)와 ST-H1(스탠드)이 같은 수요처·같은 달에 4회 함께 팔림 → 조합 추천 근거"
  - "호텔: 로비용 BX-65S가 3개 수요처에 각 2~4대 → TOP3 세 번째"
  - "오피스: MX-85P가 회의실 용도로 반복, 병원: BX-43S가 대기실 용도로 반복 (대상이 호텔일 때는 노이즈)"
  - "정답 대상: 가상 「해솔호텔 제주」 호텔 / 신축 객실 120실 + 로비"
tests:
  normal: "sales_history.csv + target_account.md → 4절 HTML, TOP3 = HX-55T · ST-H1 · BX-65S, 각 추천에 근거 행"
  boundary: "target_account.md 없이 「추천해줘」 → 버티컬·프로젝트/용도를 질문하고 추천하지 않음"
  failure: "sales_history_실패.csv (판매금액 ≠ 공급가×판매수량 3행, 버티컬 오타 1행) → 불일치 행을 표로 보이고 추천 생성을 중단"
subtotals:
  source: sales_history.csv
  sum: 판매금액
  axes: [버티컬, 제품군, 지역]
chain:
  in: [opportunity_list.csv]
  out: [recommended_models.csv]
forbidden: [SAC, HVAC, DMFP, Lead/BO, 파이프라인]
confirm:
  - "버티컬 표준 명칭 — 사내 분류가 있으면 verticals 교체"
  - "판매실적 실제 컬럼이 10열과 다르면 headers 교체 (지금은 9/7 양식 원문)"
---

# 업무 상황 (삼성 양식 원문)

신규 고객 또는 프로젝트에 적합한 제품을 제안해야 한다. 과거 B2B 판매 실적에 버티컬별·수요처별·제품별 판매 이력이 쌓여 있으나 일일이 분석해 유사 고객의 구매 패턴과 적합 제품을 찾는 데 시간이 많이 걸린다.
→ 제안 대상 수요처의 버티컬/업종 특성을 입력하면 과거 유사 버티컬 판매 데이터를 분석해 ① 어떤 제품이 주로 팔렸는지 ② 어떤 제품 조합이 효과적이었는지 ③ 어떤 제품이 이 수요처에 적합한지를 도출한다.

# Input (원문)

- 사내: B2B 과거 판매 실적 — [판매일자] [버티컬] [수요처] [제품군] [모델명] [공급가] [판매수량] [판매금액] [프로젝트/용도] [지역]
- 분석 대상: [수요처명] [버티컬] [프로젝트/용도]

# Agent 활용 / 처리 (원문)

① 대상 수요처 버티컬 분석 → ② 유사 버티컬 과거 판매 데이터 분석 (판매량·판매금액·반복 구매 패턴) → ③ 제품 추천 → ④ "왜 이 제품인가"를 과거 실적 데이터로 설명

# Output (원문)

HTML — ① 대상 수요처 분석 ② 버티컬별 판매 Insight ③ 추천 제품 TOP 3 ④ 영업 제안 Point

# 가정한 것

- 가상 모델 체계: BX(사이니지 표준) · HX(호텔 TV) · MX(회의실 대형) · KX(키오스크) · ST(스탠드/액세서리). 실제 라인업과 무관.
- 제품군 값: 사이니지 / 호텔TV / 대형디스플레이 / 키오스크 / 액세서리.
- 지역 값: 서울 / 경기 / 부산·경남 / 대구·경북 / 광주·전라 / 제주.
- 기간: 2025-01 ~ 2026-08. 52행 중 호텔 22행, 나머지 4개 버티컬 30행(노이즈). 붙여넣기 버전이 6KB 이내가 되는 최대 행 수.
- 코드 실행 불가 시 `sales_history_소계.csv` 사용 (버티컬·제품군·지역 세 축).
