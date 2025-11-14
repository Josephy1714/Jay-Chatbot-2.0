import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page setup
st.set_page_config(page_title="Jay", layout="centered")

# WhatsApp-style chat bubbles + transparent background
st.markdown("""
    <style>
    body {
        background: transparent;
        overflow-x: hidden;
    }
    .stApp {
        background: transparent;
    }
    .bubble-user {
        background-color: #25D366;
        color: black;
        padding: 10px 14px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        align-self: flex-end;
        margin-left: auto;
        position: relative;
    }
    .bubble-bot {
        background-color: #262d31;
        color: white;
        padding: 10px 14px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        align-self: flex-start;
        margin-right: auto;
        position: relative;
    }
    .tick {
        font-size: 12px;
        color: #bbb;
        position: absolute;
        bottom: 4px;
        right: 10px;
    }
    .typing {
        font-size: 12px;
        color: #aaa;
        opacity: 0.6;
        padding: 8px 14px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        align-self: flex-start;
        margin-right: auto;
        background-color: #262d31;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>💬 Jay</h2>", unsafe_allow_html=True)

# Static greeting bubble (only once)
if "greeting_shown" not in st.session_state:
    st.markdown("""
        <div class='bubble-bot'>Hi, I’m Joseph Ombati 👋 How can I assist you today?<span class='tick'>✓✓</span></div>
    """, unsafe_allow_html=True)
    st.session_state.greeting_shown = True

# Load Joseph's knowledge
with open("joseph_knowledge.txt", "r", encoding="utf-8") as f:
    joseph_knowledge = f.read()

# OpenRouter API setup
API_KEY = st.secrets["api"]["openrouter_key"] if "api" in st.secrets
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display full chat history
for msg in st.session_state.chat_history:
    bubble_class = "bubble-user" if msg["role"] == "user" else "bubble-bot"
    st.markdown(f"""
        <div class='{bubble_class}'>{msg["content"]}<span class='tick'>✓✓</span></div>
    """, unsafe_allow_html=True)

# Reserve space for Jay's reply — BELOW chat history
placeholder = st.empty()

# Input field at the bottom
def submit():
    user_input = st.session_state.input.strip()
    st.session_state.input = ""

    # Skip empty or greeting-like messages
    if user_input.lower() in ["", "hi", "hello", "hey"]:
        return

    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime('%H:%M')
    })

    # Show typing indicator in correct position
    placeholder.markdown("""
        <div class='typing'>Jay is typing... ✍️</div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

    # Prepare messages for API
    messages = [
        {
            "role": "system",
            "content": (
                "You are Jay, a friendly chatbot who speaks as Joseph Ombati in first person. "
                "Do not repeat your intro. Keep responses short, friendly, and engaging. "
                "Use emojis and ask follow-up questions. Avoid long lists or formal tone."
            )
        },
        {"role": "system", "content": joseph_knowledge}
    ]
    for msg in st.session_state.chat_history:
        if msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        try:
            answer = response.json()["choices"][0]["message"]["content"].strip()
            if not answer:
                answer = "Jay received your message but didn’t respond. Try again!"
        except:
            answer = "Jay couldn’t understand the response. Try again!"
    else:
        answer = f"Error {response.status_code}: {response.text}"

    # Add bot response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "timestamp": datetime.now().strftime('%H:%M')
    })

    # Clear typing placeholder — reply will be rendered via chat history loop
    placeholder.empty()

# Input box now appears at the bottom
st.text_input("Type your question here:", key="input", on_change=submit)

