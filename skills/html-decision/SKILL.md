---
name: html-decision
description: 사용자가 `/html-decision` 슬래시 명령으로 명시 호출 시 동작. 결정점을 HTML 결정 캔버스로 변환 (옵션 도출 → Pros/Cons → 카드/표 시각화 → MD 결과 회수). JSON spec 작성 → `scripts/render.py` 가 HTML 렌더링. HTML file 응답 (채팅 = file 경로 + 3-5줄 안내 한정). 결과 = `.claude-history/html-decision/` 안 저장 + SendUserFile 전달. ★ 자동 발동 X — 명시 슬래시 호출만.
argument-hint: <고민 설명>
---

# /html-decision

사용자 고민 → HTML 결정 캔버스. **JSON spec 생성 → render.py 가 HTML 렌더링** (Claude 는 HTML 직접 생성 X — output 토큰 절감).

호출 인자: `$ARGUMENTS` (비어있으면 종료)

★ 결정점 N=0 (설명용 문서) 도 가능 — 동일 layout, 컨텐츠만 다름.

---

## 1. 동작 (5 step)

1. `<고민>` + 현재 세션 context 흡수
2. **결정점 N개 식별** + 각 결정점 구성 (제목 / 왜 필요 / 옵션 + 권장 + Pros/Cons + 상태). N=0 가능
3. JSON spec 작성 (§3) — `references/content-rules.md` 참조
4. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/html-decision/scripts/render.py --output <path>` 호출 (JSON = stdin heredoc)
5. SendUserFile + 짧은 채팅 응답 (§5)

★ ultrathink = 결정점 ≥ 5 또는 strategy 결정 시.

---

## 2. 일관 layout (모든 case 동일)

모든 N (0, 1, 2+) 에 동일 구조. 차이 = 컨텐츠의 *값* 만.

| 영역 | 위치 | 동작 |
|---|---|---|
| **sidebar** | 좌측 240px | 진행 bar + 목차 (📋 배경 / 🎯 권장 요약 / Q1~Qn / ✏️ 결과 추출 anchor only) |
| **header** | 본문 상단 | h1 + meta (날짜·브랜치) |
| **📋 배경 카드** | 본문 (id="bg") | 분석 요약 bullet + "자세히" collapse |
| **🎯 권장 요약 dashboard** | 본문 (id="rec") | Q × 권장 옵션 × 신뢰도 × 이유 표. N=0 시 empty state |
| **Q 카드 × N** | 본문 | 권장 mini + 💡 왜 + 옵션 비교 표 + 옵션 detail (카드) + 영향 + 선택 |
| **✏️ 결과 추출** | 본문 하단 (id="submit") | 생성 / 복사 / 초기화 버튼. N=0 시 disabled |

★ Tier 분기 X — 모든 case 동일 layout. Tier 차등 = *콘텐츠 풍부도* 만 (Pros/Cons 깊이, 영향 영역 명시 등).

---

## 3. JSON spec 구조

```json
{
  "topic": "<주제>",
  "h1": "<H1 텍스트>",
  "date": "YYYY-MM-DD",
  "branch": "<git 브랜치>",
  "meta": "<context 부연>",
  "source_html": "<CWD>/.claude-history/html-decision/<filename>.html",
  "background": {
    "title": "📋 배경 — 분석 요약",
    "bullets": ["배경 bullet 1", "배경 bullet 2", "..."],
    "detail": "<선택. <details> 안 펼침 콘텐츠>"
  },
  "questions": [
    {
      "id": "q1",
      "title": "Q1. <질문>",
      "nav_label": "Q1. <짧은 제목>",
      "desc": "<한 줄 설명>",
      "why": "<💡 왜 이 결정 필요 — 1-3 문장. 결정의 근거·맥락 명시>",
      "impact": {
        "areas": ["<file/모듈/사람>", "..."],
        "mermaid": "<선택. flowchart code>"
      },
      "options": [
        {
          "value": "<slug>",
          "label": "<옵션 label>",
          "recommended": true,
          "reason": "<1줄 이유>",
          "confidence": 4,
          "matrix_summary": {
            "cost_level": "낮|중|높",
            "risk_level": "낮|중|높"
          },
          "status": "✓ 정합 | ⚠️ violation | ⚡ boundary",
          "detail": {
            "pros": "<문자열 또는 list of strings>",
            "cons": "<문자열 또는 list of strings>",
            "example": "<구체 예시>"
          }
        }
      ]
    }
  ]
}
```

### 3.1 신설 / 변경 필드 (v0.6.0)

| 필드 | 위치 | 의미 |
|---|---|---|
| `question.why` | question | 💡 왜 이 결정 필요 (highlight box 콘텐츠). **모든 Q 의무** |
| `option.status` | option | ✓ 정합 / ⚠️ violation / ⚡ boundary 등 1단어 + icon. 옵션 비교 표 안 박제 |
| `option.confidence` | option | 1-5 (●●●●○). 권장 옵션 의무. 다른 옵션 선택 |
| `option.matrix_summary` | option | `{cost_level, risk_level}` 만 — pros_core/cons_core 제거 (option detail 카드가 대체) |
| `background.bullets` | top-level | 배경 카드 bullet 영역 (기존 `ack.paragraphs` 대체) |
| `background.detail` | top-level | "자세히" collapse 안 텍스트 |

### 3.2 제거 필드

| 제거 | 사유 |
|---|---|
| `option.axes` | radar chart 제거 |
| `flow` | 본문 위 flow Mermaid 영역 제거 (Q 안 `impact.mermaid` 만 유지) |
| `section_intro` | 시각 noise — 제거 |
| `sidebar_aux` | sidebar 보조 anchor 영역 제거 (sidebar = 순수 목차) |
| `preview` | preview-panel 제거 (옵션 비교 표가 흡수) |
| `tier` | Tier 분기 제거 — 모든 case 동일 layout |

★ "기타 (직접 입력)" 옵션 = render.py 자동 박제. JSON 안 명시 X.

---

## 4. render.py 호출 패턴

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/html-decision/scripts/render.py" \
  --output "<CWD>/.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic-slug>.html" \
  <<'HTML_DECISION_SPEC_EOF'
{...JSON spec...}
HTML_DECISION_SPEC_EOF
```

- `CLAUDE_PLUGIN_ROOT` = Claude Code 가 export 한 env. 없으면 `~/.claude/plugins/cache/html-decision/html-decision/<version>/` 사용
- `<CWD>` = 현재 작업 디렉토리 절대경로
- `<topic-slug>` = 핵심 키워드 2-3 (kebab-case). 같은 시간 충돌 시 `-v2`, `-v3` suffix
- output path 와 JSON 안 `source_html` = **일치 의무 + 둘 다 절대경로**. 상대경로 박제 시 render.py 가 자동 변환

---

## 5. 짧은 채팅 응답 template

```
HTML 결정 캔버스 생성 완료.

| | |
|---|---|
| 파일 | `<output path>` |
| 결정점 | <N>개 |

브라우저 → 선택 → [생성] → [복사] → 채팅 붙여넣기.
```

★ N=0 시 "결정점 0개 (설명용 문서)" 박제.

---

## 6. 의무 invariant

| 영역 | 의무 |
|---|---|
| 응답 형식 | HTML file 응답. 채팅 = file 경로 + 안내 3-5줄 |
| render.py 호출 | Claude 가 HTML 직접 생성 X — render.py 만 사용 |
| 모든 case 동일 layout | N=0/1/2+ 무관 — sidebar + 5 영역 동일 박제 |
| 💡 왜 이 결정 필요 (`question.why`) | 모든 Q 의무 박제 |
| 권장 옵션 | `recommended: true` + `reason` 1줄 + `confidence` 박제 (가능 시) |
| matrix_summary | `cost_level` + `risk_level` 의무 (옵션 비교 표 활용) |
| option detail 카드 | 권장 옵션 = pros/cons/example 의무. 다른 옵션 = 선택 |
| MD 파싱 | paste-back parse rule = `references/output-formats.md` |
| 저장 경로 | `<CWD>/.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic-slug>.html` 절대경로 |

---

## 7. paste-back 인식

사용자가 `<!-- html-decision-result -->` 포함 MD 붙여넣기 = 결정 결과 인식. 각 `### Q<N>` 의 **답** 파싱 → 다음 step 진행.

parse 상세 = `references/output-formats.md`.

---

## 8. reference 인덱스

| 파일 | 언제 읽나 |
|---|---|
| `references/content-rules.md` | 결정점 분해 + 옵션 작성 + Pros/Cons + 💡 왜 wording + 배경/영향 content 패턴 |
| `references/output-formats.md` | paste-back 처리 시 (MD/JSON/prompt parse rule) |

★ `scripts/template.html` 과 `scripts/render.py` = 구조 SSOT. Claude 가 직접 읽을 필요 X (render.py 가 처리).
