-- Asset registry + pipeline state schema — architecture doc §6-8.
-- Applied automatically on first Postgres container boot (docker-entrypoint-initdb.d).

CREATE TABLE dramas (
    id              SERIAL PRIMARY KEY,
    prompt          TEXT NOT NULL,
    title           TEXT,
    genre           TEXT,
    tropes          JSONB DEFAULT '[]',
    setting         JSONB DEFAULT '{}',
    overall_plot    TEXT,
    final_payoff    TEXT,
    status          TEXT NOT NULL DEFAULT 'pending_bible', -- pending_bible, bible_review, in_production, published, archived
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE characters (
    id              SERIAL PRIMARY KEY,
    drama_id        INTEGER NOT NULL REFERENCES dramas(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    role            TEXT,
    appearance      TEXT,
    personality     TEXT,
    arc_start       TEXT,
    arc_end         TEXT,
    voice_profile   TEXT,
    voice_id        TEXT, -- resolved ElevenLabs voice id, assigned from the curated pool
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- A character can have multiple locked "looks" across the story (e.g. work
-- uniform vs. gala dress after the reveal) — each is its own Kling Element.
CREATE TABLE character_outfit_states (
    id                      SERIAL PRIMARY KEY,
    character_id            INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    label                   TEXT NOT NULL,
    kling_element_id        TEXT,
    reference_image_urls    TEXT[] DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE locations (
    id                      SERIAL PRIMARY KEY,
    drama_id                INTEGER NOT NULL REFERENCES dramas(id) ON DELETE CASCADE,
    name                    TEXT NOT NULL,
    description             TEXT,
    kling_element_id        TEXT,
    reference_image_urls    TEXT[] DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE props (
    id                      SERIAL PRIMARY KEY,
    drama_id                INTEGER NOT NULL REFERENCES dramas(id) ON DELETE CASCADE,
    name                    TEXT NOT NULL,
    description             TEXT,
    kling_element_id        TEXT,
    reference_image_urls    TEXT[] DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE relationships (
    id              SERIAL PRIMARY KEY,
    drama_id        INTEGER NOT NULL REFERENCES dramas(id) ON DELETE CASCADE,
    character_a_id  INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    character_b_id  INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    dynamic         TEXT,
    evolution       TEXT
);

CREATE TABLE episodes (
    id                  SERIAL PRIMARY KEY,
    drama_id            INTEGER NOT NULL REFERENCES dramas(id) ON DELETE CASCADE,
    episode_number      INTEGER NOT NULL,
    synopsis            TEXT,
    emotional_beat      TEXT,
    cliffhanger         TEXT,
    runtime_target_sec  INTEGER NOT NULL DEFAULT 75,
    estimated_runtime_sec INTEGER,
    final_video_url     TEXT,
    status              TEXT NOT NULL DEFAULT 'pending_script', -- pending_script, scripted, in_production, assembled, qa_review, ready_to_publish, published
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (drama_id, episode_number)
);

CREATE TABLE twists (
    id              SERIAL PRIMARY KEY,
    drama_id        INTEGER NOT NULL REFERENCES dramas(id) ON DELETE CASCADE,
    episode_id      INTEGER REFERENCES episodes(id) ON DELETE SET NULL,
    description     TEXT,
    foreshadowing   TEXT
);

CREATE TABLE scenes (
    id              SERIAL PRIMARY KEY,
    episode_id      INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    scene_number    INTEGER NOT NULL,
    location_id     INTEGER REFERENCES locations(id),
    time_of_day     TEXT,
    UNIQUE (episode_id, scene_number)
);

CREATE TABLE shots (
    id                          SERIAL PRIMARY KEY,
    scene_id                    INTEGER NOT NULL REFERENCES scenes(id) ON DELETE CASCADE,
    shot_number                 INTEGER NOT NULL,
    dialogue                    TEXT,
    narration                   TEXT,
    camera_direction            TEXT,
    character_emotion           TEXT,
    facial_expression           TEXT,
    environment_description     TEXT,
    sfx_suggestion              TEXT,
    bgm_mood                    TEXT,
    video_asset_url             TEXT,
    tts_asset_url               TEXT,
    lipsynced_asset_url         TEXT,
    status                      TEXT NOT NULL DEFAULT 'pending', -- pending, video_generating, video_done, voice_generating, lipsync_done, failed
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (scene_id, shot_number)
);

-- Generic async job tracking for video-gen / TTS / lip-sync provider calls,
-- since all three are submit-then-poll APIs.
CREATE TABLE jobs (
    id              SERIAL PRIMARY KEY,
    shot_id         INTEGER REFERENCES shots(id) ON DELETE CASCADE,
    episode_id      INTEGER REFERENCES episodes(id) ON DELETE CASCADE,
    job_type        TEXT NOT NULL, -- video_gen, tts, lipsync, transcription, assembly
    provider        TEXT NOT NULL, -- kling, seedance, elevenlabs, sync_so, whisper
    external_job_id TEXT,
    status          TEXT NOT NULL DEFAULT 'submitted', -- submitted, running, succeeded, failed
    payload         JSONB DEFAULT '{}',
    result          JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE publish_queue (
    id                  SERIAL PRIMARY KEY,
    episode_id          INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    platform            TEXT NOT NULL, -- tiktok, instagram, youtube
    caption             TEXT,
    hashtags            TEXT[] DEFAULT '{}',
    thumbnail_url       TEXT,
    scheduled_at        TIMESTAMPTZ,
    status              TEXT NOT NULL DEFAULT 'pending_review', -- pending_review, approved, queued, published, failed
    platform_post_id    TEXT,
    published_at        TIMESTAMPTZ
);

CREATE TABLE analytics_events (
    id                  SERIAL PRIMARY KEY,
    publish_queue_id    INTEGER NOT NULL REFERENCES publish_queue(id) ON DELETE CASCADE,
    platform            TEXT NOT NULL,
    metric              TEXT NOT NULL, -- views, completion_rate, likes, shares, comments, watch_time_sec
    value                NUMERIC,
    collected_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
