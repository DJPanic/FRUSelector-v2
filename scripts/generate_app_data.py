#!/usr/bin/env python3
"""Generate src/shared/scraped-data.json from scraped service guide data.

This bridges the gap between the monthly scraping workflow and the Electron app
so that fresh data from Microsoft Learn actually reaches the application.

Input:  scraped_data.json (from scrape_service_guides.py)
Output: src/shared/scraped-data.json (consumed by src/shared/data.ts)

The output schema is intentionally simple and stable so data.ts can re-export it
without code changes. UI-side code can map device name -> parts as needed.
"""

import json
import sys
import os
from datetime import datetime, timezone


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_app_data.py <scraped_data.json> <output.json>")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    if not os.path.exists(src):
        print(f"ERROR: input file not found: {src}")
        sys.exit(1)

    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)

    devices = data.get("devices", [])
    total_parts = sum(len(d.get("parts", [])) for d in devices)

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "https://learn.microsoft.com/en-us/surface/service-guides",
        "deviceCount": len(devices),
        "partCount": total_parts,
        "devices": devices,
    }

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {dst}: {len(devices)} devices, {total_parts} parts")


if __name__ == "__main__":
    main()
