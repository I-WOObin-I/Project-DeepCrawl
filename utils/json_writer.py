import json

OUTPUT_PATH_BASE = ""

def write_results_to_json(file_name, data):
    """
    Universal JSON writer.
    Accepts a file name and a list of dicts (data).
    Saves as UTF-8 encoded JSON file.
    """
    if not data:
        raise ValueError("No data to write.")

    full_file_path = OUTPUT_PATH_BASE + file_name

    with open(full_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


from langchain.tools import Tool
json_writer = Tool(
    name="json_writer",
    func=write_results_to_json,
    description="Writes scraped data to a JSON file. Parameters: file_name (str), data (list of dicts)."
)