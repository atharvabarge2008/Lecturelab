"""
app.py
Streamlit web application interface and state manager.
"""

import pandas as pd
import streamlit as st

from config import LANGUAGES, LEVELS
from gemini_client import (
    extract_notes,
    get_client,
    make_flashcards,
    make_quiz,
)
from helpers import (
    friendly_error,
    grade_quiz,
    summarize_log,
    validate_quiz,
    youtube_id,
)

st.set_page_config(
    page_title="LectureLab",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
    <style>
    .flashcard-box {
        background-color: #1E222A;
        border: 2px solid #3B82F6;
        border-radius: 12px;
        padding: 40px 24px;
        text-align: center;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 16px;
    }
    .flashcard-label {
        color: #9CA3AF;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        margin-bottom: 12px;
    }
    .flashcard-text {
        color: #F9FAFB;
        font-size: 1.25rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "link": None,
        "notes": None,
        "cards": None,
        "card_pos": 0,
        "flipped": False,
        "quiz": None,
        "quiz_problems": [],
        "quiz_submitted": False,
        "log": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, list) else value


def reset_state():
    defaults = {
        "link": None,
        "notes": None,
        "cards": None,
        "card_pos": 0,
        "flipped": False,
        "quiz": None,
        "quiz_problems": [],
        "quiz_submitted": False,
        "log": []
    }
    for key, value in defaults.items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value
    st.rerun()


def show_input_screen(client, level: str, language: str):
    st.title("🎓 LectureLab")
    st.caption("Transform any YouTube lecture into concise notes, interactive flashcards, and self-grading quizzes.")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        url_input = st.text_input(
            "Paste YouTube Video Link:",
            placeholder="https://www.youtube.com/watch?v=..."
        )
    with col2:
        st.write("")
        st.write("")
        build_btn = st.button("🚀 Build Study Kit", use_container_width=True, type="primary")

    if build_btn:
        if client is None:
            st.error("API key missing. Add GEMINI_API_KEY to your env file.")
            st.stop()

        v_id = youtube_id(url_input)
        if v_id is None:
            st.error("That doesn't look like a YouTube video link.")
            st.stop()

        clean_link = f"https://www.youtube.com/watch?v={v_id}"
        st.session_state.link = clean_link

        with st.spinner("Watching the lecture..."):
            try:
                notes = extract_notes(client, clean_link, level, language, st.session_state.log)
                st.session_state.notes = notes
                st.rerun()
            except Exception as e:
                st.session_state.link = None
                st.error(friendly_error(e))


def show_flashcards_tab(client, count: int, language: str):
    if st.session_state.cards is None:
        st.info("No flashcards generated yet.")
        if st.button("✨ Generate Flashcards", type="primary"):
            with st.spinner("Creating revision flashcards..."):
                try:
                    cards = make_flashcards(client, st.session_state.notes, count, language, st.session_state.log)
                    st.session_state.cards = cards
                    st.rerun()
                except Exception as e:
                    st.error(friendly_error(e))
    else:
        cards = st.session_state.cards
        if not cards:
            st.warning("No cards available.")
            return

        total = len(cards)
        idx = st.session_state.card_pos % total
        card = cards[idx]

        st.caption(f"Card {idx + 1} of {total}")
        label = "ANSWER" if st.session_state.flipped else "QUESTION"
        content = card["back"] if st.session_state.flipped else card["front"]

        st.markdown(
            f"""
            <div class="flashcard-box">
                <div class="flashcard-label">{label}</div>
                <div class="flashcard-text">{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        def toggle_flip():
            st.session_state.flipped = not st.session_state.flipped

        def next_card():
            st.session_state.card_pos += 1
            st.session_state.flipped = False

        c1.button("🔄 Flip", on_click=toggle_flip, use_container_width=True)
        c2.button("➡️ Next", on_click=next_card, use_container_width=True)


def show_quiz_tab(client, count: int, language: str):
    if st.session_state.quiz is None:
        st.info("No practice quiz generated yet.")
        if st.button("✨ Generate Quiz", type="primary"):
            with st.spinner("Building quiz..."):
                try:
                    raw_q = make_quiz(client, st.session_state.notes, count, language, st.session_state.log)
                    good_q, problems = validate_quiz(raw_q)
                    st.session_state.quiz = good_q
                    st.session_state.quiz_problems = problems
                    st.rerun()
                except Exception as e:
                    st.error(friendly_error(e))
    else:
        quiz = st.session_state.quiz
        if st.session_state.quiz_problems:
            st.warning(f"Note: {len(st.session_state.quiz_problems)} invalid question(s) were dropped.")

        if not quiz:
            st.error("No valid questions. Please regenerate.")
            return

        if not st.session_state.quiz_submitted:
            with st.form("quiz_form"):
                for i, q in enumerate(quiz):
                    st.markdown(f"**Q{i + 1}. {q['question']}**")
                    st.radio("Options:", q["options"], index=None, key=f"q_{i}", label_visibility="collapsed")
                    st.write("")

                if st.form_submit_button("Submit Answers", type="primary", use_container_width=True):
                    st.session_state.quiz_submitted = True
                    st.rerun()
        else:
            answers = [st.session_state.get(f"q_{i}") for i in range(len(quiz))]
            score, results = grade_quiz(quiz, answers)
            total = len(quiz)
            pct = int((score / total) * 100) if total > 0 else 0

            st.metric("Final Score", f"{score}/{total} ({pct}%)")
            st.markdown("---")

            for i, (q, res) in enumerate(zip(quiz, results)):
                st.markdown(f"#### Q{i + 1}. {q['question']}")
                if res["is_correct"]:
                    st.success(f"✅ Correct! Choice: `{res['chosen']}`")
                else:
                    ans_text = res['chosen'] if res['chosen'] is not None else "Skipped"
                    st.error(f"❌ Wrong. Your answer: `{ans_text}` | Correct: `{res['correct']}`")
                st.info(f"💡 Explanation: {q.get('explanation', '')}")

            if st.button("🔄 Retake Quiz"):
                st.session_state.quiz_submitted = False
                for i in range(len(quiz)):
                    st.session_state.pop(f"q_{i}", None)
                st.rerun()


def show_usage_tab():
    st.subheader("📊 Usage Tracker")
    total_calls, total_tokens, total_seconds = summarize_log(st.session_state.log)

    c1, c2, c3 = st.columns(3)
    c1.metric("API Calls", total_calls)
    c2.metric("Total Tokens Used", f"{total_tokens:,}")
    c3.metric("Total Execution Time", f"{total_seconds} s")
    st.markdown("---")

    if not st.session_state.log:
        st.info("No AI calls yet.")
    else:
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df, use_container_width=True)


def main():
    init_state()
    client = get_client()

    with st.sidebar:
        st.header("⚙️ Settings")
        language = st.selectbox("Language", LANGUAGES, index=0)
        level = st.selectbox("Difficulty Level", LEVELS, index=0)

        st.markdown("---")
        st.header("🎛️ Parameters")
        flashcard_count = st.slider("Flashcards Count", 5, 20, 10)
        quiz_count = st.slider("Quiz Questions Count", 3, 15, 5)

        st.markdown("---")
        if st.button("🆕 New Video", use_container_width=True):
            reset_state()

    if st.session_state.notes is None:
        show_input_screen(client, level, language)
    else:
        notes = st.session_state.notes

        col_v, col_n = st.columns([1, 1])
        with col_v:
            st.video(st.session_state.link)
        with col_n:
            st.title(notes.get("title", "Lecture Summary"))
            st.write(notes.get("summary", ""))

            with st.expander("📌 Key Terms & Definitions"):
                for kt in notes.get("key_terms", []):
                    st.markdown(f"• **{kt['term']}**: {kt['definition']}")

            with st.expander("📖 Chapter Breakdown"):
                for ch in notes.get("chapters", []):
                    st.markdown(f"**[{ch['start']}] {ch['heading']}**")
                    for kp in ch.get("key_points", []):
                        st.markdown(f"  - {kp}")

        st.markdown("---")
        t_cards, t_quiz, t_usage = st.tabs(["🎴 Flashcards", "📝 Quiz", "📊 Usage Tracker"])

        with t_cards:
            show_flashcards_tab(client, flashcard_count, language)
        with t_quiz:
            show_quiz_tab(client, quiz_count, language)
        with t_usage:
            show_usage_tab()


if __name__ == "__main__":
    main()
