# Resume RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about Sampada Pokharel's professional experience. Built with OpenAI embeddings, pgvector for similarity search, and Streamlit for the UI.

## How it works

1. **Ingest** (`ingest.ipynb`) — Parses `resume.pdf` and `professional_summary.txt`, splits them into chunks, generates embeddings via OpenAI, and stores them in a PostgreSQL database with the pgvector extension.
2. **Query** (`chatbot.py`) — On each question, embeds the query, retrieves the most relevant chunks via cosine similarity, and passes them as context to GPT-4.1.
3. **UI** (`app.py`) — Streamlit chat interface with conversation history.

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL with [pgvector](https://github.com/pgvector/pgvector) extension (or use Supabase)
- OpenAI API key

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
POSTGRES_HOST=your_db_host         
POSTGRES_DB=postgres
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_PORT=5432
```

### Supabase setup (if using Supabase)

Run the following in the Supabase SQL editor before ingesting:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chat_resume_embeddings (
    id bigserial PRIMARY KEY,
    chunk text,
    embedding vector(1536)
);
```

### Ingest the resume

Run all cells in `ingest.ipynb`. This loads `resume.pdf` and `professional_summary.txt`, chunks and embeds them, and inserts the results into the `chat_resume_embeddings` table.

> **Note:** Restart the notebook kernel after any `.env` changes before running.

### Run the app

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Chatbot behavior

- Answers questions about Sampada's professional experience, skills, and background only
- Handles follow-up questions using conversation history (last 4 messages / 2 turns)
- Filters out smalltalk and off-topic questions
- Session resets on page refresh or after ~1 hour of inactivity

## Key design decisions

- **Relevance threshold** (`RELEVANCE_THRESHOLD = 0.17`) — queries below this cosine similarity score return an off-topic response instead of a hallucinated answer
- **Every question hits the DB** — all questions go through vector retrieval so context is always grounded in the resume
- **Context cap** — only the last 4 messages are sent to the LLM to control token usage
- **Source documents** — both `resume.pdf` and `professional_summary.txt` are embedded; update either and re-run `ingest.ipynb` to refresh
