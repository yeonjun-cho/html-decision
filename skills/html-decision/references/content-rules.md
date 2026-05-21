# Content Rules

결정점 / 옵션 / 권장 / Pros/Cons / context / ack / flow / preview 의 **편집적 content 룰**. 구조 / CSS / JS = `scripts/template.html` + `scripts/render.py` 가 담당.

---

## 목차
- §1 결정점 분해 룰
- §2 옵션 작성 룰 + 권장 옵션 mark
- §3 Pros / Cons / 예시 작성 가이드
- §4 q-context wording (왜 결정 필요)
- §5 ack-area (선행 결정 박제) — T3 trigger #4 시
- §6 flow Mermaid (의존 sequence) — T3 의존 sequence 시
- §7 section-intro highlight — 결정점 grouping 시
- §8 preview-panel (옵션 영향 live preview) — T3 옵션 영향 예측 가능 시
- §9 vague 고민 처리

---

## 1. 결정점 분해 룰

- **독립 분해**: A 와 B 가 독립이면 별도 Q 분리
- **의존 sequence 인식**: A 결정이 B 의 input 이면 A 가 선행 (순서 의미)
- **영역 별 grouping**: 같은 영역 (예: 구조 / 적용 / 검증) = 같은 phase (T3 N≥8 시 phase 분리)
- **옵션 수**: max 5 + 기타 (1). 사용자 인지 부담 최소화

---

## 2. 옵션 작성 룰

| 필드 | 내용 |
|---|---|
| `value` | slug (kebab-case). 예: `"single"`, `"phased-2"` |
| `label` | 사용자에게 보이는 옵션 설명. HTML 허용 (`<code>`, `<strong>` 등) |
| `recommended` | `true` 1건만. Claude 가 권장 가능한 경우 한정. 사용자 결정 영역 (Claude oracle 불가) = 권장 생략 OK |
| `reason` | 1줄 이유. 권장 옵션 또는 단순 옵션에 박제 (Pros/Cons 가 필요 없을 때) |
| `detail` | Pros/Cons/예시 (§3) — strategy 결정 시 의무 |

★ "기타 (직접 입력)" 옵션 = render.py 자동 박제. JSON 안 명시 X.

---

## 3. Pros / Cons / 예시 작성 가이드

`detail: { pros, cons, example? }` — strategy 결정 시 의무 박제.

| 필드 | 내용 | 작성 가이드 |
|---|---|---|
| `pros` | 장점 1-2 문장 | 결정 영향 본질 영역. 결과 / 정합 / 단순화 등 |
| `cons` | 단점 1-2 문장 | 비용 / 부담 / risk 영역 |
| `example` | (선택) 구체 예시 | 수치 / file / code / 결과 — 가능 시 박제 |

생략 허용: 단순 binary / 명확한 차이 시 `reason` 1줄로 갈음 (`detail` 생략).

판단 기준: Pros 와 Cons 가 *같은* 문장 안 자연히 담기면 `reason` 만. *서로 다른* 영역이면 `detail` 박제.

---

## 4. q-context wording

`context` 필드 = 모든 결정점 의무. **왜 이 결정 필요한지** 1-2 문장.

### q-desc vs q-context

- `desc` = 질문 그 자체의 한 줄 부연 (예: "단일 PR vs phased")
- `context` = *왜* 이 결정 필요한지 (예: "Step 1-4 의 file 분포: references 5 / sub-agent 4 / skill body 2. 의존 sequence = Step 1 → 2 → 3 → 4.")

context 가 *명시* 불가 (단순 선호도) = 짧은 1문장 정합 박제 ("선호도 / 우선순위 결정").

---

## 5. ack-area — T3 trigger #4

연속 cycle 안 *이전 결정* 정리 highlight. working memo / 이전 결정 cross-ref.

```json
"ack": {
  "title": "이전 N 결정 확정 ack — working memo 박제",
  "paragraphs": [
    "working memo: <code>{path}</code> §{section} 안 결정 통합 표 박제.",
    "{결정 요약 1-2 문장 — 영역 별 카운트 / 핵심 결과}",
    "★ 본 결정 = 위 결정 후 다음 step 진행 전 사전 확정 의무 영역."
  ]
}
```

`paragraphs[]` = HTML 허용 (`<code>`, `<strong>` 등).

---

## 6. flow Mermaid — 의존 sequence 시각화

```json
"flow": {
  "title": "{영역} timeline",
  "mermaid": "flowchart LR\n    A[Step 1] --> B[Step 2]\n    B --> C[Step 3]\n    style A fill:#dbeafe,stroke:#1e40af"
},
"use_mermaid": true
```

★ `use_mermaid: true` 박제 시 render.py 가 Mermaid CDN 자동 박제.

발동 조건: 의존 sequence (A → B → C) 가 *명확* + 시각화 가치 있을 때 한정. 단순 list 로 갈음 가능 시 list 만 박제 (grace degradation).

---

## 7. section-intro highlight

```json
"section_intro": "Q1 = {영역 1} / Q2 = {영역 2} / Q3 = {영역 3} (★ {강조 메모})."
```

발동 조건: 결정점 grouping (phase 분리 또는 영역 별 묶음) 시 한정 박제.

---

## 8. preview-panel — 옵션 영향 live preview

옵션 선택 시 영향 영역 즉시 view (table). 질문 안 `preview` 필드:

```json
"preview": {
  "title": "📋 선택 시 PR 분포 (live)",
  "intro": "옵션 선택 시 PR 단계 / file 분포 view",
  "options": {
    "single": {
      "title": "단일 commit / PR",
      "rows": [["PR 수", "1"], ["file", "17-18"], ["line", "~+1500/-300"]]
    },
    "phased-2": {
      "title": "phased 2 단계",
      "rows": [["PR 1", "base (5 file)"], ["PR 2", "main (12 file)"]]
    }
  }
}
```

발동 조건: 옵션 영향 *예측 가능* + 영향 영역이 구체적일 때 (예: PR 분포 / file 영향 / 수치 변경) 한정 박제.

---

## 9. vague 고민 처리

- 명확치 않은 고민 = best-guess 다중 옵션 + 기타 (자동 박제) 활용
- 한 cycle 안 자체 해결 — HTML 결과로 즉시 응답 (모든 의문은 다중 옵션 + 기타 입력 으로 흡수)

---

## 10. 의무 invariant 요약

| 영역 | 의무 |
|---|---|
| 옵션 max | 5 + 기타 (자동) |
| 권장 옵션 | 1건 한정 + `reason` 1줄. 가능 시 박제 |
| context | 모든 결정점 박제 (없으면 짧은 정합 1문장) |
| Pros/Cons | strategy 결정 시 의무 박제 |
| ack/flow/preview | situational — trigger 충족 시만 박제 |
| HTML escape | `label` / `paragraphs` 등 HTML 허용 필드 = Claude 가 직접 HTML 입력. 그 외 (`title`, `desc`, `context`) = plain text (render.py 는 이 필드들도 그대로 박제 — XSS 영역 X, 자체 출력 file) |
