"""Pydantic models for the Story Bible Agent's structured output — architecture doc §2.

Passed to the Claude API as a forced tool-use schema so the response is
always a validated instance of StoryBible, never free text to parse.
"""
from pydantic import BaseModel


class Character(BaseModel):
    name: str
    role: str
    appearance: str
    personality: str
    arc_start: str
    arc_end: str
    voice_profile: str


class Relationship(BaseModel):
    character_a: str
    character_b: str
    dynamic: str
    evolution: str


class Setting(BaseModel):
    time_and_place: str
    visual_style: str


class EpisodeOutline(BaseModel):
    episode_number: int
    synopsis: str
    emotional_beat: str
    cliffhanger: str
    runtime_target_sec: int = 75


class Twist(BaseModel):
    episode_number: int
    description: str
    foreshadowing: str


class StoryBible(BaseModel):
    title: str
    genre: str
    tropes: list[str]
    characters: list[Character]
    relationships: list[Relationship]
    setting: Setting
    overall_plot: str
    episodes: list[EpisodeOutline]
    major_twists: list[Twist]
    final_payoff: str
