#!/usr/bin/env python3
import json
import argparse
import sys
import textwrap
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional


def first_byte_prefix(public_key: str) -> str:
    """Return the first byte (two hex chars) in uppercase."""
    if not public_key or len(public_key) < 2:
        return ""
    return public_key[:2].upper()


def is_hex(s: str) -> bool:
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def wrap_hex(h: str, width: int) -> str:
    """Optionally wrap a hex string to multiple lines."""
    if width <= 0:
        return h
    return "\n".join(textwrap.wrap(h, width=width))


def sanitize_name(raw: str) -> str:
    """
    Make the repeater name safe for markdown table output.

    Rule:
    - Replace '|' with '/' so we don't break markdown table cells.

    We do NOT:
    - remove emoji or unicode
    - collapse spaces
    - strip anything else
    """
    if raw is None:
        raw = ""
    return raw.replace("|", "/")


def load_height_map(csv_path: Optional[str]) -> Dict[str, str]:
    """
    Load optional height CSV mapping public_key -> height_m.

    We tolerate header variations by normalizing them.

    Expected human headers in the CSV (case/space tolerant, BOM tolerant):
      - "Public Key"
      - "Antenna Height Above Ground (m)"

    Returns a dict:
        { "<public_key_hex>": "<height_string or ''>" }
    """
    height_map: Dict[str, str] = {}

    if not csv_path:
        return height_map

    try:
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)

            # Normalise header names so we can deal with spacing/case/BOM differences.
            def norm(s: str) -> str:
                return (
                    s.strip()
                     .lstrip("\ufeff")  # handle BOM if present
                     .lower()
                     .replace(" ", "")
                )

            header_map = {norm(h): h for h in (reader.fieldnames or [])}

            # Identify actual column names in the file.
            public_key_header = None
            for candidate in [
                "publickey",           # "Public Key"
            ]:
                if candidate in header_map:
                    public_key_header = header_map[candidate]
                    break

            height_header = None
            for candidate in [
                "antennaheightaboveground(m)",  # "Antenna Height Above Ground (m)"
                "antennaheightaboveground",     # fallback if someone drops (m)
                "heightaboveground",            # legacy naming
            ]:
                if candidate in header_map:
                    height_header = header_map[candidate]
                    break

            if public_key_header is None:
                print(
                    "Warning: couldn't find 'Public Key' column in height CSV headers:",
                    reader.fieldnames,
                    file=sys.stderr,
                )
                return height_map  # cannot join heights without pubkey

            if height_header is None:
                print(
                    "Warning: couldn't find 'Antenna Height Above Ground (m)' column in height CSV headers:",
                    reader.fieldnames,
                    file=sys.stderr,
                )
                # we'll continue but all heights will remain ""

            for row in reader:
                pub_raw = (
                    (row.get(public_key_header) or "")
                    .strip()
                    .replace(" ", "")
                    .replace("\n", "")
                )
                if not pub_raw:
                    continue

                if height_header is not None:
                    height_raw = (row.get(height_header) or "").strip()
                else:
                    height_raw = ""

                height_map[pub_raw] = height_raw

    except FileNotFoundError:
        print(
            f"Warning: height CSV '{csv_path}' not found, continuing without heights",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"Warning: could not read height CSV '{csv_path}': {e}",
            file=sys.stderr,
        )

    return height_map


def _rows_from_list(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Handle list format:
    [
      {
        "name": "...",
        "public_key": "...",
        "public_key_prefix": "01",         # optional
        "last_seen": "2025-10-19T03:14Z",  # optional
        ...
      },
      ...
    ]

    We normalize into a list of dicts with consistent keys.
    """
    rows = []
    for i, item in enumerate(items, 1):
        name = (item.get("name") or "").strip()
        pub = (item.get("public_key") or "").strip().replace(" ", "").replace("\n", "")

        if not name or not pub:
            print(f"Warning: skipping item {i} (missing name or public_key)", file=sys.stderr)
            continue

        if not is_hex(pub):
            print(f"Warning: item {i} public_key is not valid hex; emitting anyway", file=sys.stderr)

        prefix = (item.get("public_key_prefix") or first_byte_prefix(pub)).upper()
        last_seen = (item.get("last_seen") or "").strip()

        rows.append({
            "public_key_prefix": prefix,
            "name": name,
            "public_key": pub,
            "last_seen": last_seen,
            "height_m": "",  # filled later from CSV
        })
    return rows


def _rows_from_dict(obj: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Handle dict format:
    {
      "<pubkey>": {
        "name": "...",
        "public_key": "<pubkey>",           # may be omitted, fallback to key
        "last_seen": "2025-10-19T03:14Z",   # optional
        "public_key_prefix": "01",          # optional
        ...
      },
      ...
    }
    """
    rows = []
    for i, (key_pub, info) in enumerate(obj.items(), 1):
        if isinstance(info, dict):
            raw_pub_in_obj = info.get("public_key") or key_pub
        else:
            raw_pub_in_obj = key_pub

        pub = str(raw_pub_in_obj).strip().replace(" ", "").replace("\n", "")

        name = ""
        last_seen = ""
        prefix = ""
        if isinstance(info, dict):
            name = (info.get("name") or "").strip()
            last_seen = (info.get("last_seen") or "").strip()
            if "public_key_prefix" in info:
                prefix = str(info["public_key_prefix"]).strip().upper()

        if not prefix:
            prefix = first_byte_prefix(pub).upper()

        if not name or not pub:
            print(f"Warning: skipping entry {i} (missing name or public_key)", file=sys.stderr)
            continue

        if not is_hex(pub):
            print(f"Warning: entry {i} public_key is not valid hex; emitting anyway", file=sys.stderr)

        rows.append({
            "public_key_prefix": prefix,
            "name": name,
            "public_key": pub,
            "last_seen": last_seen,
            "height_m": "",  # filled later from CSV
        })
    return rows


def load_rows(path: str) -> List[Dict[str, str]]:
    """
    Load entries from JSON file that is either:
      - a list of objects, OR
      - a dict keyed by public_key.

    We normalize each entry into:
    {
        "public_key_prefix": "...",
        "name": "...",
        "public_key": "...",
        "last_seen": "...",
        "height_m": ""   # will be populated from CSV if available
    }
    """
    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        return _rows_from_list(data)

    if isinstance(data, dict):
        return _rows_from_dict(data)

    raise ValueError("Data JSON must be a list or an object keyed by public_key.")


def apply_heights(rows: List[Dict[str, str]], height_map: Dict[str, str]) -> None:
    """
    Mutates rows in-place.
    For each row, if its public_key is found in height_map, set height_m.
    If not found or height blank, height_m stays "".
    """
    for r in rows:
        pub = r["public_key"]
        if pub in height_map:
            r["height_m"] = height_map[pub]


def load_meta(path: str) -> Dict[str, str]:
    """
    Load metadata with title and preamble.
    """
    with open(path, "r") as f:
        meta = json.load(f)

    title = (meta.get("title") or "").strip()
    preamble = (meta.get("preamble") or "").strip()

    if not title:
        raise ValueError("Meta JSON must include a non-empty 'title'.")
    if not preamble:
        raise ValueError("Meta JSON must include a non-empty 'preamble'.")

    return {"title": title, "preamble": preamble}


def format_as_of(date_str: str | None) -> str:
    """
    Return date formatted as '19 October 2025'.

    If --date is not provided, we use today's date from system time.
    If --date is provided but isn't ISO (YYYY-MM-DD), we just return it literally.
    """
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            return date_str
    else:
        dt = datetime.now()
    day = str(int(dt.strftime("%d")))
    return f"{day} {dt.strftime('%B %Y')}"


def table_markdown(rows: List[Dict[str, str]], wrap: int) -> str:
    """
    Convert rows to Markdown table text.

    Columns:
      public_key_prefix | name | public_key | last_seen | antenna height above ground (m)

    We sanitize only 'name' for '|' → '/'.
    """
    header = (
        "| public_key_prefix | name | public_key | last_seen | antenna height above ground (m) |\n"
        "| --- | --- | --- | --- | --- |"
    )
    body_lines = []
    for r in rows:
        safe_name = sanitize_name(r["name"])
        pubkey_cell = wrap_hex(r["public_key"], wrap)
        last_seen_cell = r.get("last_seen", "")
        height_cell = r.get("height_m", "")

        body_lines.append(
            f"| {r['public_key_prefix']} | {safe_name} | {pubkey_cell} | {last_seen_cell} | {height_cell} |"
        )

    return header + "\n" + "\n".join(body_lines) + "\n"


def build_document(title: str, preamble: str, as_of: str, table_md: str) -> str:
    """
    Assemble final markdown doc with:
    - front matter
    - 'As of <date>, <preamble>'
    - blank line
    - table
    """
    front_matter = f"---\ntitle: {title}\n---\n"
    # Two newlines after preamble = visible blank line before table
    lead = f"\nAs of {as_of}, {preamble}\n\n\n"
    return front_matter + lead + table_md


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Markdown file with title/preamble and a table "
                    "from repeater JSON and optional height CSV."
    )
    parser.add_argument(
        "data_json",
        help="Path to data JSON (either list-of-objects OR dict keyed by public_key)."
    )
    parser.add_argument(
        "meta_json",
        help="Path to meta JSON containing 'title' and 'preamble'."
    )
    parser.add_argument(
        "output_md",
        help="Path to output Markdown file."
    )
    parser.add_argument(
        "--height-csv",
        default=None,
        help="Optional CSV with columns like 'Public Key' and 'Antenna Height Above Ground (m)'."
    )
    parser.add_argument(
        "--no-sort",
        action="store_true",
        help="Do not sort rows by public_key_prefix and then name (default: sort ascending)."
    )
    parser.add_argument(
        "--wrap",
        type=int,
        default=0,
        help="Wrap public_key every N chars (default: 0 = no wrap)."
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Override date used in 'As of ...'. Accepts YYYY-MM-DD; default is today."
    )
    args = parser.parse_args()

    # 1. Load repeater rows from JSON (supports list or dict form)
    rows = load_rows(args.data_json)

    # 2. Load optional height CSV and join height into rows
    height_map = load_height_map(args.height_csv)
    apply_heights(rows, height_map)

    # 3. Sort rows unless --no-sort
    if not args.no_sort:
        rows.sort(key=lambda r: (r["public_key_prefix"], r["name"].lower()))

    # 4. Build final Markdown
    meta = load_meta(args.meta_json)
    as_of_str = format_as_of(args.date)
    table_md = table_markdown(rows, wrap=args.wrap)
    doc = build_document(meta["title"], meta["preamble"], as_of_str, table_md)

    # 5. Write output file
    with open(args.output_md, "w") as f:
        f.write(doc)

    print(f"Wrote {len(rows)} sorted rows to {args.output_md}")


if __name__ == "__main__":
    main()
