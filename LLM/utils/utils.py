async def remove_code_block_markers(response: str) -> str:
    # Remove code block markers if present
    if isinstance(response, str):
        response = response.strip()
        if response.startswith('```'):
            # Remove leading/trailing code block and optional language
            response = response.lstrip('`').lstrip('json').lstrip('\n').strip()
        if response.endswith('```'):
            response = response.rstrip('`').strip()
    return response