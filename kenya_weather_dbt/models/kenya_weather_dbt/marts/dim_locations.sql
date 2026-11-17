SELECT
    location_id,
    location_name,
    country,
    latitude,
    longitude

FROM {{ source('raw', 'locations') }}