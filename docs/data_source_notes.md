# Data Source Notes — Kenya Weather Data Platform

## 1. Overview

This document records the external data source, API configuration, response structure, weather variables and data-handling considerations for the Kenya Weather Data Platform.

The primary data source is the Open-Meteo Historical Weather API.

**API name:** Open-Meteo Historical Weather API  
**Endpoint:** `https://archive-api.open-meteo.com/v1/archive`  
**Documentation:** https://open-meteo.com/en/docs/historical-weather-api  
**Response format:** JSON  
**Data frequency:** Hourly  
**Timezone:** Africa/Nairobi

## 2. API Request Configuration

The initial API inspection used Nairobi as the test location.

| Parameter | Value |
|---|---|
| Location | Nairobi, Kenya |
| Requested latitude | -1.286389 |
| Requested longitude | 36.817223 |
| Start date | 2026-11-01 |
| End date | 2026-11-07 |
| Timezone | Africa/Nairobi |
| Temperature unit | Celsius |
| Wind speed unit | km/h |
| Precipitation unit | mm |
| Data frequency | Hourly |

### Requested Weather Variables

- `temperature_2m`
- `relative_humidity_2m`
- `precipitation`
- `rain`
- `wind_speed_10m`
- `wind_direction_10m`
- `cloud_cover`

## 3. Observed API Response Metadata

The API returned the following metadata during the initial inspection.

| Field | Returned value |
|---|---|
| Latitude | -1.3005272 |
| Longitude | 36.824646 |
| Elevation | 1671.0 metres |
| Timezone | Africa/Nairobi |
| Timezone abbreviation | GMT+3 |
| UTC offset | 10800 seconds |
| Generation time | 0.12564659118652344 ms |

**Observation:** The returned coordinates differ slightly from the requested coordinates. The API's returned location metadata should therefore be preserved separately from the configured location coordinates.

## 4. Weather Variables and Units

The API returned the following hourly variables:

| API field | Description | Unit |
|---|---|---|
| `temperature_2m` | Air temperature at 2 metres | °C |
| `relative_humidity_2m` | Relative humidity at 2 metres | % |
| `precipitation` | Total precipitation | mm |
| `rain` | Rainfall amount | mm |
| `wind_speed_10m` | Wind speed at 10 metres | km/h |
| `wind_direction_10m` | Wind direction at 10 metres | ° |
| `cloud_cover` | Percentage of sky covered | % |

The units are provided through the API's `hourly_units` object and must be checked when processing responses.

## 5. JSON Response Structure

The API response contains three important sections.

### 5.1 Location and Response Metadata

Contains information such as:

- Latitude
- Longitude
- Elevation
- Timezone
- UTC offset
- Response generation time

### 5.2 Hourly Units

The `hourly_units` object identifies the measurement unit associated with each hourly variable.

Example:

```json
{
  "time": "iso8601",
  "temperature_2m": "°C",
  "relative_humidity_2m": "%",
  "precipitation": "mm",
  "wind_speed_10m": "km/h"
}
```

### 5.3 Hourly Observations

The `hourly` object contains timestamps and measurement arrays.

Example:

```json
{
  "time": [
    "2026-11-01T00:00",
    "2026-11-01T01:00"
  ],
  "temperature_2m": [15.9, 16.1],
  "relative_humidity_2m": [98, 97],
  "precipitation": [0.70, 0.60]
}
```

Each array position corresponds to the same position in the timestamp array.

For example:

| Timestamp | Temperature | Humidity | Precipitation |
|---|---:|---:|---:|
| 2026-11-01 00:00 | 15.9 | 98 | 0.70 |
| 2026-11-01 01:00 | 16.1 | 97 | 0.60 |

The extraction process must align these arrays correctly when converting the JSON response into individual weather records.

## 6. Initial Data Inspection Results

The initial request covered seven days, from 1 November to 7 November 2026.

Expected observations:

`7 days × 24 hours = 168 hourly records`

Observed:

- Timestamp count: 168
- First timestamp: `2026-11-01T00:00`
- First temperature: 15.9 °C
- Timezone: Africa/Nairobi
- Missing values: No `null` values identified in the supplied response.

The absence of missing values in this sample does not guarantee that future API responses will be complete.

## 7. Data Quality and Processing Considerations

The extraction pipeline must implement the following checks.

### 7.1 Array Alignment

All hourly measurement arrays must have the same number of entries as the timestamp array.

### 7.2 Missing Values

The pipeline must detect `null` values and apply an appropriate handling strategy without silently converting missing measurements into zero.

### 7.3 Data Types

- Timestamps must be converted into appropriate datetime values.
- Weather measurements must be represented using suitable numeric types.
- Location coordinates must use numeric types.

### 7.4 Duplicate Observations

Each hourly observation must be uniquely identifiable by:

`location_id + observation_timestamp`

This will support idempotent loading and safe reprocessing.

### 7.5 Units

Measurement units must be explicitly configured and documented. Values from different unit systems must not be mixed without conversion.

### 7.6 Precipitation and Rain

Both `precipitation` and `rain` will initially be preserved as separate source variables.

Their definitions and relationship must be understood before deciding whether they should remain separate in the analytical model.

### 7.7 Timezone

The project will use `Africa/Nairobi` for interpreting local hourly observations.

Timezone handling must remain consistent during ingestion, storage and analysis.

## 8. Data Granularity Strategy

The platform will preserve hourly observations as its primary level of detail.

Aggregated datasets will be derived from hourly records rather than replacing them.

Planned analytical aggregations:

| Aggregation | Potential metrics |
|---|---|
| 12-hour | Average temperature, minimum and maximum temperature, total precipitation |
| Daily | Average, minimum and maximum temperature, total precipitation |
| Monthly | Average temperature, monthly rainfall and weather trends |

This approach preserves detailed historical information while supporting efficient analytical queries.

## 9. Data Source Limitations

- Historical weather data is based on modelled/reanalysis datasets and should not automatically be treated as direct weather-station measurements.
- API responses may contain missing values.
- Returned grid coordinates may differ from requested coordinates.
- API availability and response structures must be handled defensively.
- The project must comply with the source's attribution and licensing requirements.

## 10. Conclusion

Open-Meteo provides a structured JSON response containing location metadata, measurement units, timestamps and hourly weather variables.

The platform will transform the parallel hourly arrays into individual observation records, preserve the hourly level of detail and generate aggregated analytical datasets separately.

These findings establish the foundation for the Python extraction pipeline and subsequent PostgreSQL database design.

---
