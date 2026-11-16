
from datetime import date

from sqlalchemy import text

from src.extract.weather_api import fetch_weather_data
from src.load.postgres_loader import create_db_engine, load_weather_response


def ingest_location_weather(
    location_name: str,
    start_date: date,
    end_date: date,
) -> int:
    """Fetch and load historical weather for one Kenyan location."""

    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT location_id, latitude, longitude
                    FROM raw.locations
                    WHERE location_name = :location_name
                """),
                {"location_name": location_name},
            )

            location = result.mappings().one_or_none()

        if location is None:
            raise ValueError(f"Unknown location: {location_name}")

        response_payload = fetch_weather_data(
            latitude=float(location["latitude"]),
            longitude=float(location["longitude"]),
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )

        response_id = load_weather_response(
            location_id=location["location_id"],
            start_date=start_date,
            end_date=end_date,
            response_payload=response_payload,
        )

        return response_id

    finally:
        engine.dispose()


if __name__ == "__main__":
    response_id = ingest_location_weather(
        location_name="Nairobi",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
    )

    print(f"Successfully loaded weather response. ID: {response_id}")
