# 삼성전자 B2B 영업 AX 과정 — 교안 제작 폴더

기획서: [`../samsung-ax-agent-curriculum-plan.md`](../samsung-ax-agent-curriculum-plan.md)

## 무엇이 들어 있나

```
docs/samsung-ax/
├─ README.md                  (이 파일)
├─ agent_structure_v2.md      Agent 4개 확정 구조 (9/7 삼성 시나리오 반영)
├─ reuse_from_eugene.md       유진투자증권 과정에서 가져온 것 / 안 가져온 것
├─ claude_design_handoff.md   Claude Design 복붙 프롬프트 (슬라이드 제작용)
├─ handoff_review.md          핸드오프 검토 — 사내강사 운영 가능성, P0~P2 부족 항목, 작업 순서
├─ module_spec.md             **모듈 방식 제안** — 요구조건서 1장 → 7단계 빌드 → CHECK 12항목. v2 팩은 이 구조로 제작
├─ slides_outline.md          슬라이드 53장 설계서
├─ instructor_guide.md        강사용 진행 가이드 (큐시트·되묻기·보조강사 운영)
├─ workbook.md                참가자 실습 워크북 (빈칸형)
├─ faq.md                     예상 Q&A
├─ rehearsal_checklist.md     환경 리허설 점검표 + 삼성 확인 요청 사항
├─ tools/make_dummy_data.py   더미 데이터 생성기 (v1)
├─ tools/build_modules.py     v2 모듈 데이터 빌더 (요구조건서 헤더 → 데이터·소계본·paste)
├─ tools/check_module.py      모듈 완성 판정 — 자동 8항목
└─ context_pack/
   ├─ common/                 방법론·지시문 템플릿 — 팀이 바뀌어도 그대로
   ├─ modules/                **v2 Agent 모듈 4개** (D·C·A·B) + _template. 각 모듈 = 요구조건서·데이터·프롬프트·테스트·정답·시연로그
   ├─ team_b2b/               (v1) B2B팀 데이터 팩 — modules/ 완성 후 삭제
   └─ team_partner/           (v1) B2B유통전략팀 데이터 팩 — modules/ 완성 후 삭제
```

## 모듈 구조 (v2)

Agent 하나 = 폴더 하나. `00_requirement.md`(삼성 양식을 옮긴 요구조건서)가 원본이고 나머지는 파생물입니다. 자세한 것은 [`module_spec.md`](module_spec.md).

```
modules/D_analysis/
├─ 00_requirement.md   요구조건서 (헤더·출력 절·planted 신호·테스트 정의)
├─ module.md           모듈 카드 1장 = 슬라이드 [팀별] 9장
├─ 01_data/  02_prompt/  03_tests/  04_answer/  05_demo_log.md  06_paste/
└─ CHECK.md            12항목 통과 = 김승진 프로 공유 가능
```

```bash
python3 docs/samsung-ax/tools/check_module.py --all    # 자동 8항목
```

## 사내강사 인계 패키지 대응

8/6 메일에서 요청한 자료와 이 폴더의 대응 관계입니다.

| 요청 자료 | 이 폴더의 파일 |
|---|---|
| 강의 Material | `slides_outline.md` (슬라이드 제작 후 교체) |
| 스크립트 | `instructor_guide.md` 2·3장 큐시트 + 슬라이드 노트 |
| 예상 Q&A | `faq.md` |
| 참가자 자료 | `workbook.md` |
| 실습 데이터 | `context_pack/team_*/` |
| 결과물 정리표 | `context_pack/team_*/manifest.md` |

핵심 원칙은 **컨텍스트를 데이터로 분리**하는 것입니다.

| 층 | 위치 | 팀이 바뀌면 |
|---|---|---|
| 방법론·지시문 골격 | `common/` | 그대로 |
| 업무 상황·데이터·정답 | `team_*/` | **교체** |

Agent를 팀마다 따로 만들지 않고, 같은 지시문에 다른 팩을 올립니다. 사내강사가 9차수를 운영할 때도 슬라이드는 그대로 두고 팩만 바꿉니다.

## common/ 파일

| 파일 | 용도 |
|---|---|
| `web_environment.md` | **웹 접속 환경 전제.** 결과 저장법, **HTML 여는 법·Word 만드는 법**, 업로드 불가 시 대응, 코드 실행 불가 시 소계본+집계본, 지시문 보관 |
| `tool_paths.md` | **도구 클릭 경로.** ChatGPT·Gemini 에이전트 만들기, 막혔을 때 대안 3단, 강사용 시작 5분 |
| `data_capture.md` | **화면 데이터를 표로 가져오기.** 크롤링 없이 텍스트 복사·화면 캡처·PlayMCP 세 경로 비교, 정제 프롬프트, C 모듈 운영 방식 |
| `skills_and_mcp.md` | **Skill과 MCP.** SKILL.md 해부(name·description·본문), 워크플로우 5패턴, 이 환경에서 되는 것과 안 되는 것 |
| `fit_check.md` | **적합성 체크.** CANNOT 7항목, 업무 유형 A~D, 좋은 과제 3원칙, As-Is→To-Be. 사전과제 필터링과 워크북 전환 칸에 사용 |
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
| `agent*/data/` | Input 더미데이터. `*_소계.csv`는 코드 실행이 안 될 때 쓰는 집계본 |
| `agent*/test_cases/` | 경계·실패 입력 |
| `agent*/handoff/` | **정답 예시.** 앞 모듈을 못 끝낸 참가자가 다음 실습을 시작할 때 씁니다 |
| `paste/` | 모든 데이터의 **마크다운 표 버전.** 파일 업로드가 막힌 경우 복사해 붙여넣습니다 |

## 웹 환경 전제

사내 환경은 **브라우저에서 사내 포털을 통해 ChatGPT·Gemini를 불러 쓰는 방식**입니다. 여기에 맞춰 세 가지 대비를 넣었습니다.

| 웹 환경 제약 | 이 팩의 대비 |
|---|---|
| AI가 만든 파일 다운로드가 막힐 수 있음 | 화면 출력을 복사해 저장하는 절차 (`web_environment.md` 2장) |
| 파일 업로드가 막힐 수 있음 | `paste/` 폴더의 마크다운 표. 가장 큰 파일도 6KB |
| 코드 실행이 안 될 수 있음 | `*_소계.csv`. 세 축의 합계가 상세와 일치하도록 검산됨 |
| 세션이 끊기면 지시문이 사라짐 | 지시문을 로컬 `agent*_prompt.md`로 보관하는 절차 |

**네 가지가 모두 막혀도 과정은 진행됩니다.** 붙여넣기와 복사만 되면 세 Agent를 다 만들 수 있습니다.
실제 가능 여부는 [`rehearsal_checklist.md`](rehearsal_checklist.md)로 확인합니다.

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
| 슬라이드 설계서 (47장) | 완료 |
| Skill·MCP 내용 | 완료 — **Skills 사용 가능 여부는 확인 필요** |
| 강사 가이드·워크북·예상 Q&A | 완료 (v1) |
| 웹 환경 대비 (paste·소계본·저장 절차) | 완료 |
| 환경 리허설 점검표 | 완료 — **실행은 삼성 계정 필요** |
| 컬럼 헤더 확정 | **대기** — 사전과제 「필요 엑셀 컬럼 헤더 구상」과 9/8 전달 자료 반영해 v1.1 |
| 시나리오 확정 | **대기** — 9/7(또는 9/10~11) 사전 모임 결과 반영 |
| Claude Design 핸드오프 | **v3 완료** — 모듈 구조 반영 58장. 게이트가 모듈 단위로 바뀌어 **D 구간부터 제작 가능** |
| 핸드오프 검토 | 완료 — `handoff_review.md`. **P0 3건(v1/v2 불일치·완성 프롬프트·HTML 절차) 해결 전 실습 운영 불가** |
| 모듈 방식 제안 | 완료 — `module_spec.md` + `_template/` + 요구조건서 4장 + `check_module.py`. **구조 확정 후 D부터 빌드** |
| v2 모듈 빌드 (D→C→A→B) | **D 완료 (자동 9/9, 수동 #10~12는 도구 실행 대기)** · C·A·B 요구조건서만 |
| 슬라이드 실물 제작 | 미착수 — Claude Design에서 시안 생성 후 |
| 도구 리허설 (Gems 불가, Instant/Flash) | 미착수 — 9/12 예정 |

## 주의

- 이 폴더의 모든 데이터는 **가상**입니다. 삼성전자 실제 고객사·파트너·실적과 무관합니다.
- 실습 중에는 실제 업무 파일을 올리지 않습니다. `common/security_rules.md`를 따릅니다.
