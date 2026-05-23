# html-decision

> **Claude Code 용 결정 캔버스 플러그인.** 사용자의 고민·결정사항을 HTML 결정 캔버스로 변환한다. 결정점 식별 → 옵션 도출 → Pros/Cons 비교 → 카드/표 시각화 → MD 결과 회수.

**`/html-decision <고민>` 으로 명시 호출**. ★ 자동 발동 X (Claude 가 대화 문맥 보고 알아서 띄우는 일 없음).

[![Version](https://img.shields.io/badge/version-0.6.0-2563eb)](https://github.com/yeonjun-cho/html-decision)
[![License](https://img.shields.io/badge/license-MIT-10b981)](LICENSE)

---

## 🎨 결정 캔버스 — *이해 + 일관성 + 단순함*

진짜 가독성 = **빠른 인식 + 충분한 이해 + 모든 case 일관**. 이 셋이 같이 가야 결정 캔버스가 *결정 도구* 로 작동.

### 디자인 원칙

| 원칙 | 의미 |
|---|---|
| **Layering, not hiding** | 배경 / 권장 / 영향 = 본문 안 *항상 visible*. 숨김 X. 정보 위계로 정리 |
| **Why-first per Q** | 각 Q 안 *💡 왜 이 결정 필요* highlight box prominent — 결정 근거 명시 |
| **모든 case 동일 layout** | N=0 (설명용) / N=1 / N=N+ — 동일 sidebar + 동일 본문 영역. 차이 = 컨텐츠 *값* 만 |
| **Visual metaphor over text** | Pros/Cons = ✅⚠️📌 icon + bullet 카드. 빽빽 텍스트 X |
| **Sidebar = 순수 목차** | anchor only. 컨텐츠 박제 X. 본문 = 모든 정보 |

### 본문 5 영역 (모든 case 동일)

| 영역 | 역할 |
|---|---|
| 📋 **배경 카드** | 분석 요약 bullet + "자세히" collapse |
| 🎯 **권장 요약 dashboard** | Q × 권장 옵션 × 신뢰도 × 이유 한눈 표 |
| **Q 카드 × N** | 권장 mini-card + 💡 왜 + 옵션 비교 표 + 옵션 detail 카드 + 영향 |
| ✏️ **결과 추출** | 생성 / 복사 / 초기화 버튼 |
| **Sidebar** | 진행 bar + 목차 anchor (📋 배경 / 🎯 권장 / Q1~Qn / ✏️ 결과 추출) |

### Q 카드 안 영역

| 영역 | 역할 |
|---|---|
| 🎯 **권장 mini-card** | 권장 옵션 + 신뢰도 + 1줄 이유 (Q 안 가장 prominent) |
| 💡 **왜 이 결정 필요** | 결정의 근거 / 맥락 / framework 정합 highlight box |
| **옵션 비교 표** | 옵션 / 비용 / 위험도 / 신뢰도 / 상태 (5 column) |
| **옵션 detail 카드** | ✅ Pros / ⚠️ Cons / 📌 예시 bullet — collapse default |
| 📊 **영향 영역** | 영향 file / 모듈 / Mermaid — collapse default |
| **선택** | radio + 기타 + 코멘트 |

---

## 📦 설치

Claude Code 안 슬래시 커맨드로 한 번에 끝.

```text
/plugin marketplace add https://github.com/yeonjun-cho/html-decision
/plugin install html-decision@html-decision
```

확인:

```text
/plugin
```

`html-decision` 이 `installed` 로 보이면 끝.

요구 사항: `python3` (macOS/Linux 기본 설치).

> ★ 향후 자동 갱신을 원하면 [🔄 업데이트](#-업데이트) 의 `autoUpdate` 박제 참조.

---

## 🚀 쓰는 법

**오직 명시 호출만 동작.** Claude 가 대화 문맥 보고 알아서 띄우는 일 X.

```text
/html-decision 새 프로젝트 프론트엔드 스택 결정
```

설명용 문서 (결정점 없이 배경만):

```text
/html-decision PoC 결과 분석 정리 (결정 없이 공유용)
```

### 결과 흐름

1. Claude 가 `<CWD>/.claude-history/html-decision/<YYYY-MM-DD-HH>-<topic>.html` 로 캔버스 저장
2. `SendUserFile` 로 파일 전달 — 브라우저에서 열어 옵션 선택
3. `[생성]` → `[복사]` → 채팅에 다시 붙여넣기
4. Claude 가 `<!-- html-decision-result -->` 매직 코멘트로 결과 인식 → 다음 단계 진행

---

## ⏱ 케이스 별 예상 시간

| 결정점 N | Claude output | 예상 시간 |
|---|---|---|
| **N=0** (설명용) | ~600-900 tokens | **20-35초** |
| **N=1-3** (단순) | ~800-1500 tokens | **25-50초** |
| **N=4-7** (표준) | ~2000-3500 tokens | **50초-2분** |
| **N=8+** (헤비) | ~5000-8000 tokens | **2-4분** |

★ Claude 가 JSON spec 만 출력 (~5x 압축) — render.py 가 HTML 렌더링 (server-side, ~1초). bottleneck = JSON spec 작성 시간.

---

## 📂 구조

```
html-decision/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── README.md
├── LICENSE
└── skills/
    └── html-decision/
        ├── SKILL.md
        ├── scripts/
        │   ├── render.py        # JSON → HTML 렌더러 (Python 3.8+, stdlib only)
        │   └── template.html    # static scaffold (CSS + JS)
        └── references/
            ├── content-rules.md   # 결정점 / 옵션 / Pros/Cons / 💡 왜 / 배경 / 영향 편집 룰
            └── output-formats.md  # MD/JSON paste-back parse rule
```

---

## 🔄 업데이트

자동 (권장) + 수동 둘 다 지원. **권장 = 자동** — 한 번 박제하면 사용자 부담 0.

### 🟢 자동 갱신 (권장)

`~/.claude/settings.json` 의 `extraKnownMarketplaces.html-decision` entry 에 **`"autoUpdate": true` 한 줄 추가**:

```json
{
  "extraKnownMarketplaces": {
    "html-decision": {
      "source": {
        "source": "git",
        "url": "https://github.com/yeonjun-cho/html-decision.git"
      },
      "autoUpdate": true
    }
  }
}
```

- **신규 사용자** = `/plugin marketplace add ...` 후 위 entry 자동 생성 → `autoUpdate` 만 추가
- **기존 사용자** = 이미 있는 entry 에 `autoUpdate` 한 줄만 추가
- 다음 Claude Code restart 시 **marketplace + plugin 자동 갱신** 활성

### 🟡 수동 갱신

```text
/plugin marketplace update html-decision
/plugin update html-decision@html-decision
/reload-plugins
```

### 🔍 현재 버전 확인

```text
/plugin
```

→ `html-decision is already at the latest version (X.Y.Z).` 같이 출력.

---

## 🧠 설계 원칙 (Anthropic best practices 적용)

| 원칙 | 적용 |
|---|---|
| [Bundled scripts > generated code](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | `scripts/render.py` 가 결정성 boilerplate 담당. Claude 는 JSON spec 만 |
| [Progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | SKILL.md → references → scripts |
| [Process in skill.md, context in references](https://www.mindstudio.ai/blog/claude-code-skills-architecture-skill-md-reference-files) | SKILL.md = process. content-rules.md = 편집 룰. template.html = 구조 |
| Self-contained HTML | 외부 의존 X (Mermaid CDN 만 — 영향 시각화 시) |

---

## 📝 라이선스

MIT
