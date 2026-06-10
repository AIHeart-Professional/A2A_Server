#!/usr/bin/env python3
"""
Mock Narrative Agent Server - Runs without Gemini API
"""
import uvicorn
import logging
from .mock_agent import create_mock_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the mock narrative agent server"""
    app = create_mock_app()
    logger.info("Starting Mock Narrative Agent server on port 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002)

if __name__ == "__main__":
    main()
