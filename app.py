import streamlit as st
from chatbot import ask

st.title("Ask me anything about Sampada")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Ask a question:")

if question:
    with st.chat_message("user"):
        st.write(question)

    answer = ask(question, chat_history=st.session_state.messages)

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})
