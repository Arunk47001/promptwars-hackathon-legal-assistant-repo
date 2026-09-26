# Namma Nyaya

Namma Nyaya ("Our Justice") is a GenAI legal companion built for Bengaluru,
India. Renters, job-seekers, and first-time signers upload a rental
agreement or offer letter (photo, scan, or PDF, in English or Kannada) and
get back a plain-language explanation, clause-by-clause and legal-view
breakdowns, red-flag detection against known local pitfalls (excessive
deposits, one-sided lock-ins, unenforceable non-competes), a document
compare/diff tool, an old-to-new criminal law section mapper (IPC/CrPC →
BNS/BNSS), and a "what do I do now" navigator with step-by-step playbooks
for common situations. Built as a hackathon MVP slice — see
`.squad/specification/namma-nyaya.md`, `.squad/planner/namma-nyaya.md`, and
`.squad/task/namma-nyaya.md` for the full spec/plan/task-breakdown chain
this build was implemented from.

## Live deployment

- **Frontend**: https://namma-nyaya-frontend.vercel.app
- **Backend API**: https://namma-nyaya-backend.onrender.com (`/health`, `/docs`)

Hosted on Vercel (frontend) + Render free tier (backend). The backend spins
down after ~15 min idle and takes 30-50s to wake on the first request after
that. See `.squad/deploy/namma-nyaya.md` for full deploy notes, including the
open risk that the Gemini API key's free-tier daily quota (20 requests/day
per model) is tight for a live demo.

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
