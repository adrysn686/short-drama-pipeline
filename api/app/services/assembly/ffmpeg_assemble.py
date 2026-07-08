"""FFmpeg-based episode assembly — architecture doc §7 step 6e.

Concatenates lip-synced shot clips, mixes in mood-matched BGM/SFX, and burns
in subtitles from services.assembly.subtitles, exporting a vertical
1080x1920 mp4.
"""


def assemble_episode(
    shot_clip_paths: list[str],
    bgm_path: str,
    sfx_paths: list[str],
    subtitle_segments: list[dict],
    output_path: str,
) -> str:
    # TODO: shell out to ffmpeg (concat shots -> mix audio -> burn subtitles
    # via the drawtext/subtitles filter), or use ffmpeg-python bindings.
    raise NotImplementedError
