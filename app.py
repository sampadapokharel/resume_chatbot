import streamlit as st
from chatbot import ask

st.title("Ask me anything about Sampada")

question = st.text_input("Ask a question:")

if question:
    answer = ask(question)
    st.write(answer)