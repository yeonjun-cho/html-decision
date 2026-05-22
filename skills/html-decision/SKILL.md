---
name: html-decision
description: 사용자가 `/html-decision` 슬래시 명령으로 명시 호출 시 동작. 결정점을 HTML 결정 캔버스로 변환 (옵션 도출 → Pros/Cons → Mermaid/sidebar/preview-panel 시각화 → MD 결과 회수). JSON spec 작성 → `scripts/render.py` 가 HTML 렌더링. HTML file 응답 (채팅 = file 경로 + 3-5줄 안내 한정). 결과 = `.claude-history/html-decision/` 안 저장 + SendUserFile 전달. ★ 자동 발동 X — 명시 슬래시 호출만.
argument-hint: <고민 설명>
---

# /html-decision

사용자 고민 → HTML 결정 캔버스. **JSON spec 생성 → render.py 가 HTML 렌더링** (Claude 는 HTML 직접 생성 X — output 토큰 절감).

호출 인자: `$ARGUMENTS` (비어있으면 종료)

---

## 1. 동작 (5 step)

1. `<고민>` + 현재 세션 context 흡수
2. **Tier 결정** (§2) + 결정점 N개 식별 + 각 결정점 구성 (옵션 + 권장 + Pros/Cons + context). 상세 룰 = `references/content-rules.md`
3. JSON spec 작성 (§3) — Tier 별 features 포함
4. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/html-decision/scripts/render.py --output <path>` 호출 (JSON = stdin heredoc)
5. SendUserFile + 짧은 채팅 응답 (§5)

★ ultrathink = T3 시 한정.

---

## 2. Tier 분기

| Tier | trigger | JSON `tier` | render features |
|---|---|---|---|
| **T1** | N=1~3 + §2.1 미충족 | `"T1"` | radio + 기타 + MD 버튼. 코멘트 생략. layout=simple |
| **T2** | N=4~7 + §2.1 미충족 | `"T2"` | T1 + 코멘트 + 권장 옵션 강조 + MD/JSON 버튼 |
| **T3** | **§2.1 trigger 1개 이상** | `"T3"` | T2 + sidebar/sticky-nav + 3-format + 풀세트 (§2.2) |

### 2.1 T3 trigger (OR — 하나라도 충족)

1. 결정점 N ≥ 5
2. 의존 sequence 명확 (A → B → C)
3. strategy / paradigm 결정 (옵션 별 Pros/Cons 비교가 본질적)
4. 선행 결정 ack 필요 (연속 cycle)

### 2.2 T3 풀세트 (situational — JSON 필드로 박제)

| 영역 | JSON 필드 | 발동 조건 |
|---|---|---|
| ack-area | `ack: {title, paragraphs[]}` | trigger #4 시 |
| Mermaid flowchart | `flow: {title, mermaid}` + `use_mermaid: true` | 의존 sequence 시각화 시 |
| section-intro | `section_intro: "..."` | 결정점 grouping 시 |
| preview-panel | 질문 안 `preview: {title, intro, options{value: {title, rows}}}` | 옵션 영향 예측 가능 시 |
| sidebar 보조 anchor | `sidebar_aux: [{href, label}]` | ack/flow 박제 시 |
| localStorage | `use_localstorage: true` (T3 default) | N≥5 시 |

### 2.3 v0.5.0 자동 차등 widget — Claude 명시 X, Tier 별 자동 박제

| widget | T1 | T2 | T3 | JSON 필드 |
|---|---|---|---|---|
| **권장 dashboard** (본문 위 한눈 표) | ❌ | ✅ | ✅ | 자동 도출 (options 의 `recommended:true` + `reason`) |
| **옵션 비교 matrix** (각 Q 안) | ❌ | ✅ (text only) | ✅ (text + radar) | 옵션 안 `matrix_summary: {pros_core, cons_core, cost_level, risk_level}` |
| **confidence indicator** (●●●●○) | ❌ | ❌ | ✅ | 옵션 안 `confidence: 1-5` |
| **radar chart** (5축 visual) | ❌ | ❌ | ✅ | 옵션 안 `axes: {benefit, cost, risk, impact, effort}` (1-5 척도) |
| **impact area** (영향 영역 시각화) | ❌ | ❌ | ✅ | 질문 안 `impact: {title, areas[], mermaid}` |

★ 자동 차등 = 사용자가 명시 X. T3 spec 박제 시 5 widget 자동. `matrix_summary` / `confidence` / `axes` / `impact` 없으면 해당 widget 자동 skip (graceful degradation).

---

## 3. JSON spec 구조

```json
{
  "topic": "<주제>",
  "h1": "<H1 텍스트>",
  "date": "YYYY-MM-DD",
  "branch": "<git 브랜치>",
  "meta": "<context 부연 — meta line 에 박제>",
  "source_html": "<CWD>/.claude-history/html-decision/<filename>.html",
  "tier": "T1|T2|T3",
  "questions": [
    {
      "id": "q1",
      "title": "Q1. <질문>",
      "nav_label": "Q1. <짧은 제목>",
      "desc": "<한 줄 설명>",
      "context": "<왜 결정 필요 — 1-2 문장>",
      "impact": {
        "title": "📊 영향 영역",
        "areas": ["<file/모듈/사람>", "..."],
        "mermaid": "flowchart LR\\n  Q1 --> X\\n  Q1 --> Y"
      },
      "options": [
        {
          "value": "<slug>",
          "label": "<옵션 label>",
          "recommended": true,
          "reason": "<1줄 이유>",
          "confidence": 4,
          "axes": {
            "benefit": 5, "cost": 4, "risk": 2, "impact": 5, "effort": 3
          },
          "matrix_summary": {
            "pros_core": "<60 char 핵심>",
            "cons_core": "<60 char 핵심>",
            "cost_level": "高|中|低",
            "risk_level": "高|中|低"
          },
          "detail": { "pros": "...", "cons": "...", "example": "..." }
        }
      ],
      "preview": { ... }
    }
  ]
}
```

### 3.1 v0.5.0 신설 필드 (T2/T3 자동 차등 widget 활성)

| 필드 | 위치 | Tier | 의미 |
|---|---|---|---|
| `options[].confidence` | option | T3 | 1-5 (●●●●○). 권장 옵션의 Claude 확신도 |
| `options[].axes` | option | T3 | 5축 (benefit/cost/risk/impact/effort) 각 1-5. radar chart 박제 |
| `options[].matrix_summary` | option | T2+ | 옵션 비교 matrix 박제용 (pros_core/cons_core 65 char 한도, cost/risk level) |
| `questions[].impact` | question | T3 | 영향 영역 시각화 (areas list 또는 mermaid) |

★ 위 필드 없으면 해당 widget 자동 skip. graceful degradation.

★ "기타 (직접 입력)" 옵션 = render.py 가 자동 박제 (마지막 위치). JSON 안 명시 X.

---

## 4. render.py 호출 패턴

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/html-decision/scripts/render.py" \
  --output "<CWD>/.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic-slug>.html" \
  <<'HTML_DECISION_SPEC_EOF'
{...JSON spec...}
HTML_DECISION_SPEC_EOF
```

- `CLAUDE_PLUGIN_ROOT` = Claude Code 가 플러그인 루트로 export 한 env (사용 가능). 없으면 `~/.claude/plugins/cache/html-decision/html-decision/<version>/` 사용
- `<CWD>` = **현재 작업 디렉토리 절대경로** (예: `/Users/musinsa/dev/<project>`). Claude 가 system context 의 cwd 박제. ★ `--output` 인자 = **절대경로 의무**
- `<topic-slug>` = 핵심 키워드 2-3 (kebab-case). 같은 시간 안 재호출 시 `-v2`, `-v3` 자동 부여 (사용자가 책임 — Claude 가 timestamp 또는 슬러그 변형)
- output path 와 JSON 안 `source_html` 필드 = **일치 의무 + 둘 다 절대경로** (paste-back 식별 / 세션 끊김 대비). 상대경로 박제 시 render.py 가 cwd 기준 절대로 자동 변환 (safety net) 하지만 명시 절대 권장

---

## 5. 짧은 채팅 응답 template

```
HTML 결정 캔버스 생성 완료.

| | |
|---|---|
| 파일 | `.claude-history/html-decision/<filename>.html` |
| 결정점 | <N>개 (Tier <T>) |

브라우저 → 선택 → [생성] → [복사] → 채팅 붙여넣기.
```

T3 시 1줄 추가: 📄 MD (기본) / 📦 JSON (자동화) / 💬 prompt (새 세션).

---

## 6. 의무 invariant

| 영역 | 의무 |
|---|---|
| 응답 형식 | HTML file 응답. 채팅 = file 경로 + 안내 3-5줄 |
| render.py 호출 | Claude 가 HTML 직접 생성 X — render.py 만 사용 |
| 옵션 마지막 = 기타 | render.py 자동 박제 (JSON 안 명시 X) |
| 권장 옵션 | `recommended: true` + `reason` 1줄 박제 (가능 시) |
| context block | `context` 필드 = 모든 결정점 의무 (왜 결정 필요) |
| Pros/Cons detail | `detail: {pros, cons, example?}` = strategy 결정 시 의무 |
| MD 파싱 | 결과 paste-back parse rule = `references/output-formats.md` |
| 저장 경로 | `<CWD>/.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic-slug>.html` (절대경로 의무) |

---

## 7. paste-back 인식

사용자가 `<!-- html-decision-result -->` 포함 MD 붙여넣기 = 결정 결과 인식. 각 `### Q<N>` 의 **답** 파싱 → 다음 step 진행.

parse 상세 = `references/output-formats.md`.

---

## 8. reference 인덱스

| 파일 | 언제 읽나 |
|---|---|
| `references/content-rules.md` | 결정점 분해 + 옵션 작성 + Pros/Cons + 권장 mark + ack/flow/preview content 패턴 |
| `references/output-formats.md` | paste-back 처리 시 (MD/JSON/prompt parse rule) |

★ `scripts/template.html` 과 `scripts/render.py` = 구조 SSOT. Claude 가 직접 읽을 필요 X (render.py 가 처리).
