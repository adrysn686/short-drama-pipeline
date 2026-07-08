"""Instagram Reels publishing via the Meta Graph API — architecture doc §8.

Uses the async two-step container model: create a media container, poll its
processing status, then publish once ready.
"""


def publish_reel(video_url: str, caption: str) -> str:
    # TODO: POST to /{ig-user-id}/media (media_type=REELS), poll
    # /{container-id}?fields=status_code, then POST /{ig-user-id}/media_publish.
    raise NotImplementedError
