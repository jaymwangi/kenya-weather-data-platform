import math
from datetime import datetime

import requests

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "wind_direction_10m",
    "cloud_cover",
]

TIMEZONE = "Africa/Nairobi"


def validate_weather_response(data: dict) -> None:
    """
    Validate the structure and consistency of an Open-Meteo response.
    """

    if not isinstance(data, dict):
        raise ValueError("API response must be a dictionary.")

    if "hourly" not in data:
        raise ValueError("API response is missing the hourly section.")

    hourly = data["hourly"]

    if not isinstance(hourly, dict):
        raise ValueError("Hourly data must be a dictionary.")

    if "time" not in hourly:
        raise ValueError("Hourly data is missing timestamps.")

    timestamps = hourly["time"]

    if not isinstance(timestamps, list) or not timestamps:
        raise ValueError("Hourly timestamps must be a non-empty list.")

    if not all(isinstance(timestamp, str) for timestamp in timestamps):
        raise ValueError("Hourly timestamps must contain only strings.")

    parsed_timestamps = []

    for timestamp in timestamps:
        try:
            parsed_timestamp = datetime.strptime(
                timestamp,
                "%Y-%m-%dT%H:%M",
            )
            parsed_timestamps.append(parsed_timestamp)

        except ValueError as error:
            raise ValueError(
                "Hourly timestamps must use the format YYYY-MM-DDTHH:MM."
            ) from error

    if len(timestamps) != len(set(timestamps)):
        raise ValueError(
            "Hourly timestamps must not contain duplicates."
        )

    if parsed_timestamps != sorted(parsed_timestamps):
        raise ValueError(
            "Hourly timestamps must be in chronological order."
        )

    for variable in HOURLY_VARIABLES:

        if variable not in hourly:
            raise ValueError(
                f"Hourly data is missing variable: {variable}"
            )

        values = hourly[variable]

        if not isinstance(values, list):
            raise ValueError(
                f"{variable} must be represented as a list."
            )

        if len(values) != len(timestamps):
            raise ValueError(
                f"Length mismatch for {variable}: "
                f"expected {len(timestamps)}, got {len(values)}."
            )

        if not all(
            value is None or (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
            )
            for value in values
        ):
            raise ValueError(
                f"{variable} must contain finite numeric values or None."
            )


def fetch_weather_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Fetch historical hourly weather data from Open-Meteo.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": HOURLY_VARIABLES,
        "timezone": TIMEZONE,
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        validate_weather_response(data)

        return data

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Failed to retrieve weather data: {error}"
        ) from error