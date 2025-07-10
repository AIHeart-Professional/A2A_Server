from .server import main
import asyncio

if __name__ == "__main__":
    print("MCP Tool Only Server is running and waiting for requests...")    
    asyncio.run(main())
