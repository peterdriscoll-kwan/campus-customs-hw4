# Campus Customs

A customer website for Campus Customs (a New Haven Yale-merch shop) with a working, helpful chatbot: React + Vite + TypeScript front end, Python FastAPI backend, PydanticAI agent.

Full write-up of how the system works, decisions made, and evidence it works live: see `output/harness.md`, `output/design.md`, `output/usability.md`, and `output/app_check.html` (open that one directly in a browser — double-click it).

## 1. Get the data pack

Not included in this repo (per assignment instructions). Place it at:

```
data/campus_customs.db
data/products/           # product images referenced by the catalogue
```

relative to this folder (i.e. `hw4/data/...`, next to `backend/` and `frontend/`).

## 2. Configure your API key

```bash
cp .env.example .env
```

Then edit `.env` and set `PORTKEY_API_KEY` to your own Portkey key. This `.env` stays untracked (see `.gitignore`).

## 3. Run the backend

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`.

## 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (Vite's default) and talks to the backend at `http://localhost:8000` by default — no extra config needed. If you run the backend on a different port, set `VITE_API_BASE_URL` in a `frontend/.env` file to match.

## 5. Try it

- Browse products, create an account, log in.
- Chat with the assistant (bottom-right) — ask about stock, prices, or "show me some hoodies."
- Add something to your cart and visit `/cart` — checkout is intentionally not implemented (a class-project preview note explains this on that page).

## Project layout

```
hw4/
├── AI_prompts.md          # prompt log for every problem, in order
├── requirements.txt        # backend (Python) dependencies
├── .env.example
├── frontend/                # Vite React TypeScript app
├── backend/
│   ├── main.py               # FastAPI app — run with: uvicorn main:app --reload --port 8000
│   ├── agent.py               # PydanticAI agent wiring (models, tools, escalation)
│   ├── models.py               # Pydantic/PydanticAI structured types
│   ├── tools.py                  # agent tools (search, stock, alternatives)
│   ├── db.py, auth.py, guardrails.py, audit.py   # supporting backend modules
│   └── prompts/prompt.md          # agent system prompt (voice + safety rules)
└── output/
    ├── harness.md              # full system reference
    ├── design.md                # styling decisions
    ├── usability.md              # Problem 9 usability improvements
    ├── app_check.html              # live-app screenshots + captions (double-click to open)
    ├── app_check_images/
    └── audit_trail.json             # append-only agent tool-call log
```
