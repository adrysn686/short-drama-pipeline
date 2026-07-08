"""Shot-level video generation — architecture doc §4.

Builds a prompt from the shot's script fields + the drama's style prefix +
locked asset Elements, submits to the primary/secondary video-gen provider,
and polls for completion.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/shots/{shot_id}/generate")
def generate_shot_video(shot_id: int):
    # TODO: build prompt, call services.video_gen.aggregator (Kling primary,
    # Seedance for simpler/cheaper shots), create a `jobs` row, return job id.
    raise NotImplementedError


@router.get("/jobs/{job_id}")
def get_video_job_status(job_id: int):
    # TODO: poll the provider job status, update `jobs`/`shots` on completion.
    raise NotImplementedError
