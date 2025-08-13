from scraping_scripts.olx_scrape_fn import olx_scrape_fn

SEARCH_PHRASE = "tablet"
ITEM_COUNT = 20
LOCALISATION = True
MAXIMIZE_WINDOW = True

SCRAPED_FILE_PATH = "data/scraped/tablets.json"

# olx_scrape_fn(
#     search_phrase=SEARCH_PHRASE,
#     item_count=ITEM_COUNT,
#     localisation=LOCALISATION,
#     maximize_window=MAXIMIZE_WINDOW,
#     output_path=SCRAPED_FILE_PATH
# )
# print(f"\n## PIPELINE ## Scraped {ITEM_COUNT} items for '{SEARCH_PHRASE}' and saved to {SCRAPED_FILE_PATH}\n")

####################################################################
####################################################################

from parsing_agent import parse_json_file
PROCESSED_FILE_PATH = "data/processed/tablets_parsed.json"
OUTPUT_SCHEMA = [
        {"name": "manufacturer", "description": "Manufacturer of the tablet", "type": "string"},
        {"name": "model", "description": "Model of the tablet, leave as 'tablet' if not available", "type": "string"},
        {"name": "ram_size", "description": "RAM size in GB, watch out for storage size confusion", "type": "float"},
        {"name": "storage_size", "description": "Storage size in GB", "type": "float"},
        {"name": "release_date", "description": "Release date of the tablet", "type": "string"},
        {"name": "screen_size", "description": "Screen size in inches", "type": "float"},
        {"name": "price", "description": "Price of the tablet in PLN", "type": "integer"},
        {"name": "device_condition", "description": "Condition of the device, try to be precise (used briefly, used a lot etc.) if possible", "type": "string"},
        {"name": "listing_time", "description": "When the listing was created or published", "type": "string"},
        {"name": "url", "description": "URL of the listing", "type": "string"}
    ]
DYNAMIC_INSTRUCTIONS = "If a field is not available leave unknown for string and 0 for numbers."

parse_json_file(
    input_json_path=SCRAPED_FILE_PATH,
    output_json_path=PROCESSED_FILE_PATH,
    output_schema=OUTPUT_SCHEMA,
    dynamic_instructions=DYNAMIC_INSTRUCTIONS
)
print(f"\n## PIPELINE ## Parsed {ITEM_COUNT} items and saved to {PROCESSED_FILE_PATH}\n")

####################################################################
####################################################################

from utils.json_to_csv import json_to_csv
CSV_FILE_PATH = "data/processed/tablets_parsed.csv"

json_to_csv(
    input_file=PROCESSED_FILE_PATH,
    output_file=CSV_FILE_PATH
)
print(f"## PIPELINE ## Converted JSON to CSV and saved to {CSV_FILE_PATH}")
