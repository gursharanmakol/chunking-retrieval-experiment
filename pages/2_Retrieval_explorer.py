"""Retrieval explorer — frozen Experiment 2 evidence only.

Reads experiment-2-retrieval/site-artifact/retrieval-diagnosis.json.
Does not import the retrieval runner, does not load an embedding model,
and does not compute BM25 or RRF.

Run:  streamlit run app.py   then open Retrieval explorer
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path

import streamlit as st

import config

SITE_URL = "https://aiinpracticehub.com/"
REPO_URL = "https://github.com/gursharanmakol/chunking-retrieval-experiment"
ARTIFACT_PATH = (
    Path(__file__).resolve().parent.parent
    / "experiment-2-retrieval"
    / "site-artifact"
    / "retrieval-diagnosis.json"
)

HEADLINE_K = 3
EXPECTED_QUESTIONS = 5
EXPECTED_METHODS = 3
EXPECTED_CHUNKS = 13
EXPECTED_RESULTS = 15
EXPECTED_RANKING_ROWS = 195

RETRIEVED_ONLY = "Retrieved chunks only"
ALL_CHUNKS = "All chunks"

SCORE_LABELS = {
    "dense": "cosine",
    "bm25": "BM25 score",
    "rrf": "RRF score",
}

METHOD_BUTTONS = {
    "dense": "Dense",
    "bm25": "BM25",
    "rrf": "RRF",
}

METHOD_CAPTIONS = {
    "dense": "Embedding similarity · all-MiniLM-L6-v2, cosine",
    "bm25": "Keyword matching · BM25Okapi",
    "rrf": "Combines Dense and BM25 ranks · k=60",
}

_BRAND_RECTS = (
    '<rect x="12" y="50" width="40" height="32" rx="9" fill="#E7F0EE" stroke="#0F6E56" stroke-width="4.5"/>'
    '<rect x="48" y="50" width="40" height="32" rx="9" fill="#E8EFF6" stroke="#185FA5" stroke-width="4.5"/>'
    '<rect x="30" y="16" width="40" height="32" rx="9" fill="#EEEDF8" stroke="#534AB7" stroke-width="4.5"/>'
)
BRAND_MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
    f"{_BRAND_RECTS}</svg>"
)
_BRAND_FONT = "'Segoe UI',-apple-system,BlinkMacSystemFont,system-ui,sans-serif"
_BRAND_TEXT = (
    f'font-family="{_BRAND_FONT}" font-size="16.5" font-weight="800"'
    ' letter-spacing="-0.3" lengthAdjust="spacingAndGlyphs" y="22.77"'
)
BRAND_LOCKUP = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 202 34" width="202" height="34">'
    f'<g transform="scale(0.34)">{_BRAND_RECTS}</g>'
    f'<text x="45" textLength="97.9" fill="#26262C" {_BRAND_TEXT}>AI in Practice</text>'
    f'<text x="169.15" textLength="32" fill="#534AB7" {_BRAND_TEXT}>Hub</text>'
    "</svg>"
)

st.set_page_config(
    page_title="Retrieval explorer",
    page_icon=BRAND_MARK,
    layout="wide",
    initial_sidebar_state="auto",
)
st.logo(BRAND_LOCKUP, icon_image=BRAND_MARK, size="large", link=SITE_URL)

PANEL_HEIGHT = 640
CHARS_PER_LINE = 88
LINE_HEIGHT = 19
CARD_CHROME = 58

st.markdown(
    """
    <style>
      .stApp { background-color: #FCFCFB;
               background-image: radial-gradient(#E4E4E8 1.4px, transparent 1.4px);
               background-size: 32px 32px; }
      .block-container { max-width: 1600px; padding-top: 1.5rem; padding-bottom: 2rem;
                         background: #FFFFFF; border-radius: 12px;
                         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); }
      [data-testid="stMain"] { background: transparent; }
      [data-testid="stMain"] iframe { background: #FFFFFF; }
      [data-testid="stSidebar"] { min-width: 260px; max-width: 280px; }
      section[data-testid="stSidebar"] { width: 280px !important; }
      [data-testid="stSidebarCollapseButton"],
      [data-testid="stExpandSidebarButton"] {
        visibility: visible !important; opacity: 1 !important;
      }
      [data-testid="stRadioOption"] { border: 1px solid #E8E8E4; border-radius: 6px;
                              background: #FFFFFF;
                              padding: .08rem .5rem .08rem .3rem; }
      [data-testid="stRadioOption"] p { color: #5F5E5A; }
      [data-testid="stRadioOption"]:hover { background: #F4F4F1; border-color: #B4B4AE; }
      [data-testid="stRadioOption"][data-selected="true"] { background: #E7F0EE;
                              border-color: #0F6E56; }
      [data-testid="stRadioOption"][data-selected="true"] p { color: #0F6E56;
                              font-weight: 700; }
      .anchor { border: 1px solid #E8E8E4; border-left: 4px solid #0F6E56;
                border-radius: 10px; background: #FFFFFF; padding: 1rem 1.1rem;
                margin: .4rem 0 .85rem; }
      .anchor.fail { border-left-color: #534AB7; }
      .anchor .aconfig { font-size: 1.05rem; font-weight: 700; color: #1F1F1D;
                         margin-bottom: .45rem; }
      .anchor .abadge { display: inline-block; font-size: .92rem; font-weight: 800;
                        letter-spacing: .04em; padding: .2rem .65rem; border-radius: 6px;
                        margin-bottom: .55rem; }
      .anchor .abadge.pass { background: #E7F0EE; color: #0F6E56; }
      .anchor .abadge.fail { background: #EEEDF8; color: #534AB7; }
      .anchor .awhy { font-size: .95rem; color: #1F1F1D; line-height: 1.5; }
      .anchor .awhy .k { display: block; font-size: 12px; font-weight: 600;
                         color: #5F5E5A; text-transform: uppercase; letter-spacing: .02em;
                         margin-bottom: .2rem; }
      .anchor .reqset { display: flex; flex-direction: column; gap: .35rem;
                        margin-top: .1rem; }
      .anchor .reqrow { display: grid; grid-template-columns: 1.05rem minmax(0, 1fr);
                        column-gap: .4rem; align-items: start; font-size: .92rem;
                        line-height: 1.35; }
      .anchor .reqrow .mark { font-weight: 800; line-height: 1.35; }
      .anchor .reqrow .ids { font-weight: 700;
                             font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
      .anchor .reqrow .note { font-weight: 400; }
      .anchor .reqrow.ok { color: #0F6E56; }
      .anchor .reqrow.miss { color: #6B5308; }
      .anchor .reqrow .near { display: block; font-size: .82rem; font-weight: 400;
                              margin-top: .1rem; color: #6B5308; }
      .st-key-question { border: 1px solid #CFE0DB; border-left: 4px solid #0F6E56;
                        border-radius: 10px; background: #FFFFFF;
                        padding: 14px 16px 16px; }
      [data-testid="stVerticalBlock"].st-key-question { gap: 4px; }
      .st-key-question [data-testid="stWidgetLabel"] p { font-size: 28px;
                        font-weight: 700; color: #1F1F1D; }
      .st-key-question [role="radiogroup"] { gap: 8px; padding: 8px 0 0; }
      .qtext { font-size: 16px; font-weight: 500; color: #1F1F1D; line-height: 1.5;
               margin: 0 0 .1rem; }
      .explorer-nav-current {
        background: #E7F0EE; border: 1px solid #0F6E56; color: #0F6E56;
        font-weight: 700; font-size: .95rem; border-radius: 8px;
        padding: .4rem .65rem; margin: .12rem 0 .2rem;
      }
      [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        border: 1px solid #E8E8E4; border-radius: 8px;
        padding: .4rem .65rem !important; margin: .12rem 0 !important;
      }
      .st-key-explorer_nav [data-testid="stVerticalBlock"] { gap: 8px !important; }
      .st-key-method_pick {
        margin-top: .35rem; padding-top: 1rem; border-top: 1px solid #E8E8E4;
      }
      .st-key-method_pick [data-testid="stVerticalBlock"] { gap: 6px !important; }
      .st-key-method_pick [data-testid="stButton"] button {
        min-height: 2.05rem !important; padding-top: .22rem !important;
        padding-bottom: .22rem !important; font-size: .84rem !important;
      }
      .st-key-sidebar_footer { margin-top: .55rem; }
      .details-gap { height: 1.15rem; }
      [data-testid="stMain"] [data-testid="stExpander"] details {
        border: 1px solid #CFE0DB; border-left: 3px solid #0F6E56;
        border-radius: 8px; background: #F4F8F7;
      }
      [data-testid="stMain"] [data-testid="stExpander"] { margin-bottom: .4rem; }
      [data-testid="stMain"] [data-testid="stExpander"] summary { padding: .55rem .8rem; }
      [data-testid="stMain"] [data-testid="stExpander"] summary:hover { background: #E7F0EE; }
      [data-testid="stMain"] [data-testid="stExpander"] summary p {
        font-size: .95rem; font-weight: 700; color: #0F6E56;
      }
      [data-testid="stMain"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        color: #0F6E56;
      }
      .rankwrap { overflow-x: auto; margin: .2rem 0 .4rem; }
      .rankwrap table { width: 100%; min-width: 420px; border-collapse: collapse;
                        font-size: 14px; }
      .rankwrap th, .rankwrap td { padding: .38rem .55rem; text-align: left;
                        border-bottom: 1px solid #E8E8E4; vertical-align: top; }
      .rankwrap th { color: #5F5E5A; font-size: 12px; font-weight: 700; }
      .rankwrap .num { text-align: right; font-variant-numeric: tabular-nums;
                       font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
      .rankwrap tr.needed td { background: #F3F8F6; }
      .rankwrap tr.incomplete td { background: #FBF6EA; }
      .legend { display: flex; gap: 1.1rem; flex-wrap: wrap; align-items: center;
                font-size: .76rem; color: #5F5E5A; margin: .1rem 0 .6rem; }
      .legend span.key { display: inline-flex; align-items: center; gap: .35rem; }
      .swatch { width: .85rem; height: .85rem; border-radius: 3px; display: inline-block; }
      .swatch.hit { background: #E7F0EE; border: 1px solid #E8E8E4;
                    border-left: 3px solid #0F6E56; }
      @media (max-width: 640px) {
        h1 { font-size: 1.9rem !important; line-height: 1.2 !important; }
      }
      [data-testid="stMain"] code,
      [data-testid="stSidebarUserContent"] code { font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

IFRAME_CSS = """
  :root { --ink:#26262C; --gray:#5F5E5A; --line:#E8E8E4; --card:#FFFFFF;
          --wash:#F4F4F1; --teal:#0F6E56; --teal-fill:#E7F0EE; }
  * { box-sizing: border-box; }
  body { margin:0; background:#FFFFFF; color:var(--ink);
         font-family:'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
  .card { background:var(--card); border:1px solid var(--line);
          border-left:3px solid var(--line); border-radius:8px;
          margin-bottom:.6rem; overflow:hidden; }
  .card.hit { border-left-color:var(--teal); border-color:#D9E5E1; }
  .card.verdict-used { border:1px solid #9FBFB4; border-left:5px solid var(--teal);
                       background:#F3F8F6; }
  .card.verdict-used .head { background:#DCECE6; border-bottom-color:#B7D0C8; }
  .head { display:flex; gap:.55rem; flex-wrap:wrap; align-items:baseline;
          padding:.34rem .58rem; background:var(--wash);
          border-bottom:1px solid var(--line);
          font:600 .72rem/1.7 ui-monospace, SFMono-Regular, Menlo, monospace; }
  .card.hit .head { background:var(--teal-fill); border-bottom-color:#D9E5E1; }
  .primary { font-size:.84rem; font-weight:700; color:var(--ink); }
  .muted { color:#9B9A96; font-weight:400; font-size:.68rem; }
  .body { padding:.6rem; margin:0; white-space:pre-wrap; word-break:break-word;
          font:.79rem/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }
  .verdict-tag { display:inline-block; margin:.25rem .58rem .4rem;
                 font:600 .7rem/1.4 'Segoe UI', system-ui, sans-serif;
                 padding:.12rem .5rem; border-radius:4px; }
  .verdict-tag.used { color:#FFFFFF; background:var(--teal); }
  .verdict-tag.incomplete { color:#6B5308; background:#F3E8C8; font-weight:700;
                            border:1px solid #C4A35A; }
  .verdict-tag.alt { color:#5F5E5A; background:#EDEDEA; font-weight:500;
                     border:1px solid #E0DFDA; }
  .verdict-tag.unused { color:#5F5E5A; background:#EDEDEA; font-weight:500;
                        border:1px solid #E0DFDA; }
  .card.verdict-unused { border:1px solid #E0DFDA; border-left:3px solid #C8C7C1;
                         background:#FFFFFF; }
  .card.verdict-unused .head { background:#F4F4F1; border-bottom-color:#E8E8E4; }
  .card.verdict-unused .primary { color:#5F5E5A; }
  .card.verdict-incomplete { border:1px solid #E6D5A8; border-left:5px solid #B8870F;
                             background:#FBF6EA; }
  .card.verdict-incomplete .head { background:#F3E8C8; border-bottom-color:#E6D5A8; }
  mark.evidence { background:rgba(15,110,86,.28); color:inherit; border-radius:2px;
                  box-decoration-break:clone; -webkit-box-decoration-break:clone; }
  mark.incomplete { background:rgba(184,135,15,.28); color:inherit; border-radius:2px;
                    box-decoration-break:clone; -webkit-box-decoration-break:clone; }
  .gap { border:1px dashed var(--line); border-radius:8px; margin-bottom:.6rem;
         padding:.3rem .58rem; color:var(--gray); background:#FFFFFF;
         font:.72rem/1.6 ui-monospace, SFMono-Regular, Menlo, monospace; }
"""


def fail(message: str) -> None:
    st.error(message)
    st.stop()


def rank_of(ranking: list[dict], chunk_id: str) -> int:
    for row in ranking:
        if row["chunk_id"] == chunk_id:
            return int(row["rank"])
    fail(f"chunk {chunk_id} is missing from a ranking")


def validate_artifact(data: dict) -> None:
    questions = data.get("questions") or []
    methods = data.get("methods") or []
    chunks = data.get("chunks") or []
    results = data.get("results") or []
    if len(questions) != EXPECTED_QUESTIONS:
        fail(f"Expected {EXPECTED_QUESTIONS} questions, found {len(questions)}.")
    if len(methods) != EXPECTED_METHODS:
        fail(f"Expected {EXPECTED_METHODS} methods, found {len(methods)}.")
    if len(chunks) != EXPECTED_CHUNKS:
        fail(f"Expected {EXPECTED_CHUNKS} chunks, found {len(chunks)}.")
    if len(results) != EXPECTED_RESULTS:
        fail(f"Expected {EXPECTED_RESULTS} results, found {len(results)}.")
    ranking_rows = sum(len(entry.get("ranking") or []) for entry in results)
    if ranking_rows != EXPECTED_RANKING_ROWS:
        fail(f"Expected {EXPECTED_RANKING_ROWS} ranking rows, found {ranking_rows}.")

    by_key = {(entry["question_id"], entry["method"]): entry for entry in results}
    checks = (
        ("Q3", "dense", "FAIL", (("C-7", 1), ("C-3", 5), ("C-8", 6))),
        ("Q3", "bm25", "PASS", (("C-3", 1), ("C-8", 2), ("C-7", 3))),
        ("Q3", "rrf", "PASS", (("C-7", 1), ("C-3", 2), ("C-8", 3))),
    )
    for question_id, method, verdict, ranks in checks:
        entry = by_key.get((question_id, method))
        if entry is None:
            fail(f"Missing {question_id} {method} result.")
        if entry.get("verdict") != verdict:
            fail(f"{question_id} {method} verdict is {entry.get('verdict')!r}, expected {verdict}.")
        for chunk_id, expected in ranks:
            actual = rank_of(entry["ranking"], chunk_id)
            if actual != expected:
                fail(f"{question_id} {method} {chunk_id} is rank {actual}, expected {expected}.")


@st.cache_data(show_spinner=False)
def load_artifact() -> dict:
    if not ARTIFACT_PATH.is_file():
        raise FileNotFoundError(f"Missing frozen artifact: {ARTIFACT_PATH}")
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


try:
    artifact = load_artifact()
except (OSError, json.JSONDecodeError) as exc:
    fail(f"Could not load frozen artifact: {exc}")

validate_artifact(artifact)

questions = artifact["questions"]
methods_by_id = {item["id"]: item for item in artifact["methods"]}
chunks_by_id = {item["id"]: item for item in artifact["chunks"]}
chunks_in_order = artifact["chunks"]
results_by_key = {
    (entry["question_id"], entry["method"]): entry for entry in artifact["results"]
}
experiment = artifact["experiment"]
commits = experiment["commits"]


def set_method(method_id: str) -> None:
    st.session_state.retrieval_method = method_id


st.session_state.setdefault("retrieval_method", "dense")
st.session_state.setdefault("retrieval_question_index", 0)
st.session_state.setdefault("retrieval_source_view", RETRIEVED_ONLY)

if st.session_state.retrieval_method not in methods_by_id:
    fail(f"Unknown retrieval_method {st.session_state.retrieval_method!r}.")


def evidence_role(chunk_id: str, required: list[list[str]]) -> str | None:
    for group in required:
        if chunk_id in group:
            return "required" if len(group) == 1 else "alternative"
    return None


def required_group_status(
    required: list[list[str]], ranking: list[dict]
) -> list[dict]:
    """AND-of-OR groups from frozen required. A group is satisfied if any member is in top-3."""
    ranks = {row["chunk_id"]: int(row["rank"]) for row in ranking}
    top = {chunk_id for chunk_id, rank in ranks.items() if rank <= HEADLINE_K}
    rows: list[dict] = []
    for group in required:
        in_top = [chunk_id for chunk_id in group if chunk_id in top]
        ordered = sorted(group, key=lambda chunk_id: ranks[chunk_id])
        present = sorted(in_top, key=lambda chunk_id: ranks[chunk_id])
        rows.append(
            {
                "group": group,
                "satisfied": bool(in_top),
                "present": [(chunk_id, ranks[chunk_id]) for chunk_id in present],
                "nearest": [(chunk_id, ranks[chunk_id]) for chunk_id in ordered],
            }
        )
    return rows


def requirement_status_html(required: list[list[str]], ranking: list[dict]) -> str:
    rows_html: list[str] = []
    for row in required_group_status(required, ranking):
        ids = " or ".join(html.escape(chunk_id) for chunk_id in row["group"])
        if row["satisfied"]:
            if len(row["group"]) > 1:
                detail = " · ".join(
                    f"{html.escape(chunk_id)} rank {rank}"
                    for chunk_id, rank in row["present"]
                )
                note = f"— satisfied: {detail}"
            else:
                note = "— present in top-3"
            rows_html.append(
                '<div class="reqrow ok">'
                '<span class="mark">✓</span>'
                f'<span><span class="ids">{ids}</span>'
                f' <span class="note">{note}</span></span>'
                "</div>"
            )
            continue
        nearest = " · ".join(
            f"{html.escape(chunk_id)} rank {rank}" for chunk_id, rank in row["nearest"]
        )
        rows_html.append(
            '<div class="reqrow miss">'
            '<span class="mark">✕</span>'
            f'<span><span class="ids">{ids}</span>'
            ' <span class="note">— below top-3</span>'
            f'<span class="near">Nearest: {nearest}</span></span>'
            "</div>"
        )
    return (
        '<div class="awhy"><span class="k">Required evidence</span>'
        f'<div class="reqset">{"".join(rows_html)}</div></div>'
    )


def render_cards(cards: list[str], height: int) -> None:
    document = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{IFRAME_CSS}</style></head>"
        f"<body>{''.join(cards)}</body></html>"
    )
    st.iframe(document, height=height)


def estimate_height(texts: list[str], gaps: int = 0) -> int:
    total = 0
    for text in texts:
        lines = sum(max(1, math.ceil(len(line) / CHARS_PER_LINE)) for line in text.split("\n"))
        total += CARD_CHROME + lines * LINE_HEIGHT
    total += gaps * 40
    return max(260, min(PANEL_HEIGHT, total + 16))


def evidence_spans_for(chunk_id: str) -> tuple[str, ...]:
    """Reviewed configuration-C spans for this question. Never inferred."""
    table = getattr(config, "PUBLISHED_EVIDENCE_SPANS", {})
    try:
        question_index = int(question["id"][1:]) - 1
        chunk_index = int(chunk_id.split("-", 1)[1])
    except (KeyError, IndexError, ValueError):
        return ()
    annotated = table.get("C", {}).get(question_index, ())
    return tuple(span for index, span in annotated if index == chunk_index)


def body_html(text: str, evidence_spans: tuple[str, ...] = (), *, incomplete: bool = False) -> str:
    marks: list[tuple[int, int]] = []
    for span in evidence_spans:
        start = text.find(span)
        if start >= 0:
            marks.append((start, start + len(span)))
    if not marks:
        return f'<div class="body">{html.escape(text)}</div>'
    mark_cls = "incomplete" if incomplete else "evidence"
    points = sorted({0, len(text), *(start for start, _ in marks), *(end for _, end in marks)})
    parts: list[str] = []
    for left, right in zip(points, points[1:]):
        if left == right:
            continue
        segment = html.escape(text[left:right])
        if any(start <= left and right <= end for start, end in marks):
            segment = f'<mark class="{mark_cls}">{segment}</mark>'
        parts.append(segment)
    return f'<div class="body">{"".join(parts)}</div>'


def card_html(
    chunk: dict,
    rank: int | None,
    score: float | None,
    score_label: str,
    role: str | None,
    *,
    set_complete: bool,
) -> str:
    chunk_id = chunk["id"]
    heading = chunk.get("heading") or ""
    start, end = chunk["start"], chunk["end"]
    head = []
    if rank is not None and score is not None:
        head.append(
            f'<span class="primary">Rank {rank} · {html.escape(chunk_id)} · '
            f"{html.escape(score_label)} {score:.4f}</span>"
        )
    else:
        if rank is not None:
            head.append(f'<span class="primary">Rank {rank} · {html.escape(chunk_id)}</span>')
        else:
            head.append(f'<span class="primary">{html.escape(chunk_id)}</span>')
    head.append(f'<span class="muted">[{start}:{end}]</span>')
    head.append(f'<span class="muted">{end - start} chars</span>')
    if heading:
        head.append(f'<span class="muted">{html.escape(heading)}</span>')

    spans = evidence_spans_for(chunk_id) if role in {"required", "alternative"} else ()
    present = tuple(span for span in spans if span in chunk["text"])
    in_top = rank is not None and rank <= HEADLINE_K
    incomplete = role in {"required", "alternative"} and not set_complete

    tag = ""
    css = "card hit" if rank is not None else "card"
    if role == "required" and incomplete:
        css = "card verdict-incomplete"
        tag = '<div class="verdict-tag incomplete">Required evidence</div>'
    elif role == "required":
        css = "card verdict-used"
        tag = '<div class="verdict-tag used">Required evidence</div>'
    elif role == "alternative" and incomplete:
        css = "card verdict-incomplete"
        tag = '<div class="verdict-tag incomplete">Alternative qualifying evidence</div>'
    elif role == "alternative":
        css = "card verdict-used"
        tag = '<div class="verdict-tag used">Alternative qualifying evidence</div>'
    elif in_top:
        css = "card verdict-unused"
        tag = '<div class="verdict-tag unused">Retrieved, not used for verdict</div>'

    body = body_html(chunk["text"], present, incomplete=incomplete)
    return f'<div class="{css}"><div class="head">{"".join(head)}</div>{tag}{body}</div>'


def gap_html(skipped: list[dict]) -> str:
    first, last = skipped[0]["id"], skipped[-1]["id"]
    span = first if first == last else f"{first} – {last}"
    return f'<div class="gap">{html.escape(span)} not retrieved</div>'


# --- sidebar -------------------------------------------------------------

with st.sidebar:
    with st.container(key="explorer_nav"):
        st.page_link("app.py", label="Chunking explorer")
        st.markdown(
            '<div class="explorer-nav-current">Retrieval explorer</div>',
            unsafe_allow_html=True,
        )
    with st.container(key="method_pick"):
        st.markdown("**Retrieval method**")
        st.caption("Chunking stays the same. Switch how chunks are ranked.")
        selected_method = st.session_state.retrieval_method
        for method_id, label in METHOD_BUTTONS.items():
            st.button(
                label,
                use_container_width=True,
                type="primary" if method_id == selected_method else "secondary",
                on_click=set_method,
                args=(method_id,),
            )
        st.caption(METHOD_CAPTIONS[selected_method])

    with st.container(key="sidebar_footer"):
        st.markdown(
            '<div class="sidebar-meta" style="font-size:13.5px;line-height:1.55;'
            "color:#3A3A37;font-weight:400;margin:.7rem 0 0;padding:.75rem .8rem;"
            'border:1px solid #D8D8D2;border-radius:8px;background:#FFFFFF;">'
            '<div style="font-size:16px;font-weight:700;color:#1F1F1D;'
            'margin-bottom:.5rem;">What stays fixed</div>'
            '<div style="margin:.22rem 0;"><span style="font-weight:700;color:#1F1F1D;">'
            "Chunking:</span> section-aware, 13 chunks</div>"
            '<div style="margin:.22rem 0;"><span style="font-weight:700;color:#1F1F1D;">'
            "Questions:</span> 5</div>"
            '<div style="margin:.22rem 0;"><span style="font-weight:700;color:#1F1F1D;">'
            "Pass if:</span> the required evidence set is present in the top 3</div>"
            '<div style="color:#4A4A46;margin-top:.55rem;line-height:1.45;font-size:12.5px;">'
            "Held fixed so Dense, BM25, and RRF can be compared.</div></div>",
            unsafe_allow_html=True,
        )


# --- page identity -------------------------------------------------------

st.title("Retrieval explorer")
st.caption(
    "Chunking stays at section-aware (13 chunks). Only the retrieval method changes. "
    "Treat the results as an illustration, not a benchmark."
)

method_id = st.session_state.retrieval_method
method = methods_by_id[method_id]
score_label = SCORE_LABELS[method_id]

with st.container(key="question"):
    st.radio(
        "Question",
        options=range(len(questions)),
        format_func=lambda index: questions[index]["id"],
        key="retrieval_question_index",
        horizontal=True,
    )
    question = questions[st.session_state.retrieval_question_index]
    st.markdown(
        f'<div class="qtext">{html.escape(question["text"])}</div>',
        unsafe_allow_html=True,
    )

result = results_by_key[(question["id"], method_id)]
ranking = result["ranking"]
verdict = result["verdict"]
required = question["required"]
rank_lookup = {row["chunk_id"]: row for row in ranking}
top3 = [row for row in ranking if int(row["rank"]) <= HEADLINE_K]
top3.sort(key=lambda row: int(row["rank"]))

badge = "PASS" if verdict == "PASS" else "FAIL"
badge_cls = "pass" if verdict == "PASS" else "fail"
border_cls = "" if verdict == "PASS" else " fail"
why_html = requirement_status_html(required, ranking)

st.markdown(
    f'<div class="anchor{border_cls}">'
    f'<div class="aconfig">{html.escape(method["label"])}</div>'
    f'<div class="abadge {badge_cls}">Result: {badge}</div>'
    f"{why_html}</div>",
    unsafe_allow_html=True,
)

st.subheader("Top 3 chunks")
badges = " · ".join(f"`{row['chunk_id']}`" for row in top3)
st.markdown(badges)

top_cards = []
top_texts = []
for row in top3:
    chunk = chunks_by_id[row["chunk_id"]]
    role = evidence_role(row["chunk_id"], required)
    top_cards.append(
        card_html(
            chunk,
            int(row["rank"]),
            float(row["score"]),
            score_label,
            role,
            set_complete=verdict == "PASS",
        )
    )
    top_texts.append(chunk["text"])
render_cards(top_cards, estimate_height(top_texts))
if verdict != "PASS" and any(
    evidence_role(row["chunk_id"], required) in {"required", "alternative"} for row in top3
):
    st.caption(
        "Amber marks required evidence that is present, but the full required set is not in the top 3."
    )

rest = [row for row in ranking if int(row["rank"]) > HEADLINE_K]
rest.sort(key=lambda row: int(row["rank"]))
st.markdown('<div class="details-gap"></div>', unsafe_allow_html=True)
with st.expander("Ranks 4–13"):
    rows_html = []
    for row in rest:
        chunk = chunks_by_id[row["chunk_id"]]
        role = evidence_role(row["chunk_id"], required)
        status = ""
        css = ""
        if role == "required":
            status = "Required evidence"
            css = " class='incomplete'" if verdict != "PASS" else " class='needed'"
        elif role == "alternative":
            status = "Alternative qualifying evidence"
            css = " class='incomplete'" if verdict != "PASS" else " class='needed'"
        heading = html.escape(chunk.get("heading") or "")
        rows_html.append(
            f"<tr{css}><td class='num'>{int(row['rank'])}</td>"
            f"<td>{html.escape(row['chunk_id'])}</td>"
            f"<td>{heading}</td>"
            f"<td class='num'>{float(row['score']):.4f}</td>"
            f"<td>{html.escape(status)}</td></tr>"
        )
    st.markdown(
        '<div class="rankwrap"><table><thead><tr>'
        "<th class='num'>Rank</th><th>Chunk</th><th>Heading</th>"
        f"<th class='num'>{html.escape(score_label)}</th><th>Evidence</th>"
        "</tr></thead><tbody>"
        + "".join(rows_html)
        + "</tbody></table></div>",
        unsafe_allow_html=True,
    )

with st.expander(f"Where required evidence ranked · {question['id']}"):
    seen: list[str] = []
    for group in required:
        for chunk_id in group:
            if chunk_id not in seen:
                seen.append(chunk_id)
    header = (
        '<div class="rankwrap"><table><thead><tr>'
        "<th>Chunk</th><th class='num'>Dense</th>"
        "<th class='num'>BM25</th><th class='num'>RRF</th>"
        "</tr></thead><tbody>"
    )
    body = []
    for chunk_id in seen:
        dense_rank = rank_of(results_by_key[(question["id"], "dense")]["ranking"], chunk_id)
        bm25_rank = rank_of(results_by_key[(question["id"], "bm25")]["ranking"], chunk_id)
        rrf_rank = rank_of(results_by_key[(question["id"], "rrf")]["ranking"], chunk_id)
        body.append(
            f"<tr class='needed'><td>{html.escape(chunk_id)}</td>"
            f"<td class='num'>{dense_rank}</td>"
            f"<td class='num'>{bm25_rank}</td>"
            f"<td class='num'>{rrf_rank}</td></tr>"
        )
    st.markdown(header + "".join(body) + "</tbody></table></div>", unsafe_allow_html=True)
    st.caption("Rank 1 is first. A pass needs required evidence at rank 3 or better.")

with st.expander("What counts as a pass"):
    st.markdown(question["rubric"])
    st.caption("This is the recorded pass/fail rule for this question. It is not inferred from the ranking.")

with st.expander("Inspect source and chunks"):
    view = st.radio(
        "Source view",
        options=[RETRIEVED_ONLY, ALL_CHUNKS],
        key="retrieval_source_view",
        horizontal=True,
    )
    st.markdown(
        '<div class="legend">'
        '<span class="key"><span class="swatch hit"></span>retrieved for this question</span>'
        "</div>",
        unsafe_allow_html=True,
    )
    retrieved_ids = {row["chunk_id"] for row in top3}
    cards: list[str] = []
    texts: list[str] = []
    gap_count = 0
    if view == ALL_CHUNKS:
        for chunk in chunks_in_order:
            row = rank_lookup[chunk["id"]]
            rank = int(row["rank"])
            score = float(row["score"]) if rank <= HEADLINE_K else None
            role = evidence_role(chunk["id"], required) if rank <= HEADLINE_K else None
            cards.append(
                card_html(
                    chunk,
                    rank,
                    score,
                    score_label,
                    role,
                    set_complete=verdict == "PASS",
                )
            )
            texts.append(chunk["text"])
    else:
        pending: list[dict] = []
        for chunk in chunks_in_order:
            if chunk["id"] in retrieved_ids:
                if pending:
                    cards.append(gap_html(pending))
                    gap_count += 1
                    pending = []
                row = rank_lookup[chunk["id"]]
                cards.append(
                    card_html(
                        chunk,
                        int(row["rank"]),
                        float(row["score"]),
                        score_label,
                        evidence_role(chunk["id"], required),
                        set_complete=verdict == "PASS",
                    )
                )
                texts.append(chunk["text"])
            else:
                pending.append(chunk)
        if pending:
            cards.append(gap_html(pending))
            gap_count += 1
        st.caption(
            f"Showing the {HEADLINE_K} retrieved chunks in document order. "
            f"The index contains {EXPECTED_CHUNKS} chunks in total."
        )
    render_cards(cards, estimate_height(texts, gap_count))

with st.expander("How each method works"):
    dense = methods_by_id["dense"]
    bm25 = methods_by_id["bm25"]
    rrf = methods_by_id["rrf"]
    st.markdown(
        f"""
Dense ranks by embedding similarity. BM25 ranks by keyword overlap. RRF combines
those two rankings; it does not search the document on its own.

**Dense**

- model: `{dense["model"]}`
- similarity: {dense["similarity"]}

**BM25**

- implementation: `{bm25["implementation"]}`
- k1 = {bm25["k1"]}, b = {bm25["b"]}, epsilon = {bm25["epsilon"]}
- no stopword list

**RRF**

- Dense + BM25
- k = {rrf["k"]}
- fusion from full 13-chunk rankings

**Evidence commits**

- preregistration `{commits["preregistration"]}`
- implementation `{commits["implementation"]}`
- results `{commits["results"]}`

Repository: [{REPO_URL}]({REPO_URL})
        """
    )
    st.caption("These rankings are from the recorded run. This page does not rerun retrieval.")
