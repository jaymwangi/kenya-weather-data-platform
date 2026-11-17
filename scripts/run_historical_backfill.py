
from datetime import date

from src.pipeline.ingest_weather import backfill_all_locations


def main():
    start_date = date(2024, 11, 17)
    end_date = date(2026, 11, 16)
    chunk_days = 30

    print("Starting Kenya Weather historical backfill")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Chunk size: {chunk_days} days")
    print("Locations: all configured Kenyan locations")

    results = backfill_all_locations(
        start_date=start_date,
        end_date=end_date,
        chunk_days=chunk_days,
    )

    print("\nHistorical backfill summary:")

    for location_name, response_ids in results.items():
        print(
            f"{location_name}: "
            f"{len(response_ids)} chunks processed"
        )

    print("\nHistorical backfill completed.")


if __name__ == "__main__":
    main()
