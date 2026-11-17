WITH hourly_weather AS (

    SELECT
        location_id,
        (weather_timestamp AT TIME ZONE weather_timezone)::date
            AS weather_date,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        wind_speed_10m

    FROM {{ ref('stg_weather_hourly') }}

),

daily_weather AS (

    SELECT
        location_id,
        weather_date,

        AVG(temperature_2m) AS avg_temperature_2m,
        MIN(temperature_2m) AS min_temperature_2m,
        MAX(temperature_2m) AS max_temperature_2m,

        SUM(precipitation) AS total_precipitation,

        AVG(relative_humidity_2m) AS avg_relative_humidity_2m,
        AVG(wind_speed_10m) AS avg_wind_speed_10m,

        COUNT(*) AS observation_count

    FROM hourly_weather

    GROUP BY
        location_id,
        weather_date

)

SELECT *
FROM daily_weather