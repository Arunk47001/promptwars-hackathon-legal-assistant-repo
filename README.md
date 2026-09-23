# Namma Nyaya

A GenAI legal companion for Bengaluru — hackathon MVP slice covering rental
agreements and offer letters for migrant tech professionals. See
`.squad/specification/namma-nyaya.md`, `.squad/planner/namma-nyaya.md`, and
`.squad/task/namma-nyaya.md` for the full spec/plan/task-breakdown chain
this build was implemented from.

- `backend/` — Python/FastAPI, channel-agnostic resource-oriented API
  (`/documents`, `/sessions`, `/actions`), tiered Gemini wrappers, PII
  masking, red-flag/compare/Q&A/law-mapping/navigator logic. See
  `backend/README.md`.
- `frontend/` — Next.js/React web app consuming the backend API. See
  `frontend/README.md`.

Coder-lane implementation status: `.squad/coder/namma-nyaya.md`.
Deploy-lane tasks (Render/Vercel provisioning) are out of scope for this
part of the build — see `.squad/task/namma-nyaya.md`'s Deploy tasks section,
owned separately.

## Quick start (local, offline mock mode — no API key needed)

```bash
# Backend
cd backend
python -m venv .venv && ./.venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Then open http://localhost:3000. The backend runs in offline Gemini mock
mode by default (no key required) — see `backend/README.md` for how to
switch to live Gemini calls, and `backend/docs/c4_ocr_spike_log.md` for the
still-outstanding day-1 OCR go/no-go spike that must be run manually before
trusting the ingestion pipeline on real Kannada documents.
