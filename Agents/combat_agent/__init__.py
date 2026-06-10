import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def run_agent(action: str, fields: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point used by Agents/app.py to execute this agent.
    Supported actions: attack, defend, use_skill
    """
    try:
        if action == "attack":
            target = fields.get("target")
            weapon = fields.get("weapon") or fields.get("skill")
            return {"result": {"action": action, "target": target, "using": weapon, "status": "ok"}}
        if action == "defend":
            style = fields.get("style") or "guard"
            return {"result": {"action": action, "style": style, "status": "ok"}}
        if action == "use_skill":
            skill = fields.get("skill")
            target = fields.get("target")
            return {"result": {"action": action, "skill": skill, "target": target, "status": "ok"}}
        return {"error": f"Unsupported action: {action}"}
    except Exception as e:
        logger.exception("combat_agent error")
        return {"error": str(e)}
