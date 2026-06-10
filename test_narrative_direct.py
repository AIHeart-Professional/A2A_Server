#!/usr/bin/env python3
"""
Direct test of narrative agent without A2A wrapper
"""
import os
import asyncio
import logging
from google.adk.agents import Agent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_narrative_agent():
    """Test the narrative agent directly"""
    try:
        # Create the agent
        narrative = Agent(
            name="narrative_agent",
            model="gemini-2.0-flash",
            instruction="""You are a narrative agent that creates engaging stories and scenes. 
            When someone says they want to go fishing, create a vivid, immersive fishing scene.
            Respond in a friendly, storytelling manner."""
        )
        
        logger.info("Agent created successfully")
        
        # Test with a simple message
        response = await narrative.send_message("I want to go fishing")
        logger.info(f"Agent response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error testing agent: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_narrative_agent())
