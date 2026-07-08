"""ElevenLabs TTS client — architecture doc §5.

Voice assignment is not re-decided per drama: each character's voice_profile
tag (age/gender/register) maps to a pre-curated pool of voice ids picked once
by a human during setup (see docs/ARCHITECTURE.md §5).
"""


def synthesize(text: str, voice_id: str, emotion: str) -> bytes:
    # TODO: call ElevenLabs' Eleven Multilingual TTS with the given voice id
    # and emotion/style parameter, return audio bytes (or a storage URL).
    raise NotImplementedError
