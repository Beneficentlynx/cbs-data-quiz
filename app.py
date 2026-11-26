"""
CBS Data Quiz & Wrapped - Streamlit Application
"""

import os
import re
import streamlit as st
from modules.cbs_api import CBSApiManager
from modules.quiz_engine import (
    calculate_projected_value,
    format_number_dutch,
    calculate_question_score,
    calculate_choice_score,
    generate_wrapped_analytics,
)
from modules.question_importer import (
    import_questions_from_csv,
    import_questions_from_json,
    save_imported_questions,
)
from modules.ui_components import (
    apply_custom_css,
    render_header,
    render_scoreboard,
    render_preview_box,
    render_feedback_card,
    render_wrapped_screen,
)

# 1. Page Configuration
st.set_page_config(
    page_title="CBS Data Quiz & Wrapped",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

apply_custom_css()

# 2. Session State Initialization
if "cbs_manager" not in st.session_state:
    st.session_state.cbs_manager = CBSApiManager()

if "api_status" not in st.session_state or not st.session_state.get("api_status", {}).get("online", False):
    st.session_state.api_status = st.session_state.cbs_manager.check_api_status()

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

if "age_category" not in st.session_state:
    st.session_state.age_category = "25-39"

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0

if "revealed" not in st.session_state:
    st.session_state.revealed = False

if "answers" not in st.session_state:
    st.session_state.answers = []

if "last_revealed_data" not in st.session_state:
    st.session_state.last_revealed_data = None


# 3. Helpers
def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.quiz_completed = False
    st.session_state.current_idx = 0
    st.session_state.revealed = False
    st.session_state.answers = []
    st.session_state.last_revealed_data = None
    st.session_state.api_status = st.session_state.cbs_manager.check_api_status()


def get_current_running_score() -> float:
    if not st.session_state.answers:
        return 100.0
    scores = [a["score"] for a in st.session_state.answers]
    return sum(scores) / len(scores)


# 4. Header
render_header(st.session_state.api_status)

# -------------------------------------------------------------
# SCREEN 1: ONBOARDING & LEEFTIJDSKEUZE
# -------------------------------------------------------------
if not st.session_state.quiz_started and not st.session_state.quiz_completed:
    st.markdown("""
    # Statistische Feitencheck 2026
    <p class="cbs-lead">
    Het Centraal Bureau voor de Statistiek (CBS) verzamelt en publiceert onafhankelijke statistieken over Nederland. 
    Met deze interactieve toepassing toetst u uw beeld van recente maatschappelijke en economische ontwikkelingen 
    aan de geregistreerde cijfers in de CBS StatLine databank.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### Selecteer een doelgroep of interessegebied")
    st.write("De geselecteerde categorie bepaalt welke kernindicatoren aan bod komen:")

    age_options = {
        "15-24": "15 tot 25 jaar (Jongeren, studenten, starters op de arbeidsmarkt)",
        "25-39": "25 tot 40 jaar (Starters op de woningmarkt, gezinnen, kinderopvang)",
        "40-64": "40 tot 65 jaar (Huishoudens, vermogensopbouw, inflatie, energietransitie)",
        "65+": "65 jaar en ouder (Senioren, AOW-pensioen, zorg, levensverwachting)",
        "alle": "Alle categorieën (Brede representatieve doorsnede van alle indicatoren)",
    }

    selected_age = st.radio(
        "Kies uw categorie:",
        options=list(age_options.keys()),
        format_func=lambda x: age_options[x],
        index=1,
        label_visibility="collapsed",
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("Start Feitencheck", type="primary", use_container_width=False):
        st.session_state.age_category = selected_age
        questions = st.session_state.cbs_manager.get_questions_for_age(selected_age)
        st.session_state.questions = questions
        st.session_state.quiz_started = True
        st.session_state.current_idx = 0
        st.session_state.answers = []
        st.session_state.revealed = False
        st.rerun()

    st.markdown("<br/><br/>", unsafe_allow_html=True)
    with st.expander("Indicatoren beheren en importeren"):
        st.markdown("""
        Onderzoekers en redacteuren kunnen aanvullende indicatoren uploaden via een **CSV-** of **JSON-bestand**. 
        De gegevens worden gevalideerd en gekoppeld aan de officiële CBS StatLine tabellen.
        """)

        c_tpl1, c_tpl2 = st.columns(2)
        with c_tpl1:
            if os.path.exists("data/templates/questions_template.csv"):
                with open("data/templates/questions_template.csv", "r", encoding="utf-8") as f:
                    st.download_button(
                        "Download CSV-sjabloon",
                        data=f.read(),
                        file_name="cbs_indicatoren_sjabloon.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
        with c_tpl2:
            if os.path.exists("data/templates/questions_template.json"):
                with open("data/templates/questions_template.json", "r", encoding="utf-8") as f:
                    st.download_button(
                        "Download JSON-sjabloon",
                        data=f.read(),
                        file_name="cbs_indicatoren_sjabloon.json",
                        mime="application/json",
                        use_container_width=True,
                    )

        uploaded_file = st.file_uploader(
            "Selecteer een CSV of JSON bestand:",
            type=["csv", "json"],
            help="Upload een bestand met indicatoren om toe te voegen aan de database.",
            key="question_uploader",
        )

        if uploaded_file is not None:
            filename = uploaded_file.name.lower()
            if filename.endswith(".json"):
                valid_q, errs = import_questions_from_json(uploaded_file.read().decode("utf-8"))
            else:
                valid_q, errs = import_questions_from_csv(uploaded_file)

            if errs:
                st.warning(f"Aantal opmerkingen bij validatie: {len(errs)}")
                for e in errs:
                    st.caption(f"• {e}")

            if valid_q:
                st.success(f"{len(valid_q)} geldige indicatoren herkend.")
                import pandas as pd
                preview_df = pd.DataFrame([{
                    "Indicator": q["title"],
                    "Thema": q["category"],
                    "Doelgroep": ", ".join(q["target_ages"]),
                    "Basis (2025)": q["baseline_formatted"],
                    "Realisatie (2026)": q["actual_formatted"],
                    "Mutatie": f"{q['actual_change_pct']:+.1f}%",
                    "StatLine": q["statline_table_id"],
                } for q in valid_q])
                st.dataframe(preview_df, use_container_width=True)

                if st.button("Opslaan in databank", type="primary"):
                    total_cnt = save_imported_questions(valid_q)
                    st.success(f"Gegevens succesvol opgeslagen. Totaal aantal indicatoren: {total_cnt}.")
                    st.rerun()

# -------------------------------------------------------------
# SCREEN 2: HET VRAGENSPEL
# -------------------------------------------------------------
elif st.session_state.quiz_started and not st.session_state.quiz_completed:
    questions = st.session_state.questions
    total_q = len(questions)
    idx = st.session_state.current_idx
    q = questions[idx]

    # Running Scoreboard
    current_avg = get_current_running_score()
    render_scoreboard(idx + 1, total_q, current_avg)

    # Format prompt text with proper HTML bolding
    prompt_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', q['question_prompt'])

    # Question Display in standard CBS panel
    st.markdown(f"""
    <div class="cbs-question-box">
        <div class="cbs-panel-header">Thema: {q['category']}</div>
        <div class="cbs-question-title">{q['title']}</div>
        <div class="cbs-question-text">
            {prompt_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.revealed:
        if q.get("type") == "choice" and q.get("choices"):
            st.markdown("<p style='font-size:0.95rem; font-weight:600; margin-bottom:8px;'>Maak uw keuze:</p>", unsafe_allow_html=True)
            selected_choice = st.radio(
                "Keuzeopties:",
                q["choices"],
                key=f"choice_{q['id']}",
                label_visibility="collapsed",
            )

            if st.button("Bevestig keuze", type="primary"):
                score, error, bias = calculate_choice_score(
                    selected_choice, q["actual_value"]
                )

                record = {
                    "id": q["id"],
                    "title": q["title"],
                    "category": q["category"],
                    "guess_pct": 0.0,
                    "user_choice": selected_choice,
                    "projected_val": 0.0,
                    "actual_pct": 0.0,
                    "actual_value": q["actual_value"],
                    "score": score,
                    "error": error,
                    "bias": bias,
                }
                st.session_state.answers.append(record)
                q_copy = dict(q)
                q_copy["user_choice"] = selected_choice
                st.session_state.last_revealed_data = {
                    "question": q_copy,
                    "guess_pct": 0.0,
                    "projected_guess": 0.0,
                    "score": score,
                    "error": error,
                    "bias": bias,
                }
                st.session_state.revealed = True
                st.rerun()

        else:
            # User Guess Input Slider
            s_min = float(q["slider_range"]["min"])
            s_max = float(q["slider_range"]["max"])
            s_step = float(q["slider_range"]["step"])
            s_default = float(q["slider_range"]["default"])

            guess_pct = st.slider(
                "Geef uw inschatting van de procentuele verandering ten opzichte van de basiswaarde:",
                min_value=s_min,
                max_value=s_max,
                value=s_default,
                step=s_step,
                format="%+.1f%%",
                key=f"slider_{q['id']}",
            )

            # Dynamic live preview calculation
            projected_val = calculate_projected_value(q["baseline_value"], guess_pct)
            formatted_projected = format_number_dutch(projected_val, q["unit"])

            render_preview_box(guess_pct, formatted_projected, q["baseline_formatted"])

            if st.button("Bevestig inschatting", type="primary"):
                score, error, bias = calculate_question_score(
                    guess_pct, q["actual_change_pct"], q.get("tolerance_pct", 6.0)
                )

                record = {
                    "id": q["id"],
                    "title": q["title"],
                    "category": q["category"],
                    "guess_pct": guess_pct,
                    "projected_val": projected_val,
                    "actual_pct": q["actual_change_pct"],
                    "actual_value": q["actual_value"],
                    "score": score,
                    "error": error,
                    "bias": bias,
                }
                st.session_state.answers.append(record)
                st.session_state.last_revealed_data = {
                    "question": q,
                    "guess_pct": guess_pct,
                    "projected_guess": projected_val,
                    "score": score,
                    "error": error,
                    "bias": bias,
                }
                st.session_state.revealed = True
                st.rerun()

    else:
        # Revealed state
        rev = st.session_state.last_revealed_data
        render_feedback_card(
            question=rev["question"],
            guess_pct=rev["guess_pct"],
            projected_guess=rev["projected_guess"],
            score=rev["score"],
            error=rev["error"],
            bias=rev["bias"],
        )

        st.markdown("<br/>", unsafe_allow_html=True)
        is_last = idx + 1 >= total_q
        btn_label = "Bekijk definitief analyserapport ➔" if is_last else "Volgende indicator ➔"

        if st.button(btn_label, type="primary", use_container_width=True):
            if is_last:
                st.session_state.quiz_completed = True
                st.session_state.quiz_started = False
            else:
                st.session_state.current_idx += 1
                st.session_state.revealed = False
                st.session_state.last_revealed_data = None
            st.rerun()

# -------------------------------------------------------------
# SCREEN 3: RESULTATEN & WRAPPED
# -------------------------------------------------------------
elif st.session_state.quiz_completed:
    wrapped_data = generate_wrapped_analytics(st.session_state.answers)
    render_wrapped_screen(wrapped_data)

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("Opnieuw starten", type="secondary"):
        reset_quiz()
        st.rerun()

# 5. Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 0.8rem; color: #486581; line-height: 1.6;'>"
    "<strong>Centraal Bureau voor de Statistiek (CBS)</strong> • Directoraat-Generaal Statistiek<br/>"
    "<em>Voor wat er feitelijk gebeurt</em> • Gevoed door officiële CBS StatLine Open Data"
    "</div>",
    unsafe_allow_html=True,
)
