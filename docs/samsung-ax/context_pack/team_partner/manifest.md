# B2B유통전략팀 데이터 팩 매니페스트

> 삼성 측 「양성과정 결과물 정리표」(9/3 메일 첨부) 열 구성을 그대로 따랐습니다.

## 3대 Agent 정의

| 구분 (3대 Agent) | 최종 실습주제 | 업무상황 (비즈니스 Context) | Input 더미데이터 스펙 (Excel 상세 컬럼 헤더 정의) | AI Agent 상세 활용 내용 (Agent의 형태) | Output 최종 결과물 (교육생 산출 서식/결과) |
|---|---|---|---|---|---|
| ① 시장·고객 분석 (Sensing) | 사업자몰 라인업·맞춤 마케팅 — 업종별 수요와 경쟁사 라인업을 비교해 4분기 밀 품목·세그먼트 선정 | 수요 데이터와 경쟁사 몰을 각각 열어보며 감으로 라인업을 잡음 | `smb_demand.csv` — 출처ID, 기준월, 업종, 지역, 문의건수, 관심품목군, 평균구매액(원), 전월대비 (24행)<br>`competitor_lineup.csv` — 출처ID, 조사일, 경쟁사, 품목군, 모델명, 표시가(원), 프로모션, 채널 (32행) | **Gemini Deep Research + NotebookLM**<br>참조 파일: team_profile.md, 위 2개 CSV<br>지시문 7블록 (agent02_sensing.md) | `segment_profile.md`<br>세그먼트 우선순위 표 + 상위 3건 상세 + 근거표 + 확인 필요 목록 |
| ② 제안자료 작성 (Action) | 1순위 세그먼트 대상, **파트너 배포용** 제안 자료 초안 | 파트너 요청이 올 때마다 개별 작성. 파트너마다 내용이 다름 | `segment_profile.md` (① 인계물)<br>`product_catalog.csv` — 품목코드, 품목군, 모델명, 주요사양, 제안구성(예시), 참고단가(원), 비고 (7행)<br>`service_terms.md` — DMFP 구독 조건·SAC 설치·파트너 지원 | **Gemini 에이전트 + 참조 파일**<br>제안서 순서 고정: 회사소개 → 제안내용 → 제품소개 → 유지보수<br>**독자는 파트너 영업 담당**<br>지시문 7블록 (agent03_action.md) | `proposal_draft.md`<br>4개 섹션 초안 + 근거표 + 확인 필요 목록 (구독료·약정은 확정 문구 금지) |
| ③ 데이터 분석 (Analysis) | 월말 파트너 매출·구독 현황 보고 | 구독이 누적이라 매번 다시 셈. 매출과 구독을 섞어 보면 해지율이 안 보임 | `partner_sales.csv` — 기준월, 파트너코드, 파트너명, 등급, 지역, 품목군, 매출(천원), 수량, 구독건수, 해지건수 (60행)<br>`online_price_psi.csv` — 기준월, 품목군, 온라인평균가(원), 입고수량, 판매수량, 기말재고 (12행)<br>`monthly_summary.csv`, `report_template.md` | **GPT 파일 분석 (프로젝트)**<br>지시문 7블록 (agent04_analysis.md) | `report_draft.md`<br>데이터 점검 + 매출 현황 + 구독 현황 + 파트너별/등급별 + 특이사항 + 원인 가설 + 근거표 |

## ★ 통합 연계 시나리오 (영업 여정 Best 1)

**사업자몰 라인업·맞춤 마케팅**
수요·경쟁 센싱 → 파트너 배포 자료 → 라인업 성과 분석이 하나로 이어집니다.

```
smb_demand + competitor_lineup → [Sensing] → segment_profile.md
segment_profile + product_catalog + service_terms → [Action] → proposal_draft.md
partner_sales + online_price_psi + monthly_summary → [Analysis] → report_draft.md
```

## 파일 목록

```
team_partner/
├─ manifest.md                (이 파일)
├─ team_profile.md            9/4 메일 기반 팀 프로필
├─ scenario.md                통합 시나리오와 모듈별 실습 정의
├─ agent02_sensing/
│  ├─ data/  smb_demand.csv · competitor_lineup.csv
│  ├─ test_cases/  smb_demand_실패.csv
│  └─ handoff/  segment_profile.md           ← ① 정답 예시
├─ agent03_action/
│  ├─ data/  product_catalog.csv · service_terms.md
│  └─ handoff/  proposal_draft.md            ← ② 정답 예시
└─ agent04_analysis/
   ├─ data/  partner_sales.csv · online_price_psi.csv · monthly_summary.csv · report_template.md
   ├─ test_cases/  monthly_summary_경계.csv · partner_sales_실패.csv
   └─ handoff/  report_draft.md              ← ③ 정답 예시
```

## 의도적으로 심어둔 데이터 함정

| Agent | 함정 | 학습 목적 |
|---|---|---|
| ① Sensing | **`전월대비` 컬럼이 `문의건수` 추이와 불일치** (사무서비스 193→225→278인데 '감소'로 표기) | 파생 컬럼을 믿지 말고 원본에서 재계산하는 습관 |
| ① Sensing | 공방이 303 → 46건으로 급감 | 수집 오류 가능성을 단정하지 않고 확인 필요로 남기기 |
| ② Action | 독자가 **파트너**인데 소상공인에게 말하듯 쓰기 쉬움 | 독자 지정이 없으면 Agent가 질문해야 합니다 |
| ③ Analysis | `구독건수`가 **누적**인데 매출처럼 합산하기 쉬움 | 지표의 성격을 구분합니다 |
| ③ Analysis | 해지율이 높은 파트너의 **구독 분모가 6~7건으로 작음** | 비율만 보면 과대 해석됩니다. 절대 건수와 함께 봐야 합니다 |
| ③ Analysis | 경계 파일의 표지 합계가 상세와 **3,600천원 차이** | 정합성 검사 습관 |

## 갱신 이력

| 버전 | 일자 | 내용 |
|---|---|---|
| v1 | 2026-09-04 | 9/4 메일 팀 프로필과 9/7 슬라이드 후보 시나리오 기반 초판. 컬럼 헤더는 임시값 |
| v1.1 (예정) | 9/11 | 사전과제 「필요 엑셀 컬럼 헤더 구상」과 9/8 전달 자료 반영 |
