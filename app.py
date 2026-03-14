import streamlit as st
import pandas as pd
import io
from utils import (load_csv, get_basic_stats,
                   get_dataframe_summary,
                   export_chat_history,
                   clean_dataframe,
                   get_column_insights)
from gemini_engine import ask_gemini, suggest_questions
from chart_generator import generate_chart

# ── Page Configuration ──────────────────────────────────────
st.set_page_config(
    page_title="MedInsight AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0f0f1a;
        color: white;
    }
    .main-header {
        background: linear-gradient(
            135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%
        );
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #00CC96;
        box-shadow: 0 0 20px rgba(0,204,150,0.2);
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(
            135deg, #1a1a2e, #16213e
        );
        border: 1px solid #00CC96;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stChatMessage {
        border-radius: 12px;
        margin: 8px 0;
        border: 1px solid #2a2a4a;
    }
    .stButton > button {
        background: linear-gradient(
            90deg, #00CC96, #0099ff
        );
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    hr {
        border-color: #2a2a4a;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ───────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = None
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💊 MedInsight AI")
    st.markdown("---")

    st.markdown("### 📂 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="Upload any medicine CSV dataset"
    )

    if uploaded_file:
        df, error = load_csv(uploaded_file)
        if error:
            st.error(f"❌ Error: {error}")
        else:
            df = clean_dataframe(df)
            st.session_state.df = df
            st.success("✅ Dataset loaded!")
            st.info(
                f"📊 **{df.shape[0]:,}** rows × "
                f"**{df.shape[1]}** columns"
            )

    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    show_chart = st.toggle(
        "📊 Auto-generate Charts", value=True
    )
    show_data = st.toggle(
        "🔍 Show Data Preview", value=True
    )
    show_insights = st.toggle(
        "💡 Show Column Insights", value=False
    )

    st.markdown("---")

    st.markdown("### 🛠️ Actions")
    if st.session_state.chat_history:
        chat_export = export_chat_history(
            st.session_state.chat_history
        )
        st.download_button(
            label="📥 Export Chat History",
            data=chat_export,
            file_name="medinsight_chat.txt",
            mime="text/plain"
        )

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.total_queries = 0
        st.rerun()

    st.markdown("---")

    st.markdown("### 📈 Session Stats")
    st.metric(
        "Total Queries Asked",
        st.session_state.total_queries
    )

    st.markdown("---")

    st.markdown("""
    ### 📌 About
    **MedInsight AI** analyzes India's
    medicine data using natural language.

    Built with:
    - 🐍 Python & Pandas
    - 🤖 Groq AI (LLaMA)
    - 📊 Plotly Charts
    - 🎈 Streamlit

    👨‍💻 Built by **Narendra Vispute**
    """)

# ── Main Area ────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1 style='color:white; margin:0'>💊 MedInsight AI</h1>
    <p style='color:#00CC96; margin:5px 0 0 0; font-size:18px'>
        Talk to India's Medicine Data using AI
    </p>
    <p style='color:#aaaaaa; margin:5px 0 0 0; font-size:13px'>
        Powered by Groq AI • Built with Streamlit
    </p>
</div>
""", unsafe_allow_html=True)

if st.session_state.df is not None:
    df = st.session_state.df
    df_summary = get_dataframe_summary(df)
    df_sample = df.head(5).to_string()

    # ── Stats Cards ──────────────────────────────────────────
    st.subheader("📊 Dataset Overview")
    stats = get_basic_stats(df)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🗂️ Rows", f"{stats['Total Rows']:,}")
    col2.metric("📋 Columns", stats["Total Columns"])
    col3.metric("❓ Missing", stats["Missing Values"])
    col4.metric("🔢 Numeric", stats["Numeric Columns"])
    col5.metric("🔤 Text", stats["Text Columns"])

    st.markdown("---")

    # ── Data Preview ─────────────────────────────────────────
    if show_data:
        with st.expander("🔍 Data Preview", expanded=False):
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 First 10 Rows",
                "📈 Statistics",
                "❓ Missing Values",
                "🔎 Column Info"
            ])
            with tab1:
                st.dataframe(
                    df.head(10),
                    use_container_width=True
                )
            with tab2:
                st.dataframe(
                    df.describe(),
                    use_container_width=True
                )
            with tab3:
                missing = df.isnull().sum().reset_index()
                missing.columns = ["Column", "Missing"]
                missing["Missing %"] = (
                    missing["Missing"] /
                    len(df) * 100
                ).round(2)
                st.dataframe(
                    missing,
                    use_container_width=True
                )
            with tab4:
                st.dataframe(
                    get_column_insights(df),
                    use_container_width=True
                )

    # ── Column Insights ───────────────────────────────────────
    if show_insights:
        with st.expander(
            "💡 Column Insights", expanded=False
        ):
            st.dataframe(
                get_column_insights(df),
                use_container_width=True
            )

    st.markdown("---")

    # ── Suggested Questions ──────────────────────────────────
    st.subheader("💡 Try These Questions")
    if st.session_state.suggested_questions is None:
        with st.spinner("🤔 Generating smart questions..."):
            questions, err = suggest_questions(df_summary)
            if questions:
                st.session_state.suggested_questions = (
                    questions
                )

    if st.session_state.suggested_questions:
        st.info(st.session_state.suggested_questions)

    st.markdown("---")

    # ── Chat Interface ───────────────────────────────────────
    st.subheader("💬 Ask Anything About Your Data")

    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant", avatar="💊"):
            st.write(chat["answer"])
            if chat.get("chart") is not None:
                st.plotly_chart(
                    chat["chart"],
                    use_container_width=True
                )

    user_question = st.chat_input(
        "Ask anything about the medicine data... "
        "(e.g. 'Which medicine is most expensive?')"
    )

    if user_question:
        if len(user_question.strip()) < 3:
            st.warning("⚠️ Please ask a proper question!")
        else:
            with st.chat_message("user"):
                st.write(user_question)

            with st.chat_message("assistant", avatar="💊"):
                with st.spinner("🤖 Analyzing data..."):
                    answer, error = ask_gemini(
                        user_question,
                        df_summary,
                        df_sample
                    )

                    if error:
                        st.error(
                            f"❌ Error: {error}"
                        )
                    else:
                        st.write(answer)

                        chart = None
                        if show_chart:
                            chart = generate_chart(
                                df, user_question
                            )
                            if chart:
                                st.plotly_chart(
                                    chart,
                                    use_container_width=True
                                )

                        st.session_state.total_queries += 1
                        st.session_state.chat_history.append({
                            "question": user_question,
                            "answer": answer,
                            "chart": chart
                        })

else:
    # ── Welcome Screen ───────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ## 👋 Welcome to MedInsight AI!

        ### How it works:
        | Step | Action |
        |------|--------|
        | 1️⃣ | Upload medicines CSV from sidebar |
        | 2️⃣ | Preview your data instantly |
        | 3️⃣ | Ask questions in plain English |
        | 4️⃣ | Get AI answers + automatic charts |
        | 5️⃣ | Export your chat history |

        ### 💬 Example Questions:
        - *"Which medicine is most expensive?"*
        - *"Show price distribution by category"*
        - *"Which company has most medicines?"*
        - *"Compare prices across categories"*
        - *"What are common side effects?"*

        ---
        👈 **Upload your CSV file to get started!**
        """)

        st.markdown("""
        <div style='text-align:center;
                    color:#00CC96;
                    margin-top:20px'>
            Built with ❤️ by Narendra Vispute
        </div>
        """, unsafe_allow_html=True)