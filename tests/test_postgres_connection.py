
from sqlalchemy import text

from src.load.postgres_loader import create_db_engine


def test_postgres_connection():
    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database()")
            )

            database_name = result.scalar_one()

        assert database_name == "kenya_weather"

    finally:
        engine.dispose()

