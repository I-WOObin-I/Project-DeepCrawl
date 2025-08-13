import time
import random
import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.json_writer import write_results_to_json

BASE_URL = "https://www.olx.pl"
LOCALISATION_ADDON = "/gdansk"
NO_LOCALISATION_ADDON = "/oferty"
WAIT_TIME = 2
WAIT_TIME_AD_SHORT = 0.3
WAIT_TIME_AD_LONG = 0.9

def olx_scrape_json(json_params):
    """
    Accepts a JSON object/dict as input, parses the parameters, and runs the OLX scraping logic.
    """
    if isinstance(json_params, str):
        json_params = json.loads(json_params)
    # Parse parameters from JSON
    search_phrase = json_params.get("search_phrase")
    item_count = int(json_params.get("item_count", 10))
    localisation = bool(json_params.get("localisation", True))
    maximize_window = bool(json_params.get("maximize_window", True))
    output_path = json_params.get("output_path", "olx_results.csv")

    # If localisation/maximize_window may come as str (from CLI or LLM), convert to bool
    if isinstance(localisation, str):
        localisation = localisation.lower() == "true"
    if isinstance(maximize_window, str):
        maximize_window = maximize_window.lower() == "true"

    options = Options()
    if maximize_window:
        options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    if localisation:
        url = f"{BASE_URL}{LOCALISATION_ADDON}/q-{search_phrase}/"
    else:
        url = f"{BASE_URL}{NO_LOCALISATION_ADDON}/q-{search_phrase}/"

    driver.get(url)
    time.sleep(WAIT_TIME)

    ads = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='l-card']")
    out = []
    for ad in ads:
        time.sleep(random.uniform(1.0, 4.0))
        try:
            title_el = ad.find_element(By.CSS_SELECTOR, "[data-cy='ad-card-title'] h4")
            price_el = ad.find_element(By.CSS_SELECTOR, "[data-testid='ad-price']")
            location_el = ad.find_element(By.CSS_SELECTOR, "[data-testid='location-date']")
            link_el = ad.find_element(By.CSS_SELECTOR, "a")
            title = title_el.text.strip()
            price = price_el.text.strip()
            location_date = location_el.text.strip()
            link = link_el.get_attribute("href")

            main_window = driver.current_window_handle
            driver.execute_script("window.open(arguments[0], '_blank');", link)
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(WAIT_TIME)
            try:
                desc_el = driver.find_element(By.CSS_SELECTOR, "[data-cy='ad_description'] .css-19duwlz")
                description = desc_el.get_attribute("innerText").strip()
            except Exception:
                description = ""
            driver.close()
            driver.switch_to.window(main_window)

            out.append({
                "Title": title,
                "Price": price,
                "Location/Date": location_date,
                "URL": link,
                "Description": description
            })
            if len(out) >= item_count:
                break
        except Exception as e:
            continue

    write_results_to_json(output_path, out)
    driver.quit()
    return out

# CLI for JSON input
def main():
    parser = argparse.ArgumentParser(description="OLX Scraper CLI (JSON input)")
    parser.add_argument("--json_params", type=str, required=True, help="JSON string with parameters")
    args = parser.parse_args()

    params = json.loads(args.json_params)
    results = olx_scrape_json(params)
    print(f"✅ Done! {len(results)} listings saved to '{params.get('output_path', 'olx_results.csv')}'.")

# LangChain tool registration (example)
from langchain.tools import Tool
from pydantic import BaseModel, Field

class OLXScraperJsonArgs(BaseModel):
    json_params: dict = Field(..., description="A JSON object with OLX scraper parameters (search_phrase, item_count, localisation, maximize_window, output_path)")

scraper_site_olx_json = Tool(
    name="scraper for olx.pl site (json input)",
    func=olx_scrape_json,
    description="Scrapes OLX.pl for listings. Accepts a JSON object with parameters: search_phrase (str), item_count (int), localisation (bool), maximize_window (bool), output_path (str). Returns a list of dictionaries with ad details.",
    # args_schema=OLXScraperJsonArgs,
)

if __name__ == "__main__":
    main()