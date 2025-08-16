# executor.py
import asyncio
import uuid
from typing import AsyncIterator, Dict, Optional, Union

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService  # swap to VertexAiSessionService in prod
from google.adk.events import Event
from google.adk.agents import Agent
from google.genai import types
from utils.agent_display import create_agent_logger

class AgentExecutor:
    """
    Minimal A2A-style executor:
      - init(user_id) -> execution_id
      - execute(execution_id, new_message, stream=True) -> async iterator of Events (or final Event)
      - cancel(execution_id) -> stop an in-flight run
    """
    def __init__(self, agent: Agent, app_name: str = "Veritas_Agent", session_service=None):
        self.agent = agent
        self.app_name = app_name
        self.session_service = session_service or InMemorySessionService()
        self.runner = Runner(
            app_name=app_name,
            agent=agent,
            session_service=self.session_service,
        )
        self._sessions: Dict[str, tuple[str, str]] = {}  # exec_id -> (user_id, session_id)
        self._tasks: Dict[str, asyncio.Task] = {}        # exec_id -> in-flight task (optional)
        self.logger = create_agent_logger(app_name)

    async def init(self, user_id: str, *, session_id: Optional[str] = None) -> str:
        print(f"[DEBUG] Agent executor init started for user: {user_id}")
        # Create ADK session first, then track it in session manager
        if not session_id:
            print(f"[DEBUG] Creating new ADK session...")
            try:
                # Create ADK session directly
                adk_session = await self.session_service.create_session(
                    app_name=self.app_name, 
                    user_id=user_id
                )
                session_id = adk_session.id
                print(f"[DEBUG] Created ADK session: {session_id}")
                
                # Now register this ADK session with our session manager for token tracking
                from ..session_manager import session_manager
                session_manager._register_adk_session(session_id, user_id)
                print(f"[DEBUG] Registered session with session manager")
            except Exception as e:
                print(f"[DEBUG] EXCEPTION creating ADK session: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
            
            print(f"[DEBUG] Checking for context injection...")
            # Skip context injection for now to isolate the core issue
            # TODO: Re-enable context injection after fixing basic execution
            print(f"[DEBUG] Skipping context injection to isolate execution issue")
        
        exec_id = str(uuid.uuid4())
        self._sessions[exec_id] = (user_id, session_id)
        
        # Debug logging to track session creation
        self.logger.log_step('info', f'Created execution ID: {exec_id[:8]}... for session: {session_id[:8]}...')
        print(f"[DEBUG] Agent executor init completed - exec_id: {exec_id}, session_id: {session_id}")
        return exec_id

    async def execute(
        self,
        execution_id: str,
        new_message: Union[str, types.Content],
        *,
        stream: bool = True,
    ) -> AsyncIterator[Event]:
        # Validate execution ID exists
        if execution_id not in self._sessions:
            self.logger.error_execution(f"Execution ID not found: {execution_id}. Available sessions: {list(self._sessions.keys())}", "ValueError")
            raise ValueError(f"Session not found: {execution_id}")
            
        user_id, session_id = self._sessions[execution_id]
        
        # Debug logging to track execution start
        self.logger.log_step('info', f'Starting execution for ID: {execution_id[:8]}... with session: {session_id[:8]}...')

        # Convert string to Content if needed
        message_text = new_message if isinstance(new_message, str) else str(new_message)
        if isinstance(new_message, str):
            new_message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=new_message)],
            )

        # Start clean execution display
        self.logger.start_execution(user_id, execution_id, message_text)
        print(f"[DEBUG] About to call runner.run_async with user_id={user_id}, session_id={session_id}")
        
        # Add timeout to prevent infinite loops
        timeout_seconds = 30  # 30 second timeout
        start_time = asyncio.get_event_loop().time()
        
        # Track tokens for session management
        from ..session_manager import session_manager
        message_tokens = session_manager.count_tokens(str(new_message))
        response_tokens = 0
        full_response = ""
        
        try:
            if stream:
                print(f"[DEBUG] Calling self.runner.run_async...")
                async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=new_message,
                ):
                    print(f"[DEBUG] Received event from runner: {type(event)}")
                    # Check timeout manually
                    if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                        self.logger.error_execution(f"Execution timed out after {timeout_seconds} seconds", "TimeoutError")
                        raise asyncio.TimeoutError()
                    
                    # Process and display event content
                    event_content = ""
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts') and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    event_content = part.text
                                    full_response += part.text
                                elif hasattr(part, 'function_call') and part.function_call:
                                    # Log tool calls
                                    func_call = part.function_call
                                    if func_call and hasattr(func_call, 'name'):
                                        self.logger.log_tool_call(func_call.name, dict(func_call.args) if hasattr(func_call, 'args') else {})
                    
                    # Log response chunks
                    if event_content.strip():
                        self.logger.log_response_chunk(event_content)
                    
                    yield event
                    # Check if this is a final response to break early
                    if hasattr(event, 'is_final_response') and event.is_final_response():
                        break
                
                # Complete execution display
                total_time = asyncio.get_event_loop().time() - start_time
                self.logger.complete_execution(full_response, total_time)
                
                # Update session token count and store conversation context
                response_tokens = session_manager.count_tokens(full_response)
                session_manager.update_token_count(session_id, message_tokens, response_tokens)
                session_manager.update_persona_context(session_id, f"User: {new_message}\nAgent: {full_response}")
                
                # Store conversation chunk in vector database for future retrieval
                from ..context_manager import context_manager
                conversation_chunk = f"User: {new_message}\nAgent: {full_response}"
                await context_manager.store_conversation_chunk(user_id, session_id, conversation_chunk)
            else:
                last: Optional[Event] = None
                async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=new_message,
                ):
                    # Check timeout manually
                    if asyncio.get_event_loop().time() - start_time > timeout_seconds:
                        self.logger.error_execution(f"Execution timed out after {timeout_seconds} seconds", "TimeoutError")
                        raise asyncio.TimeoutError()
                    
                    # Process event for display
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts') and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    full_response += part.text
                    
                    last = event
                    # Check if this is a final response to break early
                    if hasattr(event, 'is_final_response') and event.is_final_response():
                        break
                
                if last is not None:
                    total_time = asyncio.get_event_loop().time() - start_time
                    self.logger.complete_execution(full_response, total_time)
                    yield last
                    
        except asyncio.TimeoutError:
            # Use clean error display
            self.logger.error_execution(f"Execution timed out after {timeout_seconds} seconds", "TimeoutError")
            raise
        except Exception as e:
            # Use clean error display
            print(f"[DEBUG] Exception in agent executor: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.logger.error_execution(str(e), type(e).__name__)
            raise

    def cancel(self, execution_id: str) -> None:
        # If you run execute in a background Task, cancel it here.
        task = self._tasks.get(execution_id)
        if task and not task.done():
            task.cancel()
