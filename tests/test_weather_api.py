from typing import Any
import requests

import pytest
from unittest.mock import patch

from src.extract.weather_api import (
    HOURLY_VARIABLES,
    fetch_weather_data,
    validate_weather_response,
)

def test_validate_weather_response_accepts_valid_data():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00", "2026-11-01T01:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1, 2]

    data = {
        "hourly": hourly,
    }

    validate_weather_response(data)
    
def test_validate_weather_response_rejects_missing_hourly_section():
    data = {}

    with pytest.raises(ValueError, match="API response is missing the hourly section"):
        validate_weather_response(data)
    data = {}

    try:
        validate_weather_response(data)
        assert False, "Expected ValueError was not raised."
    except ValueError as error:
        assert str(error) == "API response is missing the hourly section."
        
def test_validate_weather_response_rejects_missing_variable():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    del hourly["temperature_2m"]

    data = {"hourly": hourly}

    try:
        validate_weather_response(data)
        assert False, "Expected ValueError was not raised."
    except ValueError as error:
        assert str(error) == (
            "Hourly data is missing variable: temperature_2m"
        )
        
def test_validate_weather_response_rejects_array_length_mismatch():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00", "2026-11-01T01:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1, 2]

    hourly["temperature_2m"] = [1]

    data = {"hourly": hourly}

    with pytest.raises(ValueError, match="Length mismatch for temperature_2m"):
        validate_weather_response(data)
        
def test_validate_weather_response_rejects_empty_timestamps():
    hourly: dict[str, Any] = {
        "time": [],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = []

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="Hourly timestamps must be a non-empty list",
    ):
        validate_weather_response(data)
        
def test_validate_weather_response_rejects_non_string_timestamps():
    hourly: dict[str, Any] = {
        "time": [202611010000],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="Hourly timestamps must contain only strings",
    ):
        validate_weather_response(data)
        
def test_validate_weather_response_rejects_string_weather_values():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    hourly["temperature_2m"] = ["hot"]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="temperature_2m must contain finite numeric values or None",
    ):
        validate_weather_response(data)
        
def test_validate_weather_response_accepts_none_weather_values():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    hourly["temperature_2m"] = [None]

    data = {"hourly": hourly}

    validate_weather_response(data)
    
def test_validate_weather_response_rejects_boolean_weather_values():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    hourly["temperature_2m"] = [True]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="temperature_2m must contain finite numeric values or None",
    ):
        validate_weather_response(data)
        
def test_validate_weather_response_rejects_invalid_timestamp_format():
    hourly: dict[str, Any] = {
        "time": ["not-a-valid-timestamp"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="Hourly timestamps must use the format",
    ):
        validate_weather_response(data)
        
def test_validate_weather_response_rejects_duplicate_timestamps():
    hourly: dict[str, Any] = {
        "time": [
            "2026-11-01T00:00",
            "2026-11-01T00:00",
        ],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1, 2]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="Hourly timestamps must not contain duplicates",
    ):
        validate_weather_response(data)
        
def test_validate_weather_response_rejects_out_of_order_timestamps():
    hourly: dict[str, Any] = {
        "time": [
            "2026-11-01T00:00",
            "2026-11-01T02:00",
            "2026-11-01T01:00",
        ],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1, 2, 3]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="Hourly timestamps must be in chronological order",
    ):
        validate_weather_response(data)
        
def test_fetch_weather_data_returns_valid_response():
    mock_data: dict[str, Any] = {
        "hourly": {
            "time": ["2026-11-01T00:00"],
        }
}

    for variable in HOURLY_VARIABLES:
        mock_data["hourly"][variable] = [1]

    with patch("src.extract.weather_api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_data

        result = fetch_weather_data(
            latitude=-1.286389,
            longitude=36.817223,
            start_date="2026-11-01",
            end_date="2026-11-01",
        )

    assert result == mock_data
    
    mock_get.assert_called_once_with(
    "https://archive-api.open-meteo.com/v1/archive",
    params={
        "latitude": -1.286389,
        "longitude": 36.817223,
        "start_date": "2026-11-01",
        "end_date": "2026-11-01",
        "hourly": HOURLY_VARIABLES,
        "timezone": "Africa/Nairobi",
    },
    timeout=30,
)
    
def test_fetch_weather_data_raises_runtime_error_on_request_failure():
    with patch("src.extract.weather_api.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        with pytest.raises(
            RuntimeError,
            match="Failed to retrieve weather data",
        ):
            fetch_weather_data(
                latitude=-1.286389,
                longitude=36.817223,
                start_date="2026-11-01",
                end_date="2026-11-01",
            )
            
def test_fetch_weather_data_raises_runtime_error_on_http_error():
    with patch("src.extract.weather_api.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("500 Server Error")
        )

        with pytest.raises(
            RuntimeError,
            match="Failed to retrieve weather data",
        ):
            fetch_weather_data(
                latitude=-1.286389,
                longitude=36.817223,
                start_date="2026-11-01",
                end_date="2026-11-01",
            )
            
def test_fetch_weather_data_raises_runtime_error_on_invalid_json():
    with patch("src.extract.weather_api.requests.get") as mock_get:
        mock_get.return_value.json.side_effect = ValueError(
            "Invalid JSON"
        )

        with pytest.raises(
            ValueError,
            match="Invalid JSON",
        ):
            fetch_weather_data(
                latitude=-1.286389,
                longitude=36.817223,
                start_date="2026-11-01",
                end_date="2026-11-01",
            )
            
def test_fetch_weather_data_rejects_invalid_api_data():
    invalid_data = {"unexpected": "response"}

    with patch("src.extract.weather_api.requests.get") as mock_get:
        mock_get.return_value.json.return_value = invalid_data

        with pytest.raises(
            ValueError,
            match="API response is missing the hourly section",
        ):
            fetch_weather_data(
                latitude=-1.286389,
                longitude=36.817223,
                start_date="2026-11-01",
                end_date="2026-11-01",
            )
            
def test_validate_weather_response_rejects_non_finite_values():
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    hourly["temperature_2m"] = [float("nan")]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="temperature_2m must contain finite numeric values or None",
    ):
        validate_weather_response(data)
        
@pytest.mark.parametrize(
    "invalid_value",
    [float("inf"), float("-inf")],
)
def test_validate_weather_response_rejects_infinite_values(
    invalid_value: float,
):
    hourly: dict[str, Any] = {
        "time": ["2026-11-01T00:00"],
    }

    for variable in HOURLY_VARIABLES:
        hourly[variable] = [1]

    hourly["temperature_2m"] = [invalid_value]

    data = {"hourly": hourly}

    with pytest.raises(
        ValueError,
        match="temperature_2m must contain finite numeric values or None",
    ):
        validate_weather_response(data)