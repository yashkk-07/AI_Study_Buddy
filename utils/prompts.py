# utils/prompts.py

EXPLAIN_PROMPT = {
    "Beginner": "Explain the topic in very simple words with examples:\n",
    "Intermediate": "Explain the topic clearly with key points:\n",
    "Exam-Oriented": "Explain the topic for exams with definitions and points:\n"
}

SUMMARY_PROMPT = {
    "Beginner": "Summarize the notes in simple bullet points:\n",
    "Intermediate": "Summarize the notes concisely:\n",
    "Exam-Oriented": "Summarize the notes with exam-focused bullet points:\n"
}

QUIZ_PROMPT = """
Create 5 MCQ questions with 4 options (A, B, C, D).
Also clearly mention the correct answer.
Topic:
"""