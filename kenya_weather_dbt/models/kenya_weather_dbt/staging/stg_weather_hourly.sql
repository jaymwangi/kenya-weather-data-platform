{{ config(materialized='table') }}
WITH source_responses AS (

    SELECT
        response_id,
        location_id,
        response_payload
    FROM {{ source('raw', 'weather_api_responses') }}

),

hourly_records AS (

    SELECT
        response_id,
        location_id,
        response_payload,
        time_value,
        hour_number
    FROM source_responses

    CROSS JOIN LATERAL jsonb_array_elements(
        response_payload -> 'hourly' -> 'time'
    ) WITH ORDINALITY AS hourly(time_value, hour_number)

)

SELECT
    response_id,
    location_id,

    (time_value #>> '{}')::timestamp
        AT TIME ZONE (response_payload ->> 'timezone')
        AS weather_timestamp,

    (response_payload -> 'hourly' -> 'temperature_2m'
        ->> (hour_number - 1)::int)::numeric
        AS temperature_2m,

    (response_payload -> 'hourly' -> 'relative_humidity_2m'
        ->> (hour_number - 1)::int)::numeric
        AS relative_humidity_2m,

    (response_payload -> 'hourly' -> 'precipitation'
        ->> (hour_number - 1)::int)::numeric
        AS precipitation,

    (response_payload -> 'hourly' -> 'rain'
        ->> (hour_number - 1)::int)::numeric
        AS rain,

    (response_payload -> 'hourly' -> 'wind_speed_10m'
        ->> (hour_number - 1)::int)::numeric
        AS wind_speed_10m,

    (response_payload -> 'hourly' -> 'wind_direction_10m'
        ->> (hour_number - 1)::int)::numeric
        AS wind_direction_10m,

    (response_payload -> 'hourly' -> 'cloud_cover'
        ->> (hour_number - 1)::int)::numeric
        AS cloud_cover,

    (response_payload ->> 'latitude')::numeric
        AS api_latitude,

    (response_payload ->> 'longitude')::numeric
        AS api_longitude,

    (response_payload ->> 'elevation')::numeric
        AS elevation_m,

    response_payload ->> 'timezone'
        AS weather_timezone

FROM hourly_records
