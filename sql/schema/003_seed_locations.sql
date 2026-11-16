
-- Kenya Weather Data Platform
-- Migration 003: Seed Kenyan locations

INSERT INTO raw.locations (
    location_name,
    latitude,
    longitude,
    country
)
VALUES
    ('Nairobi', -1.286389, 36.817223, 'Kenya'),
    ('Mombasa', -4.043477, 39.668206, 'Kenya'),
    ('Kisumu', -0.091702, 34.767956, 'Kenya'),
    ('Nakuru', -0.303099, 36.080026, 'Kenya'),
    ('Eldoret', 0.514277, 35.269780, 'Kenya')
ON CONFLICT (location_name) DO NOTHING;
