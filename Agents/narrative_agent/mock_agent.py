#!/usr/bin/env python3
"""
Mock Narrative Agent - Simple FastAPI server that responds to fishing requests
This bypasses the Gemini API quota issues for testing A2A communication
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from .agent_card import agent_card
from starlette.routing import Route

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mock_app():
    """Create a mock narrative agent app"""
    app = FastAPI(title="Mock Narrative Agent")
    
    @app.post("/")
    async def handle_message(request: Request):
        """Handle A2A messages"""
        try:
            body = await request.json()
            message = body.get("message", "")
            
            logger.info(f"Mock narrative agent received: {message}")
            
            # Create a fishing story response
            if "fishing" in message.lower():
                response_text = """🎣 **A Perfect Day for Fishing** 🎣

You find yourself standing at the edge of a serene lake, the morning mist dancing across the crystal-clear water. The sun peeks through the trees, casting golden rays that shimmer on the surface. 

You cast your line with practiced ease, watching the ripples spread outward in perfect circles. The gentle lapping of water against the shore creates a peaceful rhythm. Birds chirp softly in the distance, and a cool breeze carries the fresh scent of pine and water.

As you wait patiently, you feel the stress of everyday life melting away. This is your moment of peace, your connection with nature. Suddenly, you feel a gentle tug on your line... 

*What happens next is up to you, dear adventurer!* ✨"""
            else:
                response_text = f"I received your message: '{message}'. As a narrative agent, I specialize in creating stories about adventures like fishing!"
            
            return JSONResponse({
                "response": response_text,
                "status": "success",
                "agent": "mock_narrative_agent"
            })
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return JSONResponse({
                "error": str(e),
                "status": "error"
            }, status_code=500)
    
    # Add agent card route
    app.routes.append(Route("/.well-known/agent", agent_card, methods=["GET", "POST"]))
    
    logger.info("Mock narrative agent app created")
    return app
