
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.pipeline.ingest_weather import (
    backfill_all_locations,
    ingest_all_locations,
    ingest_location_weather,
    run_daily_ingestion,
)


def test_ingest_all_locations(
    mock_create_engine=None,
    mock_ingest_location=None,
):
    with patch(
        "src.pipeline.ingest_weather.create_db_engine"
    ) as mock_create_engine, patch(
        "src.pipeline.ingest_weather.ingest_location_weather"
    ) as mock_ingest_location:

        mock_connection = (
            mock_create_engine.return_value
            .connect.return_value.__enter__.return_value
        )

        mock_connection.execute.return_value.scalars.return_value.all.return_value = [
            "Nairobi",
            "Mombasa",
            "Kisumu",
            "Nakuru",
            "Eldoret",
        ]

        mock_ingest_location.side_effect = [101, 102, 103, 104, 105]

        results = ingest_all_locations(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
        )

        assert results == {
            "Nairobi": 101,
            "Mombasa": 102,
            "Kisumu": 103,
            "Nakuru": 104,
            "Eldoret": 105,
        }

        assert mock_ingest_location.call_count == 5
        mock_create_engine.return_value.dispose.assert_called_once()


@patch("src.pipeline.ingest_weather.ingest_all_locations")
def test_backfill_all_locations_uses_correct_date_chunks(
    mock_ingest_all,
):
    mock_ingest_all.side_effect = [
        {"Nairobi": 101},
        {"Nairobi": 102},
        {"Nairobi": 103},
    ]

    results = backfill_all_locations(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 10),
        chunk_days=4,
    )

    assert mock_ingest_all.call_count == 3

    expected_calls = [
        (date(2026, 1, 1), date(2026, 1, 4)),
        (date(2026, 1, 5), date(2026, 1, 8)),
        (date(2026, 1, 9), date(2026, 1, 10)),
    ]

    actual_calls = [
        (
            call.kwargs["start_date"],
            call.kwargs["end_date"],
        )
        for call in mock_ingest_all.call_args_list
    ]

    assert actual_calls == expected_calls
    assert results == {"Nairobi": [101, 102, 103]}


@patch("src.pipeline.ingest_weather.fetch_weather_data")
@patch("src.pipeline.ingest_weather.create_db_engine")
def test_ingest_location_weather_skips_succeeded_chunk(
    mock_create_engine,
    mock_fetch_weather,
):
    mock_connection = (
        mock_create_engine.return_value
        .begin.return_value.__enter__.return_value
    )

    location_result = MagicMock()
    checkpoint_result = MagicMock()

    location_result.mappings.return_value.one_or_none.return_value = {
        "location_id": 1,
        "latitude": -1.286389,
        "longitude": 36.817223,
    }

    checkpoint_result.mappings.return_value.one_or_none.return_value = {
        "ingestion_run_id": 1,
        "status": "succeeded",
        "response_id": 3,
    }

    mock_connection.execute.side_effect = [
        location_result,
        checkpoint_result,
    ]

    response_id = ingest_location_weather(
        location_name="Nairobi",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
    )

    assert response_id == 3
    mock_fetch_weather.assert_not_called()
    mock_create_engine.return_value.dispose.assert_called_once()


@patch("src.pipeline.ingest_weather.load_weather_response")
@patch("src.pipeline.ingest_weather.fetch_weather_data")
@patch("src.pipeline.ingest_weather.create_db_engine")
def test_ingest_location_weather_retries_failed_chunk(
    mock_create_engine,
    mock_fetch_weather,
    mock_load_response,
):
    mock_connection = (
        mock_create_engine.return_value
        .begin.return_value.__enter__.return_value
    )

    location_result = MagicMock()
    checkpoint_result = MagicMock()

    location_result.mappings.return_value.one_or_none.return_value = {
        "location_id": 1,
        "latitude": -1.286389,
        "longitude": 36.817223,
    }

    checkpoint_result.mappings.return_value.one_or_none.return_value = {
        "ingestion_run_id": 7,
        "status": "failed",
        "response_id": None,
    }

    mock_connection.execute.side_effect = [
        location_result,
        checkpoint_result,
        MagicMock(),
        MagicMock(),
    ]

    mock_fetch_weather.return_value = {"hourly": {"time": []}}
    mock_load_response.return_value = 105

    response_id = ingest_location_weather(
        location_name="Nairobi",
        start_date=date(2026, 1, 3),
        end_date=date(2026, 2, 1),
    )

    assert response_id == 105
    mock_fetch_weather.assert_called_once()
    mock_load_response.assert_called_once()

    update_query = mock_connection.execute.call_args_list[2].args[0]
    update_parameters = mock_connection.execute.call_args_list[2].args[1]

    assert "attempt_count = attempt_count + 1" in str(update_query)
    assert update_parameters["run_id"] == 7

    mock_create_engine.return_value.dispose.assert_called_once()


@patch("src.pipeline.ingest_weather.fetch_weather_data")
@patch("src.pipeline.ingest_weather.create_db_engine")
def test_ingest_location_weather_records_api_failure(
    mock_create_engine,
    mock_fetch_weather,
):
    mock_connection = (
        mock_create_engine.return_value
        .begin.return_value.__enter__.return_value
    )

    location_result = MagicMock()
    checkpoint_result = MagicMock()
    insert_result = MagicMock()

    location_result.mappings.return_value.one_or_none.return_value = {
        "location_id": 1,
        "latitude": -1.286389,
        "longitude": 36.817223,
    }

    checkpoint_result.mappings.return_value.one_or_none.return_value = None
    insert_result.scalar_one.return_value = 42

    mock_connection.execute.side_effect = [
        location_result,
        checkpoint_result,
        insert_result,
        MagicMock(),
    ]

    mock_fetch_weather.side_effect = RuntimeError("API connection failed")

    with pytest.raises(RuntimeError, match="API connection failed"):
        ingest_location_weather(
            location_name="Nairobi",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 3, 2),
        )

    failure_query = mock_connection.execute.call_args_list[3].args[0]
    failure_parameters = mock_connection.execute.call_args_list[3].args[1]

    assert "status = 'failed'" in str(failure_query)
    assert failure_parameters["error_message"] == "API connection failed"
    assert failure_parameters["run_id"] == 42

    mock_create_engine.return_value.dispose.assert_called_once()


@patch("src.pipeline.ingest_weather.ingest_all_locations")
@patch("src.pipeline.ingest_weather.date")
def test_run_daily_ingestion_uses_last_seven_completed_days(
    mock_date,
    mock_ingest_all,
):
    mock_date.today.return_value = date(2026, 11, 18)
    mock_ingest_all.return_value = {"Nairobi": 101}

    results = run_daily_ingestion()

    mock_ingest_all.assert_called_once_with(
        start_date=date(2026, 11, 11),
        end_date=date(2026, 11, 17),
    )

    assert results == {"Nairobi": 101}


@patch("src.pipeline.ingest_weather.ingest_all_locations")
def test_run_daily_ingestion_uses_custom_date_window(
    mock_ingest_all,
):
    mock_ingest_all.return_value = {"Nairobi": 102}

    results = run_daily_ingestion(
        run_date=date(2026, 11, 18),
        rolling_days=3,
    )

    mock_ingest_all.assert_called_once_with(
        start_date=date(2026, 11, 15),
        end_date=date(2026, 11, 17),
    )

    assert results == {"Nairobi": 102}


@patch("src.pipeline.ingest_weather.ingest_all_locations")
def test_run_daily_ingestion_rejects_invalid_rolling_days(
    mock_ingest_all,
):
    with pytest.raises(
        ValueError,
        match="rolling_days must be at least 1.",
    ):
        run_daily_ingestion(
            run_date=date(2026, 11, 18),
            rolling_days=0,
        )

    mock_ingest_all.assert_not_called()
