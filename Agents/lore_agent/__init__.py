import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def run_agent(action: str, fields: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point used by Agents/app.py to execute this agent.
    Supported actions: query_lore, add_lore_entry
    """
    try:
        if action == "query_lore":
            question = fields.get("question") or fields.get("q")
            topic = fields.get("topic")
            return {"result": {"action": action, "question": question, "topic": topic, "status": "ok"}}
        if action == "add_lore_entry":
            title = fields.get("title")
            content = fields.get("content")
            return {"result": {"action": action, "title": title, "content": content, "status": "ok"}}
        return {"error": f"Unsupported action: {action}"}
    except Exception as e:
        logger.exception("lore_agent error")
        return {"error": str(e)}
