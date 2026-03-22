import os
import psycopg2
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    sslmode="require"
)
register_vector(conn)
cur = conn.cursor()


def get_relevant_chunks(embedding: list) -> list[tuple]:
    cur.execute(
        """
        SELECT chunk, 1 - (embedding <=> %s::vector) AS similarity
        FROM chat_resume_embeddings
        ORDER BY similarity DESC
        """,
        (embedding,)
    )
    return cur.fetchall()
