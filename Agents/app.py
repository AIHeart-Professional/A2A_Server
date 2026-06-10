import asyncio
import logging
from uuid import uuid4
from Agents.Veritas_Agent.agent_executor import AgentExecutor
from Agents.Veritas_Agent.agent import root_agent
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def execute_agent(request: dict) -> dict:
    """Entry after API call: always delegate to Veritas parent agent.

    This keeps a stable, static entry that routes all agent handling to
    `Agents.Veritas_Agent.app.execute_agent`.
    """
    logger.info(f"execute_agent called with request keys: {list(request.keys())}")
    
    # Extract user_id, character_id, server_id and message from request
    user_info = request.get("request").get("user_info", {})
    user_id = user_info.get("user_id")
    character_id = user_info.get("character_id")
    server_id = user_info.get("server_id")
    message = request.get("request").get("user_query")
    
    logger.info(f"Extracted user_id: {user_id}, character_id: {character_id}, server_id: {server_id}, message: {message[:50]}...")
    
    # Create executor with the root agent
    executor = AgentExecutor(root_agent, "Veritas_Agent")
    logger.info(f"Created executor: {executor}")
    
    # Initialize session - this stores the execution_id in executor._sessions
    logger.info(f"Calling executor.init({user_id}, character_id={character_id}, server_id={server_id})")
    try:
        execution_id = await executor.init(user_id, character_id=character_id, server_id=server_id)
        logger.info(f"Got execution_id: {execution_id}")
    except Exception as e:
        logger.error(f"EXCEPTION in executor.init: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    # Execute and collect all events with error handling
    # IMPORTANT: Use the same executor instance that has the session stored
    logger.info(f"Starting executor.execute({execution_id}, {message[:30]}...)")
    try:
        events = []
        logger.info(f"About to iterate over executor.execute()")
        logger.info(f"Executor sessions: {executor._sessions}")
        async for event in executor.execute(execution_id, message, stream=True):
            logger.info(f"Got event: {type(event)}")
            events.append(event)
        
        # Return the final event or a summary
        if events:
            final_event = events[-1]
            
            # Extract text content from the Event object
            response_text = ""
            if hasattr(final_event, 'content') and final_event.content:
                if hasattr(final_event.content, 'parts') and final_event.content.parts:
                    # Extract text from all parts
                    text_parts = []
                    for part in final_event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text.strip())
                    response_text = " ".join(text_parts)
            
            # Fallback to string representation if we can't extract text
            if not response_text:
                response_text = str(final_event)
            
            return {
                "status": "success",
                "response": response_text,
                "execution_id": execution_id
            }
        else:
            return {
                "status": "error",
                "response": "No response generated",
                "execution_id": execution_id
            }
    except asyncio.TimeoutError:
        logger.error(f"TimeoutError in execute_agent")
        return {
            "status": "error",
            "response": "Agent execution timed out after 30 seconds",
            "execution_id": execution_id
        }
    except Exception as e:
        logger.error(f"Exception in execute_agent: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "response": f"Agent execution failed: {str(e)}",
            "execution_id": execution_id,
            "error_type": type(e).__name__
        }


async def execute_agent_stream(request: dict):
    """
    Streaming version of execute_agent that yields events in real-time.
    Entry after API call: always delegate to Veritas parent agent with streaming.
    """
    # Extract user_id, character_id, server_id and message from request
    user_info = request.get("request").get("user_info", {})
    user_id = user_info.get("user_id")
    character_id = user_info.get("character_id")
    server_id = user_info.get("server_id")
    message = request.get("request").get("user_query")
    
    # Create executor with the root agent
    executor = AgentExecutor(root_agent, "Veritas_Agent")
    
    # Initialize session - this stores the execution_id in executor._sessions
    execution_id = await executor.init(user_id, character_id=character_id, server_id=server_id)
    
    # Yield initial status
    yield {
        'type': 'status',
        'message': 'Starting agent processing...',
        'execution_id': execution_id
    }
    
    # Execute and stream events with error handling
    try:
        async for event in executor.execute(execution_id, message, stream=True):
            # Extract text content from event
            event_text = ""
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    text_parts = []
                    for part in event.content.parts:
                        # Only include text parts, skip function calls
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text.strip())
                    event_text = " ".join(text_parts)
            
            # Only yield events with actual text content (skip function calls and internal events)
            if event_text:
                yield {
                    'type': 'agent_event',
                    'content': event_text,
                    'execution_id': execution_id,
                    'timestamp': asyncio.get_event_loop().time()
                }
            
            # Check if this is the final response
            if hasattr(event, 'is_final_response') and event.is_final_response():
                break
        
        # Yield completion status
        yield {
            'type': 'complete',
            'message': event_text,
            'execution_id': execution_id
        }
        
    except asyncio.TimeoutError:
        yield {
            'type': 'error',
            'message': 'Agent execution timed out after 30 seconds',
            'execution_id': execution_id
        }
    except Exception as e:
        yield {
            'type': 'error',
            'message': f'Agent execution failed: {str(e)}',
            'execution_id': execution_id,
            'error_type': type(e).__name__
        }

