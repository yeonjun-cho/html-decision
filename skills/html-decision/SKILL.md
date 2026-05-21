---
name: html-decision
description: 사용자의 고민·결정사항을 HTML 결정 캔버스로 변환. 결정점 식별 → 옵션 도출 → 시각화 → MD 출력 area. HTML file 응답 (채팅 = file 경로 + 3-5줄 안내 한정). 결과 = `.claude-history/html-decision/` 안 저장 + SendUserFile 전달. 사용자가 "고민이다", "결정 도와줘", "어떻게 할지 모르겠어" 같은 표현을 쓰거나 결정점이 2개 이상 보이면 발동.
argument-hint: <고민 설명>
---

# /html-decision

사용자 고민을 HTML 결정 캔버스로 시각화. **HTML file 로 응답** — 채팅 = file 경로 + 진행 안내 3-5줄 한정.

호출 인자: `$ARGUMENTS` (비어있으면 종료)

---

## 1. 동작 (5 step)

1. `<고민>` + 현재 세션 context 흡수
2. **결정점 (decision points) N개** 식별. 각 결정점 = title + 옵션 2-5개 + 기타 + (가능 시) 권장 옵션 1건 + 1줄 이유
3. **Tier 결정** (§2) → 필요한 reference 파일만 읽기
4. HTML 생성 → 저장 → `SendUserFile` 전달
5. 채팅에 §6 template 으로 짧게 응답

---

## 2. Tier 분기 (★ 속도 핵심)

| Tier | 결정점 N | 읽을 reference | 기능 |
|---|---|---|---|
| **T1** | 1~3 | `references/html-template.md` 만 | radio/checkbox + 기타 + MD 버튼 1개. 코멘트 X. CSS 최소. |
| **T2** | 4~7 | `html-template.md` + `output-formats.md` | T1 + 코멘트 textarea + 권장 옵션 강조 + MD/JSON 버튼 2개 |
| **T3** | 8+ | 위 + `widgets.md` | T2 + phase grouping + sticky sidebar + 3-format 풀 + Mermaid/Chart.js (필요 시) |

**원칙**: tier 초과 기능 박제 금지. T1 에 sidebar / Mermaid / localStorage / toggle-all 박제 X. 단순함이 곧 속도.

**ultrathink**: Tier 3 일 때만. T1/T2 = standard reasoning.

---

## 3. 결정점 분해 룰

- 독립 분해: A 와 B 가 독립이면 별도 Q
- 의존 sequence: A 결정이 B 의 input 이면 A 가 선행
- 같은 영역 = 같은 phase (T3 만 phase 적용)
- 옵션 max 5 + 기타 1
- 권장 옵션 1건 마킹 (가능 시) + 1줄 이유. Claude 가 판단 불가 영역은 권장 생략 OK

vague 고민 = best-guess 다중 옵션 + 기타 (직접 입력) 으로 한 cycle 안 흡수.

---

## 4. 의무 invariant (모든 Tier 공통)

| 영역 | 의무 |
|---|---|
| 응답 형식 | HTML file 응답. 채팅 = file 경로 + 안내 3-5줄 |
| 옵션 마지막 | 각 결정점 = 기타 (직접 입력) textarea, 항상 마지막 위치 |
| MD output area | `<pre id="output">` + 생성 button + 복사 button |
| magic comment | MD 첫 줄 `<!-- html-decision-result -->` 박제 |
| 출처 박제 | MD header 에 `**출처 HTML**: <filepath>` 박제 (세션 끊김 대비) |
| 저장 | `.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic-slug>.html` |
| frontend-design plugin | 활성 시 aesthetic 자동 강화 — form 동작은 그대로 보존 |

---

## 5. 저장 + 전달

### 5.1 파일명

`.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic-slug>.html`

- `<topic-slug>` = 핵심 키워드 2-3 (kebab-case)
- timestamp = 시 단위 (분/초 X)
- 같은 시 안 재호출 시 `-v2`, `-v3` … suffix (기존 보존)

### 5.2 전달

```
SendUserFile(files=[<filepath>], caption="<짧은 설명>", status="normal")
```

---

## 6. 짧은 채팅 응답 template

```
HTML 결정 캔버스 생성 완료.

| | |
|---|---|
| 파일 | `.claude-history/html-decision/<filename>.html` |
| 결정점 | <N>개 (Tier <T>) |

브라우저 → 선택 → [생성] → [복사] → 채팅 붙여넣기.
```

T3 + 다중 format 시 한 줄 추가:
- 📄 MD (기본 / 후속 reference) / 📦 JSON (자동화) / 💬 prompt (새 세션)

---

## 7. paste-back 인식

사용자가 `<!-- html-decision-result -->` 포함 MD 붙여넣기 = 결정 결과 인식. 각 `### Q<N>` 의 **답** 파싱 → 다음 step 진행.

paste-back 구조 상세는 `references/output-formats.md` 안 §parse-rule 참조 (paste-back 처리 시점에 읽기).

---

## 8. reference 인덱스

| 파일 | 언제 읽나 |
|---|---|
| `references/html-template.md` | 모든 Tier — HTML 구조 + base CSS + base JS |
| `references/output-formats.md` | T2+ — MD/JSON/prompt spec 전부. paste-back 시점에도 읽기 |
| `references/widgets.md` | T3 만 — widget matrix (slider/sortable/toggle) + 시각화 룰 (Mermaid/Chart.js) |

**규칙**: 위 표에 없는 tier 의 reference 는 절대 읽지 말 것. 토큰 절감의 핵심.
