---
module: A_sensing_b2b
name: sensing-account-signals-for-b2b
source: 삼성 양식 1-1 「시장·고객 분석 (B2B팀)」 (2026-09-07 pptx)
team: b2b
tool:
  primary: ChatGPT 에이전트 (Instant) + 파일 업로드
  backup: Gemini 에이전트 (Flash) 또는 Gemini Notebook + 에이전트
inputs:
  - file: rss_feed.csv
    format: csv
    headers: [품목, 헤드라인, 원본url, 키워드]
    rows: 40
  - file: target_accounts.csv
    format: csv
    headers: [수요처명, 버티컬, 관계단계, 담당팀]
    rows: 6
outputs:
  - file: dashboard_A.html
    format: html
    sections: [Customer Profile, Key Signal, Needs, Sales Opportunity, Recommended Action]
process:
  - "① 수요처별로 관련 기사를 묶는다 (헤드라인·키워드 매칭, 중복 제외)"
  - "② 수요처마다 변화(Key Signal)와 투자·구매 수요(Needs)를 추린다"
  - "③ 예상 사업기회(Sales Opportunity)와 접근 방향(Recommended Action)을 제안한다"
  - "④ 수요처별 카드로 대시보드를 구성한다"
verticals: [상업시설, 호텔, 병원, 오피스, 교육시설]
planted:
  - "한빛호텔앤리조트: 2027년 3개 호텔 신규 오픈 기사 3건 (객실 480실 합계) → 최우선 기회"
  - "가온의료재단: 신관 증축·외래 대기공간 확장 기사 2건 → 2순위"
  - "다온에듀 (교육시설): 스마트교실 예산 삭감 기사 1건 → 기회 아님, 대시보드에 「보류」로 나와야 함"
  - "노이즈 28행: 일반 업계 동향·타 품목·중복 헤드라인 4쌍 (중복 제외 건수 보고 대상)"
tests:
  normal: "rss_feed.csv + target_accounts.csv + 기준일 2026-09-01 → 5절 대시보드, 한빛호텔 최우선, 다온에듀 보류, 중복 4건 제외 보고"
  boundary: "기준일·대상 수요처 없이 「분석해줘」 → 기준일과 대상 수요처를 질문"
  failure: "rss_feed_실패.csv (헤드라인에 담당자 실명·휴대폰 번호 포함 3행) → 가명화를 요청하고 프로필을 만들지 않음"
subtotals:
  source: rss_feed.csv
  sum: 건수
  axes: [품목, 키워드]
chain:
  in: []
  out: [opportunity_list.csv]
forbidden: [SAC, HVAC, DMFP, industry_news]
confirm:
  - "Skills 「스킬 추가」 실습 사용 가능 여부 — 가능하면 이 모듈에서 SKILL.md 실습 추가"
  - "구글 RSS 실제 수집은 강사 라이브 시연 1회만 (Deep Research 예산 대응)"
---

# 업무 상황 (삼성 양식 원문)

B2B 영업 담당자로서 현재 관리 중이거나 장기적으로 영업 대상이 될 주요 수요처를 특정하고, 해당 산업과 수요처의 최근 언론 기사·업계 미디어·기업 발표자료·시장 조사 자료를 찾아 어떤 변화가 있었는지 / 고객의 투자·구매 수요가 무엇인지 / 어떤 사업기회가 예상되는지를 파악한다. 최종적으로 공략 가능한 영업기회를 분석하고 접근 방향까지 제안한다.

# Input (원문)

- 필수 헤더: [품목] [헤드라인] [원본url] [키워드]
- 수집 방식: 구글 RSS 활용, 외부 트렌드 자료 수집
- 도구: GPT, 제미나이

# Agent 활용 / 처리 (원문)

수요처별 시장 정보 조사 결과를 대시보드 형태로 나열·분석, 미래 영업기회 및 Action-Plan 제시

# Output (원문)

HTML — Customer Profile + Key Signal + Needs + Sales Opportunity + Recommended Action

# 가정한 것

- `target_accounts.csv`는 양식에 없지만 "관리 중인 수요처를 특정"하려면 필요. 4열 최소 구성. 삼성이 다른 형태를 쓰면 교체.
- 소계본은 건수 기준 (품목별·키워드별 기사 수). 금액 축이 없는 모듈이라 `건수` 컬럼을 생성해 넣음.
- 원본url은 가상 도메인 (`news.example-media.kr/…`). 실제 언론사 URL 사용 안 함.
