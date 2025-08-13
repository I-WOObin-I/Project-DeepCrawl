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

def json_to_csv_json(json_params):
    """
    Convert a JSON file to CSV.

    Accepts a dict or JSON string with keys:
      - input_file: path to the .json file (root can be a list or single object)
      - output_file: path to write the .csv file
      - encoding: file encoding for both read and write (default utf-8)

    Returns the number of rows written (excluding header).
    """
    # Parse json_params if string
    if isinstance(json_params, str):
        json_params = json.loads(json_params)

    input_file = json_params.get("input_file")
    output_file = json_params.get("output_file")
    encoding = json_params.get("encoding", "utf-8")

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
            writer.writerow({k: (row.get(k) if row.get(k) is not None else "") for k in fieldnames})

    return len(flattened)


from langchain.tools import Tool
from pydantic import BaseModel, Field

class JsonToCsvArgs(BaseModel):
    json_params: dict = Field(..., description="JSON object containing 'input_file' (str), 'output_file' (str), and optional 'encoding' (str).")

json_to_csv_tool = Tool(
    name="json_to_csv_tool",
    func=json_to_csv_json,
    description="Converts a JSON file to CSV format. Accepts a JSON object with keys: input_file (str), output_file (str), encoding (str, optional). Returns the number of rows written.",
    # args_schema=JsonToCsvArgs,
)

# Example usage:
if __name__ == "__main__":
    # Example with dict:
    params = {
        "input_file": "data.json",
        "output_file": "data.csv",
        "encoding": "utf-8"
    }
    n = json_to_csv_json(params)
    print(f"Wrote {n} rows to data.csv")