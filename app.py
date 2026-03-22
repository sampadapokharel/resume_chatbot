import time
import streamlit as st
from src.chatbot import ask

RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECS = 60

st.title("Ask me anything about Sampada")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "request_timestamps" not in st.session_state:
    st.session_state.request_timestamps = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Ask a question:")

if question:
    now = time.time()
    st.session_state.request_timestamps = [
        t for t in st.session_state.request_timestamps
        if now - t < RATE_LIMIT_WINDOW_SECS
    ]
    if len(st.session_state.request_timestamps) >= RATE_LIMIT_REQUESTS:
        st.warning("Too many requests. Please wait a moment before asking again.")
        st.stop()
    st.session_state.request_timestamps.append(now)

    with st.chat_message("user"):
        st.write(question)

    answer = ask(question, chat_history=st.session_state.messages)

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})
