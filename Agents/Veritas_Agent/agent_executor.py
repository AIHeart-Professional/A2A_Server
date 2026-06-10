from typing_extensions import override
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from agent import VeritasAgent
import logging
import warnings
from config.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Suppress the specific Google GenAI warning about non-text parts
warnings.filterwarnings("ignore", message=".*there are non-text parts in the response.*", category=UserWarning)

# Suppress Google GenAI warnings by setting its logger to ERROR level
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

class AgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""
    def __init__(self):
        logger.info("Initializing AgentExecutor")
        self.agent = VeritasAgent()

    @override
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Extract message text from the request context
        logger.info(f"Context!: {context.message.parts[0].root.text}")
        message_text = context.message.parts[0].root.text
        if hasattr(context, 'message') and context.message:
            if hasattr(context.message, 'parts') and context.message.parts:
                for part in context.message.parts:
                    if hasattr(part, 'text'):
                        message_text += part.text
        
        # If no message found, use a default
        if not message_text:
            raise Exception("No message found in request context")
        
        # Invoke agent with the actual message
        result = await self.agent.invoke(message_text)
        await event_queue.enqueue_event(new_agent_text_message(result))

    @override
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported") 