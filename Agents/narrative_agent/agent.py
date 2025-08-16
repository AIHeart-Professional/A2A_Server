from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from starlette.routing import Route
import logging
from .agent_card import agent_card

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    # Construct the agent
    narrative = Agent(
        name="narrative_agent",
        model="gemini-2.0-flash",
        instruction="You respond to the user as a tsundere girl."
    )
    
    # Create the A2A app
    app = to_a2a(narrative, host="127.0.0.1", port=8001)
    
    # Add our custom agent card route to override the default
    app.routes.append(Route("/.well-known/agent", agent_card, methods=["GET", "POST"]))
    
    logger.info("A2A app created with custom agent card route")
    
    return app
