import os
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

with open("system_prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

register_vector(conn)
cur = conn.cursor()

def ask(question):

    q_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    ).data[0].embedding

    cur.execute(
        """
        SELECT chunk
        FROM resume_embeddings
        ORDER BY embedding <-> %s::vector
        """,
        (q_embedding,)
    )

    context = "\n".join([row[0] for row in cur.fetchall()])

    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content