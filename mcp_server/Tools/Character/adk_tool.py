"""
ADK-compatible tool wrapper for character management.
This module provides simple callable functions for ADK agents.
"""

from typing import Optional, Dict, Any
from .tool import (
    create_character_tool as create_character_function,
    get_character_tool as get_character_function,
    update_character_tool as update_character_function,
    delete_character_tool as delete_character_function
)

def create_character_tool(
    server_id: str,
    player_id: str, 
    character_name: str,
    character_class: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    cursor_color: Optional[str] = None,
    height: Optional[str] = None,
    physique: Optional[str] = None,
    age: Optional[int] = None,
    birthday: Optional[str] = None,
    bio: Optional[str] = None
):
    """Create a new character with specified attributes."""
    return create_character_function(
        server_id=server_id,
        player_id=player_id,
        character_name=character_name,
        character_class=character_class,
        first_name=first_name,
        last_name=last_name,
        cursor_color=cursor_color,
        height=height,
        physique=physique,
        age=age,
        birthday=birthday,
        bio=bio
    )


def get_character_tool(
    player_id: str,
    server_id: str,
    character_name: Optional[str] = None,
    character_id: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve a character record by name or ID."""
    return get_character_function(
        player_id=player_id,
        server_id=server_id,
        character_name=character_name,
        character_id=character_id
    )


def update_character_tool(
    request: Dict[str, Any],
    character_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update character fields using structured request dict."""
    return update_character_function(
        request=request,
        character_data=character_data
    )


def delete_character_tool(
    player_id: str,
    server_id: str,
    character_name: Optional[str] = None,
    character_id: Optional[str] = None
) -> Dict[str, Any]:
    """Delete a character record by name or ID."""
    return delete_character_function(
        player_id=player_id,
        server_id=server_id,
        character_name=character_name,
        character_id=character_id
    )


__all__ = ["create_character_tool", "get_character_tool", "update_character_tool", "delete_character_tool"]
