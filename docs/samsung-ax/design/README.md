# 강의 덱 디자인 시스템 시안

Claude Design 캔버스의 **작업 파일**입니다. 여기서 고치고 다시 심습니다.

| 파일 | 슬라이드 |
|---|---|
| `Main.dc.html` | 표지 |
| `Section.dc.html` | 섹션 구분 (모듈 표지 + 시간 배분 바) |
| `Design6.dc.html` | 설계 6단계 |
| `Tags4.dc.html` | 꼬리표 4종 |
| `Blocks7.dc.html` | 지시문 7블록 |
| `Tests3.dc.html` | 테스트 3종 |
| `AgentSkill.dc.html` | 에이전트와 스킬 나누기 |
| `Handson.dc.html` | 실습 안내 템플릿 (8장 반복) |
| `ClickPath.dc.html` | 클릭 경로 템플릿 (5장 반복) |
| `Components.dc.html` | 컴포넌트와 토큰 (마스터) |
| `canvas.json` | 배치와 메모 |

사양은 [`../claude_design_handoff.md`](../claude_design_handoff.md). 슬라이드 72장 목록은 [`../slides_outline.md`](../slides_outline.md).

## 규칙

- **1280 × 720 고정.** 프레임은 줄어들지 않고 잘립니다. 내용을 늘릴 때 세로 합을 다시 셉니다.
- 여백 좌우 64 / 상 48 / 하 40. 헤더 하단 2px 잉크선, 푸터 상단 1px 룰.
- 서체 IBM Plex Sans KR (제목 700 / 본문 400), 경로·코드는 IBM Plex Mono. **Inter·Roboto·Arial 금지.**
- 꼬리표 네 기호는 **선 아이콘**으로 그립니다. 이모지는 인쇄·확대에서 깨지고 색을 못 바꿉니다.
  사람만 `#9A2C2C` · AI 초안 `#1C3F94` · AI 반복 `#0F6B4F` · 밖에서 `#6B6660`.
- **슬라이드에 들어가는 수치는 각 모듈 `04_answer/` 기준본에서만** 가져옵니다. 임의로 바꾸면 강사가 참가자 결과를 판정할 수 없습니다.
- 삼성 블루는 자리표시 토큰입니다. `Components.dc.html`의 토큰 값만 바꾸면 전체가 따라갑니다.

## 빌드 산출물

캔버스 파일(`samsung-b2b-ax-deck-system.html`)은 에디터가 통째로 들어가 2MB가 넘어 커밋하지 않습니다(`.gitignore`).
`.dc.html`과 `canvas.json`에서 다시 만듭니다.
