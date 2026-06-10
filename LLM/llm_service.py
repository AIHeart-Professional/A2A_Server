import hashlib
import json
import logging
import asyncio
import os
from LLM.utils import sanitize_json_text
from langchain_google_genai.llms import GoogleGenerativeAI
from dotenv import load_dotenv
from langsmith import traceable
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

async def _validate_intent_request(initial_request: str):
    """Validate the initial request for intent handling."""
    if not initial_request:
        logger.error("No user query provided in the request.")
        raise ValueError("No user query provided in the request.")


async def _prepare_agent_cards_prompt(user_query: str,  agent_cards: dict, instruction: str):
    """Prepare the prompt for the LLM agent cards request. 'intent' and 'tools' are optional."""
    prompt = instruction.replace("{{USER_QUERY}}", user_query)
    if agent_cards is not None:
        prompt = prompt.replace("{{AGENT_CARDS}}", json.dumps(agent_cards))
    return prompt

async def _execute_llm_call(prompt: str, model: str):
    """Configure and execute the LLM call."""
    api_key = os.getenv("GEMINI_API_KEY")
    llm = GoogleGenerativeAI(
        model=model, temperature=0.7, google_api_key=api_key
    )
    return await llm.ainvoke(prompt)

async def _convert_to_string(data: dict) -> str:
    """Convert data to string, handling various types."""
    if isinstance(data, (dict, list)):
        return json.dumps(data)
    elif isinstance(data, str):
        return data
    else:
        return str(data)
    
async def _process_llm_response(response: str):
    """Process the raw response from the LLM."""
    response = await sanitize_json_text(response)
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(
            "Failed to parse LLM response as JSON: %s. Raw response: %s",
            e,
            response,
        )
        return {
            "error": "Failed to parse LLM response as JSON",
            "raw_response": response,
            "exception": str(e),
        }


@traceable(name="LLM_Request", inputs={"prompt"}, outputs={"response"})
async def handle_LLM_request(request: str, agent_cards: list, instruction: str):
    """
    Handles a request to the Gemini LLM by breaking it into smaller steps.
    """
    try:
        prompt = await _prepare_agent_cards_prompt(request, agent_cards, instruction)
        response = await _execute_llm_call(prompt, "gemini-1.5-flash")
        parsed = await _process_llm_response(response)
        # Ensure we return a dict for FastAPI response model
        if isinstance(parsed, dict):
            return parsed
        else:
            return {"response": parsed}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        logger.error("An unexpected error occurred in handle_LLM_request: %s", e)
        return {"error": "An unexpected error occurred."}


@traceable(name="LLM_Response", inputs={"response"}, outputs={"response"})
async def handle_LLM_response(response: dict, instruction_key: str, instruction: str):
    """
    Handles the response from the LLM service.
    Args:
        initial_request (dict): The main request data.
        instruction_key (str): The key for the instructions to use.
    Returns:
        dict: The response from the LLM service.
    """
    # Step 0: Validate the request (query_result should not be None)
    # Extract 'success' or 'error' value from result
    if "success" in response:
        query_result = response["success"]
    else:
        query_result = response["error"]
    if query_result is None:
        logger.error("No query result provided in the request.")
        return {"error": "No query result provided in the request."}

    prompt = (
        instruction
        .replace("{{INPUT}}", str(query_result))
        .replace("{{PERSONA}}", "You are a young Tsundere girl named Yuki. You respond in very snarky responses and beat around the bush on your responses.")
        )
    # Configure Gemini LLM (adjust as needed)
    api_key = os.getenv("GEMINI_API_KEY")
    llm = GoogleGenerativeAI(model="gemini-1.5-flash", 
                            temperature=0.7,
                            google_api_key=api_key
                            )
    
    # Direct async call to LLM (faster than run_in_executor)
    response = await llm.ainvoke(prompt)
    
    # Sanitize potential code fences / language tags
    response = await sanitize_json_text(response)
    
    # Parse the response as JSON
    try:
        response_json = json.loads(response)
        # Ensure a dict is returned
        if isinstance(response_json, dict):
            return response_json
        else:
            return {"response": response_json}
    except Exception as e:
        error_result = {"error": "Failed to parse LLM response as JSON", "raw_response": response, "exception": str(e)}
        return error_result