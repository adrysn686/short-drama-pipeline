"""Episode assembly — architecture doc §7 step 6e.

Concatenates lip-synced shots, mixes BGM/SFX, transcribes with Whisper for
word-level timing, and burns in subtitles via FFmpeg (CapCut has no public
API for this — see architecture doc §9).
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/episodes/{episode_id}/assemble")
def assemble_episode(episode_id: int):
    # TODO: call services.assembly.ffmpeg_assemble, which internally calls
    # services.assembly.subtitles (Whisper) for caption timing.
    raise NotImplementedError
