# Resume RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about Sampada Pokharel's professional experience. Built with OpenAI embeddings, pgvector for similarity search, and Streamlit for the UI.

## How it works

1. **Ingest** (`ingest.ipynb`) — Parses the resume PDF, splits it into chunks, generates embeddings via OpenAI, and stores them in a PostgreSQL database with the pgvector extension.
2. **Query** (`chatbot.py`) — On each question, embeds the query, retrieves the most relevant resume chunks via cosine similarity, and passes them as context to GPT-4.1.
3. **UI** (`app.py`) — Streamlit interface for asking questions.

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL with [pgvector](https://github.com/pgvector/pgvector) extension installed
- OpenAI API key

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
POSTGRES_HOST=localhost
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
```

### Ingest the resume

Run the `ingest.ipynb` notebook to parse `resume.pdf`, generate embeddings, and populate the `resume_embeddings` table in PostgreSQL.

### Run the app

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

