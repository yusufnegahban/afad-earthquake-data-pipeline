# Goal:
# Inspect the IRSC earthquake webpage structure for schema discovery and mapping preparation.
# This code fetches the specified webpage, finds all HTML tables,
# and then extracts and prints the first 3 rows from each table.
# For each cell within these rows, it retrieves both the text content and any linked URL (href).
# This helps understand column order, data types, and identify important links like event details.
# The output will include text and href for each cell, aiding in the preparation of a robust scraper and data mapping.

from bs4 import BeautifulSoup
import requests

url = "https://deprem.afad.gov.tr/last-earthquakes.html"

try:
    # Fetch the webpage content with a timeout
    resp = requests.get(url, timeout=20)
    # Raise an exception for bad status codes (4xx or 5xx)
    resp.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find all HTML tables on the page
    tables = soup.find_all("table")

    print(f"\nTotal tables found: {len(tables)}\n")

    # Iterate through each table found
    for i, table in enumerate(tables):

        print("=" * 50)
        print(f"TABLE {i}")
        print("=" * 50)

        # Find all rows (tr) within the current table
        rows = table.find_all("tr")

        # Process the first 3 rows to understand the structure
        for r in rows[:3]: # Changed from [:2] to [:3] to get 3 rows as intended
            cells = r.find_all(["td", "th"])
            row_data = []

            # Extract text and link (href) from each cell (td or th)
            for cell in cells:
                text = cell.get_text(" ", strip=True)
                link_tag = cell.find("a")
                href = link_tag.get("href") if link_tag else None

                row_data.append({
                    "text": text,
                    "href": href
                })

            print(row_data)

        print("\n")

except requests.exceptions.RequestException as e:
    print(f"Error fetching or processing URL {url}: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
