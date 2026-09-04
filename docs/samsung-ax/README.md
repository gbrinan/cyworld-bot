# 삼성전자 B2B 영업 AX 과정 — 교안 제작 폴더

기획서: [`../samsung-ax-agent-curriculum-plan.md`](../samsung-ax-agent-curriculum-plan.md)

## 무엇이 들어 있나

```
docs/samsung-ax/
├─ README.md                  (이 파일)
├─ tools/make_dummy_data.py   더미 데이터 생성기
└─ context_pack/
   ├─ common/                 방법론·지시문 템플릿 — 팀이 바뀌어도 그대로
   ├─ team_b2b/               B2B팀 컨텍스트 데이터 팩
   └─ team_partner/           B2B유통전략팀 컨텍스트 데이터 팩
```

핵심 원칙은 **컨텍스트를 데이터로 분리**하는 것입니다.

| 층 | 위치 | 팀이 바뀌면 |
|---|---|---|
| 방법론·지시문 골격 | `common/` | 그대로 |
| 업무 상황·데이터·정답 | `team_*/` | **교체** |

Agent를 팀마다 따로 만들지 않고, 같은 지시문에 다른 팩을 올립니다. 사내강사가 9차수를 운영할 때도 슬라이드는 그대로 두고 팩만 바꿉니다.

## common/ 파일

| 파일 | 용도 |
|---|---|
| `methodology.md` | IPO 명세, 지시문 7블록, 테스트 3종, 사람 승인. 모든 모듈 공통 |
| `instruction_templates/agent02_sensing.md` | ② 시장·고객 분석 Agent 지시문 (`{{ }}`만 교체) |
| `instruction_templates/agent03_action.md` | ③ 제안자료 작성 Agent 지시문 |
| `instruction_templates/agent04_analysis.md` | ④ 데이터 분석 Agent 지시문 |
| `proposal_structure.md` | 제안서 공통 순서 (회사소개→제안내용→제품소개→유지보수, 삼성 확정) |
| `review_criteria.md` | 5분 검수 체크리스트와 등급 |
| `test_cases_guide.md` | 모듈별 테스트 3종 실행 순서와 프롬프트 |
| `security_rules.md` | 업로드 금지 목록, 실습 대체 규칙 |
| `tool_budget.md` | 기능별 실행 횟수 예산 (월 10회 제한 대응) |

## team_*/ 파일

각 팩은 같은 구조입니다.

| 파일 | 용도 |
|---|---|
| `manifest.md` | 삼성 「양성과정 결과물 정리표」 형식 (3 Agent × 5열). 그대로 제출 가능 |
| `team_profile.md` | 9/4 메일 기반 팀 프로필. 모든 Agent의 참조 파일 |
| `scenario.md` | 영업 여정 통합 시나리오 1개와 모듈별 실습 정의 |
| `agent*/data/` | Input 더미데이터 |
| `agent*/test_cases/` | 경계·실패 입력 |
| `agent*/handoff/` | **정답 예시.** 앞 모듈을 못 끝낸 참가자가 다음 실습을 시작할 때 씁니다 |

## Agent 체인

```
② Sensing  → customer_profile.md / segment_profile.md
③ Action   → proposal_draft.md
④ Analysis → report_draft.md
```

각 모듈의 출력을 파일로 저장해 다음 모듈에 올립니다. 도구가 달라도(Gemini → Gemini → GPT) 파일로 이어집니다.

## 더미 데이터 다시 만들기

```bash
python3 docs/samsung-ax/tools/make_dummy_data.py
```

- 시드가 고정되어 있어 몇 번을 돌려도 같은 값이 나옵니다.
- 컬럼 헤더를 바꾸려면 스크립트 안의 `w(...)` 호출부 헤더 리스트를 수정합니다.
- **모든 값은 가상입니다.** 실제 고객사·파트너·실적과 무관합니다.

## 지금 상태와 다음 작업

| 항목 | 상태 |
|---|---|
| common 방법론·지시문 템플릿 | 완료 (v1) |
| 팀별 팩 v1 (9/4 메일 프로필 기반) | 완료 |
| 더미 데이터 + 테스트 케이스 + 정답 인계 파일 | 완료 |
| 컬럼 헤더 확정 | **대기** — 사전과제 「필요 엑셀 컬럼 헤더 구상」과 9/8 전달 자료 반영해 v1.1 |
| 시나리오 확정 | **대기** — 9/7(또는 9/10~11) 사전 모임 결과 반영 |
| 슬라이드 | 미착수 |
| 강사 가이드·워크북 | 미착수 |
| 도구 리허설 (Gems 불가, Instant/Flash) | 미착수 — 9/12 예정 |

## 주의

- 이 폴더의 모든 데이터는 **가상**입니다. 삼성전자 실제 고객사·파트너·실적과 무관합니다.
- 실습 중에는 실제 업무 파일을 올리지 않습니다. `common/security_rules.md`를 따릅니다.
