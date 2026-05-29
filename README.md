# AudioNovel

Turn books into age-appropriate, multi-voice audio dramatizations.

Upload a PDF or TXT → an LLM pipeline simplifies it into a speaker-attributed script (`SPEAKER: line`) → ElevenLabs synthesizes per-character voices → you get an MP3 you can play in the browser. Every processed script is also embedded with Cohere and indexed in MongoDB Atlas Vector Search so you can find semantically similar books.

## Stack

- **Backend** – Python 3.11, Flask, JWT/bcrypt auth, MongoDB Atlas (in-memory `mongomock` fallback for local dev)
- **Frontend** – React 18 + TypeScript + Vite, Tailwind, React Query, React Router
- **AI services** – Cohere (`embed-english-v3.0`), ElevenLabs TTS, Qwen (text simplification, optional)

## Project layout

```
backend/
  app.py                       # Flask app, route definitions
  services/
    cohere_embeddings.py       # Cohere embed + Atlas $vectorSearch
    dialogue_generator.py      # ElevenLabs TTS pipeline
    text_processor.py          # Qwen multi-stage simplification
    audio_tag_enhancer.py      # Optional [happy]/[whisper] tag insertion
  routes/                      # auth, users, library blueprints
  models/                      # MongoDB models
  scripts/check_apis.py        # Health-check for Cohere/ElevenLabs/Qwen
  openapi.yaml                 # OpenAPI 3 spec (served at /docs)
  .env                         # COHERE_API_KEY, ELEVENLABS_API_KEY, ...
frontend/
  src/
    pages/                     # Home, Login, Register, Profile
    components/                # Upload, AudioPlayer, Navbar
    services/                  # audio.ts, auth.ts, library.ts, api.ts
    contexts/AuthContext.tsx
```

## Setup

### Prerequisites
- Python 3.11
- Node 18+
- (Optional) MongoDB Atlas cluster with a vector index named `vector_index` on field `embedding` (dimensions = 1024). Without it, the app uses an in-memory mock — embeddings still generate but `$vectorSearch` won't work.

### 1. Environment

Create `backend/.env`:

```env
COHERE_API_KEY=your_cohere_key
ELEVENLABS_API_KEY=your_elevenlabs_key
# Optional
QWEN_API_KEY=your_dashscope_key                # enables LLM text simplification
ELEVENLABS_DEFAULT_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
MONGODB_URI=mongodb+srv://...                  # enables real vector search
```

### 2. Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py                 # serves http://127.0.0.1:5001
```

Verify your API keys:

```bash
.venv/bin/python scripts/check_apis.py
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                   # serves http://localhost:5173
```

Open http://localhost:5173 in the browser.

## Key endpoints

| Endpoint                          | What it does                                           |
| --------------------------------- | ------------------------------------------------------ |
| `POST /upload`                    | Upload a PDF/TXT, kicks off background processing      |
| `GET  /status/<filename>`         | Poll processing status + final script & characters     |
| `POST /audio/generate-from-script`| Speak a `SPEAKER: line` script via ElevenLabs → MP3    |
| `POST /dialogue/convert`          | Speak an explicit `[{text, voice_id}]` list → MP3      |
| `POST /search`                    | Semantic search via Cohere + Atlas Vector Search       |
| `POST /api/auth/login` / `register` | JWT auth                                             |
| `GET  /api/library/items`         | Per-user saved library                                 |
| `GET  /openapi.yaml`, `/docs`     | OpenAPI 3 spec + Swagger UI                            |

## How Cohere is used

`backend/services/cohere_embeddings.py` wraps the official `cohere` SDK:

1. **Index time** – when a file finishes processing, `app.py` calls `generate_embedding(simplified_text, input_type="search_document")` and stores the resulting 1024-dim vector on the `processing_results` document.
2. **Query time** – `POST /search` calls `search_similar(query, collection)`, which embeds the query with `input_type="search_query"` and runs a MongoDB `$vectorSearch` aggregation against the `vector_index` index, returning the top-k matches with similarity scores.

Model: `embed-english-v3.0`, `truncate="END"` for inputs over 8000 chars.

## Notes

- `mongomock` (the local fallback DB) does **not** implement `$vectorSearch`, so `/search` only returns real results once `MONGODB_URI` points at Atlas.
- If `QWEN_API_KEY` is unset, `text_processor.py` falls back to a simple local rule-based simplifier so the rest of the pipeline still works.
- ElevenLabs makes one TTS request per script line, so long scripts can be slow and consume characters quickly. Consider trimming or paginating very long inputs.
