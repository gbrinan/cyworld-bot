---
# 요구조건서 — 모듈의 유일한 원본. 이 파일의 값이 아래 모든 파일로 파생됩니다 (module_spec.md 3장).
module: X_name                 # 폴더명과 동일
name: doing-something-for-team # SKILL.md name 규칙: 소문자-하이픈, 동명사형
source: 삼성 양식 N (2026-09-07 pptx)
team: common                   # common | b2b | partner
tool:
  primary: ChatGPT 에이전트 (Instant)
  backup: Gemini 에이전트 (Flash)
inputs:
  - file: example.csv
    format: csv                # csv | md | json
    headers: [컬럼1, 컬럼2]     # 삼성 지정 원문 그대로. 01_data CSV 1행과 문자 단위로 일치해야 함
    rows: 40
outputs:
  - file: result_X.html
    format: html               # html | docx-paste
    sections: [절1, 절2]        # 프롬프트 ⑤ 출력 형식의 헤딩 순서
process:
  - "① ..."
  - "② ..."
verticals: [상업시설, 호텔, 병원, 오피스, 교육시설]
planted:
  - "정답이 나오도록 데이터에 심는 신호 (예: 호텔에서 HX-55T가 3회 반복)"
tests:
  normal: "정상 입력 + 기대 결과 한 줄"
  boundary: "무엇을 빼면 → Agent가 무엇을 질문해야 통과"
  failure: "무엇을 넣으면 → Agent가 무엇을 하며 중단해야 통과"
subtotals:
  source: example.csv
  sum: 합계컬럼
  axes: [축1, 축2, 축3]
chain:
  in: []                       # 앞 모듈에서 받을 수 있는 파일 (선택)
  out: []                      # 뒤 모듈에 넘기는 파일 (선택)
forbidden: [SAC, HVAC, DMFP]   # 모듈 어디에도 있으면 안 되는 문자열
confirm:
  - "삼성에 확인 중인 항목. 답이 오면 이 파일만 고치고 재빌드"
---

# 업무 상황 (삼성 양식 원문)

(양식의 "업무 상황" 칸을 그대로 옮깁니다. 요약하지 않습니다.)

# Input (원문)

# Agent 활용 / 처리 (원문)

# Output (원문)

# 가정한 것

(confirm 항목에 대해 지금 어떤 가정값으로 진행하는지)
