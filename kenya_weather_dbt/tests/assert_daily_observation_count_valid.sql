SELECT *
FROM {{ ref('int_weather_daily') }}
WHERE observation_count < 1
   OR observation_count > 24
