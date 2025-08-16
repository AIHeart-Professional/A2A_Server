"""
Agent Execution Display Utilities
Provides clean, structured output formatting for agent execution flow.
"""
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

class AgentDisplayFormatter:
    """Formats agent execution output for clean, readable display."""
    
    def __init__(self):
        self.start_time = None
        self.current_step = 0
        
    def format_header(self, agent_name: str, user_id: str, execution_id: str) -> str:
        """Format execution start header."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        header = f"""
{Fore.CYAN}{'='*80}
{Fore.CYAN}🤖 AGENT EXECUTION STARTED
{Fore.CYAN}{'='*80}
{Fore.WHITE}Agent: {Fore.YELLOW}{agent_name}
{Fore.WHITE}User ID: {Fore.GREEN}{user_id}
{Fore.WHITE}Execution ID: {Fore.BLUE}{execution_id[:8]}...
{Fore.WHITE}Started: {Fore.MAGENTA}{timestamp}
{Fore.CYAN}{'='*80}{Style.RESET_ALL}
"""
        self.start_time = time.time()
        return header
    
    def format_step(self, step_type: str, content: str, details: Optional[Dict] = None) -> str:
        """Format individual execution step."""
        self.current_step += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = f"{time.time() - self.start_time:.2f}s" if self.start_time else "0.00s"
        
        # Color coding by step type
        colors = {
            'thinking': Fore.YELLOW,
            'tool_call': Fore.BLUE,
            'response': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.MAGENTA,
            'info': Fore.CYAN
        }
        
        icons = {
            'thinking': '🧠',
            'tool_call': '🔧',
            'response': '💬',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        color = colors.get(step_type, Fore.WHITE)
        icon = icons.get(step_type, '📝')
        
        step_header = f"{color}┌─ {icon} Step {self.current_step}: {step_type.upper()} [{elapsed}]{Style.RESET_ALL}"
        
        # Format content with proper indentation
        content_lines = content.strip().split('\n')
        formatted_content = []
        for line in content_lines:
            if line.strip():
                formatted_content.append(f"{color}│ {Style.RESET_ALL}{line}")
        
        # Add details if provided
        if details:
            formatted_content.append(f"{color}│ {Fore.WHITE}Details: {details}{Style.RESET_ALL}")
        
        step_footer = f"{color}└{'─' * 50}{Style.RESET_ALL}"
        
        return '\n'.join([step_header] + formatted_content + [step_footer])
    
    def format_completion(self, final_response: str, total_time: Optional[float] = None) -> str:
        """Format execution completion."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = total_time or (time.time() - self.start_time if self.start_time else 0)
        
        completion = f"""
{Fore.GREEN}{'='*80}
{Fore.GREEN}✅ AGENT EXECUTION COMPLETED
{Fore.GREEN}{'='*80}
{Fore.WHITE}Completed: {Fore.MAGENTA}{timestamp}
{Fore.WHITE}Total Time: {Fore.YELLOW}{elapsed:.2f}s
{Fore.WHITE}Total Steps: {Fore.CYAN}{self.current_step}
{Fore.GREEN}{'='*80}
{Fore.WHITE}Final Response:
{Fore.GREEN}{'-'*40}
{Style.RESET_ALL}{final_response}
{Fore.GREEN}{'-'*40}
{Fore.GREEN}{'='*80}{Style.RESET_ALL}
"""
        return completion
    
    def format_error(self, error_msg: str, error_type: str = "Unknown") -> str:
        """Format execution error."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        error = f"""
{Fore.RED}{'='*80}
{Fore.RED}❌ AGENT EXECUTION FAILED
{Fore.RED}{'='*80}
{Fore.WHITE}Failed: {Fore.MAGENTA}{timestamp}
{Fore.WHITE}Runtime: {Fore.YELLOW}{elapsed:.2f}s
{Fore.WHITE}Error Type: {Fore.RED}{error_type}
{Fore.RED}{'='*80}
{Fore.WHITE}Error Details:
{Fore.RED}{'-'*40}
{Style.RESET_ALL}{error_msg}
{Fore.RED}{'-'*40}
{Fore.RED}{'='*80}{Style.RESET_ALL}
"""
        return error

class AgentLogger:
    """Enhanced logger for agent execution with structured output."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.formatter = AgentDisplayFormatter()
        
    def start_execution(self, user_id: str, execution_id: str, message: str):
        """Log execution start."""
        header = self.formatter.format_header(self.agent_name, user_id, execution_id)
        print(header)
        
        # Log initial message
        step = self.formatter.format_step('info', f'Processing: "{message[:100]}..."')
        print(step)
        
    def log_step(self, step_type: str, content: str, details: Optional[Dict] = None):
        """Log execution step."""
        step = self.formatter.format_step(step_type, content, details)
        print(step)
        
    def log_tool_call(self, tool_name: str, parameters: Dict):
        """Log tool call."""
        content = f"Calling tool: {tool_name}"
        details = {"parameters": parameters}
        self.log_step('tool_call', content, details)
        
    def log_thinking(self, thought: str):
        """Log agent thinking process."""
        self.log_step('thinking', thought)
        
    def log_response_chunk(self, chunk: str):
        """Log response chunk."""
        if chunk.strip():
            self.log_step('response', chunk)
    
    def complete_execution(self, final_response: str, total_time: Optional[float] = None):
        """Log execution completion."""
        completion = self.formatter.format_completion(final_response, total_time)
        print(completion)
        
    def error_execution(self, error_msg: str, error_type: str = "Unknown"):
        """Log execution error."""
        error = self.formatter.format_error(error_msg, error_type)
        print(error)

def create_agent_logger(agent_name: str) -> AgentLogger:
    """Factory function to create agent logger."""
    return AgentLogger(agent_name)
