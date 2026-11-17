CREATE TABLE IF NOT EXISTS raw.ingestion_runs (
    ingestion_run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    location_id BIGINT NOT NULL
        REFERENCES raw.locations(location_id),

    requested_start_date DATE NOT NULL,
    requested_end_date DATE NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'succeeded', 'failed')),

    attempt_count INTEGER NOT NULL DEFAULT 1
        CHECK (attempt_count >= 1),

    response_id BIGINT
        REFERENCES raw.weather_api_responses(response_id),

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    CONSTRAINT valid_ingestion_date_range
        CHECK (requested_end_date >= requested_start_date),

    CONSTRAINT unique_location_date_chunk
        UNIQUE (
            location_id,
            requested_start_date,
            requested_end_date
        )
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_status
    ON raw.ingestion_runs(status);