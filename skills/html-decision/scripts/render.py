#!/usr/bin/env python3
"""html-decision 캔버스 렌더러.

사용법:
    python3 render.py --output <path> < spec.json
    python3 render.py --input <spec.json> --output <path>

JSON spec → HTML 결정 캔버스. template.html (같은 디렉토리) 박제 후 placeholders 치환.

Python 3.8+ stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape as html_escape
from pathlib import Path

TEMPLATE_NAME = "template.html"
MERMAID_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
)


def esc(s):
    """HTML escape. None → 빈 문자열."""
    if s is None:
        return ""
    return html_escape(str(s), quote=True)


def esc_attr(s):
    """attribute escape (quote=True 의 별칭)."""
    return esc(s)


def maybe(s):
    """None / 빈 문자열 → 빈 출력."""
    return s if s else ""


# ---------- per-section renderers ----------


def render_option(opt, q_id, idx):
    """단일 옵션 카드 HTML 생성."""
    is_other = opt.get("value") == "other"
    classes = ["option"]
    if opt.get("recommended"):
        classes.append("recommended")
    if is_other:
        classes.append("other-option")
    class_attr = " ".join(classes)

    rec_tag = (
        ' <span class="recommended-tag">권장</span>' if opt.get("recommended") else ""
    )
    label = opt.get("label", "")
    reason = opt.get("reason")
    detail = opt.get("detail") or {}

    parts = [
        f'  <label class="{class_attr}">',
        f'    <input type="radio" name="{q_id}" value="{esc_attr(opt["value"])}">',
        f'    <span class="opt-label">{label}{rec_tag}</span>',
    ]
    if reason:
        parts.append(f'    <span class="opt-reason">{reason}</span>')

    if detail and not is_other:
        pros = detail.get("pros")
        cons = detail.get("cons")
        example = detail.get("example")
        if pros or cons or example:
            parts.append('    <details class="option-detail">')
            parts.append("      <summary>자세히</summary>")
            parts.append('      <div class="detail-body">')
            if pros:
                parts.append(f'        <p class="pros"><strong>Pros</strong>: {pros}</p>')
            if cons:
                parts.append(f'        <p class="cons"><strong>Cons</strong>: {cons}</p>')
            if example:
                parts.append(
                    f'        <p class="example"><strong>예시</strong>: {example}</p>'
                )
            parts.append("      </div>")
            parts.append("    </details>")

    parts.append("  </label>")
    return "\n".join(parts)


def render_question(q, tier):
    """단일 결정점 카드 HTML 생성."""
    q_id = q["id"]
    title = q.get("title", "")
    desc = q.get("desc")
    context = q.get("context")
    options = q.get("options", [])
    preview = q.get("preview")

    parts = [
        f'<section class="question" id="{q_id}" data-qid="{q_id}">',
        f'  <h2 class="q-title">{title}</h2>',
    ]
    if desc:
        parts.append(f'  <p class="q-desc">{desc}</p>')
    if context:
        parts.append(f'  <div class="q-context">{context}</div>')
    parts.append("")

    for i, opt in enumerate(options):
        parts.append(render_option(opt, q_id, i))

    # 기타 옵션 (자동 박제 — 마지막 위치)
    other_in_options = any(o.get("value") == "other" for o in options)
    if not other_in_options:
        parts.append(
            f'  <label class="option other-option">\n'
            f'    <input type="radio" name="{q_id}" value="other">\n'
            f'    <span class="opt-label">기타 (직접 입력)</span>\n'
            f"  </label>"
        )
    parts.append(
        f'  <textarea class="other-input" data-for="{q_id}" rows="3" placeholder="직접 입력..."></textarea>'
    )

    # 코멘트 (T2+)
    if tier in ("T2", "T3"):
        parts.append("")
        parts.append(f'  <div class="comment-wrap" data-for-comment="{q_id}">')
        parts.append(
            '    <label class="comment-label">코멘트 (선택, 부연/조건/맥락)</label>'
        )
        parts.append(
            '    <textarea class="comment-input" rows="2" '
            'placeholder="선택 이유 / 추가 조건 / 부연 설명"></textarea>'
        )
        parts.append("  </div>")

    # preview-panel
    if preview:
        intro = preview.get("intro", "옵션 선택 시 영향 영역 view")
        parts.append("")
        parts.append(f'  <div class="preview-panel" data-for-preview="{q_id}">')
        parts.append(f'    <h5>{preview.get("title", "📋 선택 시 영향 (live)")}</h5>')
        parts.append(
            f'    <div class="preview-content"><p class="empty">{intro}</p></div>'
        )
        parts.append("  </div>")

    parts.append("</section>")
    return "\n".join(parts)


def render_sidebar(data, questions):
    """T3 sticky sidebar HTML 생성."""
    nav_items = []
    aux = data.get("sidebar_aux") or []
    for item in aux:
        href = item.get("href", "#")
        label = item.get("label", "")
        nav_items.append(f'      <li><a href="{href}" class="nav-q">{label}</a></li>')
    if aux and questions:
        nav_items.append('      <li style="margin-top: 8px;"></li>')

    for q in questions:
        q_id = q["id"]
        nav_label = q.get("nav_label") or q.get("title", q_id)
        nav_items.append(
            f'      <li><a href="#{q_id}" class="nav-q" data-q="{q_id}">{nav_label}</a></li>'
        )

    nav_items.append('      <li style="padding-top: 10px;">'
                     '<a href="#submit" class="nav-q" '
                     'style="color: var(--accent); font-weight: 600;">'
                     '✏️ 결과 추출</a></li>')

    return (
        '<aside class="sidebar">\n'
        "  <h3>진행</h3>\n"
        '  <div class="progress-wrap">\n'
        '    <div class="progress"><div class="progress-bar" id="prog-bar"></div></div>\n'
        f'    <span class="progress-text" id="prog-text">0/{len(questions)} 답함</span>\n'
        "  </div>\n"
        "  <h3>네비게이션</h3>\n"
        "  <nav>\n"
        '    <ul class="nav-list">\n'
        + "\n".join(nav_items)
        + "\n    </ul>\n"
        "  </nav>\n"
        "</aside>"
    )


def render_ack(ack):
    """ack-area 섹션 (선행 결정 박제)."""
    if not ack:
        return ""
    title = ack.get("title", "이전 결정 ack")
    paragraphs = ack.get("paragraphs") or []
    p_html = "\n".join(f"    <p>{p}</p>" for p in paragraphs)
    return (
        '<section id="ack">\n'
        '  <div class="ack-area">\n'
        f"    <h4>📥 {title}</h4>\n"
        f"{p_html}\n"
        "  </div>\n"
        "</section>"
    )


def render_flow(flow):
    """flow-area 섹션 (Mermaid timeline)."""
    if not flow:
        return ""
    title = flow.get("title", "흐름")
    mermaid = flow.get("mermaid", "")
    return (
        '<section id="flow">\n'
        '  <div class="flow-area">\n'
        f"    <h4>🔄 {title}</h4>\n"
        '    <div class="mermaid-wrap">\n'
        '      <div class="mermaid">\n'
        f"{mermaid}\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</section>"
    )


def render_section_intro(intro):
    """section-intro highlight box."""
    if not intro:
        return ""
    return f'<div class="section-intro">{intro}</div>'


def render_output_buttons(tier):
    """Tier 별 format 버튼."""
    btns = [
        '    <button class="gen active" onclick="generate(\'md\')" id="btn-md">📄 MD 생성</button>'
    ]
    if tier in ("T2", "T3"):
        btns.append(
            '    <button class="gen" onclick="generate(\'json\')" id="btn-json">📦 JSON 생성</button>'
        )
    if tier == "T3":
        btns.append(
            '    <button class="gen" onclick="generate(\'prompt\')" id="btn-prompt">💬 prompt 생성</button>'
        )
    return "\n".join(btns)


def render_preview_data_js(questions):
    """Q*_PREVIEWS const 박제 (JS data)."""
    preview_data = {}
    for q in questions:
        preview = q.get("preview")
        if not preview:
            continue
        options = preview.get("options") or {}
        if options:
            preview_data[q["id"]] = options
    if not preview_data:
        return "const PREVIEW_DATA = {}; window.PREVIEW_DATA = PREVIEW_DATA;"
    js = "const PREVIEW_DATA = " + json.dumps(preview_data, ensure_ascii=False, indent=2) + ";"
    js += "\nwindow.PREVIEW_DATA = PREVIEW_DATA;"
    return js


# ---------- main ----------


def build(data):
    """spec dict → 완성된 HTML 문자열."""
    topic = data.get("topic", "결정 캔버스")
    date = data.get("date", "")
    branch = data.get("branch")
    meta_extra = data.get("meta")
    source_html = data.get("source_html", "")
    # source_html = 절대경로 의무 (paste-back 식별 + 세션 끊김 대비).
    # 상대경로 박제 시 cwd 기준 절대경로 자동 변환 (safety net).
    if source_html and not Path(source_html).is_absolute():
        source_html = str(Path(source_html).resolve())
    tier = data.get("tier", "T1").upper()
    layout = data.get("layout") or ("with-sidebar" if tier == "T3" else "simple")
    use_mermaid = bool(data.get("use_mermaid") or data.get("flow"))
    use_localstorage = bool(data.get("use_localstorage", tier == "T3"))

    questions = data.get("questions") or []
    title = data.get("title") or topic

    meta_parts = []
    if date:
        meta_parts.append(date)
    if branch:
        meta_parts.append(branch)
    if meta_extra:
        meta_parts.append(meta_extra)
    meta_line = " · ".join(meta_parts) if meta_parts else ""

    h1 = data.get("h1") or topic

    # body 조립
    sidebar_block = render_sidebar(data, questions) if layout == "with-sidebar" else ""
    ack_section = render_ack(data.get("ack"))
    flow_section = render_flow(data.get("flow"))
    section_intro = render_section_intro(data.get("section_intro"))

    questions_block = "\n\n".join(render_question(q, tier) for q in questions)

    output_buttons = render_output_buttons(tier)
    preview_data_js = render_preview_data_js(questions)

    mermaid_script = MERMAID_CDN if use_mermaid else ""

    # template 로드 + 치환
    template_path = Path(__file__).parent / TEMPLATE_NAME
    template = template_path.read_text(encoding="utf-8")

    substitutions = {
        "{{TITLE}}": esc(title),
        "{{MERMAID_SCRIPT}}": mermaid_script,
        "{{LAYOUT_CLASS}}": layout,
        "{{SIDEBAR_BLOCK}}": sidebar_block,
        "{{H1}}": h1,
        "{{META}}": meta_line,
        "{{ACK_SECTION}}": ack_section,
        "{{FLOW_SECTION}}": flow_section,
        "{{SECTION_INTRO}}": section_intro,
        "{{QUESTIONS_BLOCK}}": questions_block,
        "{{OUTPUT_BUTTONS}}": output_buttons,
        "{{SOURCE_HTML}}": source_html,
        "{{TOPIC}}": topic.replace('"', '\\"'),
        "{{DATE}}": date,
        "{{TOTAL_Q}}": str(len(questions)),
        "{{USE_LOCALSTORAGE}}": "true" if use_localstorage else "false",
        "{{PREVIEW_DATA_JS}}": preview_data_js,
    }

    result = template
    for key, val in substitutions.items():
        result = result.replace(key, val)

    # 잔존 placeholder 검출 (디버그용)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", result)
    if leftover:
        sys.stderr.write(f"warning: unresolved placeholders: {set(leftover)}\n")

    return result


def parse_args():
    p = argparse.ArgumentParser(description="html-decision 캔버스 렌더러")
    p.add_argument("--output", "-o", required=True, help="출력 HTML 경로")
    p.add_argument(
        "--input",
        "-i",
        help="JSON spec 파일 경로 (생략 시 stdin 에서 읽음)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    if args.input:
        spec_text = Path(args.input).read_text(encoding="utf-8")
    else:
        spec_text = sys.stdin.read()

    try:
        data = json.loads(spec_text)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"JSON parse 실패: {e}\n")
        sys.exit(1)

    html = build(data)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ {output_path} ({len(html.splitlines())} 줄)")


if __name__ == "__main__":
    main()
