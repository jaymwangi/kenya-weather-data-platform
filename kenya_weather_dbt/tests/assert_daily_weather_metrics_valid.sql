SELECT *
FROM {{ ref('int_weather_daily') }}
WHERE
    (avg_relative_humidity_2m < 0 OR avg_relative_humidity_2m > 100)
    OR total_precipitation < 0
    OR avg_wind_speed_10m < 0
    OR min_temperature_2m > max_temperature_2m
