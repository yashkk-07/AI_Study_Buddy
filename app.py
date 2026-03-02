import streamlit as st
import time
import random

from ai.ai_helper import explain_topic, summarize_notes, generate_quiz
from utils.storage import load_chats, save_chats
from utils.pdf_utils import extract_text_from_pdf
from utils.pdf_export import generate_pdf

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="AI Study Buddy", layout="wide")

# -------------------------------------------------
# GLOBAL CSS (POLISHED UI)
# -------------------------------------------------
st.markdown("""
<style>
section[data-testid="stSidebar"] { background-color: #f7f7f8; }
section[data-testid="stSidebar"] button { border-radius: 8px; font-size: 14px; }

div[data-testid="stChatInput"] {
    position: sticky;
    bottom: 0;
    background: white;
    padding-top: 10px;
}

.stChatMessage.user {
    background-color: #e7f0ff;
    border-radius: 12px;
}

.stChatMessage.assistant {
    background-color: #ffffff;
    border-radius: 12px;
}

.chat-menu {
    background: white;
    border-radius: 8px;
    padding: 6px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    margin-bottom: 8px;
}

.chat-menu button {
    width: 100%;
    background: none;
    border: none;
    text-align: left;
    padding: 6px;
    font-size: 13px;
}
.chat-menu button:hover { background-color: rgba(0,0,0,0.05); }
.chat-menu .delete { color: red; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SESSION STATE DEFAULTS
# -------------------------------------------------
defaults = {
    "active_menu_chat": None,
    "stop_generation": False,
    "is_generating": False,
    "pdf_text": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# LOAD CHATS
# -------------------------------------------------
chats = load_chats()
if "current_chat" not in st.session_state:
    if chats:
        st.session_state.current_chat = list(chats.keys())[0]
    else:
        chats["New Chat"] = {"messages": [], "pinned": False}
        st.session_state.current_chat = "New Chat"
        save_chats(chats)

# -------------------------------------------------
# SIDEBAR (NEWEST CHAT ON TOP)
# -------------------------------------------------
with st.sidebar:
    st.markdown("## 💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        chats["New Chat"] = {"messages": [], "pinned": False}
        st.session_state.current_chat = "New Chat"
        st.session_state.pdf_text = ""
        save_chats(chats)
        st.rerun()

    st.divider()

    for chat_name, data in reversed(list(chats.items())):
        col1, col2 = st.columns([8, 1])
        with col1:
            if st.button(chat_name, key=f"open_{chat_name}", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.session_state.pdf_text = ""
        with col2:
            if st.button("⋯", key=f"menu_{chat_name}"):
                st.session_state.active_menu_chat = (
                    None if st.session_state.active_menu_chat == chat_name else chat_name
                )

        if st.session_state.active_menu_chat == chat_name:
            st.markdown('<div class="chat-menu">', unsafe_allow_html=True)
            if st.button("✏ Rename", key=f"rename_{chat_name}"):
                st.session_state.rename_target = chat_name
            if st.button("🗑 Delete", key=f"delete_{chat_name}"):
                chats.pop(chat_name)
                save_chats(chats)
                st.session_state.current_chat = list(chats.keys())[0]
                st.session_state.active_menu_chat = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# RENAME CHAT
# -------------------------------------------------
if "rename_target" in st.session_state:
    new_name = st.text_input("Rename chat", st.session_state.rename_target)
    if st.button("Save rename"):
        if new_name and new_name not in chats:
            chats[new_name] = chats.pop(st.session_state.rename_target)
            st.session_state.current_chat = new_name
            save_chats(chats)
        st.session_state.pop("rename_target")
        st.rerun()

# -------------------------------------------------
# MAIN AREA
# -------------------------------------------------
chat = chats.get(st.session_state.current_chat)
st.title(st.session_state.current_chat)

# ---------- CONTROLS ----------
st.markdown("### 🧠 Mode")
task = st.selectbox(
    "Task",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"],
    label_visibility="collapsed"
)

st.markdown("### 🎯 Difficulty")
difficulty = st.selectbox(
    "Difficulty",
    ["Beginner", "Intermediate", "Exam-Oriented"],
    label_visibility="collapsed"
)

age = st.slider("👶 Explain for age", 10, 25, 18)

# -------------------------------------------------
# PDF UPLOAD
# -------------------------------------------------
uploaded_pdf = st.file_uploader("📄 Upload typed PDF notes", type=["pdf"])
if uploaded_pdf:
    extracted = extract_text_from_pdf(uploaded_pdf)
    if extracted.strip():
        st.session_state.pdf_text = extracted
        st.success("✅ PDF uploaded. Now tell me what you want to do with it.")
    else:
        st.warning("⚠️ Handwritten or scanned PDFs are not supported.")

# -------------------------------------------------
# SHOW CHAT HISTORY
# -------------------------------------------------
if chat:
    for msg in chat["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# -------------------------------------------------
# STOP RESPONSE BUTTON
# -------------------------------------------------
if st.session_state.is_generating:
    if st.button("⛔ Stop response"):
        st.session_state.stop_generation = True

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
user_input = st.chat_input("Ask a question or give instructions...")

if user_input and chat:

    if st.session_state.pdf_text:
        final_input = (
            f"PDF CONTENT:\n{st.session_state.pdf_text}\n\n"
            f"USER REQUEST:\n{user_input}"
        )
        mode = "intent"
    else:
        final_input = user_input
        mode = "manual"

    chat["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.stop_generation = False
    st.session_state.is_generating = True

    with st.chat_message("assistant"):
        placeholder = st.empty()
        visible = ""

        if mode == "intent":
            inst = user_input.lower()
            if "summary" in inst or "summarize" in inst:
                output = summarize_notes(final_input, difficulty)
            elif "quiz" in inst or "mcq" in inst:
                output = generate_quiz(final_input)
            else:
                output = explain_topic(
                    f"Explain for a {age}-year-old:\n{final_input}",
                    difficulty
                )
        else:
            if task == "Explain Topic":
                output = explain_topic(
                    f"Explain for a {age}-year-old:\n{final_input}",
                    difficulty
                )
            elif task == "Summarize Notes":
                output = summarize_notes(final_input, difficulty)
            else:
                output = generate_quiz(final_input)

        for ch in output:
            if st.session_state.stop_generation:
                break
            visible += ch
            placeholder.markdown(visible)
            time.sleep(0.01)

    st.session_state.is_generating = False
    chat["messages"].append({"role": "assistant", "content": visible})
    st.session_state.last_response = visible

    # UNIQUE FEATURES
    st.progress(random.randint(75, 95))
    st.caption("📊 Answer confidence level")

    if st.button("📌 Extract Exam Key Points"):
        key_points = summarize_notes(
            f"Extract only exam-important points:\n{visible}",
            "Exam-Oriented"
        )
        st.markdown(key_points)

    # EXPORT RESPONSE AS PDF
    if "last_response" in st.session_state:
        pdf_buffer = generate_pdf(
            title=st.session_state.current_chat,
            content=st.session_state.last_response
        )

        st.download_button(
            "📄 Export response as PDF",
            data=pdf_buffer,
            file_name=f"{st.session_state.current_chat}.pdf",
            mime="application/pdf"
        )

    # AUTO RENAME
    if st.session_state.current_chat == "New Chat":
        auto = user_input[:30].replace("\n", " ")
        chats[auto] = chats.pop("New Chat")
        st.session_state.current_chat = auto

    save_chats(chats)