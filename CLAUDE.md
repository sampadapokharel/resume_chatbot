# Project Overview: Resume RAG Chatbot

A Streamlit-based chatbot that answers questions about **Sampada Pokharel's** professional experience using RAG (Retrieval-Augmented Generation) with PostgreSQL + pgvector (hosted on Supabase).

## Architecture

- **Frontend**: `app.py` — Streamlit chat UI with conversation history via `st.session_state`
- **Orchestration**: `src/chatbot.py` — question filtering, embedding lookup, and OpenAI response generation
- **Database**: `src/db.py` — psycopg2 connection + `get_relevant_chunks(embedding)` query
- **Utilities**: `src/utils.py` — `load_prompt()`, `strip_name_references()`, `is_smalltalk()`, `is_task_question()`
- **Ingestion**: `src/ingest.ipynb` — parses `resume.pdf` + `professional_summary.txt`, chunks, embeds, stores in Postgres
- **Vector DB**: PostgreSQL (Supabase) with `pgvector`; table `chat_resume_embeddings(id, chunk text, embedding vector(1536))`

## Key Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit entry point — imports `ask()` from `src.chatbot` |
| `src/chatbot.py` | Core RAG orchestration: filter → embed → vector search → GPT call |
| `src/db.py` | DB connection and `get_relevant_chunks(embedding)` |
| `src/utils.py` | `load_prompt`, `strip_name_references`, `is_smalltalk`, `is_task_question` |
| `src/ingest.ipynb` | One-time ingestion: PDF + summary → chunks → embeddings → Postgres |
| `prompts/system_prompt.txt` | GPT persona and guardrails for Sampada's profile |
| `prompts/intent_classifier_prompt.txt` | GPT judge prompt — classifies questions as RELEVANT or OFF_TOPIC |
| `professional_summary.txt` | Role-tailored summaries (AI Engineer, Solutions Architect, TPM, PM) — ingested |
| `.env` | API keys and DB credentials (not committed) |
| `requirements.txt` | Python dependencies |

## Environment Variables (`.env`)

```
OPENAI_API_KEY=...
POSTGRES_HOST=db.xxxx.supabase.co   # hostname only — NOT a full connection URL
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
POSTGRES_PORT=5432
```

> `POSTGRES_HOST` must be the bare hostname. Passing a full `postgresql://` URL will cause `could not translate host name` error.

## Database Setup (Supabase)

Run once in the Supabase SQL editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chat_resume_embeddings (
    id bigserial PRIMARY KEY,
    chunk text,
    embedding vector(1536)
);
```

## How It Works

1. User submits a question via `st.chat_input`
2. `is_smalltalk()` checks for greetings/smalltalk via regex — returns canned response if matched
3. `is_task_question()` calls `gpt-4.1-mini` with the intent classifier prompt (`max_tokens=5`, `temperature=0`) — returns canned response if OFF_TOPIC
4. `strip_name_references()` removes name tokens (Sampada, she, her) before embedding
5. Embeds cleaned question with `text-embedding-3-small`, queries Postgres for top chunks by cosine similarity
6. If top similarity < `0.17` (RELEVANCE_THRESHOLD), returns canned response
7. Passes `prompts/system_prompt.txt` + last 4 messages of history + retrieved context + question to `gpt-4.1-mini`
8. Response is displayed and appended to `st.session_state.messages`

## Adding or Editing Prompts

All prompts live in `prompts/`. Load them via `utils.load_prompt(filename, replacements)`:

```python
# With placeholder substitution
load_prompt("system_prompt.txt", {"{today}": "March 21, 2026"})

# Without substitution
load_prompt("intent_classifier_prompt.txt")
```

To add a new prompt, drop a `.txt` file in `prompts/` and call `load_prompt()`.

## Session Behavior

- Conversation history is stored in `st.session_state` — resets on page refresh or ~1 hour of inactivity
- Only the last 4 messages (2 turns) are sent to the LLM per request to control token usage

## Running

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Re-ingesting

After updating `resume.pdf`, `professional_summary.txt`, or `extended_context.txt`:
1. Restart the notebook kernel
2. Re-run all cells in `src/ingest.ipynb`
3. Optionally clear old rows first: `DELETE FROM chat_resume_embeddings;`

## Common Issues

- **`vector type not found`**: pgvector extension not enabled — run `CREATE EXTENSION IF NOT EXISTS vector;` in Supabase SQL editor
- **`ModuleNotFoundError: No module named 'src'`**: run `streamlit run app.py` from the project root, not from inside `src/`
- **`could not translate host name`**: `POSTGRES_HOST` is set to a full URL — use bare hostname only
