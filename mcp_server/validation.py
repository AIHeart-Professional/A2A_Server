import re

UUID_REGEX = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

async def validate_request(request: dict) -> bool:
    """
    Validates that 'user_query' and 'id' exist in 'initial_request', and 'id' is a valid UUID.
    Returns True if valid, False otherwise.
    """
    initial = request.get("initial_request", {})
    user_query = initial.get("user_query")
    user_id = initial.get("user_id")
    server_id = initial.get("server_id")
    if not user_query or not user_id:
        return False
    # Validate UUID format
    if not UUID_REGEX.match(user_id) and not UUID_REGEX.match(server_id):
        return False
    return True