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

# Map of device display names -> (dir_slug, page_slug) for nested URL structure.
# URL pattern: {LEARN_BASE}/{dir_slug}/{page_slug}-device-information-and-service-parts
# When dir_slug == page_slug, only one URL is tried; otherwise dir_slug is tried first,
# then page_slug as fallback.
SERVICE_GUIDE_SLUGS = [
    ("Surface Laptop 5G for Business", "surface-laptop-5g-business", "surface-laptop-5g-business"),
    ("Surface Laptop 13-in", "surface-laptop-13in", "surface-laptop-13in"),
    ("Surface Laptop 7th Edition for Business", "surface-laptop-7-business", "surface-laptop-7-business"),
    ("Surface Laptop 7th Edition", "surface-laptop-7", "surface-laptop-7"),
    ("Surface Laptop 6th for Business", "surface-laptop-6", "surface-laptop-6-business"),
    ("Surface Laptop 5", "surface-laptop-5", "surface-laptop-5"),
    ("Surface Laptop 3 and Laptop 4", "surface-laptop-3-and-4", "surface-laptop-3-and-4"),
    ("Surface Laptop Studio 2", "surface-laptop-studio-2", "surface-laptop-studio-2"),
    ("Surface Laptop Studio", "surface-laptop-studio", "surface-laptop-studio"),
    ("Surface Laptop Go 3", "surface-laptop-go3", "surface-laptop-go3"),
    ("Surface Laptop Go 2", "surface-laptop-go2", "surface-laptop-go2"),
    ("Surface Laptop Go", "surface-laptop-go-removable", "surface-laptop-go-removable"),
    ("Surface Laptop SE", "surface-laptop-se", "surface-laptop-se"),
    ("Surface Pro 12-in", "surface-pro-12in", "surface-pro-12in"),
    ("Surface Pro 11th Edition with 5G and Pro 10 with 5G for Business", "surface-pro-11-with-5g-and-surface-pro-10-with-5g", "surface-pro-11-5g-and-10-5g"),
    ("Surface Pro Business 11th Edition with Intel", "surface-pro-11-business", "surface-pro-11-business"),
    ("Surface Pro 11th Edition and Pro 10 for Business", "surface-pro-11-and-pro-10-business", "surface-pro-11-and-pro-10-business"),
    ("Surface Pro 9 with 5G", "surface-pro9-5g", "surface-pro9-5g"),
    ("Surface Pro 9", "surface-pro-9", "surface-pro-9"),
    ("Surface Pro 8", "surface-pro8", "surface-pro8"),
    ("Surface Pro X", "surface-prox", "surface-prox"),
    ("Surface Pro 7+ for Business", "surface-pro7-plus-business", "surface-pro7-plus-business"),
    ("Surface Pro 7 Kickstand", "surface-pro7-kickstand-replacement", "surface-pro7-kickstand-replacement"),
    ("Surface Go 4", "surface-go-4", "surface-go-4"),
    ("Surface Go 2 and 3 Kickstand Replacement", "surface-go-2-and-3-kickstand-replacement", "surface-go-2-and-3-kickstand-replacement"),
    ("Surface Studio 2+", "surface-studio-2-plus", "surface-studio-2-plus"),
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
    """Parse HTML tables with hierarchical FRU data.

    Microsoft Learn service guide tables use a hierarchical structure:
    - Category rows: have an item number (e.g. "1", "(1)") and component name, no part number
    - Part rows: empty item, component = description/variant, with part number(s)

    Handles multiple header formats:
    - ['Item', 'Component', 'FRU/ASP Part No.', 'CRU Part No.', 'Substitute SKU']
    - ['Item', 'Component', 'SKU Part No.']
    - Legacy flat table formats
    """
    parts = []
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.I)

    for table_html in tables:
        # Extract headers
        headers = []
        thead = re.search(r'<thead[^>]*>(.*?)</thead>', table_html, re.DOTALL | re.I)
        if thead:
            header_cells = re.findall(r'<th[^>]*>(.*?)</th>', thead.group(1), re.DOTALL | re.I)
            headers = [re.sub(r'<[^>]+>', '', h).strip().lower() for h in header_cells]
        
        # If headers are empty/useless (e.g., "---" or all blank), check first body row
        headers_useful = [h for h in headers if h and h.replace('-', '').strip()]
        skip_first_body_row = False
        if not headers_useful or all(h in ('', '---', 'models', 'model') for h in headers):
            tbody = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_html, re.DOTALL | re.I)
            body_html_check = tbody.group(1) if tbody else table_html
            first_row = re.search(r'<tr[^>]*>(.*?)</tr>', body_html_check, re.DOTALL | re.I)
            if first_row:
                first_cells = re.findall(r'<td[^>]*>(.*?)</td>', first_row.group(1), re.DOTALL | re.I)
                candidate = [re.sub(r'<[^>]+>', '', c).strip().lower() for c in first_cells]
                if any('component' in c or 'part' in c for c in candidate):
                    headers = candidate
                    skip_first_body_row = True
        
        if not headers:
            first_row = re.search(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.I)
            if first_row:
                header_cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', first_row.group(1), re.DOTALL | re.I)
                headers = [re.sub(r'<[^>]+>', '', h).strip().lower() for h in header_cells]

        if not headers:
            continue

        # Skip non-FRU tables (e.g. screw maps)
        has_component = any('component' in h for h in headers)
        if not has_component:
            # Check for legacy format with 'description' or 'category' columns
            has_desc = any('description' in h or 'config' in h or 'detail' in h for h in headers)
            if not has_desc:
                continue

        # Find part number column(s)
        pn_col = None
        for i, h in enumerate(headers):
            if 'part' in h and ('number' in h or 'no' in h):
                pn_col = i
                break
            if h in ('asp', 'fru', 'service part number', 'sku part no.'):
                pn_col = i
                break

        if pn_col is None:
            continue

        # Find other columns
        comp_col = next((i for i, h in enumerate(headers) if 'component' in h), None)
        desc_col = next((i for i, h in enumerate(headers) if 'description' in h or 'config' in h or 'detail' in h), None)
        cat_col = next((i for i, h in enumerate(headers) if 'category' in h), None)
        item_col = next((i for i, h in enumerate(headers) if h == 'item'), None)
        sub_col = next((i for i, h in enumerate(headers) if 'substitute' in h or 'sub sku' in h or 'replacement' in h), None)
        # Secondary part number column (CRU)
        cru_col = next((i for i, h in enumerate(headers) if 'cru' in h and ('part' in h or 'no' in h)), None)

        # Extract body rows
        tbody = re.search(r'<tbody[^>]*>(.*?)</tbody>', table_html, re.DOTALL | re.I)
        body_html = tbody.group(1) if tbody else table_html

        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', body_html, re.DOTALL | re.I)
        if skip_first_body_row and rows:
            rows = rows[1:]  # First row was used as headers
        current_category = ""

        for row_html in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL | re.I)
            cells_clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]

            if len(cells_clean) <= pn_col:
                continue

            item_val = cells_clean[item_col] if item_col is not None and item_col < len(cells_clean) else ""
            comp_val = cells_clean[comp_col] if comp_col is not None and comp_col < len(cells_clean) else ""
            pn_val = cells_clean[pn_col]

            # Category header row: has item number but no part number
            is_category_row = bool(re.match(r'^\(?(\d+)\)?$', item_val)) and not pn_val
            if is_category_row:
                current_category = comp_val
                continue

            # Part data row: has a part number
            if not pn_val or not re.match(r'^[A-Z0-9]', pn_val):
                # Try CRU column as fallback
                if cru_col is not None and cru_col < len(cells_clean):
                    pn_val = cells_clean[cru_col]
                if not pn_val or not re.match(r'^[A-Z0-9]', pn_val):
                    continue

            if pn_val.lower() in ('part number', 'asp', 'fru', 'n/a'):
                continue

            # Build description and category
            if desc_col is not None and desc_col < len(cells_clean):
                description = cells_clean[desc_col]
            elif comp_col is not None and comp_col < len(cells_clean):
                description = comp_val
            else:
                description = ""

            if cat_col is not None and cat_col < len(cells_clean):
                category = cells_clean[cat_col]
            else:
                category = current_category

            sub_val = cells_clean[sub_col] if sub_col is not None and sub_col < len(cells_clean) else ""

            part = {"part_number": pn_val, "description": description, "category": category}
            if sub_val:
                part["substitute"] = sub_val
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


def _try_url(url):
    """Try fetching parts from a URL (HTML then markdown fallback)."""
    html = fetch_url(url)
    if html and '<table' in html:
        parts = parse_html_tables(html)
        if parts:
            return parts

    # Try with ?accept=text/markdown as secondary attempt
    md_url = f"{url}?accept=text/markdown"
    md = fetch_url(md_url)
    if md and '|' in md and '---' in md:
        parts = parse_markdown_tables(md)
        if parts:
            return parts

    return []


def scrape_device(device_name, dir_slug, page_slug):
    """Try to scrape a single device using nested URL patterns.

    Tries {dir_slug}/{page_slug}-device-information-and-service-parts first
    (since page_slug is the known-correct slug from the hub page).
    Falls back to {dir_slug}/{dir_slug}-... if they differ.
    """
    suffix = "-device-information-and-service-parts"

    # Primary: use page_slug (matches the hub page link pattern)
    primary_url = f"{LEARN_BASE}/{dir_slug}/{page_slug}{suffix}"
    parts = _try_url(primary_url)
    if parts:
        return parts

    # Fallback: try dir_slug as page name if it differs
    if page_slug != dir_slug:
        fallback_url = f"{LEARN_BASE}/{dir_slug}/{dir_slug}{suffix}"
        time.sleep(1)  # Rate limiting between attempts
        parts = _try_url(fallback_url)
        if parts:
            return parts

    return []


def scrape_all(output_path):
    """Scrape all service guide pages and save to JSON."""
    all_devices = []
    success_count = 0
    
    for device_name, dir_slug, page_slug in SERVICE_GUIDE_SLUGS:
        print(f"Fetching {device_name}...", end=" ", flush=True)
        parts = scrape_device(device_name, dir_slug, page_slug)
        
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
