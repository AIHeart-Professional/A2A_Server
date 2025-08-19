#!/usr/bin/env python3
"""
Standalone script to run the mock narrative agent server
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.narrative_agent.mock_server import main

if __name__ == "__main__":
    main()
