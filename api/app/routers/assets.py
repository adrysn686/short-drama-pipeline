"""Asset registry endpoints (character/location/prop look-lock) — architecture doc §6.

Human Gate 2 sits after this stage: character/location/prop reference images
and their Kling Elements must be approved before any episode video generation
starts, since every episode reuses these by ID.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/{drama_id}/characters/{character_id}/reference-images")
def generate_character_reference_images(drama_id: int, character_id: int):
    # TODO: call services.video_gen (Seedream/Kling text-to-image) for the
    # character's appearance description, store URLs, create a locked Kling
    # Element, persist to `character_outfit_states`.
    raise NotImplementedError


@router.post("/{drama_id}/locations/{location_id}/reference-images")
def generate_location_reference_images(drama_id: int, location_id: int):
    # TODO: same pattern as above, persist to `locations`.
    raise NotImplementedError


@router.get("/{drama_id}/registry")
def get_asset_registry(drama_id: int):
    # TODO: return all locked characters/outfit-states/locations/props for a
    # drama, used by the video-gen prompt builder to reference Elements by ID.
    raise NotImplementedError
