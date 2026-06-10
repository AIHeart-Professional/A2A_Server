#!/usr/bin/env python3
"""
Narrative Agent A2A Server
Runs the narrative agent as an A2A server on port 8002
"""
import uvicorn
import logging
from .agent import create_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the narrative agent server"""
    app = create_app()
    logger.info("Starting Narrative Agent A2A server on port 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002)

if __name__ == "__main__":
    main()
