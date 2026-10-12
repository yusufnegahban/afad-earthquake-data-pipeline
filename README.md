# Earthquake Data Engineering Pipeline

An end-to-end data engineering project that collects earthquake data from AFAD, processes it with Apache Spark, stores cleaned data in Delta Lake, and prepares analytical datasets for Apache Superset.

## Architecture

AFAD → MinIO (Bronze) → Apache Spark → Delta Lake (Silver) → Gold → Apache Superset

## Technologies

- Python
- Apache Spark
- Delta Lake
- MinIO
- Apache Superset
- Docker

## Key Features

- Automated earthquake data collection
- Data cleaning and transformation
- Bronze, Silver, and Gold data layers
- Analytical datasets for visualization

## Project Status

Portfolio project under development.

## Note

Configuration files and credentials are intentionally excluded from this public repository. Local environment variables are required to run the pipeline.