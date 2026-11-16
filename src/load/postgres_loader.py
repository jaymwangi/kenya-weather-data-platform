
import os
from pathlib import Path

from datetime import date
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine,bindparam,text
from sqlalchemy.engine import Engine


# Locate the project root and load environment variables.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def get_database_url() -> URL:
    """Build the PostgreSQL connection URL from environment variables."""

    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise RuntimeError(
            f"Missing database environment variables: {missing_variables}"
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )


def create_db_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL."""

    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )


def load_weather_response(
    location_id: int,
    start_date: date,
    end_date: date,
    response_payload: dict[str, Any],
) -> int:
    """Store an original Open-Meteo response in PostgreSQL."""

    engine = create_db_engine()
    
    insert_query = text("""
        INSERT INTO raw.weather_api_responses (
            location_id,
            requested_start_date,
            requested_end_date,
            response_payload
        )
        VALUES (
            :location_id,
            :start_date,
            :end_date,
            :response_payload
        )
        RETURNING response_id;
    """).bindparams(
        bindparam("response_payload", type_=JSONB)
    )

    try:
        with engine.begin() as connection:
            result = connection.execute(
                insert_query,
                {
                    "location_id": location_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "response_payload": response_payload,
                },
            )

            response_id = result.scalar_one()

        return response_id

    finally:
        engine.dispose()
