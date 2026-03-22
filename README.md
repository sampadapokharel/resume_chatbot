# Resume RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about Sampada Pokharel's professional experience. Built with OpenAI embeddings, pgvector for similarity search, and Streamlit for the UI.

## How it works

1. **Ingest** (`src/ingest.ipynb`) — Parses `resume.pdf` and `professional_summary.txt`, splits them into chunks, generates embeddings via OpenAI, and stores them in a PostgreSQL database with the pgvector extension.
2. **Filter** (`src/utils.py`) — Each question is checked for smalltalk and classified by a GPT judge to block off-topic or task-oriented questions before hitting the DB.
3. **Query** (`src/chatbot.py`) — Embeds the query, retrieves the most relevant chunks via cosine similarity (`src/db.py`), and passes them as context to GPT-4.1-mini.
4. **UI** (`app.py`) — Streamlit chat interface with conversation history.

## Project structure

```
rag/
├── app.py                          # Streamlit entry point
├── prompts/
│   ├── system_prompt.txt           # GPT persona and guardrails
│   └── intent_classifier_prompt.txt # Off-topic question classifier
├── src/
│   ├── chatbot.py                  # Core RAG orchestration
│   ├── db.py                       # DB connection and vector query
│   ├── utils.py                    # Prompt loading, filtering helpers
│   └── ingest.ipynb                # One-time ingestion script
├── resume/                         # Source resume files
├── professional_summary.txt        # Role-tailored summaries (ingested)
├── requirements.txt
└── .env                            # API keys and DB credentials (not committed)
```

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

> `POSTGRES_HOST` must be the bare hostname, not a full `postgresql://` URL.

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

Run all cells in `src/ingest.ipynb`. This loads `resume.pdf` and `professional_summary.txt`, chunks and embeds them, and inserts the results into the `chat_resume_embeddings` table.

> **Note:** Restart the notebook kernel after any `.env` changes before running.

### Run the app

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Chatbot behavior

- Answers questions about Sampada's professional experience, skills, and background only
- Filters smalltalk and off-topic questions via regex + GPT intent classifier
- Blocks task-oriented questions (e.g. "write a sorting algorithm") even when framed around her background
- Handles follow-up questions using conversation history (last 4 messages / 2 turns)
- Session resets on page refresh or after ~1 hour of inactivity

## Key design decisions

- **GPT intent classifier** — a `gpt-4.1-mini` judge call with `max_tokens=5` classifies each question as `RELEVANT` or `OFF_TOPIC` before any DB query, preventing the LLM from hallucinating CS lessons framed around Sampada's background
- **Relevance threshold** (`RELEVANCE_THRESHOLD = 0.17`) — queries below this cosine similarity score return an off-topic response instead of a hallucinated answer
- **Every question hits the DB** — all questions go through vector retrieval so context is always grounded in the resume
- **Context cap** — only the last 4 messages are sent to the LLM to control token usage
- **Source documents** — both `resume.pdf` and `professional_summary.txt` are embedded; update either and re-run `src/ingest.ipynb` to refresh
