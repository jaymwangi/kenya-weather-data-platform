
from datetime import date, timedelta

from sqlalchemy import text

from src.extract.weather_api import fetch_weather_data
from src.load.postgres_loader import create_db_engine, load_weather_response


def ingest_location_weather(
    location_name: str,
    start_date: date,
    end_date: date,
) -> int | None:
    """Fetch and load weather unless this date chunk already succeeded."""

    engine = create_db_engine()

    try:
        with engine.begin() as connection:
            location = connection.execute(
                text("""
                    SELECT location_id, latitude, longitude
                    FROM raw.locations
                    WHERE location_name = :location_name
                """),
                {"location_name": location_name},
            ).mappings().one_or_none()

            if location is None:
                raise ValueError(f"Unknown location: {location_name}")

            location_id = location["location_id"]

            checkpoint = connection.execute(
                text("""
                    SELECT ingestion_run_id, status, response_id
                    FROM raw.ingestion_runs
                    WHERE location_id = :location_id
                      AND requested_start_date = :start_date
                      AND requested_end_date = :end_date
                    FOR UPDATE
                """),
                {
                    "location_id": location_id,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            ).mappings().one_or_none()

            if checkpoint and checkpoint["status"] == "succeeded":
                print(
                    f"{location_name}: skipping completed chunk "
                    f"{start_date} to {end_date}"
                )
                return checkpoint["response_id"]

            if checkpoint:
                connection.execute(
                    text("""
                        UPDATE raw.ingestion_runs
                        SET status = 'running',
                            attempt_count = attempt_count + 1,
                            started_at = NOW(),
                            completed_at = NULL,
                            response_id = NULL,
                            error_message = NULL
                        WHERE ingestion_run_id = :run_id
                    """),
                    {"run_id": checkpoint["ingestion_run_id"]},
                )

                run_id = checkpoint["ingestion_run_id"]

            else:
                run_id = connection.execute(
                    text("""
                        INSERT INTO raw.ingestion_runs (
                            location_id,
                            requested_start_date,
                            requested_end_date
                        )
                        VALUES (
                            :location_id,
                            :start_date,
                            :end_date
                        )
                        RETURNING ingestion_run_id
                    """),
                    {
                        "location_id": location_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                ).scalar_one()

        try:
            response_payload = fetch_weather_data(
                latitude=float(location["latitude"]),
                longitude=float(location["longitude"]),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            )

            response_id = load_weather_response(
                location_id=location_id,
                start_date=start_date,
                end_date=end_date,
                response_payload=response_payload,
            )

            with engine.begin() as connection:
                connection.execute(
                    text("""
                        UPDATE raw.ingestion_runs
                        SET status = 'succeeded',
                            response_id = :response_id,
                            completed_at = NOW(),
                            error_message = NULL
                        WHERE ingestion_run_id = :run_id
                    """),
                    {
                        "response_id": response_id,
                        "run_id": run_id,
                    },
                )

            return response_id

        except Exception as error:
            with engine.begin() as connection:
                connection.execute(
                    text("""
                        UPDATE raw.ingestion_runs
                        SET status = 'failed',
                            completed_at = NOW(),
                            error_message = :error_message
                        WHERE ingestion_run_id = :run_id
                    """),
                    {
                        "error_message": str(error)[:5000],
                        "run_id": run_id,
                    },
                )

            raise

    finally:
        engine.dispose()


def ingest_all_locations(
    start_date: date,
    end_date: date,
) -> dict[str, int]:
    """Fetch and load weather for every configured Kenyan location."""

    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            location_names = connection.execute(
                text("""
                    SELECT location_name
                    FROM raw.locations
                    ORDER BY location_id
                """)
            ).scalars().all()

    finally:
        engine.dispose()

    if not location_names:
        raise ValueError("No locations found in raw.locations.")

    ingestion_results = {}

    for location_name in location_names:
        response_id = ingest_location_weather(
            location_name=location_name,
            start_date=start_date,
            end_date=end_date,
        )

        if response_id is not None:
            ingestion_results[location_name] = response_id

        print(
            f"{location_name}: successfully loaded "
            f"response ID {response_id}"
        )

    return ingestion_results


def backfill_all_locations(
    start_date: date,
    end_date: date,
    chunk_days: int = 30,
) -> dict[str, list[int]]:
    """Backfill historical weather for all locations in date chunks."""

    if end_date < start_date:
        raise ValueError("end_date must not be earlier than start_date.")

    if chunk_days < 1:
        raise ValueError("chunk_days must be at least 1.")

    results = {}
    chunk_start = start_date

    while chunk_start <= end_date:
        chunk_end = min(
            chunk_start + timedelta(days=chunk_days - 1),
            end_date,
        )

        print(f"\nProcessing {chunk_start} to {chunk_end}")

        chunk_results = ingest_all_locations(
            start_date=chunk_start,
            end_date=chunk_end,
        )

        for location_name, response_id in chunk_results.items():
            results.setdefault(location_name, []).append(response_id)

        chunk_start = chunk_end + timedelta(days=1)

    return results


def run_daily_ingestion(
    run_date: date | None = None,
    rolling_days: int = 7,
) -> dict[str, int]:
    """Ingest the most recent completed days for all locations."""

    if rolling_days < 1:
        raise ValueError("rolling_days must be at least 1.")

    if run_date is None:
        run_date = date.today()

    end_date = run_date - timedelta(days=1)
    start_date = end_date - timedelta(days=rolling_days - 1)

    print(
        f"\nStarting daily ingestion: "
        f"{start_date} to {end_date}"
    )

    return ingest_all_locations(
        start_date=start_date,
        end_date=end_date,
    )


if __name__ == "__main__":
    results = ingest_all_locations(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
    )

    print("\nIngestion summary:")

    for location_name, response_id in results.items():
        print(f"{location_name}: response ID {response_id}")
