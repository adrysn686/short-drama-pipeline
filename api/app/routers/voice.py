"""TTS + lip sync — architecture doc §5."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/shots/{shot_id}/tts")
def generate_shot_tts(shot_id: int):
    # TODO: call services.voice.elevenlabs_client with the shot's dialogue,
    # the character's assigned voice_id, and character_emotion as the
    # style/emotion parameter.
    raise NotImplementedError


@router.post("/shots/{shot_id}/lipsync")
def lipsync_shot(shot_id: int):
    # TODO: call services.voice.synclabs_client with the shot's video asset +
    # TTS audio asset, store the resulting lip-synced clip URL.
    raise NotImplementedError
