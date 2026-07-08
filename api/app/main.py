"""FastAPI entrypoint. Each router exposes one pipeline stage from docs/ARCHITECTURE.md,
called by n8n via HTTP Request nodes."""
from fastapi import FastAPI

from .routers import analytics, assembly, assets, publish, scripts, story_bible, video, voice

app = FastAPI(title="Short Drama Factory API")

app.include_router(story_bible.router, prefix="/story-bible", tags=["story-bible"])
app.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
app.include_router(assets.router, prefix="/assets", tags=["assets"])
app.include_router(video.router, prefix="/video", tags=["video"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(assembly.router, prefix="/assembly", tags=["assembly"])
app.include_router(publish.router, prefix="/publish", tags=["publish"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


@app.get("/health")
def health():
    return {"status": "ok"}
