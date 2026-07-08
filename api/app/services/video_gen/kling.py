"""Kling 3.0 client (primary video generator) — architecture doc §4.

Character/location/prop consistency comes from Kling's "Elements" feature:
train once on reference images, then reference the Element by id in every
shot prompt instead of re-describing the subject each time.
"""


def create_element(name: str, reference_image_urls: list[str]) -> str:
    # TODO: call the Kling (via fal.ai/PiAPI aggregator) Elements endpoint,
    # return the element id to store in the asset registry.
    raise NotImplementedError


def submit_shot(prompt: str, element_ids: list[str]) -> str:
    # TODO: submit an image/text-to-video job referencing the given elements,
    # return a provider job id.
    raise NotImplementedError


def poll_job(job_id: str) -> dict:
    # TODO: return {"status": ..., "video_url": ...} once complete.
    raise NotImplementedError
