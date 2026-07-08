"""Story Bible Agent endpoint — architecture doc §2.

Takes the user's one-line prompt and returns a structured StoryBible via the
Claude API (see services/claude_client.py). This is the step gated by Human
Gate 1 in the pipeline: n8n should pause for approval before triggering the
Character Bible stage.
"""
from fastapi import APIRouter

from ..schemas.story_bible import StoryBible

router = APIRouter()


@router.post("/generate", response_model=StoryBible)
def generate_story_bible(prompt: str) -> StoryBible:
    # TODO: call services.claude_client with the story-bible system prompt +
    # StoryBible schema as a forced tool-use output, persist to `dramas`.
    raise NotImplementedError
