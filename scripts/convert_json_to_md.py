#!/usr/bin/env python3
import json
import argparse
import sys
import textwrap
from datetime import datetime
from typing import List, Dict, Any

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

def _rows_from_list(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Handle old format: [ {name, public_key, [public_key_prefix], [last_seen], ... }, ... ]"""
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
        })
    return rows

def _rows_from_dict(obj: Dict[str, Any]) -> List[Dict[str, str]]:
    """Handle new format:
    {
      "<pubkey>": {
        "name": "...",
        "public_key": "<pubkey>",
        "last_seen": "2025-10-19T03:14:07Z",   # optional
        "public_key_prefix": "01"             # optional
      },
      ...
    }
    """
    rows = []
    for i, (key_pub, info) in enumerate(obj.items(), 1):
        # Prefer info["public_key"], fall back to key
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
        })
    return rows

def load_rows(path: str) -> List[Dict[str, str]]:
    """Load entries from JSON file that is either:
       - a list of objects, OR
       - a dict keyed by public_key.
    Normalizes each entry to {
        "public_key_prefix": "...",
        "name": "...",
        "public_key": "...",
        "last_seen": "..." (may be "")
    }
    """
    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        return _rows_from_list(data)

    if isinstance(data, dict):
        return _rows_from_dict(data)

    raise ValueError("Data JSON must be a list or an object keyed by public_key.")

def load_meta(path: str) -> Dict[str, str]:
    """Load metadata with title and preamble."""
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
    """Return date formatted as '19 October 2025'."""
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            # If user gave a non-ISO string, just use it literally
            return date_str
    else:
        dt = datetime.now()
    day = str(int(dt.strftime("%d")))
    return f"{day} {dt.strftime('%B %Y')}"

def table_markdown(rows: List[Dict[str, str]], wrap: int) -> str:
    """Convert rows to Markdown table text, including last_seen."""
    header = (
        "| public_key_prefix | name | public_key | last_seen |\n"
        "| --- | --- | --- | --- |"
    )
    body_lines = []
    for r in rows:
        pubkey_cell = wrap_hex(r["public_key"], wrap)
        last_seen_cell = r.get("last_seen", "")
        body_lines.append(
            f"| {r['public_key_prefix']} | {r['name']} | {pubkey_cell} | {last_seen_cell} |"
        )
    return header + "\n" + "\n".join(body_lines) + "\n"

def build_document(title: str, preamble: str, as_of: str, table_md: str) -> str:
    """Assemble final markdown doc with front matter, preamble, spacing."""
    front_matter = f"---\ntitle: {title}\n---\n"
    # Two blank lines after preamble => visual gap before table
    lead = f"\nAs of {as_of}, {preamble}\n\n\n"
    return front_matter + lead + table_md

def main():
    parser = argparse.ArgumentParser(
        description="Generate a Markdown file with title/preamble and a table from JSON."
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

    rows = load_rows(args.data_json)

    # Default sort: prefix asc, then name asc (case-insensitive)
    if not args.no_sort:
        rows.sort(key=lambda r: (r["public_key_prefix"], r["name"].lower()))

    meta = load_meta(args.meta_json)
    as_of_str = format_as_of(args.date)
    table_md = table_markdown(rows, wrap=args.wrap)
    doc = build_document(meta["title"], meta["preamble"], as_of_str, table_md)

    with open(args.output_md, "w") as f:
        f.write(doc)

    print(f"Wrote {len(rows)} sorted rows to {args.output_md}")

if __name__ == "__main__":
    main()
