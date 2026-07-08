"""Whisper-based transcription for subtitle timing — architecture doc §9.

CapCut has no public API for server-side captioning, so subtitle burn-in is
done via Whisper (timing) + FFmpeg (rendering) instead of routing through it.
"""


def transcribe(audio_path: str) -> list[dict]:
    # TODO: call the Whisper API, return word/segment-level timestamps for
    # ffmpeg_assemble to render as burned-in captions.
    raise NotImplementedError
