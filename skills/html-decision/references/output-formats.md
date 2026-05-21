# Output Formats

T2+ 에서 읽기. MD / JSON / prompt 세 format 의 정합 spec + paste-back parse rule.

---

## 1. MD format (기본 의무 — 모든 Tier)

```markdown
<!-- html-decision-result -->
# {주제} — 결정 결과

**출처 HTML**: `.claude-history/html-decision/{filename}.html`
**날짜**: YYYY-MM-DD

---

## {Phase 명}  ← T3 phase grouping 시만

### Q1. {질문}
- **답**: {단일 답}
- **코멘트**:
  {멀티라인 텍스트 — newline 그대로 보존}

### Q2. {질문}
**답**:
- {답 1}
- {답 2}
**코멘트**:
{텍스트}
```

### 1.1 핵심 rule

- **첫 줄 magic comment** `<!-- html-decision-result -->` 의무 (paste-back 인식 마커)
- **출처 HTML 박제** 의무 (세션 끊김 대비 — 다른 시점 paste-back 시 식별)
- **단일 답**: `- **답**: {답}`
- **다중 답**: `**답**:\n- {답 1}\n- {답 2}`
- **코멘트**: 옵션 (1·2·…) 선택 시 + 사용자 입력 있을 때만 박제. 빈 코멘트 = 박제 X
- **기타 선택 시**: `- **답**: 기타: {free-form}` — 코멘트 박제 X (mutual exclusive)
- **멀티라인 보존**: textarea `\n` 그대로. 한 줄 처리 / truncate 금지

### 1.2 mutual exclusive (paste-back parse 단순화)

| 선택 | 박제 |
|---|---|
| 옵션 1·2·… + 코멘트 | `**답**: {옵션}` + `**코멘트**: {부연}` |
| 기타 | `**답**: 기타: {free-form}` (코멘트 X) |

---

## 2. JSON format (T2+)

```json
{
  "topic": "{주제}",
  "source_html": "{filepath}",
  "date": "YYYY-MM-DD",
  "decisions": {
    "q1": {
      "type": "radio",
      "value": "{선택 옵션 label}",
      "comment": "{있을 시}",
      "is_other": false
    },
    "q2": {
      "type": "checkbox",
      "values": ["{답 1}", "{답 2}"],
      "comment": "..."
    },
    "q3": {
      "type": "slider",
      "value": 7,
      "max": 10
    }
  }
}
```

### JS 구현

```javascript
function toJSON(answers) {
  const decisions = {};
  for (const [qid, a] of Object.entries(answers)) {
    const d = { type: a.type };
    if (Array.isArray(a.value)) d.values = a.value;
    else d.value = a.value;
    if (a.comment && !a.isOther) d.comment = a.comment;
    if (a.isOther) d.is_other = true;
    decisions[qid] = d;
  }
  return JSON.stringify({
    topic: TOPIC, source_html: SOURCE_HTML, date: DATE, decisions
  }, null, 2);
}
```

---

## 3. prompt format (T3)

MD 의 자연어 풀어쓰기 + 다음 step instruction 박제. 새 Claude 세션 시작 시 직접 prompt 로 사용.

```
이전 HTML 결정 캔버스 (`{filepath}`) 결과를 정리한 내용입니다.

주제: {주제}
날짜: {date}

결정 사항:

Q1. {질문}
→ {답}
  부연: {코멘트}

Q2. {질문}
→ {답 1}, {답 2}
  부연: {코멘트}

이 결정들을 기반으로 다음을 도와주세요: [사용자가 채울 영역]
```

### JS 구현

```javascript
function toPrompt(answers) {
  let p = `이전 HTML 결정 캔버스 (\`${SOURCE_HTML}\`) 결과를 정리한 내용입니다.\n\n`;
  p += `주제: ${TOPIC}\n날짜: ${DATE}\n\n결정 사항:\n\n`;
  for (const a of Object.values(answers)) {
    p += `${a.title}\n`;
    if (Array.isArray(a.value)) {
      p += `→ ${a.value.join(', ')}\n`;
    } else {
      p += `→ ${a.value || '(미선택)'}\n`;
    }
    if (a.comment && !a.isOther) {
      p += `  부연: ${a.comment.replace(/\n/g, ' ')}\n`;
    }
    p += '\n';
  }
  p += '이 결정들을 기반으로 다음을 도와주세요: [사용자가 채울 영역]\n';
  return p;
}
```

---

## 4. paste-back parse rule (Claude 가 MD 흡수 시)

사용자가 채팅에 `<!-- html-decision-result -->` 첫 줄 포함 MD 붙여넣기 = 결정 결과 인식.

### 4.1 parse 순서

1. 첫 줄 magic comment 확인 → 결정 결과 mode 진입
2. `**출처 HTML**: \`{path}\`` 추출 → 어떤 캔버스인지 식별
3. 각 `### Q<N>. {질문}` block 파싱
4. block 안:
   - `**답**:` line = 답 본문
   - `**답**:` 뒤 list (`- {답}`) = 다중 답
   - `**코멘트**:` line = 부연 (없으면 skip)
   - multi-line 코멘트 = 다음 빈 줄 또는 `**답**` / `### Q` 만날 때까지

### 4.2 답 종류 식별

- `**답**: 기타: {text}` → 사용자 자유 입력 답
- `**답**: {label}` → 옵션 선택 답
- `**답**:\n- ...` → 다중 선택 답

### 4.3 다음 step

paste-back 흡수 후 사용자가 명시 요청한 다음 행동 수행. 흔한 패턴:

- 새 코드 작성 / 수정
- 다음 결정 cycle 시작 (`/html-decision` 재호출)
- 결정 요약 정리
- 결정 기반 문서 생성 (Confluence / Jira / Slack 메시지)
