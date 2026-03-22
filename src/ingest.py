import os
import re
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from openai import OpenAI

load_dotenv()

client = OpenAI()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
conn.autocommit = True
register_vector(conn)
cur = conn.cursor()


def load_documents() -> list:
    docs = PyPDFLoader("resume.pdf").load()
    with open("professional_summary.txt", "r") as f:
        docs.append(Document(page_content=f.read(), metadata={"source": "professional_summary.txt"}))
    return docs


def chunk_documents(docs: list) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    return splitter.split_documents(docs)


def embed_and_insert(chunks: list) -> None:
    for i, chunk in enumerate(chunks, 1):
        text = re.sub(r"[^\w\s]", "", chunk.page_content).strip()
        try:
            embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            ).data[0].embedding
            cur.execute(
                "INSERT INTO chat_resume_embeddings (chunk, embedding) VALUES (%s, %s)",
                (text, embedding)
            )
            print(f"Inserted chunk {i}/{len(chunks)}")
        except Exception as e:
            print(f"Skipped chunk {i} due to error: {e}")
            conn.rollback()


if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)
    embed_and_insert(chunks)
    print("Ingestion complete.")
