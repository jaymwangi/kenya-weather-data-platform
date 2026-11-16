
-- Kenya Weather Data Platform
-- Migration 002: Create raw data tables

-- 1. Reference table for Kenyan weather locations
CREATE TABLE IF NOT EXISTS raw.locations (
    location_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL UNIQUE,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'Kenya',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_location_latitude
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT chk_location_longitude
        CHECK (longitude BETWEEN -180 AND 180)
);


-- 2. Archive of original Open-Meteo API responses
CREATE TABLE IF NOT EXISTS raw.weather_api_responses (
    response_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_id BIGINT NOT NULL,
    requested_start_date DATE NOT NULL,
    requested_end_date DATE NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_payload JSONB NOT NULL,

    CONSTRAINT fk_weather_response_location
        FOREIGN KEY (location_id)
        REFERENCES raw.locations (location_id),

    CONSTRAINT chk_requested_date_range
        CHECK (requested_end_date >= requested_start_date),

    CONSTRAINT chk_response_payload_object
        CHECK (jsonb_typeof(response_payload) = 'object')
);


-- 3. Index to support location-based response lookups
CREATE INDEX IF NOT EXISTS idx_weather_responses_location_id
    ON raw.weather_api_responses (location_id);
