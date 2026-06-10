async def get_agent_card_name_and_description(agent_cards: list) -> dict:
    """
    Retrieves the agent card name and description based on the user query and intents.
    """
    result = []
    # Step 0: For each record in the  list, create a new List with name and description
    for agent_card in agent_cards:
        name = agent_card.get("name")
        description = agent_card.get("description")
        result.append({"name": name, "description": description})
    return result

async def sanitize_json_text(text: str) -> str:
    """
    Sanitize LLM output that is intended to be JSON by:
    - Removing triple-backtick code fences
    - Removing leading language tags like 'json' on the first line
    - Stripping leading/trailing quotes
    - Extracting the core JSON payload between the first '{'/'[' and the last '}'/']'
    """
    if text is None:
        return ""

    # Remove code block markers first
    cleaned = text.replace("```", "")
    cleaned = cleaned.strip()

    # Strip wrapping quotes if present
    if (cleaned.startswith("'") and cleaned.endswith("'")) or (
        cleaned.startswith('"') and cleaned.endswith('"')
    ):
        cleaned = cleaned[1:-1].strip()

    # If the first line is a language tag (e.g., json, yaml, python), drop it
    lines = cleaned.splitlines()
    if lines:
        first = lines[0].strip().lower()
        if first in {"json", "javascript", "js", "ts", "typescript", "python", "yaml", "yml"}:
            cleaned = "\n".join(lines[1:]).lstrip()

    # Some models may prepend 'json' without a newline
    if cleaned.lower().startswith("json"):
        remainder = cleaned[4:]
        if remainder[:1] in {"\n", "\r", " "}:
            cleaned = remainder.lstrip()

    # Extract core JSON payload between the first opening brace/bracket and the last closing brace/bracket
    first_obj = cleaned.find("{")
    first_arr = cleaned.find("[")
    start_candidates = [i for i in [first_obj, first_arr] if i != -1]
    start = min(start_candidates) if start_candidates else -1
    end_obj = cleaned.rfind("}")
    end_arr = cleaned.rfind("]")
    end = max(end_obj, end_arr)
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    return cleaned