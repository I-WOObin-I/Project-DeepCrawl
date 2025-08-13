import csv

OUTPUT_PATH_BASE = ""

def write_results_to_csv(file_name, data):
    """
    Universal CSV writer.
    Accepts a path to file, a list of data (list of lists or list of dicts), and optional headers.
    
    - If data is a list of dicts, writes keys as headers if not provided.
    - If data is a list of lists, uses provided headers or none.
    """
    if not data:
        raise ValueError("No data to write.")

    full_file_path = OUTPUT_PATH_BASE + file_name

    # Handle list-of-dicts
    if isinstance(data[0], dict):
        with open(full_file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    # Handle list-of-lists (assume headers provided or none)
    elif isinstance(data[0], (list, tuple)):
        with open(full_file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data[0].keys())
            for row in data:
                writer.writerow(row.values())
    else:
        raise ValueError("Data must be a list of dicts or a list of lists/tuples.")
    

from langchain.tools import Tool
csv_writer = Tool(
    name="csv_writer",
    func=write_results_to_csv,
    description="Writes scraped data to a CSV file. Parameters: file_name (str), data (list of dicts or list of lists)."
)