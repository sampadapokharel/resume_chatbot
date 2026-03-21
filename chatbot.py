import os
import re
import psycopg2
from datetime import date
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

with open("system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read().replace("{today}", date.today().strftime("%B %d, %Y"))

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

register_vector(conn)
cur = conn.cursor()

RELEVANCE_THRESHOLD = 0.17
NAME_PATTERN = re.compile(r"\b(sampada|pokharel|she|her)\b", re.IGNORECASE)
SMALLTALK_PATTERN = re.compile(
    r"^\s*(hi|hello|hey|howdy|how are you|how('s| is) it going|what'?s up|good (morning|afternoon|evening)|thanks|thank you|bye|goodbye)\s*[!?.]*\s*$",
    re.IGNORECASE
)
OFF_TOPIC_RESPONSE = "Please ask another question relevant to Sampada's professional experience."

def ask(question, chat_history=None):
    if chat_history is None:
        chat_history = []

    if SMALLTALK_PATTERN.match(question):
        return OFF_TOPIC_RESPONSE

    stripped_question = re.sub(r"[^\w\s]", "", NAME_PATTERN.sub("", question)).strip()
    if not stripped_question:
        return OFF_TOPIC_RESPONSE

    q_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=stripped_question
    ).data[0].embedding

    cur.execute(
        """
        SELECT chunk, 1 - (embedding <=> %s::vector) AS similarity
        FROM chat_resume_embeddings
        ORDER BY similarity DESC
        """,
        (q_embedding,)
    )

    rows = cur.fetchall()
    if not rows or rows[0][1] < RELEVANCE_THRESHOLD:
        return OFF_TOPIC_RESPONSE

    context = "\n".join([row[0] for row in rows])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *chat_history[-4:],
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages
    )
    return response.choices[0].message.content