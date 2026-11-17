
WITH ranked_hourly_weather AS (

    SELECT
        location_id,
        weather_timestamp,
        response_id,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        rain,
        wind_speed_10m,
        wind_direction_10m,
        cloud_cover,

        ROW_NUMBER() OVER (
            PARTITION BY location_id, weather_timestamp
            ORDER BY response_id DESC
        ) AS observation_rank

    FROM {{ ref('stg_weather_hourly') }}

),

final AS (

    SELECT
        location_id,
        weather_timestamp,
        response_id,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        rain,
        wind_speed_10m,
        wind_direction_10m,
        cloud_cover

    FROM ranked_hourly_weather
    WHERE observation_rank = 1

)

SELECT *
FROM final
