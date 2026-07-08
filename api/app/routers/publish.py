"""Publishing — architecture doc §8.

Handles caption/hashtag/thumbnail generation and per-platform posting,
including the TikTok publish-queue workaround (no native scheduling in its
Content Posting API — see architecture doc §9).
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/episodes/{episode_id}/prepare")
def prepare_episode_for_publish(episode_id: int):
    # TODO: generate caption/hashtags/thumbnail via Claude, write to
    # `publish_queue` with status=pending_review (Human Gate 3).
    raise NotImplementedError


@router.post("/queue/{queue_id}/publish")
def publish_queued_episode(queue_id: int):
    # TODO: dispatch to services.publish.{tiktok,instagram,youtube} based on
    # `platform`, handle each API's async container/poll pattern.
    raise NotImplementedError
