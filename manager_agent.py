from langchain.llms import Ollama
from langchain.agents import initialize_agent
from langchain.agents import AgentType

from scraping_scripts.olx_scrape_fn_json import scraper_site_olx_json
from utils.json_writer_2 import json_writer
from utils.json_to_csv_2 import json_to_csv_tool
from parsing_agent_2 import parse_json_tool

llm = Ollama(model="qwen3:8b")

tools = [
    scraper_site_olx_json,
    json_writer,
    json_to_csv_tool,
    parse_json_tool
]

manager_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

manager_agent.run(
    "you must first scrape OLX.pl site for tablets and you must use scraper_site_olx tool, scrape for 10 items."
    "then parse the results with parse_json_tool, that will save results to json file."
    "Then parse the JSON file to extract relevant fields and save the processed data to 'data/processed/tablets_parsed.json'. "
    "Include ram size, storage size, release date, screen size, price, device condition, listing time, and URL in the parsed data. "
    "Finally, convert the parsed JSON to CSV format and save it to 'data/processed/tablets_parsed.csv'."
)