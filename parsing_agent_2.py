import json
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

MODEL_NAME = "qwen3:8b"

def parse_json_file_json(json_params):
    """
    Parsing agent that runs locally with LangChain & Ollama.
    Accepts parameters as a JSON string or dict:
      - input_json_path (str)
      - output_json_path (str)
      - output_schema (dict or list of response schemas)
      - dynamic_instructions (str, optional)
    Dynamically builds parsing prompt and parses each row of a JSON file.
    Updates output JSON file every time a new item is processed.
    """
    # Parse json_params if it's a string
    if isinstance(json_params, str):
        json_params = json.loads(json_params)

    input_json_path = json_params.get("input_json_path")
    output_json_path = json_params.get("output_json_path")
    output_schema = json_params.get("output_schema")
    dynamic_instructions = json_params.get("dynamic_instructions", "")

    llm = Ollama(model=MODEL_NAME)
    output_parser = StructuredOutputParser.from_response_schemas(output_schema)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template="""
        You are a strict data parsing assistant.
        Input: {input_data}

        {dynamic_instructions}

        Only return JSON that matches the following rules and fields:
        {format_instructions}
        Do not return any other text or explanations.
        """,
        input_variables=["input_data", "dynamic_instructions"],
        partial_variables={"format_instructions": format_instructions}
    )

    results = []
    with open(input_json_path, encoding="utf-8") as f:
        data = json.load(f)
        for idx, row in enumerate(data):
            llm_input = prompt.format(input_data=row, dynamic_instructions=dynamic_instructions)
            print(f"Processing row {idx + 1}/{len(data)}")

            raw_output = llm(llm_input)
            try:
                parsed_output = output_parser.parse(raw_output)
                results.append(parsed_output)
            except Exception as e:
                print(f"Parsing failed for row: {row}")
                print("Raw output was:\n", raw_output)
                continue

            # Update output file after each item
            with open(output_json_path, "w", encoding="utf-8") as out_f:
                json.dump(results, out_f, ensure_ascii=False, indent=2)
            print(f"Updated {output_json_path} with {len(results)} items.")

    print(f"Finished. Parsed {len(results)} rows, saved to {output_json_path}")
    return results


from langchain.tools import Tool
from pydantic import BaseModel, Field

class ParseJsonFileArgs(BaseModel):
    json_params: dict = Field(..., description="JSON object containing 'input_json_path' (str), 'output_json_path' (str), 'output_schema' (list of response schemas or dict), and optional 'dynamic_instructions' (str).")

parse_json_tool = Tool(
    name="parse_json_tool",
    func=parse_json_file_json,
    description="Parses a JSON file using a specified schema. Accepts a JSON object with keys: input_json_path (str), output_json_path (str), output_schema (dict or list), dynamic_instructions (str, optional). Returns parsed data as a list of dictionaries.",
    # args_schema=ParseJsonFileArgs,
)