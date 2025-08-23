"""
Context-specific logging utilities for debugging context passing
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

class ContextLogger:
    """Logger specifically for context passing operations"""
    
    def __init__(self, name: str = "context_passing"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create console handler with custom formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            
            # Custom formatter for context operations
            formatter = logging.Formatter(
                '%(asctime)s | CONTEXT | %(levelname)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_context_retrieval_start(self, user_id: str, query: str):
        """Log start of context retrieval"""
        self.logger.info(f"🔍 RETRIEVING CONTEXT for user={user_id[:8]}... query='{query[:50]}...'")
    
    def log_context_found(self, user_id: str, context_length: int, chunks_found: int):
        """Log successful context retrieval"""
        self.logger.info(f"✅ CONTEXT FOUND for user={user_id[:8]}... | {chunks_found} chunks | {context_length} chars")
    
    def log_no_context(self, user_id: str):
        """Log when no context is found"""
        self.logger.warning(f"❌ NO CONTEXT found for user={user_id[:8]}...")
    
    def log_context_injection(self, user_id: str, original_message: str, enhanced_length: int):
        """Log context injection into message"""
        self.logger.info(f"💉 INJECTING CONTEXT for user={user_id[:8]}...")
        self.logger.info(f"   Original message: '{original_message[:100]}...'")
        self.logger.info(f"   Enhanced message length: {enhanced_length} chars")
    
    def log_context_storage(self, user_id: str, session_id: str, chunk_id: str, tokens: int):
        """Log context storage"""
        self.logger.info(f"💾 STORING CONTEXT | user={user_id[:8]}... | session={session_id[:8]}... | chunk={chunk_id} | {tokens} tokens")
    
    def log_message_enhancement(self, sections: Dict[str, bool]):
        """Log which sections were added to enhanced message"""
        sections_added = [k for k, v in sections.items() if v]
        if sections_added:
            self.logger.info(f"📝 MESSAGE ENHANCED with: {', '.join(sections_added)}")
        else:
            self.logger.info("📝 MESSAGE NOT ENHANCED (no context available)")
    
    def log_context_error(self, error: Exception, operation: str):
        """Log context-related errors"""
        self.logger.error(f"❌ CONTEXT ERROR in {operation}: {type(error).__name__}: {str(error)}")
    
    def log_api_request(self, user_id: str, message: str, endpoint: str):
        """Log incoming API request"""
        self.logger.info(f"🌐 API REQUEST | {endpoint} | user={user_id[:8]}... | message='{message[:50]}...'")
    
    def log_agent_response(self, user_id: str, response_length: int, execution_time: float):
        """Log agent response"""
        self.logger.info(f"🤖 AGENT RESPONSE | user={user_id[:8]}... | {response_length} chars | {execution_time:.2f}s")

# Global context logger instance
context_logger = ContextLogger()
