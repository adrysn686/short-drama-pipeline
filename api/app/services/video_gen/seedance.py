"""Seedance 2.0 client (cost/speed workhorse) — architecture doc §4.

Used for high-volume B-roll and simpler dialogue shots to control cost;
Kling remains primary for hero/dialogue shots that need the strongest
character-lock via Elements.
"""


def submit_shot(prompt: str, reference_image_urls: list[str]) -> str:
    # TODO: submit an image/text-to-video job via the fal.ai/PiAPI aggregator,
    # return a provider job id.
    raise NotImplementedError


def poll_job(job_id: str) -> dict:
    raise NotImplementedError
