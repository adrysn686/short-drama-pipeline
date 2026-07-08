"""YouTube Shorts publishing via the YouTube Data API v3 — architecture doc §8.

Supports native scheduling via publishAt. Default quota is 10,000 units/day
(~1,600/upload, ~6 uploads/day/app) — request a quota increase before
scaling past prototype volume.
"""


def upload_short(video_path: str, title: str, description: str, publish_at: str | None = None) -> str:
    # TODO: call videos.insert with status.privacyStatus="private" and
    # status.publishAt set for scheduled release, or "public" for immediate.
    raise NotImplementedError
