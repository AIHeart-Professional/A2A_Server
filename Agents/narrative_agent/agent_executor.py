# executor.py
import asyncio
import uuid
from typing import AsyncIterator, Dict, Optional, Union

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService  # swap to VertexAiSessionService in prod
from google.adk.events import Event
from google.adk.agents import Agent
from google.genai import types

class AgentExecutor:
    """
    Minimal A2A-style executor:
      - init(user_id) -> execution_id
      - execute(execution_id, new_message, stream=True) -> async iterator of Events (or final Event)
      - cancel(execution_id) -> stop an in-flight run
    """
    def __init__(self, agent: Agent, app_name: str = "Character_Agent", session_service=None):
        self.agent = agent
        self.runner = Runner(
            app_name=app_name,
            agent=agent,
            session_service=session_service or InMemorySessionService(),
        )
        self._sessions: Dict[str, tuple[str, str]] = {}  # exec_id -> (user_id, session_id)
        self._tasks: Dict[str, asyncio.Task] = {}        # exec_id -> in-flight task (optional)

    async def init(self, user_id: str, *, session_id: Optional[str] = None) -> str:
        # Create a brand-new ADK session unless one is provided
        if not session_id:
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name, user_id=user_id
            )
            session_id = session.id
        exec_id = str(uuid.uuid4())
        self._sessions[exec_id] = (user_id, session_id)
        return exec_id

    async def execute(
        self,
        execution_id: str,
        new_message: Union[str, types.Content],
        *,
        stream: bool = True,
    ) -> AsyncIterator[Event] | Event:
        user_id, session_id = self._sessions[execution_id]

        # You can pass a plain string; the SDK will make it user Content for you,
        # but showing the explicit form is sometimes clearer for multimodal input.
        if isinstance(new_message, str):
            new_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=new_message)],
            )

        # ADK's Runner yields Event objects as the agent runs.
        # You can stream them or consume to completion and return the final one. 
        # (run_async is the async variant; there's also run() if you don't use asyncio.)
        # Docs: Runner.run_async(...) -> AsyncGenerator[Event, None]
        #       Event has helpers like is_final_response().
        if stream:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            ):
                yield event
        else:
            last: Optional[Event] = None
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            ):
                last = event
            return last

    def cancel(self, execution_id: str) -> None:
        # If you run execute in a background Task, cancel it here.
        task = self._tasks.get(execution_id)
        if task and not task.done():
            task.cancel()
