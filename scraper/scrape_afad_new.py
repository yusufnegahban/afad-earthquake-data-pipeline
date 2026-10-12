
# -*- coding: utf-8 -*-
"""
AFAD Earthquake Scraper

This script:
1. Fetches earthquake data from AFAD
2. Normalizes the data
3. Uploads the result as JSON to MinIO

AFAD column mapping:
0 = Tarih(TS)
1 = Enlem
2 = Boylam
3 = Derinlik(Km)
4 = Tip
5 = Büyüklük
6 = Yer
7 = Deprem Id
"""

import json
import os
import re
from datetime import datetime
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from minio import Minio


# ============================================================
# MinIO Configuration
# ============================================================

MINIO_ENDPOINT = os.environ.get(
    "MINIO_ENDPOINT",
    "localhost:18080"
)

MINIO_ACCESS_KEY = os.environ.get(
    "MINIO_ACCESS_KEY",
    "minio"
)

MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]

MINIO_BUCKET_NAME = "afad-earthquakes"


# ============================================================
# AFAD Configuration
# ============================================================

TARGET_URL = "https://deprem.afad.gov.tr/last-earthquakes.html"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": (
        "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    ),
}


# ============================================================
# Helper Functions
# ============================================================

def to_float(value):
    """
    Converts a string value to float safely.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):

        cleaned_value = value.strip()

        # Remove common units
        cleaned_value = re.sub(
            r"(km|miles?)",
            "",
            cleaned_value,
            flags=re.IGNORECASE
        )

        # Remove commas
        cleaned_value = cleaned_value.replace(",", "")

        try:
            return float(cleaned_value)

        except ValueError:
            return None

    return None


# ============================================================
# MinIO Bucket
# ============================================================

def ensure_bucket(client: Minio, bucket_name: str):
    """
    Checks whether the MinIO bucket exists.
    Creates it if it does not exist.
    """

    try:

        found = client.bucket_exists(bucket_name)

        if not found:

            client.make_bucket(bucket_name)

            print(
                f"Bucket '{bucket_name}' created."
            )

        else:

            print(
                f"Bucket '{bucket_name}' already exists."
            )

    except Exception as e:

        print(
            f"Error checking/creating bucket "
            f"'{bucket_name}': {e}"
        )

        raise


# ============================================================
# Fetch AFAD Table
# ============================================================

def fetch_table_data(
    url: str,
    headers: dict
) -> list[list[str]] | None:
    """
    Fetches the AFAD earthquake table
    and returns raw rows.
    """

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as e:

        print(
            f"Error fetching URL {url}: {e}"
        )

        return None

    # Force UTF-8 decoding
    response.encoding = "utf-8"

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    tables = soup.find_all("table")

    print(
        f"Total tables found: {len(tables)}"
    )

    if not tables:

        print(
            "Could not find any table "
            "on the AFAD page."
        )

        return None

    target_table = None

    # ========================================================
    # Find AFAD Earthquake Table
    # ========================================================

    for table in tables:

        header_row = table.find("tr")

        if not header_row:
            continue

        header_cells = header_row.find_all("th")

        if not header_cells:
            continue

        header_texts = [
            cell.get_text(
                strip=True
            ).lower()
            for cell in header_cells
        ]

        # AFAD table contains Tarih and Enlem
        has_tarih = any(
            "tarih" in h
            for h in header_texts
        )

        has_enlem = any(
            "enlem" in h
            for h in header_texts
        )

        if has_tarih and has_enlem:

            target_table = table

            break

    if target_table is None:

        print(
            "Could not find the target "
            "AFAD earthquake table."
        )

        return None

    # ========================================================
    # Extract Data Rows
    # ========================================================

    rows_data = []

    all_rows = target_table.find_all("tr")

    for row in all_rows:

        cells = row.find_all(
            ["td", "th"]
        )

        row_text = [
            cell.get_text(
                " ",
                strip=True
            )
            for cell in cells
        ]

        # AFAD currently has 8 columns
        if len(row_text) < 7:
            continue

        # First column must look like:
        # 2026-09-05 15:58:17

        if re.match(
            r"\d{4}-\d{2}-\d{2}\s"
            r"\d{2}:\d{2}:\d{2}",
            row_text[0]
        ):

            rows_data.append(row_text)

    if not rows_data:

        print(
            "No earthquake data rows found."
        )

        return None

    print(
        f"Fetched {len(rows_data)} "
        f"potential data rows."
    )

    return rows_data


# ============================================================
# Normalize AFAD Data
# ============================================================

def normalize_data(
    data_rows: list[list[str]]
) -> list[dict]:
    """
    Converts raw AFAD rows into the standardized
    schema expected by the Silver Spark pipeline.

    AFAD columns:

    0 = Tarih(TS)
    1 = Enlem
    2 = Boylam
    3 = Derinlik(Km)
    4 = Tip
    5 = Büyüklük
    6 = Yer
    7 = Deprem Id
    """

    normalized_data = []

    if not data_rows:
        return normalized_data

    for r in data_rows:

        try:

            # ------------------------------------------------
            # Safety check
            # ------------------------------------------------

            if len(r) < 7:

                print(
                    "Skipping row due to "
                    f"insufficient columns: {r}"
                )

                continue

            # ------------------------------------------------
            # AFAD Field Mapping
            # ------------------------------------------------

            # 0 = Tarih(TS)
            timestamp_str = r[0].strip()

            # 1 = Enlem
            latitude = to_float(r[1])

            # 2 = Boylam
            longitude = to_float(r[2])

            # 3 = Derinlik(Km)
            depth_km = to_float(r[3])

            # 4 = Tip
            earthquake_type = r[4].strip()

            # 5 = Büyüklük
            magnitude = to_float(r[5])

            # 6 = Yer
            location = r[6].strip()

            # Remove trailing check mark if present
            location = re.sub(
                r"✓$",
                "",
                location
            ).strip()

            # ------------------------------------------------
            # Timestamp
            # ------------------------------------------------

            try:

                dt_object = parse(
                    timestamp_str
                )

                timestamp_ts = (
                    dt_object.isoformat()
                )

                # AFAD timestamp is UTC
                if not timestamp_ts.endswith("Z"):

                    timestamp_ts += "Z"

            except Exception as e:

                print(
                    f"Error parsing timestamp "
                    f"'{timestamp_str}': {e}"
                )

                continue

            # ------------------------------------------------
            # Ingestion Time
            # ------------------------------------------------

            ingested_at = (
                datetime.utcnow().isoformat()
                + "Z"
            )

            # ------------------------------------------------
            # Source URL
            # ------------------------------------------------

            source_url = TARGET_URL

            # ------------------------------------------------
            # Validation
            # ------------------------------------------------

            if (
                timestamp_ts
                and magnitude is not None
                and latitude is not None
                and longitude is not None
            ):

                normalized_record = {
                    "timestamp_ts": timestamp_ts,
                    "magnitude": magnitude,
                    "latitude": latitude,
                    "longitude": longitude,
                    "depth_km": depth_km,
                    "location": location,
                    "source_url": source_url,
                    "ingested_at": ingested_at,
                }

                normalized_data.append(
                    normalized_record
                )

            else:

                print(
                    "Skipping row due to "
                    f"missing critical data: {r}"
                )

        except Exception as e:

            print(
                f"Error normalizing row "
                f"{r}: {e}"
            )

    return normalized_data


# ============================================================
# Write Data to MinIO
# ============================================================

def write_to_minio(
    client: Minio,
    bucket_name: str,
    data: list[dict]
):
    """
    Uploads normalized earthquake data
    to MinIO as JSON.
    """

    if not data:

        print(
            "No data to write to MinIO."
        )

        return False

    # Current UTC time
    now = datetime.utcnow()

    # Example:
    # afad/2026/09/05/earthquakes_153012123456.json

    path = (
        f"afad/"
        f"{now.strftime('%Y/%m/%d')}/"
        f"earthquakes_"
        f"{now.strftime('%H%M%S%f')}.json"
    )

    try:

        # ----------------------------------------------------
        # Convert Python objects to JSON
        # ----------------------------------------------------

        json_data = json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )

        # ----------------------------------------------------
        # Convert JSON string to bytes
        # ----------------------------------------------------

        data_bytes = json_data.encode(
            "utf-8"
        )

        # ----------------------------------------------------
        # Create file-like stream
        # MinIO put_object requires .read()
        # ----------------------------------------------------

        data_stream = BytesIO(
            data_bytes
        )

        # ----------------------------------------------------
        # Upload to MinIO
        # ----------------------------------------------------

        client.put_object(
            bucket_name,
            path,
            data_stream,
            len(data_bytes),
            content_type="application/json"
        )

        # ----------------------------------------------------
        # Success message
        # ----------------------------------------------------

        print(
            f"Successfully uploaded "
            f"{len(data)} records to MinIO."
        )

        print(
            f"MinIO path: "
            f"{bucket_name}/{path}"
        )

        return True

    except Exception as e:

        print(
            f"Error writing data to MinIO: {e}"
        )

        return False


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("AFAD Earthquake Scraper")
    print("=" * 60)

    # --------------------------------------------------------
    # Initialize MinIO
    # --------------------------------------------------------

    try:

        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )

        ensure_bucket(
            client,
            MINIO_BUCKET_NAME
        )

    except Exception as e:

        print(
            "Failed to initialize MinIO client "
            f"or ensure bucket: {e}"
        )

        return

    # --------------------------------------------------------
    # Fetch AFAD
    # --------------------------------------------------------

    print(
        f"Fetching data from: {TARGET_URL}"
    )

    raw_data_rows = fetch_table_data(
        TARGET_URL,
        REQUEST_HEADERS
    )

    if not raw_data_rows:

        print(
            "Failed to fetch or find "
            "AFAD earthquake data."
        )

        return

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    normalized_earthquakes = normalize_data(
        raw_data_rows
    )

    if not normalized_earthquakes:

        print(
            "No earthquake data "
            "was normalized."
        )

        return

    print(
        f"Successfully normalized "
        f"{len(normalized_earthquakes)} "
        f"earthquake records."
    )

    # --------------------------------------------------------
    # Write to MinIO
    # --------------------------------------------------------

    upload_success = write_to_minio(
        client,
        MINIO_BUCKET_NAME,
        normalized_earthquakes
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    if upload_success:

        print(
            "AFAD scraper finished successfully."
        )

    else:

        print(
            "AFAD scraper finished "
            "with upload error."
        )


# ============================================================
# Script Execution
# ============================================================

if __name__ == "__main__":
    main()

