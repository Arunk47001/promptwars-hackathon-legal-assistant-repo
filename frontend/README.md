# Namma Nyaya — Frontend (Next.js)

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_BASE_URL if backend isn't on :8000
npm run dev
```

Requires the backend (see `../backend/README.md`) running and reachable at
`NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000`).

## Build / lint

```bash
npm run build   # verified clean in this build pass
npm run lint    # verified clean in this build pass
```

## Pages

- `/` — document upload, side-by-side document viewer + three-level
  explanation panel (EN/KN + gist/clause/legal-view toggles), red-flag
  highlighting, and a Q&A chat panel (C17, C18, C20).
- `/compare` — upload two documents and view C12's structured diff (C19).
- `/law-mapping` — standalone IPC/CrPC/Evidence Act ↔ BNS/BNSS/BSA lookup,
  no document required (C21).
- `/navigator` — pick a recognized situation and generate/download a
  playbook draft (C22).

## Guardrail UX (C23)

- `components/DisclaimerBanner.tsx` renders on every page.
- `components/LegalAidRedirect.tsx` renders in place of explanation/Q&A
  content whenever the backend's guardrail metadata reports
  `high_stakes: true`.

## Known limitations

- All API calls are live against the backend (never mocked in the frontend
  code) — but the backend itself may be running in Gemini **offline mock
  mode** if no API key is configured server-side, in which case explanation/
  Q&A text will visibly say `[MOCK ... offline mode]`. This is a backend
  concern (see `../backend/README.md`), not a frontend bug.
- No automated frontend test suite (e.g. Playwright/Jest) was added in this
  pass — verification here was `npm run build` (type-checked, succeeds),
  `npm run lint` (clean), and a manual local run against the live backend
  (`/health`, all four routes render, uploaded-document flow exercised via
  the API directly). A full click-through browser rehearsal (C24) should
  still be done by the team before a live demo.
