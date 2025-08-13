import json
import csv
from typing import Any, Dict, List
from collections.abc import Mapping

def _flatten(obj: Any, prefix: str = "") -> Dict[str, Any]:
    """
    Recursively flatten a nested dict into dot-notated keys.
    Lists/tuples are converted to JSON strings.
    Non-dict primitives are returned as-is.
    """
    out: Dict[str, Any] = {}
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, Mapping):
                out.update(_flatten(v, key))
            elif isinstance(v, (list, tuple)):
                # Represent lists as JSON strings (so CSV cell keeps content)
                out[key] = json.dumps(v, ensure_ascii=False)
            else:
                out[key] = v
    else:
        # Not a dict (primitive or list) — put it under the prefix key
        out[prefix] = json.dumps(obj, ensure_ascii=False) if isinstance(obj, (list, tuple)) else obj
    return out

def json_to_csv(input_file: str, output_file: str, encoding: str = "utf-8") -> int:
    """
    Convert a JSON file to CSV.

    - input_file: path to the .json file (root can be a list or single object)
    - output_file: path to write the .csv file
    - encoding: file encoding for both read and write (default utf-8)

    Returns the number of rows written (excluding header).
    """
    # Load JSON
    with open(input_file, "r", encoding=encoding) as f:
        data = json.load(f)

    # If root is a dict, try to find a list inside; otherwise treat as single record
    if isinstance(data, Mapping):
        # find first list value (common case: {"items": [...]})
        list_value = None
        for v in data.values():
            if isinstance(v, list):
                list_value = v
                break
        records: List[Dict[str, Any]]
        if list_value is not None:
            records = list_value
        else:
            # single object -> one record
            records = [data]
    elif isinstance(data, list):
        records = data
    else:
        # primitive at root -> write single row with key "value"
        records = [{"value": data}]

    # Flatten and collect headers
    flattened: List[Dict[str, Any]] = []
    fieldnames_set = set()
    for rec in records:
        if not isinstance(rec, Mapping):
            # non-dict entries (e.g., list of strings) -> wrap
            rec = {"value": rec}
        flat = _flatten(rec)
        flattened.append(flat)
        fieldnames_set.update(flat.keys())

    fieldnames = sorted(fieldnames_set)

    # Write CSV
    with open(output_file, "w", newline="", encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in flattened:
            # Ensure every field present (DictWriter will fill missing with None -> empty)
            writer.writerow({k: (row.get(k) if row.get(k) is not None else "") for k in fieldnames})

    return len(flattened)


from langchain.tools import Tool
json_to_csv_tool = Tool(
    name="json_to_csv",
    func=json_to_csv,
    description="Converts a JSON file to CSV format. Parameters: input_file (str), output_file (str), encoding (str). Returns the number of rows written."
)


# Example usage:
if __name__ == "__main__":
    n = json_to_csv("data.json", "data.csv")
    print(f"Wrote {n} rows to data.csv")
