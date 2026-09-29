# VivaForge

**AI-Powered Video-to-Learning, Viva & Knowledge-Gap Platform**

Most tools answer "what was in this video?" VivaForge additionally asks:
*can you explain it, did you actually understand it, what are you weak
in, and what should you revise next?*

Long-form lecture content (video, audio, PDF, PPTX) goes in. Structured
notes, source-grounded viva questions, an adaptive AI viva simulator, a
knowledge graph, flashcards, and a personalized revision plan come out.

---

## Architecture

```
Frontend (Next.js/TS/Tailwind)
        ↓
Backend API (FastAPI)
        ↓
Auth (JWT + bcrypt-hashed passwords)
        ↓
Content Processing (FFmpeg → faster-whisper / pypdf / python-pptx → chunking)
        ↓
Embeddings (sentence-transformers, local, no API cost) → Chroma vector store
        ↓
RAG retrieval — one reusable retrieve_context() function
        ↓
LLM layer (Groq API — free tier, structured + Pydantic-validated JSON, prompts in app/ai/prompts)
        ↓
PostgreSQL (relational data) + local artifact storage (PDFs, JSON exports)
        ↓
Frontend: dashboard / viva / knowledge graph / revision / flashcards
```

**Why PostgreSQL, not MongoDB:** viva sessions, questions, answers, and
per-concept mastery scores are inherently relational — the dashboard's
"weak concepts" view is a join across mastery -> concept -> content.
Postgres + SQLAlchemy gives referential integrity and clean migrations;
the "knowledge graph" is just concept/edge tables queried relationally.

**Why Chroma, not FAISS:** Chroma persists to disk with metadata
filtering (by `content_id`) built in — every retrieval query needs to be
scoped to one piece of content. `app/rag/retriever.py`'s
`retrieve_context()` is the single seam every feature calls, so the
backing store can be swapped later without touching feature code.

**Why local embeddings (sentence-transformers), not a paid API:** free,
no key required, no per-request cost, and more than accurate enough for
chunk retrieval at this scale (section 20: cost control).

---

## Folder structure

```
vivaforge/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (auth, content, viva, graph, knowledge, flashcards, explain_back, revision_video)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response + LLM-output validation schemas
│   │   ├── services/       # business logic (one file per feature)
│   │   ├── ai/prompts/     # LLM prompt templates, one file per task
│   │   ├── ai/llm_client.py   # the one function every LLM call goes through
│   │   ├── rag/             # chunking, embeddings, vector store, retriever
│   │   ├── media/            # FFmpeg, Whisper, PDF/PPTX text extraction
│   │   ├── pdf/                # ReportLab viva-PDF generation
│   │   ├── utils/
│   │   ├── config.py           # env-driven settings
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   └── main.py                # FastAPI app entrypoint
│   ├── alembic/                     # DB migrations (0001_initial_schema.py = full schema)
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js App Router pages (see route list below)
│   ├── components/          # Navbar, StatusBadge, MasteryBar
│   ├── lib/                   # typed axios client
│   ├── services/                # one file per API group
│   └── types/
├── docker-compose.yml       # local dev: Postgres + backend in one command
├── render.yaml                # backend deployment blueprint
├── .env.example
└── .gitignore
```

## Frontend routes

| Route | What it does |
|---|---|
| `/` | Landing page |
| `/login`, `/register` | Auth |
| `/dashboard` | Content list, knowledge mastery bars, today's revision |
| `/upload` | Upload + live processing-status polling |
| `/content/[id]` | Workspace: status, start viva, download viva PDF, tab links |
| `/content/[id]/summary` | Structured summary |
| `/content/[id]/concepts` | Concepts with source grounding |
| `/content/[id]/graph` | Knowledge graph (expandable concept list + relationships) |
| `/content/[id]/flashcards` | Flip/next/prev, mark mastered/difficult |
| `/content/[id]/explain-back` | Explain-It-Back mode |
| `/content/[id]/revision-video` | Revision reel (storyboard — see Known Limitations) |
| `/viva/[sessionId]` | Live adaptive AI viva, with browser speech-to-text |
| `/revision` | Personalized revision plan |
| `/profile` | Account + overall knowledge profile |
| `/settings` | Account email (honest placeholder — see Known Limitations) |

## Backend API

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/auth/register`, `/login`, `GET /me` | Auth |
| `POST /api/v1/content/upload` | Upload (validates type/size) |
| `GET /api/v1/content`, `GET /content/{id}` | List/get |
| `POST /api/v1/content/{id}/process` | Kick off the background pipeline |
| `GET /api/v1/content/{id}/status` | Poll processing status |
| `GET /api/v1/content/{id}/summary`, `/concepts`, `/graph`, `/flashcards`, `/revision-video` | Generated study material |
| `POST /api/v1/content/{id}/viva/generate` | Viva PDF (ReportLab) |
| `GET /api/v1/artifacts/{id}` | Download any generated artifact |
| `POST /api/v1/viva/session`, `POST /viva/session/{id}/answer` | Adaptive AI viva |
| `GET /api/v1/explain-back/{id}/prompt`, `POST /explain-back/evaluate` | Explain-It-Back |
| `GET /api/v1/knowledge-profile`, `/revision-plan`, `POST /revision-plan/regenerate` | Knowledge gaps |

---

## Environment variables

See `.env.example`. Copy to `backend/.env` and fill in real values —
**never commit a file with real secrets.**

Required to run anything beyond `/health`:
- `JWT_SECRET_KEY` — `python -c "import secrets; print(secrets.token_urlsafe(48))"`
- `DATABASE_URL` — a running PostgreSQL instance
- `GROQ_API_KEY` — required from summary generation onward (every AI feature). Get a free key at https://console.groq.com/keys — no credit card required.

## Local development

**Prerequisites:** Python 3.11+, Node.js 18+, PostgreSQL 15+ (or Docker), `ffmpeg` on PATH.

### Option A — Docker (recommended, starts Postgres + backend together)
```bash
cp .env.example backend/.env   # then edit backend/.env with real values
docker compose up --build
```
Verify: `curl http://localhost:8000/health`

### Option B — manual
```bash
# Database (if not using Docker)
docker run --name vivaforge-db -e POSTGRES_USER=vivaforge -e POSTGRES_PASSWORD=vivaforge \
  -e POSTGRES_DB=vivaforge -p 5432:5432 -d postgres:16

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # edit with real values
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

### Running tests
```bash
cd backend
pytest -v
```
Tests cover: password hashing, JWT issuing/expiry/tampering, registration/login,
transcript/page chunking, LLM-output schema validation (malformed JSON rejected),
knowledge-gap classification, revision-plan prioritization, upload validation.
They run against in-memory SQLite — no Postgres or API keys needed.

---

## Deployment

- **Backend:** `render.yaml` blueprint — connect the repo in Render's dashboard,
  set `JWT_SECRET_KEY` and `GROQ_API_KEY` manually (never in the blueprint file).
  Render's free web-service tier has no persistent disk by default — Chroma's
  index and uploaded files will be wiped on every redeploy unless you add a paid
  disk. Fine for a portfolio demo; flag this if you rely on it staying warm.
- **Frontend:** deploy `frontend/` to Vercel, set `NEXT_PUBLIC_API_BASE_URL` to
  your deployed backend URL.
- **Database:** Render's free Postgres (in the blueprint) or any hosted Postgres.

---

## Feature checklist — implemented vs. planned

| # | Feature | Status |
|---|---|---|
| 1 | Upload video/audio/PDF/PPTX | Implemented |
| 2 | AI-generated structured summary | Implemented |
| 3 | Topic-wise notes, definitions, examples | Implemented |
| 4 | Viva preparation PDF | Implemented |
| 5 | Easy/medium/hard question chains | Implemented |
| 6 | Follow-up questions | Implemented (in PDF + adaptive session) |
| 7 | Source references/timestamps | Implemented |
| 8 | Short revision video | Honest fallback: narrated storyboard (script + subtitles + source), not a rendered .mp4. See below. |
| 9 | Concept/knowledge graph | Implemented (list-based UI, not a force-directed canvas) |
| 10 | Flashcards | Implemented |
| 11 | AI Viva Simulator | Implemented, adaptive difficulty + concept targeting |
| 12 | Speech-based viva answering | Implemented via browser Web Speech API (Chrome/Edge only) |
| 13 | Answer evaluation | Implemented, LLM + Pydantic-validated, never keyword matching |
| 14 | Explain-It-Back mode | Implemented |
| 15 | Knowledge-gap detection | Implemented |
| 16 | Personalized revision plan | Implemented |
| 17 | Learning progress dashboard | Implemented |
| 18 | Public video URL ingestion | Not implemented — file upload only |
| 19 | Settings (notifications, export, deletion) | Not implemented — honest placeholder in UI |

## Known limitations

- **Revision video is a storyboard, not a rendered video file.** Section 19 of
  the original spec explicitly permits this fallback when full automatic video
  generation is unreliable — implementing real clip extraction + TTS + subtitle
  burn-in reliably was out of scope here; faking a "video" that's actually a
  static export would have violated the "don't fake AI-generated video" rule.
- **This codebase has been syntax-checked (`py_compile`) but not executed
  end-to-end** — the sandbox it was built in has no internet access, so
  `pip install`, `npm install`, `pytest`, and a live server run have not
  happened yet. Run it locally per the steps above; if something breaks,
  the traceback is the fastest way to get it fixed.
- Whisper transcription, LLM calls, and embeddings need real API
  keys/model downloads — none of that ran during development.
- No public video URL ingestion (YouTube etc.) — only direct file upload.
- Knowledge graph renders as an expandable list, not a force-directed
  canvas — a deliberate simplicity trade-off (section 33: don't overengineer),
  not a missing feature; all the same data (nodes, edges, mastery) is there.
- No rate limiting or CSRF protection beyond CORS + JWT — fine for a
  portfolio demo, would need hardening for real users.

## Future improvements

- Real revision-video rendering (moviepy/ffmpeg clip assembly + TTS)
- Public video URL ingestion (yt-dlp)
- Force-directed knowledge graph visualization
- Rate limiting, refresh tokens, email verification
- Multi-user classroom/cohort features
