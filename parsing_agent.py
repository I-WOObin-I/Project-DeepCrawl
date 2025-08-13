import json
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

MODEL_NAME = "qwen3:8b"

def parse_json_file(input_json_path, output_json_path, output_schema, dynamic_instructions=""):
    """
    Parsing agent that runs locally with LangChain & Ollama.
    Dynamically builds parsing prompt and parses each row of a JSON file.
    Updates output JSON file every time a new item is processed.
    """

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


from langchain.tools import Tool
parse_json_tool = Tool(
    name="parse_json_file_for_items",
    func=parse_json_file,
    description="Parses a JSON file using a specified schema. Parameters: input_json_path (str), output_json_path (str), output_schema (dict), dynamic_instructions (str). Returns parsed data as a list of dictionaries."
)