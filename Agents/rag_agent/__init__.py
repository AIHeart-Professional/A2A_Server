import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def run_agent(action: str, fields: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point used by Agents/app.py to execute this agent.
    Supported actions: retrieve_documents, answer_with_context
    """
    try:
        if action == "retrieve_documents":
            query = fields.get("query") or fields.get("q")
            top_k = int(fields.get("top_k", 5))
            return {"result": {"action": action, "query": query, "top_k": top_k, "status": "ok"}}
        if action == "answer_with_context":
            question = fields.get("question")
            context_docs = fields.get("context") or []
            return {"result": {"action": action, "question": question, "context_count": len(context_docs), "status": "ok"}}
        return {"error": f"Unsupported action: {action}"}
    except Exception as e:
        logger.exception("rag_agent error")
        return {"error": str(e)}
