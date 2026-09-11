---
module: B_sensing_partner
name: sensing-district-opportunities-for-partners
source: 삼성 양식 1-2 「시장·고객 분석 (B2B유통전략팀)」 (2026-09-07 pptx)
team: partner
tool:
  primary: ChatGPT 에이전트 (Instant) + 파일 업로드
  backup: Gemini 에이전트 (Flash) 또는 Gemini Notebook + 에이전트
inputs:
  - file: naver_news_dummy.json
    format: json
    headers: [title, originallink, link, description, pubDate]
    rows: 30
  - file: district_info.csv
    format: csv
    headers: [권역, 행정구역, 시설유형, 시설명, 단계, 예정시기, 규모]
    rows: 18
  - file: partner_info.csv
    format: csv
    headers: [파트너사, 담당권역, 주력버티컬, 최근분기실적등급]
    rows: 4
outputs:
  - file: report_B.md
    format: docx-paste
    sections: [권역시장 요약, Key Sales Signal, 영업기회 리스트, 근거, 파트너사와 논의사항]
process:
  - "프롬프트 ① 권역·버티컬을 받아 검색 키워드 조합을 만든다"
  - "프롬프트 ② 네이버 뉴스 API 더미데이터(JSON)를 연동해 권역 시장 변화를 분석하는 Agent를 만든다"
  - "프롬프트 ③ 분석 결과를 Word 보고서 양식(5절)에 맞춰 출력한다"
verticals: [상업시설, 호텔, 병원, 오피스, 교육시설]
planted:
  - "부산 해운대 권역: 호텔 리뉴얼 2건(객실 200·150실) 기사 + 상권정보 「착공」 단계 → 영업기회 1·2순위"
  - "부산 해운대 권역: 교육시설 신축 1건(사립고 신설) → 3순위"
  - "타 권역 기사 12건(대구·광주)은 권역 필터에서 제외돼야 함"
  - "파트너사 「남해정보통신」 주력버티컬 호텔 + 실적 A → 논의사항이 이 파트너를 지목해야 함"
tests:
  normal: "파일 3개 + 프롬프트 ①→②→③ + 권역 「부산 해운대」 → 5절 보고서, 기회 3건, 논의사항에 남해정보통신"
  boundary: "권역을 지정하지 않고 「분석해줘」 → 권역을 질문"
  failure: "partner_info_실패.csv (파트너별 계약단가·마진율 컬럼 추가) → 업로드 금지 항목임을 알리고 해당 컬럼을 제외하기 전까지 중단"
subtotals:
  source: district_info.csv
  sum: 건수
  axes: [시설유형, 단계]
chain:
  in: []
  out: [opportunity_list.csv]
forbidden: [SAC, HVAC, DMFP, smb_demand, competitor_lineup]
confirm:
  - "Word 보고서 — docx 파일 생성인지 Word에 붙여넣는 텍스트인지. 지금은 붙여넣기용 마크다운으로 진행"
  - "네이버 뉴스 API 실제 연동은 없음 (9/9 사내 연동 없음). JSON은 API 응답 형식만 흉내"
---

# 업무 상황 (삼성 양식 원문)

B2B 경로 영업 담당자로서 특정 권역의 여러 파트너사를 관리하며 담당 권역 시장상황을 점검하던 중, 최근 신규 상업시설·호텔·병원·오피스·교육시설의 개점·이전·신축·리뉴얼이 증가한다는 정보를 입수. 언론기사·지역 미디어·기업 홈페이지·시장조사 자료·상권정보를 각각 검색해 변화를 확인하고 이를 담당 파트너사의 영업기회와 연결해야 한다.
→ 담당 권역을 입력하면 시장·상권 정보를 분석하고, 주요 영업기회를 찾아 수주 확정을 위해 파트너사와 무엇을 논의해야 할지 제안하는 Agent를 만든다.

# Input (원문)

- 네이버 뉴스 Data API 더미데이터 (외부 API 연동 가정)
- API 데이터 예시, 상권정보, 파트너사 통한 정보

# Agent 활용 / 처리 (원문)

제공 프롬프트 3종 — ① 검색 키워드 작성 ② API 더미데이터 연동해 Agent 제작 ③ 원하는 양식에 맞춰 결과물 출력

# Output (원문)

Word 보고서 — 권역시장 요약 / Key Sales Signal(시장·지역별 Insight) / 영업기회 리스트 / 근거 / 파트너사와 논의사항

# 가정한 것

- JSON은 네이버 뉴스 검색 API 응답 구조(`lastBuildDate` `total` `items[]`)를 따르되 값은 전부 가상. `originallink`는 가상 도메인.
- 상권정보 7열, 파트너 정보 4열은 우리 가정. 파트너 정보에 단가·마진은 절대 넣지 않음 (실패 테스트에서만 별도 파일).
- 소계본은 건수 기준 (시설유형별·단계별).
