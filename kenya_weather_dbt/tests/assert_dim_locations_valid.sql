SELECT *
FROM {{ ref('dim_locations') }}
WHERE
    latitude < -90
    OR latitude > 90
    OR longitude < -180
    OR longitude > 180
    OR country <> 'Kenya'
