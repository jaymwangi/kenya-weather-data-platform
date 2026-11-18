SELECT *
FROM {{ ref('fact_weather_hourly') }}
WHERE
    (relative_humidity_2m < 0 OR relative_humidity_2m > 100)
    OR precipitation < 0
    OR rain < 0
    OR wind_speed_10m < 0
    OR (wind_direction_10m < 0 OR wind_direction_10m > 360)
    OR (cloud_cover < 0 OR cloud_cover > 100)
