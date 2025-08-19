#!/usr/bin/env python3
"""
Standalone script to run the narrative agent server
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agents.narrative_agent.server import main

if __name__ == "__main__":
    main()
