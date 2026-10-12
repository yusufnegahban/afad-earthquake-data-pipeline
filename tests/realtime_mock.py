import json
import random
import time
import os
from datetime import datetime

# Path to save data on your host (mapped to Docker)
LANDING_PATH = "./data/landing/afad/"

# Ensure the directory exists
os.makedirs(LANDING_PATH, exist_ok=True)

print("🚀 Mock Scraper started. Generating data every 5 minutes...")

try:
    while True:
        # 1. Generate random but realistic data
        quake_id = f"irsc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Random coordinates within Iran's approximate range
        lat = round(32.0 + random.uniform(-2.0, 2.0), 4)
        lon = round(53.0 + random.uniform(-2.0, 2.0), 4)
        
        data = {
            "quake_id": quake_id,
            "timestamp_ts": datetime.now().isoformat(),
            "latitude": lat,
            "longitude": lon,
            "depth_km": round(random.uniform(5.0, 35.0), 1),
            "magnitude": round(random.uniform(3.0, 6.5), 1),
            "location": f"Region-{random.randint(1, 30)}",
            "source_url": "http://irsc.ut.ac.ir",
            "ingested_at": datetime.now().isoformat()
        }

        # 2. Save to a JSON file with a unique name (to prevent overwriting)
        filename = os.path.join(LANDING_PATH, f"quake_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(filename, "w") as f:
            json.dump([data], f) # Save as a list
        
        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] New earthquake data saved: {filename}")

        # 3. Wait for 5 minutes (300 seconds)
        time.sleep(300)

except KeyboardInterrupt:
    print("\n⛔ Scraper stopped by user.")