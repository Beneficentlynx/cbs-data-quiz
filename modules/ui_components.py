"""
CBS Design System UI Components.
Follows the official CBS Design System (https://designsystem.cbs.nl/).
Strictly professional government/statistical web design:
- Typography: Clean sans-serif hierarchy (Akko / Inter / System Sans)
- Palette: CBS Corporate Blue (#271D6C), CBS Black (#091D23), CBS Aqua (#00A1CD), Neutral (#F4F6F8), Border (#D9E2EC)
- No decorative gradients, glowing effects or AI-style card gloss.
"""

import os
import base64
import urllib.parse
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from modules.quiz_engine import format_number_dutch
from modules.story_card_generator import generate_spotify_wrapped_story_card

_CBS_LOGO_SRC = None


def get_cbs_logo_src() -> str:
    """Returns official CBS logo data URI with fallbacks."""
    global _CBS_LOGO_SRC
    if _CBS_LOGO_SRC is None:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cbs_logo.svg")
        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    _CBS_LOGO_SRC = f"data:image/svg+xml;base64,{b64}"
            except Exception:
                _CBS_LOGO_SRC = "https://cdn.cbs.nl/icons/navigation/cbs-logo-brand-nl.svg"
        else:
            _CBS_LOGO_SRC = "https://cdn.cbs.nl/icons/navigation/cbs-logo-brand-nl.svg"
    return _CBS_LOGO_SRC


def apply_custom_css():
    """Injects official CBS Design System CSS."""
    st.markdown("""
    <style>
    /* System Typography */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown {
        font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        color: #091D23 !important;
    }

    /* Completely hide Streamlit default chrome (Deploy button, settings menu, header, footer) */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }
    footer {
        display: none !important;
        visibility: hidden !important;
    }
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Standard responsive page container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 920px !important;
    }

    /* Top Government / CBS Bar */
    .cbs-topbar {
        border-bottom: 1px solid #D9E2EC;
        padding-bottom: 14px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .cbs-logo-container {
        display: inline-flex;
        align-items: center;
        text-decoration: none;
        line-height: 1;
    }
    .cbs-logo-img {
        height: 50px;
        max-width: 175px;
        width: auto;
        display: block;
        object-fit: contain;
    }
    @media (max-width: 600px) {
        .cbs-logo-img {
            height: 40px;
            max-width: 140px;
        }
    }
    .cbs-meta-status {
        font-size: 0.8rem;
        color: #52606D;
        background: #F0F4F8;
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid #D9E2EC;
    }

    /* Headings */
    h1 {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #091D23 !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        line-height: 1.3 !important;
    }
    h2 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #091D23 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    h3 {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #271D6C !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Intro Lead Text */
    .cbs-lead {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #334E68;
        margin-bottom: 20px;
    }

    /* Breadcrumbs */
    .cbs-breadcrumbs {
        font-size: 0.8rem;
        color: #627D98;
        margin-bottom: 12px;
    }
    .cbs-breadcrumbs a {
        color: #271D6C;
        text-decoration: none;
    }
    .cbs-breadcrumbs a:hover {
        text-decoration: underline;
    }

    /* Standard CBS Content Box */
    .cbs-panel {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-radius: 4px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .cbs-panel-header {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        color: #271D6C;
        margin-bottom: 8px;
    }

    /* Question Box */
    .cbs-question-box {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-left: 4px solid #271D6C;
        border-radius: 4px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .cbs-question-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #091D23;
        margin-bottom: 10px;
    }
    .cbs-question-text {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #102A43;
    }

    /* Scoreboard */
    .cbs-status-bar {
        background: #F0F4F8;
        border: 1px solid #D9E2EC;
        border-radius: 4px;
        padding: 10px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        font-size: 0.9rem;
    }

    /* Value Preview Banner */
    .cbs-preview-box {
        background: #F8FAFC;
        border: 1px solid #BCCCDC;
        border-radius: 4px;
        padding: 14px 18px;
        margin: 16px 0;
    }
    .cbs-preview-label {
        font-size: 0.8rem;
        color: #486581;
        text-transform: uppercase;
        font-weight: 700;
    }
    .cbs-preview-number {
        font-size: 1.35rem;
        font-weight: 700;
        color: #271D6C;
        margin: 2px 0;
    }

    /* Button Overrides */
    div.stButton > button[kind="primary"] {
        background-color: #271D6C !important;
        color: #FFFFFF !important;
        border: 1px solid #271D6C !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1.2rem !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #181045 !important;
        border-color: #181045 !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #271D6C !important;
        border: 1px solid #271D6C !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }

    /* Standard Form Labels */
    label[data-testid="stWidgetLabel"] {
        color: #091D23 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* Footnotes */
    .cbs-footer {
        border-top: 1px solid #D9E2EC;
        padding-top: 20px;
        margin-top: 30px;
        font-size: 0.8rem;
        color: #627D98;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(api_status: Dict[str, Any]):
    """Renders the official CBS government top bar with authentic logo."""
    status_label = "Verbonden met CBS StatLine Open Data" if api_status.get("online") else "CBS Open Data Offline"
    status_dot = "#10B981" if api_status.get("online") else "#F59E0B"
    logo_src = get_cbs_logo_src()

    html = f"""<div class="cbs-topbar">
<a href="https://www.cbs.nl" target="_blank" class="cbs-logo-container" title="Centraal Bureau voor de Statistiek">
<img src="{logo_src}" alt="Centraal Bureau voor de Statistiek" class="cbs-logo-img" />
</a>
<div class="cbs-meta-status">
<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{status_dot}; margin-right:6px;"></span>
{status_label}
</div>
</div>
<div class="cbs-breadcrumbs">
<span><a href="https://www.cbs.nl" target="_blank">Home</a> / <a href="https://opendata.cbs.nl/statline" target="_blank">StatLine</a> / Feitencheck 2026</span>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_scoreboard(current_q: int, total_q: int, current_score: float):
    """Renders clean progress bar."""
    st.markdown(f"""
    <div class="cbs-status-bar">
        <div>
            <strong>Onderdeel {current_q} van {total_q}</strong>
        </div>
        <div>
            Nauwkeurigheid: <strong style="color: #271D6C;">{current_score:.1f}%</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_preview_box(guess_pct: float, projected_formatted: str, baseline_formatted: str):
    """Renders the slider live calculation preview in clean CBS styling."""
    html = f"""<div class="cbs-preview-box">
<div class="cbs-preview-label">Uw inschatting</div>
<div class="cbs-preview-number">{guess_pct:+.1f}% mutatie</div>
<div style="font-size: 0.95rem; color: #486581;">Dit resulteert in: <strong>{projected_formatted}</strong> (basis 2025: <em>{baseline_formatted}</em>)</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_feedback_card(
    question: Dict[str, Any],
    guess_pct: float,
    projected_guess: float,
    score: float,
    error: float,
    bias: str,
):
    """
    Renders the statistical evaluation in an objective, professional layout.
    """
    actual_pct = question["actual_change_pct"]
    sign_actual = "+" if actual_pct > 0 else ""
    sign_guess = "+" if guess_pct > 0 else ""

    st.markdown("### Uitkomst en statistische toelichting")

    # Side-by-side comparison using standard metrics
    m1, m2 = st.columns(2)
    if question.get("type") == "choice":
        user_choice = question.get("user_choice", str(guess_pct))
        is_correct = score >= 90
        with m1:
            st.metric(
                label="Uw antwoord",
                value=str(user_choice),
                delta="Correct" if is_correct else "Niet correct",
                delta_color="normal" if is_correct else "inverse",
            )
            st.caption(f"Situatie {question.get('period_baseline', '2025')}: {question.get('baseline_formatted', '')}")

        with m2:
            st.metric(
                label="CBS uitkomst 2026",
                value=str(question.get("actual_value", "")),
                delta="Feitelijke registratie",
                delta_color="off",
            )
            st.caption(f"Gevalideerd via StatLine tabel {question.get('statline_table_id', '')}")
    else:
        with m1:
            st.metric(
                label="Uw schatting",
                value=f"{sign_guess}{guess_pct:.1f}%",
                delta=bias,
                delta_color="off",
            )
            st.caption(f"Geschatte peilwaarde: {format_number_dutch(projected_guess, question['unit'])} (was: {question['baseline_formatted']})")

        with m2:
            st.metric(
                label="CBS realisatie 2026",
                value=f"{sign_actual}{actual_pct:.1f}%",
                delta=f"Afwijking: {error:.1f} procentpunt",
                delta_color="off",
            )
            st.caption(f"Feitelijke uitkomst: {question['actual_formatted']}")

    # Editorial Context in standard informational block
    st.info(f"**Achtergrond van de mutatie:**\n\n{question['explanation']}", icon="ℹ️")

    # Direct source button
    btn_col, info_col = st.columns([1, 1])
    with btn_col:
        st.link_button(
            "Tabel openen in CBS StatLine ↗",
            question["cbs_article_url"],
            type="primary",
            use_container_width=True,
        )
    with info_col:
        st.caption(f"StatLine tabelcode: `{question.get('statline_table_id', 'CBS')}`")


def render_wrapped_screen(wrapped: Dict[str, Any]):
    """
    Renders an uncluttered, professional CBS results report without AI gimmicks.
    Includes the official 9:16 Spotify-Wrapped share card export.
    """
    best_cat = wrapped["best_category"]
    worst_cat = wrapped["worst_category"]
    best_3 = wrapped["best_3_questions"]
    worst_3 = wrapped["worst_3_questions"]

    # 1. SAMENVATTING
    st.markdown("## Samenvatting van uw uitkomsten")

    res_col1, res_col2 = st.columns([1, 2])
    with res_col1:
        st.metric(
            label="Totale score",
            value=f"{wrapped['total_score']:.0f}%",
            delta=wrapped['bias_label'],
            delta_color="off",
        )
    with res_col2:
        st.markdown(f"""
        <div style="background: #F0F4F8; border-left: 4px solid #271D6C; padding: 14px 18px; border-radius: 4px;">
            <div style="font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #271D6C;">Profielkwalificatie</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #091D23; margin: 2px 0;">{wrapped['archetype']}</div>
            <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #334E68; line-height: 1.5;">{wrapped['archetype_desc']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 2. THEMA EVALUATIE (Clean standard columns)
    st.markdown("### Analyse per statistisch thema")
    col_best, col_worst = st.columns(2)
    with col_best:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-top: 3px solid #10B981; border-radius: 4px; padding: 14px 18px;">
            <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #059669;">Hoogste nauwkeurigheid</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #091D23; margin: 4px 0;">{best_cat[0]}</div>
            <div style="font-size: 0.9rem; color: #486581;">Gemiddelde score: <strong>{best_cat[1]:.0f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

    with col_worst:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #D9E2EC; border-top: 3px solid #E11D48; border-radius: 4px; padding: 14px 18px;">
            <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #E11D48;">Grootste afwijking</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #091D23; margin: 4px 0;">{worst_cat[0]}</div>
            <div style="font-size: 0.9rem; color: #486581;">Gemiddelde score: <strong>{worst_cat[1]:.0f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 3. OVERZICHTSTABEL (Standard data table)
    st.markdown("### Gedetailleerd overzicht per indicator")

    table_rows = []
    # Add best 3
    for q in best_3:
        table_rows.append({
            "Indicator": q["title"],
            "Thema": q["category"],
            "Uw schatting": f"{q['guess_pct']:+.1f}%",
            "CBS realisatie": f"{q['actual_pct']:+.1f}%",
            "Score": f"{q['score']:.0f}%",
            "Status": "Nauwkeurig",
        })
    # Add worst
    for q in worst_3[:2]:
        table_rows.append({
            "Indicator": q["title"],
            "Thema": q["category"],
            "Uw schatting": f"{q['guess_pct']:+.1f}%",
            "CBS realisatie": f"{q['actual_pct']:+.1f}%",
            "Score": f"{q['score']:.0f}%",
            "Status": "Afwijking",
        })

    df_results = pd.DataFrame(table_rows)
    st.dataframe(df_results, use_container_width=True, hide_index=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 4. RESULTATEN EXPORTEREN EN DELEN (Spotify-Wrapped Story Formaat)
    st.markdown("### Resultaat exporteren en delen")
    st.write(
        "U kunt uw resultaten downloaden als verticale **Story-kaart (9:16 formaat)** "
        "in Spotify-Wrapped stijl voor weergave op mobiele apparaten, Instagram Stories of WhatsApp Status."
    )

    story_png = generate_spotify_wrapped_story_card(wrapped)

    col_btn, col_img = st.columns([1, 1])

    with col_btn:
        st.download_button(
            label="Story-kaart downloaden (PNG)",
            data=story_png,
            file_name="cbs_feitencheck_2026.png",
            mime="image/png",
            type="primary",
            use_container_width=True,
        )

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

        share_msg = (
            f"CBS Feitencheck 2026\n"
            f"Totale score: {wrapped['total_score']:.0f}%\n"
            f"Kwalificatie: {wrapped['archetype']}\n"
            f"Beste thema: {best_cat[0]} ({best_cat[1]:.0f}%)\n"
            f"Centraal Bureau voor de Statistiek — Voor wat er feitelijk gebeurt."
        )
        encoded_msg = urllib.parse.quote(share_msg)

        st.link_button("Deel via WhatsApp", f"https://api.whatsapp.com/send?text={encoded_msg}", use_container_width=True)
        st.link_button("Deel op LinkedIn", f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_msg}", use_container_width=True)
        st.link_button("Deel op X", f"https://twitter.com/intent/tweet?text={encoded_msg}", use_container_width=True)

        with st.expander("Tekstversie voor klembord"):
            st.code(share_msg, language="text")

    with col_img:
        st.image(
            story_png,
            caption="Voorbeeld: Story-kaart (9:16 formaat)",
            use_container_width=True,
        )
