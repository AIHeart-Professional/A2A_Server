from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from starlette.routing import Route
import logging
import os
from dotenv import load_dotenv
from .agent_card import agent_card

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    try:
        # Construct the agent
        narrative = Agent(
            name="narrative_agent",
            model="gemini-2.0-flash",
            instruction="""You are a narrative agent that creates engaging stories and scenes. 
            When someone says they want to go fishing, create a vivid, immersive fishing scene.
            Respond in a friendly, storytelling manner.""",
        )
        
        logger.info("Agent created successfully")
        
        # Create the A2A app
        app = to_a2a(narrative, host="127.0.0.1", port=8002)
        
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
