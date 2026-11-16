# Kenya Weather Data Platform
## Project Specification

**Project name:** Kenya Weather Data Platform  
**Repository:** `kenya-weather-data-platform`  
**Document:** Project Specification  
**Version:** 1.0  
**Status:** Approved for development

---

## 1. Problem Statement

Weather data is continuously generated, but raw API responses are not immediately suitable for reliable analysis. They may contain missing values, duplicate records, inconsistent data types and different measurement units.

This project aims to engineer an automated data pipeline that collects historical weather data for selected Kenyan locations, validates and transforms it, and stores it in a structured PostgreSQL analytical database.

The resulting datasets will support weather trend analysis, rainfall comparisons and other analytical use cases.

## 2. Project Objectives

The project will demonstrate practical Data Engineering capabilities, including:

- Extracting data from external REST APIs.
- Building maintainable Python ETL pipelines.
- Designing relational databases for analytical workloads.
- Implementing data validation and quality checks.
- Handling duplicate records and incremental ingestion.
- Transforming raw data into analytics-ready models.
- Orchestrating and monitoring scheduled pipeline execution.
- Testing, containerizing and documenting a data engineering system.

## 3. Project Scope

### 3.1 Initial Scope (MVP)

The first version will include:

- Five Kenyan locations:
  - Nairobi
  - Mombasa
  - Kisumu
  - Nakuru
  - Eldoret
- Historical hourly weather data.
- An initial two-year historical backfill.
- Daily incremental ingestion.
- A rolling seven-day reprocessing window.
- PostgreSQL data storage.
- Python-based extraction and loading.
- dbt transformations and data tests.
- Apache Airflow orchestration.
- Docker-based local development.

### 3.2 Out of Scope

The following features are excluded from the initial version:

- Machine-learning weather prediction.
- Mobile applications.
- Real-time streaming with Kafka.
- Complex cloud infrastructure.
- User authentication and multi-tenant access.

These may be considered in future versions.

## 4. Data Source

**Primary source:** Open-Meteo Historical Weather API.

Documentation: https://open-meteo.com/en/docs/historical-weather-api

The API will provide historical weather data in JSON format.

The project will use the Africa/Nairobi timezone and explicitly configure measurement units.

**Data interpretation:** Historical API values are model-based historical weather data, not necessarily direct measurements from weather stations. The project must preserve this distinction in its documentation and analytical outputs.

### 4.1 Weather Variables

| Variable | Description | Unit |
|---|---|---|
| Temperature | Air temperature at 2 metres | °C |
| Relative humidity | Relative humidity at 2 metres | % |
| Precipitation | Total precipitation | mm |
| Rain | Rainfall amount | mm |
| Wind speed | Wind speed at 10 metres | km/h |
| Wind direction | Wind direction at 10 metres | ° |
| Cloud cover | Percentage of sky covered | % |

## 5. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Retrieve historical weather data from the API. |
| FR-02 | Support all five configured locations. |
| FR-03 | Store raw API responses for traceability. |
| FR-04 | Validate required fields and data types. |
| FR-05 | Detect and handle duplicate records. |
| FR-06 | Load clean weather data into PostgreSQL. |
| FR-07 | Support historical backfills and incremental updates. |
| FR-08 | Generate analytical models using dbt. |
| FR-09 | Schedule pipeline execution through Airflow. |
| FR-10 | Record ingestion status, errors and execution times. |

## 6. Non-Functional Requirements

### Reliability
Failed API requests must not corrupt existing data. The pipeline should handle transient failures and recover safely.

### Idempotency
Re-running an ingestion job must not create duplicate weather records.

### Maintainability
Extraction, transformation, loading and orchestration logic must be separated into manageable modules.

### Observability
Each pipeline execution must have a traceable status, execution timestamp and relevant error information.

### Data Quality
The system must enforce appropriate uniqueness, valid ranges and non-null requirements.

### Reproducibility
Another developer should be able to reproduce the local environment using documented instructions and Docker.

### Security
Configuration and credentials must be stored outside source control.

## 7. Proposed System Architecture

The platform will use a layered data architecture.

### Layer 1 — Raw Data

**Table:** `raw_weather_responses`

Stores original API payloads and ingestion metadata.

Purpose:
- Preserve source data.
- Support traceability.
- Enable reprocessing when transformations change.

### Layer 2 — Staging

**Model:** `stg_weather_observations`

Contains cleaned, typed and standardized hourly weather records.

Purpose:
- Normalize source fields.
- Handle missing and invalid values.
- Standardize timestamps and units.

### Layer 3 — Analytics

**Models:**
- `dim_locations`
- `fact_weather_hourly`

Contains structured analytical datasets ready for SQL queries and reporting.

### Pipeline Metadata

**Table:** `ingestion_runs`

Records:
- Run identifier.
- Start and end timestamps.
- Execution status.
- Records processed.
- Error details.

## 8. Data Integrity and Duplicate Handling

The natural uniqueness key for an hourly weather record will be:

`location_id + observation_timestamp`

This key will support safe upserts when the pipeline reprocesses previously ingested dates.

The system must distinguish between:
- New records.
- Existing records that require updates.
- Invalid records that should be rejected or quarantined.

## 9. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| API communication | Requests / HTTPX |
| Data processing | Pandas |
| Database | PostgreSQL |
| Data transformation | dbt |
| Workflow orchestration | Apache Airflow |
| Containerization | Docker |
| Testing | Pytest |
| Version control | Git and GitHub |

Technology choices may be refined during implementation when justified by engineering requirements.

## 10. Development Milestones

| Milestone | Expected Deliverable |
|---|---|
| 1. Project foundation | Specification, repository and environment |
| 2. API exploration | API integration and response understanding |
| 3. Extraction | Working Python ingestion pipeline |
| 4. Database | PostgreSQL raw data layer |
| 5. Transformation | Clean analytical models using dbt |
| 6. Orchestration | Scheduled execution using Airflow |
| 7. Reliability | Logging, retries, validation and tests |
| 8. Delivery | Docker setup, documentation and deployment |

## 11. Success Criteria

The MVP will be considered complete when:

1. Historical weather data has been retrieved for all five locations.
2. The initial two-year backfill completes successfully.
3. Incremental ingestion works without creating duplicate records.
4. Invalid data is detected and handled appropriately.
5. PostgreSQL contains clean analytical datasets.
6. dbt data quality tests pass.
7. Airflow can execute and monitor the pipeline.
8. Docker can reproduce the local environment.
9. The README explains architecture, setup, data lineage and engineering decisions.

## 12. Final Project Definition

The Kenya Weather Data Platform is a modular, automated data engineering system that ingests historical hourly weather data for five Kenyan locations, validates and transforms the data, and loads it into a PostgreSQL analytical warehouse using Python, dbt and Apache Airflow.

Its primary purpose is to demonstrate practical competence in batch ETL, incremental data loading, database design, data modelling, orchestration, reliability and data quality.

---
