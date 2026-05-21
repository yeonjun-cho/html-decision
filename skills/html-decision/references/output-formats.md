# Output Formats — paste-back parse rule

★ MD/JSON/prompt 출력 *생성 로직* = `scripts/template.html` 안 embedded JS (`toMarkdown` / `toJSON` / `toPrompt`). 이 문서는 **paste-back 시 Claude 가 흡수하는 rule** 만 담당.

---

## 1. MD format 예시 (template JS 출력)

```markdown
<!-- html-decision-result -->
# {주제} — 결정 결과

**출처 HTML**: `.claude-history/html-decision/{filename}.html`
**날짜**: YYYY-MM-DD

---

### Q1. {질문}
- **답**: {단일 답}
- **코멘트**:
  {멀티라인 텍스트 — newline 그대로 보존}

### Q2. {질문}
**답**:
- {답 1}
- {답 2}
```

### 1.1 핵심 rule

- **첫 줄 magic comment** `<!-- html-decision-result -->` (paste-back 인식 마커)
- **출처 HTML 박제** (세션 끊김 대비)
- **단일 답**: `- **답**: {답}`
- **다중 답**: `**답**:\n- {답 1}\n- {답 2}`
- **코멘트**: 옵션 (1·2·…) 선택 + 입력 값 존재 시 한정 박제
- **기타 선택 시**: `- **답**: 기타: {free-form}` 박제 (코멘트 생략 — mutual exclusive)
- **멀티라인 보존**: textarea `\n` 그대로 박제

---

## 2. JSON format 예시

```json
{
  "topic": "...",
  "source_html": "...",
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
      "values": ["{답 1}", "{답 2}"]
    }
  }
}
```

---

## 3. prompt format 예시

```
이전 HTML 결정 캔버스 (`{filepath}`) 결과를 정리한 내용입니다.

주제: {주제}
날짜: {date}

결정 사항:

Q1. {질문}
→ {답}
  부연: {코멘트}

이 결정들을 기반으로 다음을 도와주세요: [사용자가 채울 영역]
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
   - `**코멘트**:` line = 부연 (있을 시 본문 흡수)
   - multi-line 코멘트 = 다음 빈 줄 또는 `**답**` / `### Q` 만날 때까지

### 4.2 답 종류 식별

- `**답**: 기타: {text}` → 사용자 자유 입력 답
- `**답**: {label}` → 옵션 선택 답
- `**답**:\n- ...` → 다중 선택 답

### 4.3 다음 step

paste-back 흡수 후 사용자 명시 요청 수행. 흔한 패턴:

- 새 코드 작성 / 수정
- 다음 결정 cycle 시작 (`/html-decision` 재호출)
- 결정 요약 정리
- 결정 기반 문서 생성 (Confluence / Jira / Slack 메시지)
