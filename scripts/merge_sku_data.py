#!/usr/bin/env python3
"""Merge SKU data from sku_matrix_data.json into docs/index.html.

Reads the Excel-sourced JSON, maps device names to existing HTML device names,
and inserts new SKUs / box contents into the DATA and BOX_CONTENTS objects.
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
HTML_PATH = os.path.join(ROOT_DIR, "docs", "index.html")
JSON_PATH = os.path.join(SCRIPT_DIR, "sku_matrix_data.json")

# SKU format: 2-5 alphanumeric chars, dash, 5 digits
SKU_PATTERN = re.compile(r"^[A-Za-z0-9]{2,5}-\d{5}$")

# Maps Excel short device names → HTML device names.
# Multiple Excel names can map to the same HTML name.
DEVICE_NAME_MAP = {
    # Pro series
    "Pro 7": "Surface Pro 7 Kickstand",
    "Pro 7+": "Surface Pro 7 Kickstand",
    "Pro 8": "Surface Pro 8",
    "Pro 9": "Surface Pro 9",
    "Pro 9 5G": "Surface Pro 9 with 5G",
    "Pro X": "Surface Pro X",
    "Pro 10 for Business": "Surface Pro 11th Edition and Pro 10 for Business",
    "Surface Pro, 11th Edition": "Surface Pro 11th Edition and Pro 10 for Business",
    "Surface Pro, 11th Edition for Business": "Surface Pro Business 11th Edition with Intel",
    "Surface Pro, 12-inch": "Surface Pro 12-in",
    "Surface Pro 5G, 11th Edition": "Surface Pro 11th Edition with 5G and Pro 10 with 5G for Business",
    "Surface Pro 10 for Business 5G": "Surface Pro 11th Edition with 5G and Pro 10 with 5G for Business",
    # Laptop series
    "Laptop 3 Intel 13\"": "Surface Laptop 3 and Laptop 4",
    "Laptop 3 Intel 15\"": "Surface Laptop 3 and Laptop 4",
    "Laptop 4 Intel 13''": "Surface Laptop 3 and Laptop 4",
    "Laptop 4 AMD 13''": "Surface Laptop 3 and Laptop 4",
    "Laptop 4 Intel 15\"": "Surface Laptop 3 and Laptop 4",
    "Laptop 5 Intel 13\"": "Surface Laptop 5",
    "Laptop 5 Intel 15\"": "Surface Laptop 5",
    "Laptop 6 for Business Intel 13\"": "Surface Laptop 6th for Business",
    "Laptop 6 for Business Intel 15\"": "Surface Laptop 6th for Business",
    "Surface Laptop 7th Edition 13\"": "Surface Laptop 7th Edition",
    "Surface Laptop 7th Edition 15\"": "Surface Laptop 7th Edition",
    "Surface Laptop 7th Edition 13\" For Business": "Surface Laptop 7th Edition for Business",
    "Surface Laptop 7th Edition 15\" For Business": "Surface Laptop 7th Edition for Business",
    "Surface Laptop, 13-inch": "Surface Laptop 13-in",
    "Surface Laptop 5G for Business (13\")": "Surface Laptop 5G for Business",
    # Laptop Go / SE / Studio
    "Laptop Go 2": "Surface Laptop Go 2",
    "Laptop Go 3": "Surface Laptop Go 3",
    "Laptop SE": "Surface Laptop SE",
    "Laptop Studio": "Surface Laptop Studio",
    "Laptop Studio 2": "Surface Laptop Studio 2",
    # Studio / Go
    "Studio 2+": "Surface Studio 2+",
    "Go 2/Go 3": "Surface Go 4",  # Go 2/Go 3 kickstands — closest existing device
    "Go 4": "Surface Go 4",
}


def extract_js_object(html: str, var_name: str):
    """Extract a JS object assigned to `const <var_name> = {...};` from HTML.

    Returns (parsed_object, start_of_json, end_of_json) where start/end are
    byte offsets into *html* marking the JSON literal (excluding the trailing ;).
    """
    pattern = re.compile(rf"const\s+{re.escape(var_name)}\s*=\s*")
    m = pattern.search(html)
    if not m:
        raise ValueError(f"Could not find 'const {var_name} = ...' in HTML")

    json_start = m.end()

    # Walk forward to find the matching closing brace
    depth = 0
    in_string = False
    escape_next = False
    i = json_start
    while i < len(html):
        ch = html[i]
        if escape_next:
            escape_next = False
            i += 1
            continue
        if ch == "\\":
            escape_next = True
            i += 1
            continue
        if ch == '"':
            in_string = not in_string
        elif not in_string:
            if ch == "{" or ch == "[":
                depth += 1
            elif ch == "}" or ch == "]":
                depth -= 1
                if depth == 0:
                    json_end = i + 1
                    raw_json = html[json_start:json_end]
                    obj = json.loads(raw_json)
                    return obj, json_start, json_end
        i += 1

    raise ValueError(f"Could not find closing brace for 'const {var_name}'")


def clean_text(s: str) -> str:
    """Remove zero-width spaces and normalize whitespace."""
    return s.replace("\u200b", "").strip()


def main():
    # ── Load files ──────────────────────────────────────────────────────
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        excel_data = json.load(f)

    # ── Extract current DATA and BOX_CONTENTS ───────────────────────────
    data_obj, data_start, data_end = extract_js_object(html, "DATA")
    box_obj, _, _ = extract_js_object(html, "BOX_CONTENTS")

    devices = data_obj["devices"]       # list of {id, name, pdf_file, part_count}
    parts = data_obj["parts"]           # list of part dicts

    # Build lookups
    device_name_set = {d["name"] for d in devices}
    device_by_name = {d["name"]: d for d in devices}
    existing_skus = set()  # (part_number, device_name) tuples
    for p in parts:
        existing_skus.add((p["part_number"], p["device_name"]))

    max_part_id = max(p["id"] for p in parts)
    next_part_id = max_part_id + 1

    # ── Build validated device-name mapping ─────────────────────────────
    resolved_map: dict[str, str | None] = {}
    unmapped_devices: list[str] = []

    for excel_name in excel_data.get("devices", {}):
        if excel_name in DEVICE_NAME_MAP:
            html_name = DEVICE_NAME_MAP[excel_name]
            if html_name in device_name_set:
                resolved_map[excel_name] = html_name
            else:
                # Try fuzzy fallback: maybe the exact name is already a full Surface name
                resolved_map[excel_name] = None
                unmapped_devices.append(
                    f"  {excel_name!r} -> mapped to {html_name!r} but NOT found in DATA.devices"
                )
        else:
            # Not in static map — check if the Excel name itself is a device name
            if excel_name in device_name_set:
                resolved_map[excel_name] = excel_name
            elif f"Surface {excel_name}" in device_name_set:
                resolved_map[excel_name] = f"Surface {excel_name}"
            else:
                resolved_map[excel_name] = None
                unmapped_devices.append(
                    f"  {excel_name!r} -> no mapping found in DATA.devices"
                )

    # ── Merge parts and box contents ────────────────────────────────────
    added_parts = 0
    skipped_invalid_sku = 0
    skipped_existing = 0
    added_box = 0
    updated_box = 0
    skipped_device = 0

    for excel_device, device_info in excel_data.get("devices", {}).items():
        html_device_name = resolved_map.get(excel_device)
        if html_device_name is None:
            # Count skipped parts for reporting
            for part in device_info.get("parts", []):
                sku = part.get("sku", "")
                if SKU_PATTERN.match(sku):
                    skipped_device += 1
            continue

        device_entry = device_by_name[html_device_name]
        device_id = device_entry["id"]

        for part in device_info.get("parts", []):
            sku = part.get("sku", "")
            description = part.get("description", "")
            category = part.get("category", "")
            box_contents = part.get("box_contents", "")

            # Validate SKU format
            if not SKU_PATTERN.match(sku):
                skipped_invalid_sku += 1
                continue

            # ── Add to DATA.parts if new ────────────────────────────────
            if (sku, html_device_name) not in existing_skus:
                new_part = {
                    "id": next_part_id,
                    "device_id": device_id,
                    "part_number": sku,
                    "description": description,
                    "component_category": category,
                    "config_detail": html_device_name,
                    "device_name": html_device_name,
                }
                parts.append(new_part)
                existing_skus.add((sku, html_device_name))
                next_part_id += 1
                added_parts += 1
            else:
                skipped_existing += 1

            # ── Update BOX_CONTENTS ─────────────────────────────────────
            if box_contents:
                clean_new = clean_text(box_contents)
                if sku not in box_obj:
                    box_obj[sku] = clean_new
                    added_box += 1
                else:
                    clean_old = clean_text(box_obj[sku])
                    if clean_old != clean_new:
                        box_obj[sku] = clean_new
                        updated_box += 1

    # ── Update part_count on each device ────────────────────────────────
    count_by_device = {}
    for p in parts:
        dn = p["device_name"]
        count_by_device[dn] = count_by_device.get(dn, 0) + 1
    for d in devices:
        d["part_count"] = count_by_device.get(d["name"], 0)

    data_obj["devices"] = devices
    data_obj["parts"] = parts

    # ── Write back into HTML ────────────────────────────────────────────
    new_data_json = json.dumps(data_obj, indent=2, ensure_ascii=False)
    html = html[:data_start] + new_data_json + html[data_end:]

    # Re-find BOX_CONTENTS (positions shifted after DATA replacement)
    box_obj_sorted = dict(sorted(box_obj.items()))
    new_box_json = json.dumps(box_obj_sorted, indent=2, ensure_ascii=False)

    _, box_start2, box_end2 = extract_js_object(html, "BOX_CONTENTS")
    html = html[:box_start2] + new_box_json + html[box_end2:]

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    # ── Summary ─────────────────────────────────────────────────────────
    print("=" * 60)
    print("  SKU Data Merge — Summary")
    print("=" * 60)
    print(f"  Parts added to DATA:           {added_parts}")
    print(f"  Parts already existing:        {skipped_existing}")
    print(f"  Parts skipped (invalid SKU):   {skipped_invalid_sku}")
    print(f"  Parts skipped (unmapped dev):  {skipped_device}")
    print(f"  BOX_CONTENTS entries added:    {added_box}")
    print(f"  BOX_CONTENTS entries updated:  {updated_box}")
    print(f"  Total parts now in DATA:       {len(parts)}")
    print(f"  Total BOX_CONTENTS entries:    {len(box_obj)}")
    print()

    if unmapped_devices:
        print("⚠ Unmapped Excel devices (skipped):")
        for msg in unmapped_devices:
            print(msg)
        print()

    print("✓ docs/index.html updated successfully.")


if __name__ == "__main__":
    main()
