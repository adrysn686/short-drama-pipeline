"""Sync.so lip-sync client — architecture doc §5.

Joins the video branch (Kling/Seedance clip) and the voice branch (ElevenLabs
audio) of the pipeline into one lip-synced shot.
"""


def lipsync(video_url: str, audio_url: str) -> str:
    # TODO: submit a lip-sync job, poll until complete, return the resulting
    # clip URL.
    raise NotImplementedError
