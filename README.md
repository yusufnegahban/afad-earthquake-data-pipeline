# Earthquake Data Engineering Pipeline

An end-to-end data engineering project that collects earthquake data from AFAD, processes it with Apache Spark, stores cleaned data in Delta Lake, and prepares analytical datasets for Apache Superset.

## Architecture

AFAD → MinIO (Bronze) → Apache Spark → Delta Lake (Silver) → Gold → Apache Superset


flowchart TD
    A["🌍 AFAD Earthquake Data"] --> B["🐍 Python Scraper"]
    B --> C["🪣 MinIO - Bronze"]
    C --> D["⚡ Apache Spark"]
    D --> E["🧹 Data Cleaning"]
    E --> F["🗄️ Delta Lake - Silver"]
    F --> G["📊 Gold Analytical Data"]
    G --> H["📈 Apache Superset Dashboard"]

    D -.-> I["🧪 Data Quality Tests"]


## Dashboard Preview

![Earthquake Dashboard](screenshots/earthquake-dashboard.png)

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
