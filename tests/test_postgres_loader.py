
from datetime import date

from sqlalchemy import text

from src.load.postgres_loader import (
    create_db_engine,
    load_weather_response,
)


def test_load_weather_response():
    payload = {
        "hourly": {
            "time": ["2026-01-01T00:00"],
            "temperature_2m": [21.5],
        }
    }

    response_id = load_weather_response(
        location_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 1),
        response_payload=payload,
    )

    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT response_payload
                    FROM raw.weather_api_responses
                    WHERE response_id = :response_id
                """),
                {"response_id": response_id},
            )

            stored_payload = result.scalar_one()

        assert response_id > 0
        assert stored_payload == payload

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM raw.weather_api_responses
                    WHERE response_id = :response_id
                """),
                {"response_id": response_id},
            )

        engine.dispose()
