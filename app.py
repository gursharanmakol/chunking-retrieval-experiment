"""Companion UI for the article "Why Fixed-Size Chunking Breaks Retrieval".

A reader-facing explorer, not an experiment. It re-runs the same retrieval
pipeline the article used while letting the reader vary chunk size, overlap and
top-k, so the effect of a boundary change is visible on one screen.

Retrieval evidence only: no answer generation, no reranking, no keyword search,
no query rewriting. Sufficiency is never judged automatically, and every
explanation shown for a published configuration is hand-written in config.py.

Chunk text is rendered inside an iframe rather than through st.markdown, because
Streamlit's markdown parser would interpret the document's own `##` headings and
`**bold**` markers and stop the text from being shown literally.

Run:  streamlit run app.py
"""

import html
import math

import streamlit as st

import config
import explorer_core as core

SITE_URL = "https://aiinpracticehub.com/"

# The site's nav mark, copied from its BaseLayout.astro: three overlapping rounded
# blocks in the teal, blue and purple that identify the RAG, MCP and Agents series.
# Held as inline SVG rather than a committed image because the site has no logo
# file either, so there is no binary asset to keep in sync. Streamlit accepts an
# SVG string wherever it accepts an image. The site declares these colours as CSS
# variables, resolved here to their published values so the mark stands alone.
_BRAND_RECTS = (
    '<rect x="12" y="50" width="40" height="32" rx="9" fill="#E7F0EE" stroke="#0F6E56" stroke-width="4.5"/>'
    '<rect x="48" y="50" width="40" height="32" rx="9" fill="#E8EFF6" stroke="#185FA5" stroke-width="4.5"/>'
    '<rect x="30" y="16" width="40" height="32" rx="9" fill="#EEEDF8" stroke="#534AB7" stroke-width="4.5"/>'
)

BRAND_MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
    f"{_BRAND_RECTS}</svg>"
)

# The nav lockup: the mark scaled to the 34px the site renders it at, then the
# wordmark in Segoe UI 800 with "Hub" in purple. Each text run carries a textLength
# measured from the real Segoe UI Bold at 16.5px with the site's -0.3px tracking, so
# a platform that substitutes another font still fills the same box instead of
# clipping or drifting away from the mark.
#
# The x offsets reproduce the site's flex spacing. Its .brand rule sets gap:11px,
# and the &nbsp; between the two words is a non-breaking space, so flex treats it
# as an item in its own right and puts a gap on either side of it. The wordmark
# therefore sits 11px after the mark, and "Hub" a further 11 + 4.25 + 11 on.
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
    page_title="Chunking and retrieval explorer",
    page_icon=BRAND_MARK,
    layout="wide",
    # "auto" rather than "expanded": expanded keeps the sidebar pinned open at
    # phone width, where it takes most of a 380px viewport and squeezes the panels
    # into a sliver. "auto" still opens it on a wide screen.
    initial_sidebar_state="auto",
)

# Full lockup while the sidebar is open, falling back to the mark alone when it is
# collapsed, which is how the site treats the wordmark on narrow screens.
st.logo(BRAND_LOCKUP, icon_image=BRAND_MARK, size="large", link=SITE_URL)

PANEL_HEIGHT = 640
RETRIEVED_ONLY = "Retrieved chunks only"
ALL_CHUNKS = "All chunks"

st.markdown(
    """
    <style>
      /* Dot grid stays as page atmosphere only. Content sits on solid white so
         reading surfaces (question, source, retrieval, method) never show dots
         through the text. */
      .stApp { background-color: #FCFCFB;
               background-image: radial-gradient(#E4E4E8 1.4px, transparent 1.4px);
               background-size: 32px 32px; }
      .block-container { max-width: 1600px; padding-top: 1.5rem; padding-bottom: 2rem;
                         background: #FFFFFF; border-radius: 12px;
                         box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); }
      [data-testid="stMain"] { background: transparent; }
      /* Chunk cards live in iframes; paint the frame itself white so no page
         dots leak around the document body. */
      [data-testid="stMain"] iframe { background: #FFFFFF; }
      /* Narrower sidebar so the evidence column gets more horizontal room. */
      [data-testid="stSidebar"] { min-width: 260px; max-width: 280px; }
      section[data-testid="stSidebar"] { width: 280px !important; }
      .selection { display: flex; gap: .4rem; flex-wrap: wrap; align-items: center;
                   margin: .2rem 0 .6rem; }
      /* Selected result: the first thing a reader should absorb. */
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
      .anchor .abadge.inspect { background: #F4F4F1; color: #5F5E5A; font-weight: 700;
                                letter-spacing: 0; }
      .anchor .awhy { font-size: .95rem; color: #1F1F1D; line-height: 1.5; }
      .anchor .awhy .k { display: block; font-size: 12px; font-weight: 600;
                         color: #5F5E5A; text-transform: uppercase; letter-spacing: .02em;
                         margin-bottom: .2rem; }
      .configline { font: .9rem/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
                    color: #5F5E5A; margin: .15rem 0 .85rem; }
      .abcrow { display: flex; gap: .6rem; flex-wrap: wrap; margin: .2rem 0 .9rem; }
      .abcrow .abc { border: 1px solid #E8E8E4; border-radius: 8px; padding: .35rem .7rem;
                     background: #FFFFFF; font-size: .9rem; }
      .abcrow .abc.now { border-color: #0F6E56; background: #F4F8F7; }
      .abcrow .ok { color: #0F6E56; font-weight: 700; }
      .abcrow .no { color: #534AB7; font-weight: 700; }
      /* The settings row is the reader's answer to "what am I looking at", and the
         panels below it are long, so it stays put while they scroll through them. */
      .sticky-selection { position: sticky; top: 0; z-index: 5; background: #FFFFFF;
                          border-bottom: 1px solid #E8E8E4; padding: .45rem 0 .1rem;
                          margin-bottom: .35rem; }
      .sticky-selection .selection { margin: 0; }
      .sticky-selection .lab { font-size: 12px; font-weight: 600; color: #5F5E5A;
                               letter-spacing: .02em; text-transform: uppercase;
                               margin-bottom: .25rem; }
      /* One-line headline for the verdict grid. The grid itself lives behind a tab,
         so the totals stay visible to a reader who never opens it. */
      .vsum { display: flex; gap: .45rem; flex-wrap: wrap; align-items: center;
              font-size: .78rem; margin: .1rem 0 .5rem; }
      .vsum .k { color: #5F5E5A; }
      .vsum .t { border: 1px solid #E8E8E4; border-radius: 6px; padding: .12rem .5rem;
                 background: #FFFFFF; font: .76rem ui-monospace, SFMono-Regular, Menlo,
                 monospace; font-variant-numeric: tabular-nums; }
      /* Tabs. Streamlit's default marks the selected tab with two low-contrast
         indicators, a colour change and a thin rule. NN/g's guidance is to make the
         selection unmistakable, so the active tab also takes the teal fill, a heavier
         weight and a thicker underline, and the resting tabs get a hover state. */
      [role="tablist"] { gap: .25rem; border-bottom: 1px solid #E8E8E4; }
      [data-testid="stTab"] { padding: .45rem 1rem; border-radius: 8px 8px 0 0;
                              background: transparent; color: #5F5E5A; }
      [data-testid="stTab"] p { font-size: .92rem; font-weight: 600; color: inherit; }
      [data-testid="stTab"]:hover { background: #F4F4F1; color: #26262C; }
      [data-testid="stTab"][aria-selected="true"] { background: #E7F0EE; color: #0F6E56; }
      [data-testid="stTab"][aria-selected="true"] p { font-weight: 800; }
      [data-testid="stTab"] .react-aria-SelectionIndicator { background: #0F6E56;
                              height: 3px; border-radius: 2px 2px 0 0; }
      /* Expanders. The stock header is a thin hairline on the page background and
         barely reads as clickable. Give it a filled, bordered bar with a teal
         accent edge, bolder teal label and a hover state so it registers as an
         actionable control. Scoped to the main pane. */
      [data-testid="stMain"] [data-testid="stExpander"] details {
                              border: 1px solid #CFE0DB; border-left: 3px solid #0F6E56;
                              border-radius: 8px; background: #F4F8F7; }
      [data-testid="stMain"] [data-testid="stExpander"] summary { padding: .55rem .8rem; }
      [data-testid="stMain"] [data-testid="stExpander"] summary:hover { background: #E7F0EE; }
      [data-testid="stMain"] [data-testid="stExpander"] summary p {
                              font-size: .95rem; font-weight: 700; color: #0F6E56; }
      [data-testid="stMain"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
                              color: #0F6E56; }
      /* The full policy renders as raw Markdown inside the expander, so its own
         H1/H2/H3 arrive at document scale and dwarf the app. Scale them down to
         reader size. Scoped to expander body headings, so the summary label and the
         page title are untouched. */
      [data-testid="stMain"] [data-testid="stExpander"] h1 { font-size: 1.5rem; }
      [data-testid="stMain"] [data-testid="stExpander"] h2 { font-size: 1.2rem; }
      [data-testid="stMain"] [data-testid="stExpander"] h3 { font-size: 1.02rem; }
      /* Radio options. The stock selected state is a 16px teal ring with a white
         centre, and the unselected ring is #F4F4F1, the sidebar's own background:
         one reads as hollow, the other as absent. The whole option becomes a chip
         instead, so the selection carries a fill, a colour and a weight the way the
         tabs do, and does not depend on a 16px circle being legible.

         A resting option is outlined rather than bare for the same reason: the stock
         empty circle is a #E8E8E4 ring around a #F4F4F1 centre, which is the panel
         colour behind it, so an unselected option did not read as a control at all.
         The outline is also the one handle here that survives Streamlit's hashed
         class names, since only the test id and data-selected are stable. */
      [data-testid="stRadioOption"] { border: 1px solid #E8E8E4; border-radius: 6px;
                              background: #FFFFFF;
                              padding: .08rem .5rem .08rem .3rem; }
      [data-testid="stRadioOption"] p { color: #5F5E5A; }
      [data-testid="stRadioOption"]:hover { background: #F4F4F1; border-color: #B4B4AE; }
      [data-testid="stRadioOption"][data-selected="true"] { background: #E7F0EE;
                              border-color: #0F6E56; }
      [data-testid="stRadioOption"][data-selected="true"] p { color: #0F6E56;
                              font-weight: 700; }
      .selection .chip { display: inline-flex; align-items: baseline; gap: .4rem;
                         background: #FFFFFF; border: 1px solid #E8E8E4; border-radius: 6px;
                         padding: .2rem .52rem; font-size: .76rem; }
      .selection .ck { color: #5F5E5A; }
      .selection .cv { font: .78rem/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
                       font-variant-numeric: tabular-nums; }
      .selection .pub { background: #E7F0EE; border-color: #0F6E56; color: #0F6E56;
                        font-weight: 600; }
      .selection .custom { color: #5F5E5A; font-weight: 600; }
      /* 5x3 verdict summary. Pass and Fail carry the same teal and purple the
         retrieval panel already uses, so the shape of the run reads at a glance. */
      .verdicts { background: #FFFFFF; border: 1px solid #E8E8E4; border-radius: 8px;
                  padding: .55rem .7rem; max-width: 660px; margin: .1rem 0 .4rem; }
      .verdicts .vr { display: flex; gap: .3rem; align-items: stretch;
                      margin-bottom: .25rem; }
      .verdicts .vr:last-child { margin-bottom: 0; }
      .verdicts .q { flex: 0 0 3.6rem; align-self: center; color: #5F5E5A;
                     font: .76rem ui-monospace, SFMono-Regular, Menlo, monospace; }
      .verdicts .vr.here .q { color: #26262C; font-weight: 700; }
      .verdicts .h, .verdicts .cell { flex: 1 1 0; text-align: center; }
      .verdicts .h { font-size: .7rem; font-weight: 600; color: #5F5E5A; }
      .verdicts .cell { border-radius: 5px; padding: .16rem 0 .2rem;
                        font-size: .74rem; font-weight: 600; }
      .verdicts .cell .why { display: block; font-size: .62rem; font-weight: 400;
                             margin-top: .05rem; }
      .verdicts .pass { background: #E7F0EE; color: #0F6E56; }
      .verdicts .fail { background: #EEEDF8; color: #534AB7; }
      .verdicts .tot { border-top: 1px solid #E8E8E4; padding-top: .35rem; }
      .verdicts .tot .cell { background: transparent; color: #26262C;
                             font: .8rem ui-monospace, SFMono-Regular, Menlo, monospace;
                             font-variant-numeric: tabular-nums; }
      /* Verdict and the winning cosine score sit on one line, so a high score
         attached to insufficient evidence cannot be missed. */
      .vline { display: flex; gap: .4rem; flex-wrap: wrap; align-items: center;
               margin: .1rem 0 .45rem; }
      .vline .vchip { display: inline-flex; align-items: baseline; gap: .4rem;
                      border: 1px solid #E8E8E4; border-radius: 6px;
                      padding: .2rem .52rem; font-size: .76rem; font-weight: 600; }
      .vline .pass { background: #E7F0EE; border-color: #0F6E56; color: #0F6E56; }
      .vline .fail { background: #EEEDF8; border-color: #534AB7; color: #534AB7; }
      .vline .score { background: #FFFFFF; color: #26262C; font-weight: 400;
                      font: .76rem ui-monospace, SFMono-Regular, Menlo, monospace; }
      .modes { display: flex; gap: .4rem; flex-wrap: wrap; align-items: center;
               margin: 0 0 .5rem; font-size: .74rem; }
      .modes .k { color: #5F5E5A; }
      .modes .mode { border: 1px dashed #534AB7; color: #534AB7; border-radius: 5px;
                     padding: .08rem .42rem; }
      /* Guard against the one wrong lesson the strip could teach: an all-Fail Q3
         row reading as "chunking is hopeless". */
      .q3note { max-width: 660px; margin: 0 0 .35rem; padding: .4rem .6rem;
                background: #FFFFFF; border: 1px solid #E8E8E4;
                border-left: 3px solid #534AB7; border-radius: 6px;
                font-size: .78rem; line-height: 1.5; color: #26262C; }
      /* Phone width: the verdict grid is the element most at risk, so the label
         column narrows and the type steps down rather than the cells overflowing. */
      @media (max-width: 720px) {
        .verdicts { padding: .45rem .5rem; }
        .verdicts .vr { gap: .2rem; }
        .verdicts .q { flex: 0 0 2rem; font-size: .7rem; }
        .verdicts .h { font-size: .58rem; line-height: 1.25; word-break: break-word; }
        .verdicts .cell { font-size: .68rem; padding: .14rem .1rem .18rem; }
        .verdicts .cell .why { font-size: .55rem; line-height: 1.2; }
        .verdicts .tot .cell { font-size: .72rem; }
        .q3note { font-size: .74rem; }
        .selection .chip { font-size: .7rem; }
      }
      /* Phone: st.columns stacks in DOM order, which would put the whole source
         panel between the reader and the answer to the question they picked.
         Reversing the stack puts the retrieval results first. Desktop is untouched,
         since the two panels only sit side by side above this breakpoint. */
      @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"] { flex-direction: column-reverse; }
        /* The chip row wraps to three lines on a phone. Pinned, that would hold a
           fifth of the viewport for the whole scroll, so it stays inline here and
           is sticky only where it costs a single line. */
        .sticky-selection { position: static; border-bottom: none; padding-top: 0; }
        h1 { font-size: 1.9rem !important; line-height: 1.2 !important; }
        /* The bar fits 380px with no slack, so the new padding comes back off here
           rather than pushing the labels into a horizontal scroll. */
        [data-testid="stTab"] { padding: .4rem .6rem; }
        [data-testid="stTab"] p { font-size: .86rem; }
      }
      .legend { display: flex; gap: 1.1rem; flex-wrap: wrap; align-items: center;
                font-size: .76rem; color: #5F5E5A; margin: .1rem 0 .6rem; }
      .legend span.key { display: inline-flex; align-items: center; gap: .35rem; }
      .swatch { width: .85rem; height: .85rem; border-radius: 3px; display: inline-block; }
      .swatch.hit { background: #E7F0EE; border: 1px solid #E8E8E4; border-left: 3px solid #0F6E56; }
      .swatch.dup { background: rgba(24,95,165,.16); border: 1px solid #E8EFF6; }
      .swatch.flag { background: transparent; border: 1px dashed #534AB7; }
      .stats, .compare { background: #FFFFFF; border: 1px solid #E8E8E4; border-radius: 8px;
                         padding: .55rem .75rem; margin: .1rem 0 .7rem;
                         font: .8rem/1.85 ui-monospace, SFMono-Regular, Menlo, monospace; }
      .stats .row, .compare .row { display: flex; justify-content: space-between; gap: 1.2rem; }
      .stats .k, .compare .k { color: #5F5E5A; }
      .stats .v, .compare .v { font-variant-numeric: tabular-nums; }
      .stats .dup { color: #185FA5; }
      .compare .now { color: #0F6E56; font-weight: 600; }
      .compare .ok { color: #0F6E56; }
      .compare .no { color: #534AB7; }

      /* --- typography & spacing polish ------------------------------------
         No new colours or fonts: #1F1F1D and #5F5E5A are named in the brief,
         and the mono stack is the one already in use. */

      /* Spacing rhythm. Label sits 8px above its control; options within a group
         sit 12px apart; groups sit 24px apart. Divider-separated sidebar sections
         are already 32px apart (hr margins), so they are left alone. */
      [data-testid="stWidgetLabel"] { margin-bottom: 8px; }
      [role="radiogroup"] { gap: 12px; }
      [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"],
      [data-testid="stTabPanel"] [data-testid="stVerticalBlock"] { gap: 24px; }
      /* Dividers get a modest margin so a section header is not crammed against the
         hairline, without returning to the old 32px-per-side void. Lands roughly
         midway: enough of a break to read as a new section, not a gap. */
      [data-testid="stSidebarUserContent"] hr { margin-top: 12px; margin-bottom: 12px; }

      /* Question block. Wrapped in a bordered card with a teal accent edge so a
         reader sees at a glance that this is the question the results answer,
         rather than one more control. The label takes the same uppercase
         micro-style as "CURRENTLY SHOWING"; the chips are 13px / 500 with an 8px
         gap and a 10px row inset; the selected question text is the dominant line
         beneath them. */
      .st-key-question { border: 1px solid #CFE0DB; border-left: 4px solid #0F6E56;
                        border-radius: 10px; background: #FFFFFF;
                        padding: 14px 16px 16px; }
      [data-testid="stVerticalBlock"].st-key-question { gap: 4px; }
      .st-key-question [data-testid="stWidgetLabel"] p { font-size: 28px;
                        font-weight: 700; color: #1F1F1D; text-transform: none;
                        letter-spacing: normal; line-height: 1.2; }
      .st-key-question [role="radiogroup"] { gap: 8px; padding: 8px 0 0; }
      .st-key-question [data-testid="stRadioOption"] p { font-size: 13px;
                        font-weight: 500; }
      .st-key-question [data-testid="stRadioOption"][data-selected="true"] p {
                        font-weight: 700; }
      .qtext { font-size: 16px; font-weight: 500; color: #1F1F1D; line-height: 1.5;
               margin: 0 0 .1rem; }

      /* Sidebar footer at the 12px floor in the muted grey; model stays monospace. */
      .st-key-sidebar_footer p, .st-key-sidebar_footer code { font-size: 12px;
               color: #5F5E5A; }

      /* Inline code tokens (chunk IDs, the source path, the model name) render at
         0.75em, which drops to 10.5px inside a caption. Hold them at the 12px floor.
         Chunk cards live in iframes and the verdict strip uses spans, so neither is
         touched. */
      [data-testid="stMain"] code,
      [data-testid="stSidebarUserContent"] code { font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- cached layers --------------------------------------------------------
# Chunking and embedding are keyed on (strategy, chunk size, overlap) only, so
# changing the question or top-k never re-embeds anything.


@st.cache_resource(show_spinner=False)
def get_model():
    return core.load_model()


@st.cache_data(show_spinner=False)
def get_source() -> str:
    return core.load_source()


@st.cache_data(show_spinner=False)
def get_chunks(cache_key: tuple[str, int, int]):
    return core.chunks_for(*cache_key)


@st.cache_data(show_spinner="Embedding chunks for this configuration…")
def get_chunk_matrix(cache_key: tuple[str, int, int]):
    chunks = get_chunks(cache_key)
    return core.embed_texts(get_model(), [chunk.text for chunk in chunks])


@st.cache_data(show_spinner="Embedding the five questions…")
def get_question_matrix():
    return core.embed_texts(get_model(), list(config.QUESTIONS))


@st.cache_data(show_spinner=False)
def published_top_ids(letter: str, question: int) -> list[int]:
    """Top-3 chunk indices for a published configuration, at its published top-k."""
    published = core.PUBLISHED_SETTINGS[letter]
    chunks = get_chunks(published.cache_key)
    matrix = get_chunk_matrix(published.cache_key)
    hits = core.top_hits(
        get_question_matrix()[question], matrix, chunks, published.top_k
    )
    return [chunk.index for chunk, _ in hits]


# --- controls ------------------------------------------------------------

DEFAULTS = {
    "strategy": core.FIXED_SIZE,
    "size": config.FIXED_CHUNK_SIZE,
    "overlap_percent": 0,
    "top_k": config.TOP_K,
    "question_index": 0,
    "source_view": RETRIEVED_ONLY,
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def load_published(letter: str) -> None:
    published = core.PUBLISHED_SETTINGS[letter]
    st.session_state.strategy = published.strategy
    st.session_state.size = published.size
    st.session_state.overlap_percent = published.overlap_percent
    st.session_state.top_k = published.top_k


def current_settings() -> core.Settings:
    """The live control values as one canonical configuration.

    Read before the sidebar renders so the preset button matching the current
    configuration can be drawn in its selected state. Streamlit writes widget
    changes into session state before rerunning the script, so this already
    sees the values the widgets are about to display.
    """
    strategy = st.session_state.strategy
    return core.Settings(
        strategy=strategy,
        size=st.session_state.size,
        overlap_percent=(
            0 if strategy == core.SECTION_AWARE else st.session_state.overlap_percent
        ),
        top_k=st.session_state.top_k,
    )


settings = current_settings()
published_letter = core.match_published(settings)
section_aware = settings.strategy == core.SECTION_AWARE

with st.sidebar:
    st.markdown("**Published experiment**")
    st.caption("Load a configuration from the article.")
    for letter, label in core.PUBLISHED_SHORT_LABELS.items():
        st.button(
            label,
            use_container_width=True,
            type="primary" if letter == published_letter else "secondary",
            on_click=load_published,
            args=(letter,),
        )
    if published_letter:
        st.caption(core.PUBLISHED_LABELS[published_letter])
    else:
        if section_aware:
            detail = f"section-aware, top-k {settings.top_k}"
        else:
            detail = (
                f"fixed-size, {settings.size} chars, "
                f"{settings.overlap_percent}% overlap, top-k {settings.top_k}"
            )
        st.caption(f"Custom — {detail}. Not one of the three published configurations.")

    # Custom controls stay available but collapsed so A/B/C are the default path.
    with st.expander("Explore custom settings"):
        st.radio("Strategy", options=[core.FIXED_SIZE, core.SECTION_AWARE], key="strategy")
        st.radio(
            "Chunk size (characters)",
            options=core.CHUNK_SIZES,
            key="size",
            horizontal=True,
            disabled=section_aware,
        )
        st.radio(
            "Overlap",
            options=core.OVERLAP_PERCENTS,
            format_func=lambda percent: f"{percent}%",
            key="overlap_percent",
            horizontal=True,
            disabled=section_aware,
        )
        if section_aware:
            st.caption(
                "Section-aware splitting follows the document's `##` headings, "
                "so chunk size and overlap do not apply."
            )
        st.radio("Top-k", options=core.TOP_K_CHOICES, key="top_k", horizontal=True)

    with st.container(key="sidebar_footer"):
        st.caption(
            f"`{config.EMBEDDING_MODEL}` · {config.SIMILARITY} similarity · "
            "the five questions are fixed and cannot be edited"
        )

question_index = st.session_state.question_index
question = config.QUESTIONS[question_index]

raw = get_source()
chunks = get_chunks(settings.cache_key)
matrix = get_chunk_matrix(settings.cache_key)
hits = core.top_hits(get_question_matrix()[question_index], matrix, chunks, settings.top_k)
rank_of = {chunk.index: rank for rank, (chunk, _) in enumerate(hits, start=1)}
stats = core.chunk_stats(chunks)

if settings.strategy == core.SECTION_AWARE:
    settings_label = f"section-aware, top-k {settings.top_k}"
else:
    settings_label = (
        f"{settings.size} chars, {settings.overlap_percent}% overlap, top-k {settings.top_k}"
    )

# Verdict totals for the published run, counted from the reviewed verdicts rather
# than transcribed, so the strip and the surrounding prose cannot disagree.
TOTALS = {
    letter: config.PUBLISHED_SUFFICIENCY[letter].count("sufficient")
    for letter in core.PUBLISHED_SETTINGS
}
_best = max(TOTALS.values())
_tied = [letter for letter, total in TOTALS.items() if total == _best]
TIE_NOTE = (
    f"{' and '.join(_tied)} tie at {_best}/{len(config.QUESTIONS)}, so the totals do "
    "not rank the strategies."
    if len(_tied) > 1
    else "The totals describe this one run and are not a ranking."
)
# The same point, short enough to sit on the always-visible summary line.
TIE_SHORT = (
    f"{' and '.join(_tied)} tie, so this is not a ranking"
    if len(_tied) > 1
    else "one run, not a ranking"
)


# --- iframe rendering ----------------------------------------------------
# Palette lifted from aiinpracticehub.com. Teal is the RAG series accent and marks
# retrieved chunks, blue tints text repeated across a boundary, purple marks a
# boundary that fell inside a word. The site is light-only, and .streamlit/config.toml
# pins the app to a light base, so there is no dark variant to carry here.

IFRAME_CSS = """
  :root { --ink:#26262C; --gray:#5F5E5A; --line:#E8E8E4; --card:#FFFFFF;
          --wash:#F4F4F1; --teal:#0F6E56; --teal-fill:#E7F0EE;
          --blue-mark:rgba(24,95,165,.16); --purple:#534AB7;
          --bar:rgba(15,110,86,.28); }
  * { box-sizing: border-box; }
  body { margin:0; background:#FFFFFF; color:var(--ink);
         font-family:'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
  .card { background:var(--card); border:1px solid var(--line);
          border-left:3px solid var(--line); border-radius:8px;
          margin-bottom:.6rem; overflow:hidden; }
  .card.hit { border-left-color:var(--teal); border-color:#D9E5E1; }
  .head { display:flex; gap:.55rem; flex-wrap:wrap; align-items:baseline;
          padding:.34rem .58rem; background:var(--wash);
          border-bottom:1px solid var(--line);
          font:600 .72rem/1.7 ui-monospace, SFMono-Regular, Menlo, monospace; }
  .card.hit .head { background:var(--teal-fill); border-bottom-color:#D9E5E1; }
  .primary { font-size:.84rem; font-weight:700; color:var(--ink); }
  .id { font-size:.78rem; }
  .muted { color:#9B9A96; font-weight:400; font-size:.68rem; }
  .flag { color:var(--purple); font-weight:400; font-size:.68rem; }
  .rank { background:var(--teal); color:#fff; padding:.04rem .42rem; border-radius:4px;
          font-size:.7rem; }
  .score { font-size:.75rem; color:var(--teal); }
  .bar { height:3px; background:var(--bar); }
  .body { padding:.6rem; margin:0; white-space:pre-wrap; word-break:break-word;
          font:.79rem/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }
  mark.dup { background:var(--blue-mark); color:inherit; border-radius:2px; }
  .gap { border:1px dashed var(--line); border-radius:8px; margin-bottom:.6rem;
         padding:.3rem .58rem; color:var(--gray); background:#FFFFFF;
         font:.72rem/1.6 ui-monospace, SFMono-Regular, Menlo, monospace; }
"""

CHARS_PER_LINE = 88
LINE_HEIGHT = 19
CARD_CHROME = 58


def render_cards(cards: list[str], height: int) -> None:
    document = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{IFRAME_CSS}</style></head>"
        f"<body>{''.join(cards)}</body></html>"
    )
    st.iframe(document, height=height)


def estimate_height(texts: list[str], gaps: int = 0) -> int:
    """Rough panel height so a short view does not leave a tall empty frame."""
    total = 0
    for text in texts:
        lines = sum(max(1, math.ceil(len(line) / CHARS_PER_LINE)) for line in text.split("\n"))
        total += CARD_CHROME + lines * LINE_HEIGHT
    total += gaps * 40
    return max(260, min(PANEL_HEIGHT, total + 16))


def chunk_label(index: int) -> str:
    return f"{published_letter}-{index}" if published_letter else f"Chunk {index}"


def body_html(text: str, duplicated_prefix: int) -> str:
    cut = min(duplicated_prefix, len(text))
    if cut > 0:
        marked = f'<mark class="dup">{html.escape(text[:cut])}</mark>'
        return f'<div class="body">{marked}{html.escape(text[cut:])}</div>'
    return f'<div class="body">{html.escape(text)}</div>'


def card_html(chunk, duplicated_prefix: int, rank: int | None, score: float | None) -> str:
    head = []
    label = chunk_label(chunk.index)
    # Primary line: Rank · ID · cosine. Offsets and boundary notes stay quieter.
    if rank is not None and score is not None:
        head.append(
            f'<span class="primary">Rank {rank} · {html.escape(label)} · '
            f"cosine {score:.4f}</span>"
        )
    else:
        if rank is not None:
            head.append(f'<span class="rank">Rank {rank}</span>')
        head.append(f'<span class="id">{html.escape(label)}</span>')
        if score is not None:
            head.append(f'<span class="score">cosine {score:.4f}</span>')
    head.append(f'<span class="muted">[{chunk.start}:{chunk.end}]</span>')
    head.append(f'<span class="muted">{chunk.char_count} chars</span>')
    if chunk.heading:
        head.append(f'<span class="muted">{html.escape(chunk.heading)}</span>')

    starts_inside, ends_inside = core.cut_mid_word(raw, chunk)
    flags = []
    if starts_inside:
        flags.append("starts mid-word")
    if ends_inside:
        flags.append("ends mid-word")
    if flags:
        head.append(f'<span class="flag">{" · ".join(flags)}</span>')

    bar = ""
    if score is not None:
        bar = f'<div class="bar" style="width:{max(0.0, min(1.0, score)) * 100:.1f}%"></div>'
    css = "card hit" if rank is not None else "card"
    return (
        f'<div class="{css}"><div class="head">{"".join(head)}</div>{bar}'
        f"{body_html(chunk.text, duplicated_prefix)}</div>"
    )


def gap_html(skipped: list) -> str:
    first, last = skipped[0].index, skipped[-1].index
    span = f"{chunk_label(first)}" if first == last else f"{chunk_label(first)} – {chunk_label(last)}"
    word = "chunk" if len(skipped) == 1 else "chunks"
    return f'<div class="gap">{len(skipped)} {word} not retrieved · {span}</div>'


def stats_html() -> str:
    duplicated = stats["indexed"] - len(raw)
    if duplicated > 0:
        dup_value = (
            f'<span class="dup">{duplicated:,} chars '
            f"(+{duplicated / len(raw) * 100:.0f}%)</span>"
        )
    else:
        dup_value = "0 chars (+0%)"
    rows = [
        ("Source", f"{len(raw):,} chars"),
        ("Indexed", f"{stats['indexed']:,} chars"),
        ("Duplicated", dup_value),
        ("Chunks", f"{stats['count']:,}"),
        (
            "Chunk size",
            f"min {stats['min']:,} · mean {stats['mean']:,} · max {stats['max']:,} chars",
        ),
    ]
    body = "".join(
        f'<div class="row"><span class="k">{label}</span><span class="v">{value}</span></div>'
        for label, value in rows
    )
    return f'<div class="stats">{body}</div>'


def chip(label: str, value: str) -> str:
    return (
        f'<span class="chip"><span class="ck">{label}</span>'
        f'<span class="cv">{html.escape(value)}</span></span>'
    )


def selection_html() -> str:
    """Every live control value in one row, so the current state is never implicit."""
    if published_letter:
        chips = [f'<span class="chip pub">Published experiment {published_letter}</span>']
    else:
        chips = ['<span class="chip custom">Custom configuration</span>']

    chips.append(chip("Strategy", settings.strategy))
    if section_aware:
        chips.append(chip("Boundaries", "## sections"))
    else:
        chips.append(chip("Chunk size", f"{settings.size} chars"))
        chips.append(
            chip("Overlap", f"{settings.overlap_percent}% · {settings.overlap} chars")
        )
    chips.append(chip("Top-k", str(settings.top_k)))
    chips.append(chip("Question", f"Q{question_index + 1}"))
    chips.append(chip("Chunks", f"{stats['count']}"))
    return f'<div class="selection">{"".join(chips)}</div>'


SHORT_MODE = {
    config.BOUNDARY_CUT: "boundary",
    config.RANKING_MISS: "ranking",
    config.CROSS_REFERENCE: "cross-ref",
}


def verdict_strip_html() -> str:
    """The published 5x3 verdict grid, with each configuration's total.

    Failing cells also name how they failed, so the reader can see that most
    shortfalls here are ranking outcomes rather than damaged text.
    """
    letters = list(core.PUBLISHED_SETTINGS)
    head = "".join(f'<span class="h">{config.PUBLISHED_COLUMNS[x]}</span>' for x in letters)
    rows = [f'<div class="vr"><span class="q"></span>{head}</div>']

    for index in range(len(config.QUESTIONS)):
        cells = []
        for letter in letters:
            if config.PUBLISHED_SUFFICIENCY[letter][index] == "sufficient":
                cells.append('<span class="cell pass">Pass</span>')
            else:
                modes = config.PUBLISHED_FAILURE_MODES.get(letter, {}).get(index, ())
                why = " + ".join(SHORT_MODE[mode] for mode in modes)
                cells.append(
                    f'<span class="cell fail">Fail<span class="why">{why}</span></span>'
                )
        here = " here" if index == question_index else ""
        rows.append(
            f'<div class="vr{here}"><span class="q">Q{index + 1}</span>{"".join(cells)}</div>'
        )

    totals = "".join(
        f'<span class="cell">{TOTALS[letter]}/{len(config.QUESTIONS)}</span>'
        for letter in letters
    )
    rows.append(f'<div class="vr tot"><span class="q">Total</span>{totals}</div>')
    return f'<div class="verdicts">{"".join(rows)}</div>'


def verdict_summary_html() -> str:
    """One-line totals, counted from the same data as the grid it summarises.

    The grid sits behind a tab, and content in a non-default tab is easy to miss,
    so the headline it carries stays on the page whether or not the tab is opened.
    """
    totals = "".join(
        f'<span class="t">{letter} {TOTALS[letter]}/{len(config.QUESTIONS)}</span>'
        for letter in core.PUBLISHED_SETTINGS
    )
    return (
        '<div class="vsum"><span class="k">Reviewed verdicts</span>'
        f'{totals}<span class="k">{TIE_SHORT}</span></div>'
    )


def verdict_line_html(verdict: str, label: str, score: float) -> str:
    """Verdict and the rank 1 cosine score side by side, deliberately adjacent."""
    state = "pass" if verdict == "sufficient" else "fail"
    return (
        '<div class="vline">'
        f'<span class="vchip {state}">Reviewed verdict: {verdict}</span>'
        f'<span class="vchip score">rank 1 · {label} · cosine {score:.4f}</span>'
        "</div>"
    )


def failure_modes_html(letter: str, index: int) -> str:
    modes = config.PUBLISHED_FAILURE_MODES.get(letter, {}).get(index, ())
    if not modes:
        return ""
    chips = "".join(f'<span class="mode">{mode}</span>' for mode in modes)
    return f'<div class="modes"><span class="k">Failure mode</span>{chips}</div>'


def compare_html() -> str:
    rows = []
    for letter in core.PUBLISHED_SETTINGS:
        ids = ", ".join(f"{letter}-{index}" for index in published_top_ids(letter, question_index))
        verdict = config.PUBLISHED_SUFFICIENCY[letter][question_index]
        verdict_class = "ok" if verdict == "sufficient" else "no"
        name_class = "now" if letter == published_letter else "k"
        rows.append(
            f'<div class="row"><span class="{name_class}">{letter}</span>'
            f'<span class="v">{ids}</span>'
            f'<span class="{verdict_class}">{verdict}</span></div>'
        )
    return f'<div class="compare">{"".join(rows)}</div>'


def compact_abc_html() -> str:
    """Pass/Fail only for the selected question across A/B/C."""
    parts = []
    for letter in core.PUBLISHED_SETTINGS:
        verdict = config.PUBLISHED_SUFFICIENCY[letter][question_index]
        label = "PASS" if verdict == "sufficient" else "FAIL"
        cls = "ok" if verdict == "sufficient" else "no"
        now = " now" if letter == published_letter else ""
        parts.append(
            f'<span class="abc{now}"><b>{letter}</b> '
            f'<span class="{cls}">{label}</span></span>'
        )
    return f'<div class="abcrow">{"".join(parts)}</div>'


def config_line() -> str:
    """One concise line instead of a row of equal-weight chips."""
    if section_aware:
        return (
            f"Section-aware · ## sections · top-k {settings.top_k} · "
            f"{stats['count']} chunks"
        )
    overlap_bit = (
        "0 overlap"
        if settings.overlap == 0
        else f"{settings.overlap_percent}% overlap ({settings.overlap} chars)"
    )
    return (
        f"Fixed-size · {settings.size} chars · {overlap_bit} · "
        f"top-k {settings.top_k} · {stats['count']} chunks"
    )


def result_anchor_html() -> str:
    """Configuration, PASS/FAIL, and the frozen Why — before any internals."""
    if published_letter:
        verdict = config.PUBLISHED_SUFFICIENCY[published_letter][question_index]
        observation = config.PUBLISHED_OBSERVATIONS[published_letter][question_index]
        badge = "PASS" if verdict == "sufficient" else "FAIL"
        badge_cls = "pass" if verdict == "sufficient" else "fail"
        border_cls = "" if verdict == "sufficient" else " fail"
        why_label = "Why this passed" if verdict == "sufficient" else "Why this failed"
        return (
            f'<div class="anchor{border_cls}">'
            f'<div class="aconfig">{html.escape(core.PUBLISHED_LABELS[published_letter])}</div>'
            f'<div class="abadge {badge_cls}">{badge}</div>'
            f'<div class="awhy"><span class="k">{why_label}</span>'
            f"{html.escape(observation)}</div></div>"
        )
    if section_aware:
        title = f"Custom — section-aware, top-k {settings.top_k}"
    else:
        title = (
            f"Custom — Fixed-size, {settings.size} chars, "
            f"{settings.overlap_percent}% overlap"
        )
    return (
        f'<div class="anchor">'
        f'<div class="aconfig">{html.escape(title)}</div>'
        f'<div class="abadge inspect">Inspect evidence</div>'
        f'<div class="awhy"><span class="k">No published verdict</span>'
        "No Pass/Fail is recorded for this parameter combination, and none is inferred. "
        "Compare the retrieved chunks against the rubric below.</div></div>"
    )


# --- page ----------------------------------------------------------------
# Reader-first order: preset (sidebar) → question → result → why → A/B/C compare
# → top-k evidence. Tuning machinery and chunk internals sit in expanders.

st.title("Chunking explorer")
st.caption(
    "This demo uses one small policy and one embedding model. Treat the results as "
    "an illustration, not a universal benchmark."
)

with st.container(key="question"):
    st.radio(
        "Question",
        options=range(len(config.QUESTIONS)),
        format_func=lambda index: f"Q{index + 1}",
        key="question_index",
        horizontal=True,
    )
    st.markdown(
        f'<div class="qtext">{html.escape(config.QUESTIONS[st.session_state.question_index])}</div>',
        unsafe_allow_html=True,
    )

st.markdown(result_anchor_html(), unsafe_allow_html=True)

# Extra failure context for published shortfalls, still above the evidence.
if published_letter:
    verdict = config.PUBLISHED_SUFFICIENCY[published_letter][question_index]
    if verdict != "sufficient":
        st.markdown(
            failure_modes_html(published_letter, question_index),
            unsafe_allow_html=True,
        )
        missed = config.PUBLISHED_MISSED_EVIDENCE.get(published_letter, {}).get(
            question_index
        )
        if missed:
            st.info(f"{config.MISSED_EVIDENCE_HEADLINE} {missed}")
        if config.CROSS_REFERENCE in config.PUBLISHED_FAILURE_MODES.get(
            published_letter, {}
        ).get(question_index, ()):
            st.markdown(
                f'<div class="q3note">{config.Q3_CROSS_REFERENCE_NOTE}</div>',
                unsafe_allow_html=True,
            )

st.caption(f"Published A / B / C for Q{question_index + 1}")
st.markdown(compact_abc_html(), unsafe_allow_html=True)

st.markdown(
    f'<div class="configline">{html.escape(config_line())}</div>',
    unsafe_allow_html=True,
)

# --- primary evidence: top-k retrieved chunks --------------------------------
st.subheader("Top retrieved chunks")
retrieved_chunks = [chunk for chunk, _ in hits]
unique, total = core.unique_coverage(retrieved_chunks)
badges = " ".join(f"`{chunk_label(chunk.index)}`" for chunk in retrieved_chunks)
st.markdown(f"**Top-{settings.top_k}:** {badges}")
if unique == total:
    st.caption(f"Covering {unique:,} unique characters of the source.")
else:
    st.caption(
        f"Covering {unique:,} unique characters of the source, from {total:,} characters "
        f"across the {settings.top_k} chunks, so {total - unique:,} are retrieved twice."
    )

history = st.session_state.setdefault("previous_view", {})
earlier = history.get(question_index)
if earlier and earlier["label"] != settings_label:
    st.caption(
        f"Previously on this question — {earlier['label']}: {earlier['ids']} "
        f"({earlier['unique']:,} unique chars)."
    )
history[question_index] = {
    "label": settings_label,
    "ids": ", ".join(chunk_label(chunk.index) for chunk in retrieved_chunks),
    "unique": unique,
}

render_cards(
    [
        card_html(chunk, settings.overlap if chunk.index > 0 else 0, rank, score)
        for rank, (chunk, score) in enumerate(hits, start=1)
    ],
    estimate_height([chunk.text for chunk in retrieved_chunks]),
)

with st.expander("Sufficiency rubric for this question"):
    st.markdown(config.SUFFICIENCY_RUBRIC_DISPLAY[question_index])
    if published_letter:
        st.caption(
            "Verdict and explanation above were written by hand after the published "
            "run, for this configuration only."
        )
    else:
        st.caption(
            "No verdict is recorded for this parameter combination, and none is inferred."
        )

# --- optional deeper inspection ---------------------------------------------
with st.expander("View all experiment results"):
    st.markdown("**Reviewed verdicts for the published experiment**")
    st.markdown(verdict_strip_html(), unsafe_allow_html=True)
    st.markdown(
        f'<div class="q3note">{config.Q3_CROSS_REFERENCE_NOTE}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"{config.VERDICT_SCOPE_NOTE} {TIE_NOTE}")
    st.caption(
        f"Top-{config.TOP_K} chunk IDs for Q{question_index + 1} under each published "
        "configuration:"
    )
    st.markdown(compare_html(), unsafe_allow_html=True)

with st.expander("Index statistics"):
    st.markdown(stats_html(), unsafe_allow_html=True)

with st.expander("Inspect source and chunk boundaries"):
    view = st.radio(
        "Source view",
        options=[RETRIEVED_ONLY, ALL_CHUNKS],
        key="source_view",
        horizontal=True,
    )
    if settings.overlap:
        st.caption(
            f"Highlighted text at the start of a chunk is the {settings.overlap} characters "
            "it repeats from the end of the previous chunk."
        )
    st.markdown(
        '<div class="legend">'
        '<span class="key"><span class="swatch hit"></span>retrieved for this question</span>'
        '<span class="key"><span class="swatch dup"></span>text repeated from the previous chunk</span>'
        '<span class="key"><span class="swatch flag"></span>boundary falls inside a word</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    cards: list[str] = []
    texts: list[str] = []
    gap_count = 0
    if view == ALL_CHUNKS:
        for position, chunk in enumerate(chunks):
            cards.append(
                card_html(
                    chunk,
                    settings.overlap if position > 0 else 0,
                    rank_of.get(chunk.index),
                    None,
                )
            )
            texts.append(chunk.text)
    else:
        pending: list = []
        for position, chunk in enumerate(chunks):
            if chunk.index in rank_of:
                if pending:
                    cards.append(gap_html(pending))
                    gap_count += 1
                    pending = []
                cards.append(
                    card_html(
                        chunk,
                        settings.overlap if position > 0 else 0,
                        rank_of[chunk.index],
                        None,
                    )
                )
                texts.append(chunk.text)
            else:
                pending.append(chunk)
        if pending:
            cards.append(gap_html(pending))
            gap_count += 1
        st.caption(
            f"Showing the {len(hits)} retrieved chunks in document order. The index "
            f"contains {stats['count']} chunks in total."
        )

    render_cards(cards, estimate_height(texts, gap_count))

with st.expander("Method"):
    st.markdown(
        "Companion to *Why Fixed-Size Chunking Breaks Retrieval*, from the "
        f"[RAG in Practice]({SITE_URL}) series. Changing chunk boundaries changes both "
        "the evidence stored in each chunk and which chunks compete for the top-k "
        "retrieval slots."
    )
    st.markdown(
        f"""
- The document is `source/{config.SOURCE_DOCUMENT.name}`, {len(raw):,} characters, loaded raw.
- Chunks are embedded with `{config.EMBEDDING_MODEL}` and ranked by {config.SIMILARITY}
  similarity. Ties resolve to the lower chunk index.
- **Retrieval evidence only.** No answer is generated, and no keyword search, reranking,
  contextual retrieval or query rewriting is applied. Only chunking settings and top-k vary.
- Chunks are numbered from 0, matching the chunk IDs published with the article. When the
  settings reproduce a published configuration, IDs appear as `A-9`, `B-11`, `C-6` and so on.
- Chunk text is shown exactly as stored, including Markdown markers, table pipes and `---`
  rules. Nothing is normalized or re-wrapped.
- Verdicts and explanations exist only for the three published configurations, are written
  by hand, and are never generated. Every other combination shows the rubric alone.
- The Q5 rubric wording was clarified after the published run to say plainly that the
  generic "may inspect" sentence is not sufficient on its own. The change narrows the
  criterion and alters no recorded verdict; `config.SUFFICIENCY_RUBRIC` still holds the
  text exactly as frozen before the run.
        """
    )
    with st.expander("Read the full policy document"):
        st.caption(
            f"Verbatim contents of `source/{config.SOURCE_DOCUMENT.name}` "
            f"({len(raw):,} characters) — the one document behind every result here."
        )
        st.markdown(raw)
