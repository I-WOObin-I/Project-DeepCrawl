import json
from langchain.output_parsers import StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

MODEL_NAME = "qwen3:8b"

def parse_json_file(input_json_path, output_json_path, output_schema, dynamic_instructions=""):
    """
    Parsing agent that runs locally with LangChain & Ollama.
    Dynamically builds parsing prompt and parses the whole JSON file in one LLM call.
    """

    llm = Ollama(model=MODEL_NAME)
    output_parser = StructuredOutputParser.from_response_schemas(output_schema)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template="""
        You are a strict data parsing assistant.
        Input (list of records): {input_data}

        {dynamic_instructions}

        Only return JSON (list of objects) that matches the following rules and fields:
        {format_instructions}
        Do not return any other text or explanations.
        """,
        input_variables=["input_data", "dynamic_instructions"],
        partial_variables={"format_instructions": format_instructions}
    )

    with open(input_json_path, encoding="utf-8") as f:
        data = json.load(f)  # a list of dicts

    llm_input = prompt.format(input_data=json.dumps(data, ensure_ascii=False), dynamic_instructions=dynamic_instructions)
    print("Prompt for LLM:\n", llm_input)

    raw_output = llm(llm_input)
    try:
        parsed_output = output_parser.parse(raw_output)
    except Exception as e:
        print(f"Parsing failed for bulk data.")
        print("Raw output was:\n", raw_output)
        parsed_output = []

    # Save to output file
    with open(output_json_path, "w", encoding="utf-8") as out_f:
        json.dump(parsed_output, out_f, ensure_ascii=False, indent=2)
    print(f"Finished. Parsed {len(parsed_output)} rows, saved to {output_json_path}")