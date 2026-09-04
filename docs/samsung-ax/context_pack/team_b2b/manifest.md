# B2B팀 데이터 팩 매니페스트

> 삼성 측 「양성과정 결과물 정리표」(9/3 메일 첨부) 열 구성을 그대로 따랐습니다.
> 양성과정이 끝나면 이 표를 그대로 결과물 정리표로 제출할 수 있습니다.

## 3대 Agent 정의

| 구분 (3대 Agent) | 최종 실습주제 | 업무상황 (비즈니스 Context) | Input 더미데이터 스펙 (Excel 상세 컬럼 헤더 정의) | AI Agent 상세 활용 내용 (Agent의 형태) | Output 최종 결과물 (교육생 산출 서식/결과) |
|---|---|---|---|---|---|
| ① 시장·고객 분석 (Sensing) | 수요처 AX전략 기반 NBM Lead 발굴 — 업종 뉴스에서 담당 고객사의 투자·조직 신호를 찾아 제안 우선순위 도출 | 유통·서비스·통신·공공 업종 담당. 매일 뉴스를 훑지만 놓치는 날이 많고, 신호를 찾아도 과거 거래 이력을 따로 열어봐야 함 | `industry_news.csv` — 출처ID, 보도일, 매체, 업종, 고객사명, 신호유형, 요약, 관련품목군, 신뢰도 (48행)<br>`target_accounts.csv` — 고객사코드, 고객사명, 업종, 임직원수, 지역, 담당경로, 최근거래품목군, 최근거래일, 거래상태, 담당자(가명) (15행) | **Gemini Deep Research + NotebookLM**<br>참조 파일: team_profile.md, 위 2개 CSV<br>지시문 7블록 (agent02_sensing.md) | `customer_profile.md`<br>우선순위 표 + 상위 3건 상세 + 근거표 + 확인 필요 목록 |
| ② 제안자료 작성 (Action) | 1순위 고객 대상 HVAC 통합 제안서 초안 | 제안할 때마다 처음부터 작성. 담당자마다 구성이 달라짐 | `customer_profile.md` (① 인계물)<br>`product_catalog.csv` — 품목코드, 품목군, 모델명, 주요사양, 제안구성(예시), 참고단가(원), 비고 (8행)<br>`service_terms.md` — 서비스 범위·대응 체계·계약 형태 | **Gemini 에이전트 + 참조 파일**<br>제안서 순서 고정: 회사소개 → 제안내용 → 제품소개 → 유지보수<br>지시문 7블록 (agent03_action.md) | `proposal_draft.md`<br>4개 섹션 초안 + 근거표 + 확인 필요 목록 (가격·납기는 확정 문구 금지) |
| ③ 데이터 분석 (Analysis) | 월말 Lead·BO 파이프라인 현황 보고 | 표지 합계와 상세가 안 맞아 다시 세는 일이 있음. 매출만 보고 선행 지표를 놓침 | `lead_bo_pipeline.csv` — LeadID, 고객사코드, 고객사명, 업종, 담당경로, 품목군, 단계, 발굴일, 예상규모(백만원), 확률(%), 전환여부, 마감예정월 (66행)<br>`monthly_summary.csv` — 기준월, 항목, 값 (5행)<br>`report_template.md` | **GPT 파일 분석 (프로젝트)**<br>지시문 7블록 (agent04_analysis.md) | `report_draft.md`<br>데이터 점검 + 요약 + 지표 현황 + 단계별/경로별/품목군별 + 특이사항 + 원인 가설 + 근거표 |

## ★ 통합 연계 시나리오 (영업 여정 Best 1)

**수요처 AX전략 기반 NBM Lead 발굴**
뉴스 센싱 → 제안서 작성 → 파이프라인 실적 분석이 하나로 이어집니다.
각 Agent의 출력을 파일로 저장해 다음 Agent의 입력으로 넘깁니다.

```
industry_news + target_accounts → [Sensing] → customer_profile.md
customer_profile + product_catalog + service_terms → [Action] → proposal_draft.md
lead_bo_pipeline + monthly_summary → [Analysis] → report_draft.md
```

## 파일 목록

```
team_b2b/
├─ manifest.md                (이 파일)
├─ team_profile.md            9/4 메일 기반 팀 프로필
├─ scenario.md                통합 시나리오와 모듈별 실습 정의
├─ agent02_sensing/
│  ├─ data/  industry_news.csv · target_accounts.csv
│  ├─ test_cases/  industry_news_실패.csv
│  └─ handoff/  customer_profile.md          ← ① 정답 예시
├─ agent03_action/
│  ├─ data/  product_catalog.csv · service_terms.md
│  └─ handoff/  proposal_draft.md            ← ② 정답 예시
└─ agent04_analysis/
   ├─ data/  lead_bo_pipeline.csv · monthly_summary.csv · report_template.md
   ├─ test_cases/  monthly_summary_경계.csv · lead_bo_pipeline_실패.csv
   └─ handoff/  report_draft.md              ← ③ 정답 예시
```

## 의도적으로 심어둔 데이터 함정

| Agent | 함정 | 학습 목적 |
|---|---|---|
| ① Sensing | 같은 고객사·같은 신호유형 기사가 매체를 달리해 **중복 6건** | 중복 제거 없이 세면 우선순위가 뒤바뀝니다 |
| ② Action | 카탈로그 단가가 **참고 단가** | 확정 가격으로 쓰면 안 되는 값을 구분합니다 |
| ③ Analysis | 경계 파일의 표지 합계가 상세와 **140백만원 차이** | 정합성 검사 없이 표지를 인용하는 습관을 잡습니다 |
| ③ Analysis | `monthly_summary`에 **전월 단계별 분포가 없음** | 없는 값을 추정해 채우지 않는 훈련 |

## 갱신 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1 | 2026-09-04 | 9/4 메일 팀 프로필과 9/7 슬라이드 후보 시나리오 기반 초판. 컬럼 헤더는 임시값 |
| v1.1 (예정) | 9/11 | 사전과제 「필요 엑셀 컬럼 헤더 구상」과 9/8 전달 자료(Workflow 리스트, AX T/F 과제 리스트) 반영 |
