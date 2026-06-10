import asyncio
import logging
from typing import Dict, Any, Optional
from .agent_discovery import agent_discovery, AgentInfo

logger = logging.getLogger(__name__)

async def discover_available_agents() -> str:
    """Tool to discover all available A2A agents"""
    try:
        discovered = await agent_discovery.discover_agents()
        logger.info(f"Discovery complete. Found {len(discovered)} agents: {list(discovered.keys())}")
        for name, agent in discovered.items():
            logger.info(f"Agent {name}: {agent.description} with {len(agent.skills)} skills")
        return agent_discovery.get_agent_capabilities_summary()
    except Exception as e:
        logger.error(f"Error discovering agents: {e}")
        return f"Failed to discover agents: {str(e)}"

async def delegate_to_agent(task_description: str, additional_context: str = "") -> Dict[str, Any]:
    """Tool to find and delegate a task to the most appropriate A2A agent"""
    try:
        # Find the best agent for this task
        agent_info = await agent_discovery.find_agent_for_task(task_description)
        
        if not agent_info:
            return {
                "success": False,
                "error": "No suitable agent found for this task",
                "available_agents": agent_discovery.get_agent_capabilities_summary()
            }
        
        # Find the best skill for this task
        best_skill = None
        if agent_info.skills:
            task_lower = task_description.lower()
            for skill in agent_info.skills:
                skill_tags = [tag.lower() for tag in skill.get("tags", [])]
                if any(tag in task_lower for tag in skill_tags):
                    best_skill = skill
                    break
            
            # If no skill matched by tags, use the first skill
            if not best_skill:
                best_skill = agent_info.skills[0]
        
        if not best_skill:
            return {
                "success": False,
                "error": f"Agent {agent_info.name} has no available skills",
                "agent_info": {
                    "name": agent_info.name,
                    "description": agent_info.description
                }
            }
        
        # Prepare the request
        request_data = {
            "task": task_description,
            "context": additional_context,
            "user_query": task_description
        }
        
        # Call the agent
        result = await agent_discovery.call_agent_skill(
            agent_info, 
            best_skill.get("id", best_skill.get("name", "default")), 
            request_data
        )
        
        return {
            "success": True,
            "delegated_to": agent_info.name,
            "skill_used": best_skill.get("name", "unknown"),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error delegating task: {e}")
        return {
            "success": False,
            "error": f"Failed to delegate task: {str(e)}"
        }

async def call_specific_agent(agent_name: str, skill_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tool to call a specific agent and skill directly"""
    try:
        # Refresh agent list
        await agent_discovery.discover_agents()
        
        # Find the specified agent
        agent_info = agent_discovery.known_agents.get(agent_name)
        if not agent_info:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found",
                "available_agents": list(agent_discovery.known_agents.keys())
            }
        
        # Find the specified skill
        target_skill = None
        for skill in agent_info.skills:
            if skill.get("name", "").lower() == skill_name.lower() or skill.get("id", "").lower() == skill_name.lower():
                target_skill = skill
                break
        
        if not target_skill:
            return {
                "success": False,
                "error": f"Skill '{skill_name}' not found on agent '{agent_name}'",
                "available_skills": [skill.get("name", skill.get("id", "unknown")) for skill in agent_info.skills]
            }
        
        # Call the agent
        result = await agent_discovery.call_agent_skill(
            agent_info,
            target_skill.get("id", target_skill.get("name", "default")),
            request_data
        )
        
        return {
            "success": True,
            "agent": agent_name,
            "skill": skill_name,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error calling specific agent: {e}")
        return {
            "success": False,
            "error": f"Failed to call agent: {str(e)}"
        }
