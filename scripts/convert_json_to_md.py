#!/usr/bin/env python3
import json
import argparse
import sys
import textwrap
from datetime import datetime
from typing import List, Dict

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

def load_rows(path: str) -> List[Dict]:
    """Load entries from JSON file."""
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Data JSON must be a list of objects.")
    rows = []
    for i, item in enumerate(data, 1):
        name = (item.get("name") or "").strip()
        pub = (item.get("public_key") or "").strip().replace(" ", "").replace("\n", "")
        if not name or not pub:
            print(f"Warning: skipping item {i} (missing name or public_key)", file=sys.stderr)
            continue
        if not is_hex(pub):
            print(f"Warning: item {i} public_key is not valid hex; emitting anyway", file=sys.stderr)
        prefix = (item.get("public_key_prefix") or first_byte_prefix(pub)).upper()
        rows.append({"public_key_prefix": prefix, "name": name, "public_key": pub})
    return rows

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
            return date_str
    else:
        dt = datetime.now()
    day = str(dt.strftime("%dth"))
    return f"{day} {dt.strftime('%B %Y')}"

def table_markdown(rows: List[Dict], wrap: int) -> str:
    """Convert rows to Markdown table."""
    header = "| public_key_prefix | name | public_key |\n| --- | --- | --- |"
    body_lines = []
    for r in rows:
        pubkey = wrap_hex(r["public_key"], wrap)
        body_lines.append(f"| {r['public_key_prefix']} | {r['name']} | {pubkey} |")
    return header + "\n" + "\n".join(body_lines) + "\n"

def build_document(title: str, preamble: str, as_of: str, table_md: str) -> str:
    """Combine metadata and table into a Markdown document."""
    front_matter = f"---\ntitle: {title}\n---\n"
    # Add two blank lines after preamble for readability
    lead = f"\nAs of {as_of}, {preamble}\n\n\n"
    return front_matter + lead + table_md

def main():
    parser = argparse.ArgumentParser(
        description="Generate a Markdown file with title/preamble and a table from JSON."
    )
    parser.add_argument("data_json", help="Path to data JSON (list of objects with name, public_key, optional public_key_prefix).")
    parser.add_argument("meta_json", help="Path to meta JSON containing 'title' and 'preamble'.")
    parser.add_argument("output_md", help="Path to output Markdown file.")
    parser.add_argument("--no-sort", action="store_true",
                        help="Do not sort rows by public_key_prefix and name (default: sort ascending).")
    parser.add_argument("--wrap", type=int, default=0,
                        help="Wrap public_key every N chars (default: 0 = no wrap).")
    parser.add_argument("--date", default=None,
                        help="Override date used in 'As of ...'. Accepts YYYY-MM-DD; default is today.")
    args = parser.parse_args()

    rows = load_rows(args.data_json)
    if not args.no_sort:
        # Sort first by prefix, then by name (case-insensitive)
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
