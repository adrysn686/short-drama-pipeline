"""Analytics feedback loop — architecture doc §8.

Polls each platform's Insights/Analytics API and feeds a "what worked"
summary back into the next Story Bible Agent prompt.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/collect/{queue_id}")
def collect_analytics(queue_id: int):
    # TODO: call the platform-specific insights API for this published post,
    # persist to `analytics_events`.
    raise NotImplementedError


@router.get("/{drama_id}/summary")
def get_performance_summary(drama_id: int):
    # TODO: aggregate analytics_events across a drama's episodes into a short
    # text summary to prepend to the next Story Bible prompt.
    raise NotImplementedError
