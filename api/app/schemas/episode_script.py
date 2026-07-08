"""Pydantic models for the per-episode Script Agent's structured output — architecture doc §3.

Each Shot doubles as a video-gen prompt source and a TTS script line, so the
schema is designed once and consumed twice downstream.
"""
from pydantic import BaseModel


class Shot(BaseModel):
    shot_number: int
    dialogue: str | None = None
    narration: str | None = None
    camera_direction: str
    character_emotion: str
    facial_expression: str
    environment_description: str
    sfx_suggestion: str | None = None
    bgm_mood: str | None = None


class Scene(BaseModel):
    scene_number: int
    location: str
    time_of_day: str
    shots: list[Shot]


class EpisodeScript(BaseModel):
    episode_number: int
    scenes: list[Scene]
    estimated_runtime_sec: int
