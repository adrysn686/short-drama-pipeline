# Short Drama Pipeline

Automated pipeline that turns a one-line prompt ("CEO falls in love with his bodyguard") into a 13-episode, vertical, AI-generated short drama — story bible, scripts, video, voice, subtitles, and a published post — with human review at three checkpoints.

Full architecture, tool comparisons, and rationale: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Status

Skeleton stage — structure and stubs only, no live API integrations wired yet. See the phase roadmap in the architecture doc (§12) for build order.

## Repo layout

- `api/` — FastAPI service exposing each pipeline step as an endpoint (story bible, scripts, video gen, voice gen, assembly, publishing, analytics). n8n calls into this service via HTTP.
- `n8n/workflows/` — exported n8n workflow JSON (orchestration layer).
- `db/migrations/` — Postgres schema for the asset registry (dramas, characters, locations, props, episodes, shots, publish queue, analytics).
- `docker-compose.yml` — Postgres + n8n + the API service.
- `storage/` — local media output (gitignored; swap for S3/R2 at scale).
- `docs/ARCHITECTURE.md` — the full technical architecture document.

## Setup

1. Copy `.env.example` to `.env` and fill in API keys (Anthropic, video-gen aggregator, ElevenLabs, Sync.so, platform publishing credentials).
2. `docker compose up -d` — starts Postgres (migrations auto-applied on first boot), n8n, and the API service.
3. n8n UI: http://localhost:5678 (basic auth from `.env`).
4. API service: http://localhost:8000 (interactive docs at `/docs`).

`scripts/setup.ps1` does steps 1-2 for you on Windows.

## Build order

Follow the phases in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#12-implementation-phases):

0. Manual dry run of one drama, no automation — validate the quality bar before building plumbing.
1. Automate story bible + script generation (Human Gate 1 stays manual).
2. Automate video/voice/assembly (Human Gate 2 stays manual).
3. Automate publishing (Human Gate 3 stays manual).
4. Wire the analytics feedback loop into story generation, scale up.
