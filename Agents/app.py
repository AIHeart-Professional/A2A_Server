import asyncio
from Agents.Veritas_Agent.agent_executor import AgentExecutor
from Agents.Veritas_Agent.agent import root_agent


async def execute_agent(request: dict) -> dict:
    """Entry after API call: always delegate to Veritas parent agent.

    This keeps a stable, static entry that routes all agent handling to
    `Agents.Veritas_Agent.app.execute_agent`.
    """
    # Extract user_id and message from request
    user_id = request.get("request").get("user_info").get("user_id")
    message = request.get("request").get("user_query")
    
    # Create executor with the root agent
    executor = AgentExecutor(root_agent, "Veritas_Agent")
    
    # Initialize session
    execution_id = await executor.init(user_id)
    
    # Execute and collect all events with error handling
    try:
        events = []
        async for event in executor.execute(execution_id, message, stream=True):
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
        return {
            "status": "error",
            "response": "Agent execution timed out after 30 seconds",
            "execution_id": execution_id
        }
    except Exception as e:
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
    # Extract user_id and message from request
    user_id = request.get("request").get("user_info").get("user_id")
    message = request.get("request").get("user_query")
    
    # Create executor with the root agent
    executor = AgentExecutor(root_agent, "Veritas_Agent")
    
    # Initialize session
    execution_id = await executor.init(user_id)
    
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
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text.strip())
                    event_text = " ".join(text_parts)
            
            # Yield agent event
            yield {
                'type': 'agent_event',
                'content': event_text or str(event),
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

