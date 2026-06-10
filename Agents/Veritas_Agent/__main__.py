from agent_executor import AgentExecutor
from agent_card import agent_card

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
import uvicorn

if __name__ == '__main__':
    # 1. Request Handler
    request_handler = DefaultRequestHandler(
        agent_executor=AgentExecutor(),
        task_store=InMemoryTaskStore()
    )

    # 2. Starlette Application
    server_app_builder = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # ---------- ROUTE CHECK BEGIN ----------
    app = server_app_builder.build()
    print("Registered Starlette Routes:")
    for route in app.routes:
        print(route)
    # ---------- ROUTE CHECK END ------------

    # 3. Start Server
    uvicorn.run(app, host='0.0.0.0', port=9999)
