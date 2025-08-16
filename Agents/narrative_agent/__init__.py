import logging
from typing import Dict, Any
from .agent import create_app

logger = logging.getLogger(__name__)

async def run_agent(action: str, fields: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point used by Agents/app.py to execute this agent.
    Supported actions: compose_scene, summarize_events
    """
    try:
        if action == "compose_scene":
            prompt = fields.get("prompt") or fields.get("topic")
            style = fields.get("style")
            return {"result": {"action": action, "prompt": prompt, "style": style, "status": "ok"}}
        if action == "summarize_events":
            events = fields.get("events") or []
            return {"result": {"action": action, "summary_of": events, "status": "ok"}}
        return {"error": f"Unsupported action: {action}"}
    except Exception as e:
        logger.exception("narrative_agent error")
        return {"error": str(e)}

# Export create_app for uvicorn
__all__ = ['run_agent', 'create_app']
