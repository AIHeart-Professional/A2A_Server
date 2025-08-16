"""
Test script to demonstrate the improved agent execution display.
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.agent_display import create_agent_logger
from config.logging_config import setup_logging

async def test_agent_display():
    """Test the new agent execution display system."""
    
    # Setup logging
    setup_logging()
    
    # Create test logger
    logger = create_agent_logger("TestAgent")
    
    # Simulate agent execution flow
    user_id = "test_user_123"
    execution_id = "exec_abc123def456"
    message = "Tell me about the weather and then check my inventory"
    
    # Start execution
    logger.start_execution(user_id, execution_id, message)
    
    # Simulate some processing steps
    await asyncio.sleep(0.5)
    logger.log_thinking("Analyzing user request: weather + inventory check")
    
    await asyncio.sleep(0.3)
    logger.log_tool_call("weather_api", {"location": "user_location", "format": "current"})
    
    await asyncio.sleep(0.7)
    logger.log_step('info', 'Weather API returned: Sunny, 72°F')
    
    await asyncio.sleep(0.4)
    logger.log_tool_call("get_character_tool", {"player_id": "test_user_123", "server_id": "server_1"})
    
    await asyncio.sleep(0.6)
    logger.log_step('info', 'Retrieved character inventory: 5 items found')
    
    await asyncio.sleep(0.3)
    logger.log_response_chunk("The weather is currently sunny and 72°F. ")
    
    await asyncio.sleep(0.2)
    logger.log_response_chunk("I checked your inventory and found 5 items: ")
    
    await asyncio.sleep(0.2)
    logger.log_response_chunk("Iron Sword, Health Potion x2, Magic Scroll, and Gold Coins (150).")
    
    # Complete execution
    final_response = "The weather is currently sunny and 72°F. I checked your inventory and found 5 items: Iron Sword, Health Potion x2, Magic Scroll, and Gold Coins (150)."
    logger.complete_execution(final_response, 3.2)

async def test_agent_error():
    """Test error display."""
    logger = create_agent_logger("ErrorAgent")
    
    user_id = "test_user_456"
    execution_id = "exec_error_123"
    message = "This will cause an error"
    
    logger.start_execution(user_id, execution_id, message)
    
    await asyncio.sleep(0.5)
    logger.log_thinking("Processing request...")
    
    await asyncio.sleep(0.3)
    logger.error_execution("Connection timeout to external API", "TimeoutError")

if __name__ == "__main__":
    print("Testing Agent Execution Display System")
    print("=" * 50)
    
    # Test successful execution
    asyncio.run(test_agent_display())
    
    print("\n" + "=" * 50)
    print("Testing Error Display")
    print("=" * 50)
    
    # Test error execution
    asyncio.run(test_agent_error())
