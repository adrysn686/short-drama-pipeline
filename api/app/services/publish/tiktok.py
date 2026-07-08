"""TikTok Content Posting API client — architecture doc §8-9.

The API has no scheduled_publish_time param, so scheduling is implemented as
an internal queue (see the `publish_queue` table) fired by an n8n Cron node
at the target time via an immediate-publish call.
"""


def publish_video(video_path: str, caption: str, hashtags: list[str]) -> str:
    # TODO: call the Content Posting API's init + upload + publish endpoints,
    # return the platform post id.
    raise NotImplementedError
