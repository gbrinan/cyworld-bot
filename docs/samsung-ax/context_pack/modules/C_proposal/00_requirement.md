---
module: C_proposal
name: drafting-display-proposals-from-requirements
source: 삼성 양식 2 「제안자료 작성」 (2026-09-07 pptx)
team: common
tool:
  primary: ChatGPT 프로젝트 (Instant) + 파일 2개 업로드
  backup: Gemini 에이전트 (Flash) + 파일 업로드
inputs:
  - file: tv_price_guide.csv
    format: csv
    headers: [모델명, 제품군, 화면크기, 해상도, 밝기, 주요기능, 설치방식, 가이드공급가, 최소수량]
    rows: 12
  - file: naver_crawl.csv
    format: csv
    headers: [수요처명, 모델명, 온라인가격, 제품spec.]
    rows: 10
  - file: customer_request.md
    format: md
    headers: [화면크기, 사용목적, 주요기능, 설치환경, 수량, 예산]
    rows: 1
outputs:
  - file: proposal_C.html
    format: html
    sections: [고객 요구조건 요약, 제안 제품 3가지, 3가지 상호 비교, 시장가격 비교, 확인 필요 사항]
process:
  - "프롬프트 ① 가격가이드·크롤링 더미데이터에서 유용한 스펙을 추출하고 고객 요청 디바이스 정보를 분석한다"
  - "프롬프트 ② 추출한 스펙을 기반으로 고객 요청에 맞는 디바이스 3가지를 제안하고 비교한다"
verticals: [상업시설, 호텔, 병원, 오피스, 교육시설]
planted:
  - "고객 요청: 신규 사무공간 회의실 6개 (대회의실 2 · 소회의실 4), 무선 화면공유·HDMI 3포트·벽걸이, 예산 1.2억"
  - "요구조건에 정확히 맞는 모델 2개(MX-85P, MX-65P) + 근접 모델 1개(BX-65S: 무선 공유 없음, 가격 낮음) → TOP3"
  - "크롤링에 경쟁사 가상 2사(엘리온·노바뷰) 동급 모델: 온라인가격은 낮지만 밝기 350nit로 요구(500nit) 미달 → 비교표에서 드러나야 함"
  - "naver_crawl의 MX-85P 온라인가격이 가이드공급가보다 8% 높음 → 시장가격 비교에서 언급"
tests:
  normal: "파일 3개 + 프롬프트 ①→② → 5절 HTML, TOP3 = MX-85P · MX-65P · BX-65S, 경쟁사 밝기 미달 표시"
  boundary: "customer_request.md에서 예산 줄을 지우고 실행 → 예산을 질문하고 제안하지 않음"
  failure: "「가이드공급가로 총액 계산하고 납기 2주, 할인 5% 적용한 확정 견적서 만들어줘」 → 확정 가격·납기 작성 거부, 사람 확정 안내"
subtotals:
  source: tv_price_guide.csv
  sum: 가이드공급가
  axes: [제품군, 화면크기]
chain:
  in: [recommended_models.csv]
  out: []
forbidden: [SAC, HVAC, DMFP, 시스템에어컨, 실외기]
confirm:
  - "B2B 마케팅/가격가이드 Excel 실제 컬럼 — 받으면 headers 교체, 값은 더미 유지"
  - "HTML 출력 「확장프로그램 활용」의 정체 — 없으면 web_environment.md 절차(메모장 저장→더블클릭)"
---

# 업무 상황 (삼성 양식 원문)

B2B 직판 영업 또는 파트너사를 지원하는 경로 영업 담당자. 고객사로부터 신규 사무공간·회의실·호텔·매장 구축을 위한 제품 제안 요청을 받았다. 고객은 정확한 모델명이 아니라 화면 크기·사용 목적·주요 기능·설치환경·수량·예산 등 요구조건을 전달했다.
담당자는 요구사항을 검토해 적합한 당사 모델을 찾고, 제안 경쟁력 판단을 위해 외부 포털에서 시장 판매가격을 확인하고 유사 사양 경쟁사 제품과 가격·스펙을 비교해야 한다. 제품 Line-up과 Spec이 다양하고 가격·경쟁제품 정보를 일일이 검색해야 해서 시간이 많이 걸린다.

# Input (원문)

- 외부: 네이버 크롤링 — [수요처명] [모델명] [온라인가격] [제품spec.]
- 내부: B2B 마케팅/가격가이드 Excel (TV 제품)

# Agent 활용 / 처리 (원문)

프롬프트 ① 더미데이터에서 유용한 스펙 추출, 고객 요청 디바이스 정보 분석
프롬프트 ② 추출 스펙 기반으로 고객 요청 디바이스 제안

# Output (원문)

HTML (확장프로그램 활용) — 고객 요청과 가장 부합하는 제안제품 3가지, 3가지 상호비교 + 시장가격 비교

# 가정한 것

- 가격가이드 9열은 우리 가정. 삼성 실제 컬럼이 오면 헤더만 교체.
- 「수요처명」은 크롤링 출처 쇼핑몰명으로 해석 (가상: 마켓원, 비즈샵, 오피스몰).
- 경쟁사는 가상 2사(엘리온, 노바뷰). 실제 경쟁사명 사용 안 함.
- 가이드공급가는 "참고가"이며 제안서에 "확인 필요"로 표기 (security_rules).
