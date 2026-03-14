# AI Finance Robot

**Automates invoice recognition, voucher entry, three-way matching, and tax assistance for small businesses.**

Saves SMEs **~$50K/year** by replacing 3 finance roles: data entry, matching, and tax prep.

## Features

- **Invoice Recognition**: Upload PDFs or images; OCR + LLM extracts date, amount, vendor, line items.
- **Automatic Voucher Entry**: Generate accounting vouchers from extracted data; store in DB.
- **Three-Way Matching**: Compare invoice vs. purchase order vs. receipt; flag mismatches.
- **Tax Filing Assistance**: VAT/GST summaries, deduction flags, filing suggestions from extracted data.

## Tech Stack

- **Frontend**: React (Vite), Material-UI
- **Backend**: Python, FastAPI, SQLAlchemy (SQLite)
- **AI**: LangChain agents, Ollama (local) or OpenAI (fallback), FAISS RAG

## Quick Start (Local)

### Prerequisites

- Python 3.11+, Node 18+, [Ollama](https://ollama.ai) (for local LLM)
- Optional: Docker & Docker Compose

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Ollama (local LLM)

```bash
ollama pull llama3
```

Open **http://localhost:5173** (Vite) and **http://localhost:8000/docs** (API).

### Docker (all-in-one)

```bash
docker-compose up
```

Then open **http://localhost:3000** (frontend) and **http://localhost:8000** (backend).

## Project Structure

```
ai-finance-robot/
├── backend/          # FastAPI app, agents, RAG, DB
├── frontend/         # React + Vite + MUI
├── docker-compose.yml
└── README.md
```

## Environment

Copy `env.example` to `.env` and set as needed:

- `OLLAMA_HOST` — Ollama API URL (default `http://localhost:11434`)
- `DB_URL` — SQLite path (default `sqlite:///./app.db`)
- `OPENAI_API_KEY` — optional; if set, use OpenAI for LLM and embeddings instead of Ollama

## Demo Flow

1. Start backend and frontend (or `docker-compose up`).
2. Open the app; upload an invoice (PDF or image) on the Dashboard.
3. Go to **Invoices** to see the extracted list (date, vendor, amount).
4. Use **Match** to run three-way matching (invoice vs PO/receipt when provided).
5. Use **Tax** to generate a VAT/tax report and filing suggestions.

## Testing

- **Backend**: `cd backend && pytest`
- **Frontend**: `cd frontend && npm test`

## Contributing

1. Fork the repo; create a branch for your change.
2. Run tests and keep the codebase formatted.
3. Open a PR with a short description of the change.

## License

MIT — see [LICENSE](LICENSE).
