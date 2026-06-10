import asyncio
import aiohttp
import logging
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    """Information about a discovered A2A agent"""
    name: str
    description: str
    url: str
    skills: List[Dict]
    version: str = "1.0.0"

class A2AAgentDiscovery:
    """Discovers and manages A2A agents running on different ports"""
    
    def __init__(self):
        self.known_agents: Dict[str, AgentInfo] = {}
        self.agent_ports = [8001, 8002, 8003, 8004, 8005]  # Common A2A agent ports
        
    async def discover_agents(self) -> Dict[str, AgentInfo]:
        """Discover all available A2A agents by checking their agent card endpoints"""
        discovered = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for port in self.agent_ports:
                try:
                    agent_info = await self._check_agent_endpoint(session, port)
                    if agent_info:
                        discovered[agent_info.name] = agent_info
                        logger.info(f"Discovered agent: {agent_info.name} at port {port}")
                except Exception as e:
                    logger.debug(f"No agent found on port {port}: {e}")
                    
        self.known_agents.update(discovered)
        return discovered
    
    async def _check_agent_endpoint(self, session: aiohttp.ClientSession, port: int) -> Optional[AgentInfo]:
        """Check if an agent is running on the given port"""
        url = f"http://localhost:{port}/.well-known/agent"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Agent card received from port {port}: {data['name']}")
                    return AgentInfo(
                        name=data.get("name", f"agent_port_{port}"),
                        description=data.get("description", ""),
                        url=data.get("url", f"http://localhost:{port}"),
                        skills=data.get("skills", []),
                        version=data.get("version", "1.0.0")
                    )
                else:
                    logger.debug(f"Port {port} returned status {response.status}")
        except Exception as e:
            logger.debug(f"Error checking port {port}: {e}")
        
        return None
    
    async def find_agent_for_task(self, task_description: str) -> Optional[AgentInfo]:
        """Find the best agent for a given task based on skills and description"""
        await self.discover_agents()  # Refresh agent list
        
        task_lower = task_description.lower()
        best_match = None
        best_score = 0
        
        for agent in self.known_agents.values():
            score = 0
            
            # Check skills
            for skill in agent.skills:
                skill_name = skill.get("name", "").lower()
                skill_desc = skill.get("description", "").lower()
                skill_tags = [tag.lower() for tag in skill.get("tags", [])]
                
                # Score based on skill relevance
                if any(tag in task_lower for tag in skill_tags):
                    score += 3
                if any(word in task_lower for word in skill_name.split()):
                    score += 2
                if any(word in task_lower for word in skill_desc.split()):
                    score += 1
            
            # Check agent description
            desc_words = agent.description.lower().split()
            if any(word in task_lower for word in desc_words):
                score += 1
                
            if score > best_score:
                best_score = score
                best_match = agent
                
        return best_match
    
    async def call_agent_skill(self, agent_info: AgentInfo, skill_id: str, request_data: Dict) -> Dict:
        """Call a specific skill on an A2A agent"""
        # For A2A agents created with to_a2a(), we need to call the /tasks endpoint
        url = agent_info.url.rstrip('/')
        
        # A2A agents expect a SendMessageRequest format
        message_text = request_data.get("task", request_data.get("user_query", ""))
        payload = {
            "id": str(uuid.uuid4()),
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [{"text": message_text}]
                },
                "user_id": "user",
                "session_id": "default_session"
            }
        }
                
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            try:
                async with session.post(url, json=payload) as response:
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            return await response.json()
                        except:
                            # If not JSON, return as text
                            return {"response": response_text}
                    else:
                        return {"error": f"Agent call failed with status {response.status}: {response_text}"}
            except Exception as e:
                logger.error(f"Exception calling agent: {e}")
                return {"error": f"Failed to call agent: {str(e)}"}
    
    def get_available_agents(self) -> Dict[str, AgentInfo]:
        """Get all currently known agents"""
        return self.known_agents.copy()
    
    def get_agent_capabilities_summary(self) -> str:
        """Get a summary of all available agents and their capabilities"""
        if not self.known_agents:
            return "No agents currently discovered."
        
        summary = "Available A2A Agents:\n"
        for name, agent in self.known_agents.items():
            summary += f"\n• {name}: {agent.description}\n"
            if agent.skills:
                summary += "  Skills:\n"
                for skill in agent.skills:
                    skill_name = skill.get("name", "Unknown")
                    skill_desc = skill.get("description", "")
                    summary += f"    - {skill_name}: {skill_desc}\n"
        
        return summary

# Global discovery instance
agent_discovery = A2AAgentDiscovery()
