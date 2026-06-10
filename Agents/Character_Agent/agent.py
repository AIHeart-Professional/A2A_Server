import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from starlette.routing import Route
# ADK imports
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .agent_card import agent_card

# Ensure project root is on sys.path so `mcp_server` can be imported when ADK runs from Agents/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load environment variables from project root .env
load_dotenv(dotenv_path=Path(PROJECT_ROOT) / ".env")

# Configure API credentials (preserve if already set)
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")
if not os.environ["GOOGLE_API_KEY"]:
    logging.getLogger(__name__).warning(
        "GOOGLE_API_KEY is not set. Ensure it is present in your environment or .env file."
    )
# Alternatively, you can use Vertex AI
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/credentials.json"
from mcp_server.Tools.Character.adk_tool import (
    create_character_tool,
    update_character_tool,
    get_character_tool,
    delete_character_tool
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    try:
        # Construct the agent
        root_agent = character_agent()
        
        logger.info("Agent created successfully")
        
        # Create the A2A app for direct usage
        app = to_a2a(root_agent, host="127.0.0.1", port=8002)
        
        logger.info("A2A app created")
        
        # Add our custom agent card route to override the default
        app.routes.append(Route("/.well-known/agent", agent_card, methods=["GET", "POST"]))

        
        logger.info("A2A app created")
        
        # Add our custom agent card route to override the default
        app.routes.append(Route("/.well-known/agent", agent_card, methods=["GET", "POST"]))

        logger.info("A2A app created with custom agent card route")
        
        # Add middleware to log all requests
        @app.middleware("http")
        async def log_requests(request, call_next):
            logger.info(f"Received request.")
            try:
                response = await call_next(request)
                logger.info(f"Response status: {response.status_code}")
                return response
            except Exception as e:
                logger.error(f"Request processing error: {e}")
                raise
        
        return app
        
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        raise

character_handler_sub_agent = Agent(
    name="character_handler_sub_agent",
    model="gemini-1.5-flash",
    description="Agent designed to handle character interactions for a roleplaying game.",
    instruction="You are an expert at managing characters for a roleplaying game. You can help with things such as editing character information, creating characters, and deleting characters.",
    tools=[create_character_tool, update_character_tool, get_character_tool, delete_character_tool],
)
def character_agent():
    return Agent(
        name="character_agent",
        model="gemini-1.5-flash",
        description="Agent designed to interact with players characters",
        instruction="You are an expert at managing characters for a roleplaying game. Your role is to only call out to required sub-agents to handle the work.",
        sub_agents=[character_handler_sub_agent],
    )
