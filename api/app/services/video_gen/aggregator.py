"""Unified job-submit/poll interface over the video-gen providers — architecture doc §4.

Routes hero/dialogue shots to Kling, cheaper B-roll/establishing shots to
Seedance, so callers don't need to know which provider handled a given shot.
"""
from . import kling, seedance


def submit_shot(prompt: str, element_ids: list[str], tier: str = "primary") -> str:
    # TODO: tier == "primary" -> kling.submit_shot, "secondary" -> seedance.submit_shot.
    # Returns a provider-agnostic job id (store which provider owns it).
    raise NotImplementedError


def poll_job(job_id: str) -> dict:
    # TODO: look up which provider owns this job id (via the `jobs` table),
    # poll accordingly.
    raise NotImplementedError
