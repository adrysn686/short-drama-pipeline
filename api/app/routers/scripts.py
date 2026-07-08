"""Per-episode Script Agent endpoint — architecture doc §3."""
from fastapi import APIRouter

from ..schemas.episode_script import EpisodeScript

router = APIRouter()


@router.post("/generate/{drama_id}/{episode_number}", response_model=EpisodeScript)
def generate_episode_script(drama_id: int, episode_number: int) -> EpisodeScript:
    # TODO: load the StoryBible + prior episode scripts for continuity, call
    # services.claude_client, validate estimated_runtime_sec is 60-90s (kick
    # back for a trim pass if not), persist to `scenes`/`shots`.
    raise NotImplementedError
