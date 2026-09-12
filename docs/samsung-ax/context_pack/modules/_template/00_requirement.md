---
# 요구조건서 — 모듈의 유일한 원본. 이 파일의 값이 아래 모든 파일로 파생됩니다 (module_spec.md 3장).
# 채우는 법은 ../TEMPLATE.md 참고. 다 채운 뒤 tools/check_module.py 로 검사합니다.
module: X_name                 # 폴더명과 동일
name: doing-something-for-team # SKILL.md name 규칙: 소문자-하이픈, 동명사형
source: "출처 양식 번호와 날짜"
team: common                   # common | 팀 코드
case: "한 문장으로 쓴 케이스. 누구를 대상으로 무엇을 하는가"
agent_count: 1                 # 에이전트는 모듈당 1개. 2시간에 하나를 끝까지 만든다
tool:
  primary: "주 도구 (에이전트 종류·모델까지)"
  backup: "대체 도구"
skill:                         # agent_and_skill_split.md 2장 기준
  name: doing-something-for-team
  scope: "스킬로 뗄 것 — 절차·출력 양식·금지 사항·검수 기준 (누가 해도 같은 것)"
  agent_side: "에이전트에 둘 것 — 참조 파일·팀 용어·담당 범위·실행 주기"
steps:                         # 🔒 이 없으면 나누지 말고 단계로 (task_decomposition.md 4장)
  - id: 1
    label: 단계 이름
    prompt: prompt_1.md
    do: "이 단계가 무엇을 받아 무엇을 내놓는가"
inputs:
  - file: example.csv
    format: csv                # csv | md | json
    headers: [컬럼1, 컬럼2]     # 원문 그대로. 01_data CSV 1행과 문자 단위로 일치해야 함
    rows: 40
outputs:
  - file: result_X.html
    format: html               # html | docx-paste | csv | md
    sections: [절1, 절2]        # 프롬프트 ⑤ 출력 형식의 헤딩 순서
    from: 단계 1
process:
  - "단계1 ① ..."
  - "단계1 ② ..."
planted:
  - "정답이 나오도록 데이터에 심는 신호. 판단을 시험하는 함정 3~4개"
tests:
  normal: "정상 입력 + 기대 결과 한 줄 (검증 가능한 수치로)"
  boundary: "무엇을 빼면 → Agent가 무엇을 질문해야 통과"
  failure: "무엇을 넣으면 → Agent가 무엇을 하며 중단해야 통과"
subtotals:                     # 코드 실행 불가 대비. 없으면 통째로 뺀다
  source: example.csv
  sum: 합계컬럼               # 원본에 없으면 건수로 센다
  axes: [축1, 축2, 축3]
chain:
  in: []                       # 앞 모듈에서 받을 수 있는 파일 (선택)
  out: []                      # 뒤 모듈에 넘기는 파일 (선택)
forbidden: []                  # 모듈 어디에도 있으면 안 되는 문자열 (구 과정 품목명 등)
confirm:
  - "고객사에 확인 중인 항목. 답이 오면 이 파일만 고치고 재빌드"
---

# 업무 상황 (출처 원문)

(요약하지 않고 그대로 옮깁니다.)

# 케이스 — 왜 이 대상인가

(이 케이스를 고른 이유 2~3개. 신호가 공개돼 있다, 날짜가 박혀 있어 역산이 된다 같은 실질적 이유)

# Input / 처리 / Output (원문)

# 일 분해 (task_decomposition.md 순서)

| # | 단계 | I 받는 것 | O 내놓는 것 | 시간 | 꼬리표 | 어디로 |
|---|---|---|---|---|---|---|
| 1 | | | | | 🔌 | 입력 |
| 2 | | | | | ⚙️ | 단계 1 |
| 3 | | | | | ✍️ | 단계 2 |
| 4 | | | | | 🔒 | **경계** |

**🔒 사이에 없으면 에이전트는 하나입니다.** 성격이 다른 덩어리는 단계로 둡니다.

# 가정한 것

(confirm 항목에 대해 지금 어떤 가정값으로 진행하는지. 모든 데이터가 가상임을 명시)
