from .server import main
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("MCP Tool Only Server is running and waiting for requests...")
    asyncio.run(main())
