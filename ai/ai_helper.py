import os
from dotenv import load_dotenv
from groq import Groq

from utils.prompts import EXPLAIN_PROMPT, SUMMARY_PROMPT, QUIZ_PROMPT

# -------------------------------------------------
# LOAD ENV VARIABLES
# -------------------------------------------------
load_dotenv("utils/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in utils/.env file")

# -------------------------------------------------
# GROQ CLIENT SETUP
# -------------------------------------------------
client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.1-8b-instant"

# -------------------------------------------------
# AI FUNCTIONS
# -------------------------------------------------
def explain_topic(topic: str, level: str) -> str:
    """
    Explain a topic based on difficulty level
    """
    prompt = EXPLAIN_PROMPT[level] + topic

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


def summarize_notes(text: str, level: str) -> str:
    """
    Summarize notes based on difficulty level
    """
    prompt = SUMMARY_PROMPT[level] + text

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


def generate_quiz(topic: str) -> str:
    """
    Generate quiz questions from topic or text
    """
    prompt = QUIZ_PROMPT + topic

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()