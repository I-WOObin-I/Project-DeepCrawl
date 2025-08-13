import time
import random
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

def olx_scrape_fn(search_phrase, item_count=10, localisation=True, maximize_window=True, output_path="olx_results.csv"):
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
        # Add random timer between each ad
        time.sleep(random.uniform(1.0, 4.0))  # Random sleep between 1 and 4 seconds

        try:
            title_el = ad.find_element(By.CSS_SELECTOR, "[data-cy='ad-card-title'] h4")
            price_el = ad.find_element(By.CSS_SELECTOR, "[data-testid='ad-price']")
            location_el = ad.find_element(By.CSS_SELECTOR, "[data-testid='location-date']")
            link_el = ad.find_element(By.CSS_SELECTOR, "a")
            title = title_el.text.strip()
            price = price_el.text.strip()
            location_date = location_el.text.strip()
            link = link_el.get_attribute("href")

            # Open link in new tab and get description
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

def main():
    parser = argparse.ArgumentParser(description="OLX Scraper CLI")
    parser.add_argument("--search_phrase", type=str, required=True, help="Phrase to search for (e.g. 'tablet')")
    parser.add_argument("--item_count", type=int, default=10, help="Max number of items to scrape")
    parser.add_argument("--localisation", type=str, choices=["true", "false"], default="true", help="Use localisation (gdansk) or not")
    parser.add_argument("--maximize_window", type=str, choices=["true", "false"], default="true", help="Start browser maximized")
    parser.add_argument("--output_path", type=str, default="olx_results.csv", help="Output CSV file name")

    args = parser.parse_args()

    # Convert string args to booleans
    localisation = args.localisation.lower() == "true"
    maximize_window = args.maximize_window.lower() == "true"

    results = olx_scrape_fn(
        search_phrase=args.search_phrase,
        item_count=args.item_count,
        localisation=localisation,
        maximize_window=maximize_window,
        output_path=args.output_path
    )
    print(f"✅ Done! {len(results)} listings saved to '{args.output_path}'.")

from langchain.tools import Tool
from pydantic import BaseModel, Field

class OLXScraperArgs(BaseModel):
    search_phrase: str = Field(..., description="Phrase to search for (e.g. 'tablet')")
    item_count: int = Field(10, description="Max number of items to scrape")
    localisation: bool = Field(True, description="Use localisation (gdansk) or not")
    maximize_window: bool = Field(True, description="Start browser maximized")
    output_path: str = Field("olx_results.json", description="Output JSON file name")
    
scraper_site_olx = Tool(
    name="scraper for olx.pl site",
    func=olx_scrape_fn,
    description="Scrapes OLX.pl for listings based on a search phrase. Saves results to a JSON file. Parameters: search_phrase (str, only the item like 'tablet' not all specifics of it), item_count (int), localisation (bool), maximize_window (bool), output_path (str). Returns a list of dictionaries with ad details.",
    args_schema=OLXScraperArgs,
)

if __name__ == "__main__":
    main()