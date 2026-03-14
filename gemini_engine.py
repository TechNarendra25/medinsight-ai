from groq import Groq
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv(override=True)

api_key = None

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    pass

if not api_key:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ API key not found!")
    st.stop()

print(f"Groq API Key loaded: {api_key[:10]}...")
client = Groq(api_key=api_key)


def ask_gemini(user_question, df_summary, df_sample):
    prompt = f"""
You are MedInsight AI, an expert data analyst for
India's pharmaceutical and medicine data.

=== DATASET SUMMARY ===
{df_summary}

=== SAMPLE DATA ===
{df_sample}

=== USER QUESTION ===
{user_question}

Answer clearly, provide exact figures if numbers involved,
give insights, and suggest a chart type if helpful.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


def suggest_questions(df_summary):
    prompt = f"""
Based on this medicine dataset:
{df_summary}

Generate exactly 6 smart questions numbered 1-6.
Keep each under 15 words.
Medicine/pharma domain only.
Return ONLY questions, no explanation.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)