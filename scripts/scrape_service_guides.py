#!/usr/bin/env python3
"""Scrape Surface FRU parts data from Microsoft Learn service guides.

Fetches pages from learn.microsoft.com and parses HTML tables for each
Surface device. Falls back to baseline_data.json if scraping fails.

Output: JSON file with structure:
  {"devices": [{"name": "...", "parts": [{"part_number": "...", "description": "...", "category": "...", "substitute": "..."}]}]}
"""

import json
import re
import sys
import os
import time
import urllib.request
import urllib.error

LEARN_BASE = "https://learn.microsoft.com/en-us/surface/service-guides"

# Map of device display names -> URL slug for service parts page
SERVICE_GUIDE_SLUGS = [
    ("Surface Laptop 5G for Business", "surface-laptop-5g-for-business-device-information-and-service-parts"),
    ("Surface Laptop 13-in", "surface-laptop-13-in-device-information-and-service-parts"),
    ("Surface Laptop 7th Edition for Business", "surface-laptop-7-for-business-device-information-and-service-parts"),
    ("Surface Laptop 7th Edition", "surface-laptop-7-device-information-and-service-parts"),
    ("Surface Laptop 6th for Business", "surface-laptop-6-for-business-device-information-and-service-parts"),
    ("Surface Laptop 5", "surface-laptop-5-device-information-and-service-parts"),
    ("Surface Laptop 3 and Laptop 4", "surface-laptop-3-and-4-device-information-and-service-parts"),
    ("Surface Laptop Studio 2", "surface-laptop-studio-2-device-information-and-service-parts"),
    ("Surface Laptop Studio", "surface-laptop-studio-device-information-and-service-parts"),
    ("Surface Laptop Go 3", "surface-laptop-go-3-device-information-and-service-parts"),
    ("Surface Laptop Go 2", "surface-laptop-go-2-device-information-and-service-parts"),
    ("Surface Laptop Go", "surface-laptop-go-device-information-and-service-parts"),
    ("Surface Laptop SE", "surface-laptop-se-device-information-and-service-parts"),
    ("Surface Pro 12-in", "surface-pro-12-in-device-information-and-service-parts"),
    ("Surface Pro 11th Edition with 5G and Pro 10 with 5G for Business", "surface-pro-11-and-10-with-5g-for-business-device-information-and-service-parts"),
    ("Surface Pro Business 11th Edition with Intel", "surface-pro-business-11-with-intel-device-information-and-service-parts"),
    ("Surface Pro 11th Edition and Pro 10 for Business", "surface-pro-11-and-10-for-business-device-information-and-service-parts"),
    ("Surface Pro 9 with 5G", "surface-pro-9-with-5g-device-information-and-service-parts"),
    ("Surface Pro 9", "surface-pro-9-device-information-and-service-parts"),
    ("Surface Pro 8", "surface-pro-8-device-information-and-service-parts"),
    ("Surface Pro X", "surface-pro-x-device-information-and-service-parts"),
    ("Surface Pro 7+ for Business", "surface-pro-7-plus-for-business-device-information-and-service-parts"),
    ("Surface Pro 7 Kickstand", "surface-pro-7-kickstand-device-information-and-service-parts"),
    ("Surface Go 4", "surface-go-4-device-information-and-service-parts"),
    ("Surface Go 2 and 3 Kickstand Replacement", "surface-go-2-and-3-kickstand-replacement-device-information-and-service-parts"),
    ("Surface Studio 2+", "surface-studio-2-plus-device-information-and-service-parts"),
]


def fetch_url(url, retries=2):
    """Fetch a URL and return the text content."""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,text/markdown",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < retries:
                time.sleep(2)
                continue
            return None
    return None


def parse_html_tables(html):
    """Parse HTML tables and extract rows.
    
    Handles <table> elements with <thead>/<tbody> structure.
    """
    parts = []
    # Find all tables
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.I)
    
    for table_html in tables:
        # Extract headers
        headers = []
        thead = re.search(r'<thead[^>]*>(.*?)</thead>', table_html, re.DOTALL | re.I)
        if thead:
            header_cells = re.findall(r'<th[^>]*>(.*?)</th>', thead.group(1), re.DOTALL | re.I)
            headers = [re.sub(r'<[^>]+>', '', h).strip().lower() for h in header_cells]
        else:
            # Try first row as header
            first_row = re.search(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.I)
            if first_row:
                header_cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', first_row.group(1), re.DOTALL | re.I)
                headers = [re.sub(r'<[^>]+>', '', h).strip().lower() for h in header_cells]
        
        if not headers:
            continue
        
        # Find part number column
        pn_col = None
        for i, h in enumerate(headers):
            if 'part' in h and 'number' in h:
                pn_col = i; break
            if h in ('asp', 'fru', 'service part number'):
                pn_col = i; break
        
        if pn_col is None:
            continue
        
        # Find other columns
        desc_col = next((i for i, h in enumerate(headers) if 'description' in h or 'config' in h or 'detail' in h), None)
        cat_col = next((i for i, h in enumerate(headers) if 'component' in h or 'category' in h or 'type' in h), None)
        sub_col = next((i for i, h in enumerate(headers) if 'substitute' in h or 'sub sku' in h or 'replacement' in h), None)
        
        # Extract body rows
        tbody = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_html, re.DOTALL | re.I)
        body_html = tbody.group(1) if tbody else table_html
        
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body_html, re.DOTALL | re.I)
        for row_html in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL | re.I)
            if len(cells) <= pn_col:
                continue
            
            pn = re.sub(r'<[^>]+>', '', cells[pn_col]).strip()
            if not pn or not re.match(r'^[A-Z0-9]', pn):
                continue
            if pn.lower() in ('part number', 'asp', 'fru'):
                continue
            
            desc = re.sub(r'<[^>]+>', '', cells[desc_col]).strip() if desc_col is not None and desc_col < len(cells) else ""
            cat = re.sub(r'<[^>]+>', '', cells[cat_col]).strip() if cat_col is not None and cat_col < len(cells) else ""
            sub = re.sub(r'<[^>]+>', '', cells[sub_col]).strip() if sub_col is not None and sub_col < len(cells) else ""
            
            part = {"part_number": pn, "description": desc, "category": cat}
            if sub:
                part["substitute"] = sub
            parts.append(part)
    
    return parts


def parse_markdown_tables(text):
    """Parse markdown-formatted tables."""
    parts = []
    lines = text.split("\n")
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 2 < len(lines) and "---" in lines[i + 1]:
            # Found a markdown table
            headers = [h.strip().lower() for h in line.split("|")[1:-1]]
            
            pn_col = next((j for j, h in enumerate(headers) if 'part' in h and 'number' in h), None)
            if pn_col is None:
                pn_col = next((j for j, h in enumerate(headers) if h in ('asp', 'fru')), None)
            
            if pn_col is not None:
                desc_col = next((j for j, h in enumerate(headers) if 'description' in h or 'config' in h), None)
                cat_col = next((j for j, h in enumerate(headers) if 'component' in h or 'category' in h), None)
                sub_col = next((j for j, h in enumerate(headers) if 'substitute' in h or 'sub' in h), None)
                
                i += 2  # Skip separator
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c.strip() for c in lines[i].split("|")[1:-1]]
                    if len(cells) > pn_col:
                        pn = cells[pn_col].strip()
                        if pn and re.match(r'^[A-Z0-9]', pn) and pn.lower() not in ('part number', 'asp', 'fru'):
                            desc = cells[desc_col].strip() if desc_col is not None and desc_col < len(cells) else ""
                            cat = cells[cat_col].strip() if cat_col is not None and cat_col < len(cells) else ""
                            sub = cells[sub_col].strip() if sub_col is not None and sub_col < len(cells) else ""
                            part = {"part_number": pn, "description": desc, "category": cat}
                            if sub:
                                part["substitute"] = sub
                            parts.append(part)
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return parts


def scrape_device(device_name, slug):
    """Try to scrape a single device from multiple sources."""
    # Try learn.microsoft.com HTML
    url = f"{LEARN_BASE}/{slug}"
    html = fetch_url(url)
    if html and '<table' in html:
        parts = parse_html_tables(html)
        if parts:
            return parts
    
    # Try with ?accept=text/markdown (older API)
    md_url = f"{url}?accept=text/markdown"
    md = fetch_url(md_url)
    if md and '|' in md and '---' in md:
        parts = parse_markdown_tables(md)
        if parts:
            return parts
    
    return []


def scrape_all(output_path):
    """Scrape all service guide pages and save to JSON."""
    all_devices = []
    success_count = 0
    
    for device_name, slug in SERVICE_GUIDE_SLUGS:
        print(f"Fetching {device_name}...", end=" ", flush=True)
        parts = scrape_device(device_name, slug)
        
        if parts:
            print(f"{len(parts)} parts")
            success_count += 1
        else:
            print("SKIPPED (no parts found)")
        
        all_devices.append({"name": device_name, "parts": parts})
        time.sleep(1)  # Rate limiting
    
    result = {"devices": all_devices}
    total_parts = sum(len(d["parts"]) for d in all_devices)
    
    print(f"\nScraped: {success_count}/{len(SERVICE_GUIDE_SLUGS)} devices, {total_parts} parts total")
    
    if total_parts > 100:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_path}")
        return True
    else:
        print("Scraping produced insufficient data")
        return False


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else "scraped_data.json"
    baseline = os.path.join(os.path.dirname(__file__), "baseline_data.json")
    
    print("Attempting to scrape fresh data from Microsoft Learn...")
    success = scrape_all(output)
    
    if not success:
        if os.path.exists(baseline):
            print(f"\nFalling back to baseline data: {baseline}")
            # Copy baseline to output
            with open(baseline, "r", encoding="utf-8") as f:
                data = json.load(f)
            with open(output, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            total = sum(len(d["parts"]) for d in data["devices"])
            print(f"Using baseline: {len(data['devices'])} devices, {total} parts")
        else:
            print("ERROR: No baseline data available and scraping failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
