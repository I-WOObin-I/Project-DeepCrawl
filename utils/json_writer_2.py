import json

OUTPUT_PATH_BASE = ""

def write_results_to_json_json(json_params):
    """
    Universal JSON writer that accepts parameters as a JSON string or dict.
    Expects 'file_name' and 'data' keys.
    Saves 'data' to the given file name as UTF-8 encoded JSON.
    """
    # Ensure json_params is a dict
    if isinstance(json_params, str):
        json_params = json.loads(json_params)

    file_name = json_params.get("file_name")
    data = json_params.get("data")
    if not data:
        raise ValueError("No data to write.")

    full_file_path = OUTPUT_PATH_BASE + file_name

    with open(full_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


from langchain.tools import Tool
from pydantic import BaseModel, Field

class JsonWriterArgs(BaseModel):
    json_params: dict = Field(..., description="JSON object containing 'file_name' (str) and 'data' (list of dicts) to write.")

json_writer = Tool(
    name="json_writer",
    func=write_results_to_json_json,
    description="Writes scraped data to a JSON file. Accepts a JSON object with keys: 'file_name' (str), 'data' (list of dicts).",
    # args_schema=JsonWriterArgs,
)