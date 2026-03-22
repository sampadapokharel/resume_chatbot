from datetime import date
from openai import OpenAI
from src.db import get_relevant_chunks
from src.utils import load_prompt, strip_name_references, is_smalltalk, is_task_question

client = OpenAI()

RELEVANCE_THRESHOLD = 0.17
OFF_TOPIC_RESPONSE = "Please ask another question relevant to Sampada's professional experience."

today = date.today().strftime("%B %d, %Y")
SYSTEM_PROMPT = load_prompt("system_prompt.txt", {"{today}": today})
INTENT_CLASSIFIER_PROMPT = load_prompt("intent_classifier_prompt.txt")


def ask(question: str, chat_history: list = None) -> str:
    if chat_history is None:
        chat_history = []

    if is_smalltalk(question):
        return OFF_TOPIC_RESPONSE

    if is_task_question(question, INTENT_CLASSIFIER_PROMPT):
        return OFF_TOPIC_RESPONSE

    stripped_question = strip_name_references(question)
    if not stripped_question:
        return OFF_TOPIC_RESPONSE

    q_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=stripped_question
    ).data[0].embedding

    rows = get_relevant_chunks(q_embedding)
    if not rows or rows[0][1] < RELEVANCE_THRESHOLD:
        return OFF_TOPIC_RESPONSE

    context = "\n".join([row[0] for row in rows])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *chat_history[-4:],
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        max_tokens=300
    )
    return response.choices[0].message.content
