#!/usr/bin/env python3
"""Build DATA and CATALOG from scraped service guide JSON, validate all
dimension extractors, apply known data fixes, and update the HTML file.

Exit codes:
  0 = success, HTML updated
  1 = fatal error (missing data, broken HTML structure)
  2 = validation warnings (HTML updated but issues found)
"""

import json
import re
import sys
import os

# ── Configuration ──

SKIP_DEVICES = {
    "Surface Laptop Go",
    "Surface Pro 7+ for Business",
    "Surface Go 2 and 3 Kickstand Replacement",
}

CATALOG_GROUPS = [
    ("Surface Laptop", [
        "Surface Laptop 5G for Business",
        "Surface Laptop 13-in",
        "Surface Laptop 7th Edition for Business",
        "Surface Laptop 7th Edition",
        "Surface Laptop 6th for Business",
        "Surface Laptop 5",
        "Surface Laptop 3 and Laptop 4",
        "Surface Laptop Go 3",
        "Surface Laptop Go 2",
        "Surface Laptop SE",
    ]),
    ("Surface Laptop Studio", [
        "Surface Laptop Studio 2",
        "Surface Laptop Studio",
    ]),
    ("Surface Pro", [
        "Surface Pro 12-in",
        "Surface Pro 11th Edition with 5G and Pro 10 with 5G for Business",
        "Surface Pro Business 11th Edition with Intel",
        "Surface Pro 11th Edition and Pro 10 for Business",
        "Surface Pro 9 with 5G",
        "Surface Pro 9",
        "Surface Pro 8",
        "Surface Pro X",
        "Surface Pro 7 Kickstand",
    ]),
    ("Surface Go", [
        "Surface Go 4",
    ]),
    ("Surface Studio", [
        "Surface Studio 2+",
    ]),
]

# ── Known data fixes ──
# Dict of (device_name, part_number) -> {field: new_value}
DATA_FIXES = {
    # Laptop 13-in PCBA descriptions missing "GB" suffix
    ("Surface Laptop 13-in", "EP2-35079"): {"description": "16GB"},
    ("Surface Laptop 13-in", "EP2-35080"): {"description": "24GB"},
}

# ── Dimension extractors (mirrors the JS logic) ──

COLORS = [
    'Battleship (Green)', 'Matte Black', 'Cobalt Blue', 'Ice Blue', 'Poppy Red',
    'Platinum', 'Graphite', 'Sapphire', 'Sandstone', 'Black',
    'Dune', 'Sage', 'Forest', 'Silver', 'Ocean', 'Violet'
]

FIVE_G_CODES = ['AOC', 'APAC', 'EOC1', 'EOC2']


def extract_processor(desc):
    if re.search(r'\bElite\b', desc, re.I): return 'X Elite'
    if re.search(r'\bPlus\b', desc, re.I): return 'X Plus'
    if re.search(r'\bUltra\s*7\b', desc, re.I): return 'Intel Core Ultra 7'
    if re.search(r'\bUltra\s*5\b', desc, re.I): return 'Intel Core Ultra 5'
    if re.search(r'\bi7\b', desc, re.I): return 'Intel Core i7'
    if re.search(r'\bi5\b', desc, re.I): return 'Intel Core i5'
    if re.search(r'\bi3\b', desc, re.I): return 'Intel Core i3'
    return None


def extract_memory(desc):
    m = re.search(r'\b(4|8|16|24|32|64)\s*GB\b(?!\s*(?:Storage|SSD|rSSD))', desc, re.I)
    return m.group(1) + ' GB' if m else None


def extract_storage(desc):
    m = re.search(r'\b(128|256|512)\s*GB\b', desc, re.I)
    if m: return m.group(1) + ' GB'
    t = re.search(r'\b([12])\s*TB\b', desc, re.I)
    if t: return t.group(1) + ' TB'
    if re.search(r'\b64\s*GB\s*Storage', desc, re.I): return '64 GB'
    return None


def extract_color(desc):
    dl = desc.lower()
    for c in COLORS:
        if c.lower() in dl: return c
    return None


def extract_fiveg(desc):
    for code in FIVE_G_CODES:
        if re.search(r'\b' + code + r'\s*$', desc): return code
    if re.search(r'\bChina\s*$', desc): return 'China'
    if re.search(r'\bJapan\s*$', desc): return 'Japan'
    return None


def extract_edition(desc):
    if re.search(r'\bCommercial\b', desc, re.I): return 'Commercial'
    if re.search(r'\bConsumer\b', desc, re.I): return 'Consumer'
    return None


def extract_size(desc):
    m = re.search(r'\b(10\.5|13\.?[58]?|15|12\.?[34]?)(?!\d)', desc, re.I)
    if not m:
        m2 = re.search(r'\b(10|12|13|15)-inch\b', desc, re.I)
        return m2.group(1) + '"' if m2 else None
    v = m.group(1)
    if v in ('13','138','13.8'): return '13.8"' if '.' in v or v == '138' else '13"'
    if v in ('135','13.5'): return '13.5"'
    if v == '15': return '15"'
    if v == '10.5': return '10.5"'
    return v + '"'


EXTRACTORS = {
    'processor': extract_processor,
    'memory': extract_memory,
    'storage': extract_storage,
    'color': extract_color,
    'fiveG': extract_fiveg,
    'edition': extract_edition,
    'size': extract_size,
}


# ── Build functions ──

def build_data_and_catalog(scraped):
    """Build DATA and CATALOG objects from scraped JSON."""
    devices_raw = [d for d in scraped["devices"]
                   if d["name"] not in SKIP_DEVICES and len(d["parts"]) > 0]

    name_to_raw = {d["name"]: d for d in devices_raw}

    # Assign IDs in catalog order
    catalog_names = []
    for _, names in CATALOG_GROUPS:
        for name in names:
            if name in name_to_raw:
                catalog_names.append(name)

    # Append any new devices not yet in catalog groups
    catalog_set = set(catalog_names)
    new_devices = []
    for d in devices_raw:
        if d["name"] not in catalog_set:
            new_devices.append(d["name"])
            catalog_names.append(d["name"])

    device_id_map = {}
    devices_out = []
    for i, name in enumerate(catalog_names, 1):
        d = name_to_raw[name]
        device_id_map[name] = i
        devices_out.append({
            "id": i,
            "name": name,
            "pdf_file": "",
            "part_count": len(d["parts"]),
        })

    # Build parts
    parts_out = []
    pid = 1
    for name in catalog_names:
        d = name_to_raw[name]
        dev_id = device_id_map[name]
        for p in d["parts"]:
            part = {
                "id": pid,
                "device_id": dev_id,
                "part_number": p["part_number"],
                "description": p["description"],
                "component_category": p.get("category", ""),
                "config_detail": name,
                "device_name": name,
            }
            if p.get("substitute"):
                part["substitute"] = p["substitute"]

            # Apply known fixes
            fix_key = (name, p["part_number"])
            if fix_key in DATA_FIXES:
                for field, value in DATA_FIXES[fix_key].items():
                    part[field] = value

            parts_out.append(part)
            pid += 1

    data_obj = {"devices": devices_out, "parts": parts_out}

    # Build CATALOG with correct field names (family/deviceId)
    catalog_out = []
    for group_name, names in CATALOG_GROUPS:
        items = []
        for name in names:
            if name in device_id_map:
                items.append({"deviceId": device_id_map[name], "name": name})
        if items:
            catalog_out.append({"family": group_name, "items": items})

    # Add uncategorized devices
    if new_devices:
        items = [{"deviceId": device_id_map[n], "name": n} for n in new_devices]
        catalog_out.append({"family": "Other", "items": items})

    return data_obj, catalog_out, new_devices


def update_html(html_path, data_obj, catalog_out):
    """Replace DATA and CATALOG in the HTML file."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    data_json = json.dumps(data_obj, ensure_ascii=False, separators=(",", ":"))
    catalog_json = json.dumps(catalog_out, ensure_ascii=False, separators=(",", ":"))

    lines = html.split("\n")
    new_lines = []
    replaced_data = False
    replaced_catalog = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("const DATA = ") and not replaced_data:
            new_lines.append(f"const DATA = {data_json};")
            replaced_data = True
        elif stripped.startswith("const CATALOG = ") and not replaced_catalog:
            new_lines.append(f"const CATALOG = {catalog_json};")
            replaced_catalog = True
        else:
            new_lines.append(line)

    if not replaced_data:
        print("ERROR: Could not find 'const DATA = ' in HTML!")
        sys.exit(1)
    if not replaced_catalog:
        print("ERROR: Could not find 'const CATALOG = ' in HTML!")
        sys.exit(1)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    return True


# ── Validation ──

def validate(data_obj):
    """Run logic checks on the data. Returns (errors, warnings)."""
    errors = []
    warnings = []
    devices = data_obj["devices"]
    parts = data_obj["parts"]
    dev_map = {d["id"]: d["name"] for d in devices}

    for d in devices:
        did = d["id"]
        dname = d["name"]
        dparts = [p for p in parts if p["device_id"] == did]

        if not dparts:
            warnings.append(f"[{dname}] 0 parts")
            continue

        # Check each part
        dim_values = {}
        for ext_name in EXTRACTORS:
            dim_values[ext_name] = set()

        for p in dparts:
            desc = p["description"]
            cat = p["component_category"].lower()

            for ext_name, extractor in EXTRACTORS.items():
                val = extractor(desc)
                if val:
                    dim_values[ext_name].add(val)

            # Check: memory values > 64GB are suspicious
            mem = extract_memory(desc)
            if mem and int(mem.split()[0]) > 64:
                errors.append(f"[{dname}] Suspicious memory value: {p['part_number']} '{desc}' => {mem}")

            # Check: keyboard/keyset parts should ideally have a color or region tag
            if ('keyboard' in cat or 'keyset' in cat or 'c cover' in cat):
                color = extract_color(desc)
                if not color and not re.search(r'\b(104|105|106|109)\b', desc):
                    warnings.append(f"[{dname}] Keyboard part with no color/key-count: {p['part_number']} '{desc}'")

            # Check: empty description
            if not desc.strip():
                errors.append(f"[{dname}] Empty description: {p['part_number']}")

            # Check: empty category
            if not p["component_category"].strip():
                warnings.append(f"[{dname}] Empty category: {p['part_number']} '{desc}'")

        # Report selectors that will appear
        selectors = {k: sorted(v) for k, v in dim_values.items() if len(v) > 1}
        if selectors:
            for k, v in selectors.items():
                if len(v) > 20:
                    warnings.append(f"[{dname}] {k} has {len(v)} values (may be too many for a selector)")

    # Cross-device checks
    total_parts = len(parts)
    if total_parts < 100:
        errors.append(f"Only {total_parts} total parts — expected 1000+")

    active_devices = sum(1 for d in devices if any(p["device_id"] == d["id"] for p in parts))
    if active_devices < 15:
        errors.append(f"Only {active_devices} active devices — expected 15+")

    return errors, warnings


def verify_html(html_path):
    """Verify the HTML file structure after update."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    checks = {
        "const DATA =": "const DATA =" in html,
        "const BOX_CONTENTS =": "const BOX_CONTENTS =" in html,
        "const CATALOG =": "const CATALOG =" in html,
        "const DIMENSIONS =": "const DIMENSIONS =" in html,
        "const KB_PATTERNS =": "const KB_PATTERNS =" in html,
    }

    all_ok = True
    for label, ok in checks.items():
        status = "OK" if ok else "MISSING!"
        print(f"  {label}: {status}")
        if not ok:
            all_ok = False

    # Parse DATA from file to verify
    m = re.search(r'const DATA\s*=\s*', html)
    if m:
        start = m.end()
        semi = html.find(';\n', start)
        try:
            data = json.loads(html[start:semi])
            print(f"  Devices in file: {len(data['devices'])}")
            print(f"  Parts in file: {len(data['parts'])}")
        except json.JSONDecodeError as e:
            print(f"  ERROR parsing DATA: {e}")
            all_ok = False

    print(f"  File size: {len(html):,} bytes")
    return all_ok


# ── Main ──

def main():
    if len(sys.argv) < 3:
        print("Usage: build_and_validate.py <scraped_json> <html_file>")
        sys.exit(1)

    json_path = sys.argv[1]
    html_path = sys.argv[2]

    # Load scraped data
    print(f"Loading scraped data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        scraped = json.load(f)

    total_scraped = sum(len(d["parts"]) for d in scraped["devices"])
    print(f"  {len(scraped['devices'])} devices, {total_scraped} parts")

    # Build DATA and CATALOG
    print("\nBuilding DATA and CATALOG...")
    data_obj, catalog_out, new_devices = build_data_and_catalog(scraped)
    print(f"  {len(data_obj['devices'])} active devices, {len(data_obj['parts'])} parts")

    if new_devices:
        print(f"  NEW devices not in catalog: {new_devices}")
        print("  → Added to 'Other' group. Update CATALOG_GROUPS in this script to categorize them.")

    # Validate
    print("\nRunning validation...")
    errors, warnings = validate(data_obj)

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    {e}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    {w}")

    if not errors:
        print("\n  ✓ No errors found")

    # Update HTML
    print(f"\nUpdating {html_path}...")
    update_html(html_path, data_obj, catalog_out)

    # Verify HTML structure
    print("\nVerifying HTML structure...")
    html_ok = verify_html(html_path)

    if not html_ok:
        print("\nFAILED: HTML structure verification failed!")
        sys.exit(1)

    if errors:
        print(f"\nCOMPLETED WITH {len(errors)} ERRORS — review needed")
        sys.exit(2)

    print(f"\nSUCCESS: HTML updated with {len(data_obj['parts'])} parts across {len(data_obj['devices'])} devices")
    sys.exit(0)


if __name__ == "__main__":
    main()
