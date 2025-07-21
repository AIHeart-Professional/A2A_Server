from fastapi import FastAPI
from pydantic import BaseModel
from Orchestrator.orchestrator import run_orchestrator


async def execute_orchestrator(request: dict, details: dict):
    result = await run_orchestrator(request, details)
    
    # Extract only the last result from the results array
    if result and "results" in result and result["results"]:
        last_result = result["results"][-1]
        try:
            # Try to parse the string result back to dict if it's JSON
            import json
            if isinstance(last_result, str):
                return json.loads(last_result.replace("'", '"'))
            return last_result
        except (json.JSONDecodeError, AttributeError):
            # If parsing fails, return the raw last result
            return last_result
    
    # Fallback to return the full result if no results array found
    return result