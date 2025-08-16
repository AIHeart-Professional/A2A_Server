import asyncio
import logging
import sys
import os

# Set up logging to see the debug output
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from Agents.Veritas_Agent.delegation_tools import discover_available_agents

async def test_discovery():
    print("Testing agent discovery...")
    result = await discover_available_agents()
    print("\n=== DISCOVERY RESULT ===")
    print(result)
    print("========================")

if __name__ == "__main__":
    asyncio.run(test_discovery())
