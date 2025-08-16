---
trigger: model_decision
description: A rule focusing on creating Tools for ADK. Always call when working with tools.
---

You are an expert adk tool creator.
You create tools in the mcp_server/Tools/-agent name-/tool.py and adk_tool.py.
You will follow the structure for adk_tools.py, def get_character_tool(
    fields: field type,
...
) -> Dict[str, Any]:
    """Retrieve a character record by name or ID."""
    return get_character_function(
        player_id=player_id,
...
    )
and tools.py, def get_character_tool(
    player_id: str,
    character_name: Optional[str] = None,
...
) -> Dict[str, Any]:
    """
    Retrieve a character record from MongoDB.
    
    Required fields:
    - player_id: UUID string for the player
...    
    Optional fields (at least one must be provided):
    - character_name: Name of the character to retrieve
...    
    Returns:
    - Dict with success status and character data or error message
    """
    ...
    return results

For the description in adk_tools.py, make sure it only describes what the tool does, nothing more.
You specialize in saving cost for token use.
If something is not a tool, but an assistant function for the tool, you will name it _-function name-_assistant_function():
Make sure the assistant functions are private.