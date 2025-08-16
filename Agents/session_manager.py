import asyncio
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import tiktoken

logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    """Information about a user session"""
    session_id: str
    user_id: str
    token_count: int
    created_at: datetime
    last_used: datetime
    persona_context: str

class SessionManager:
    """Manages persistent sessions with token-based clearing and persona preservation"""
    
    def __init__(self, max_tokens: int = 8000, session_timeout_hours: int = 24):
        self.max_tokens = max_tokens
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.sessions: Dict[str, SessionInfo] = {}
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using character estimate")
            return len(text) // 4  # Rough estimate: 4 chars per token
    
    def extract_persona_context(self, conversation_history: str) -> str:
        """Extract key persona information to preserve across session resets"""
        # This could be enhanced with more sophisticated extraction
        persona_keywords = [
            "tsundere", "personality", "character", "name", "role", 
            "I am", "my name", "personality", "trait", "behavior"
        ]
        
        lines = conversation_history.split('\n')
        persona_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in persona_keywords):
                persona_lines.append(line)
                
        # Keep only the most recent persona-related content
        return '\n'.join(persona_lines[-5:]) if persona_lines else ""
    
    def _register_adk_session(self, session_id: str, user_id: str):
        """Register an ADK-created session with our session manager for tracking"""
        now = datetime.now()
        
        # Clean up expired sessions first
        self._cleanup_expired_sessions(now)
        
        # Check if user already has a session we should replace
        existing_session = None
        for session_info in self.sessions.values():
            if session_info.user_id == user_id:
                existing_session = session_info
                break
        
        if existing_session and existing_session.token_count >= self.max_tokens:
            # Store old session context before replacing
            logger.info(f"Replacing token-heavy session {existing_session.session_id} with new ADK session {session_id}")
            # Remove old session
            if existing_session.session_id in self.sessions:
                del self.sessions[existing_session.session_id]
        
        # Register the ADK session
        self.sessions[session_id] = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            token_count=0,
            created_at=now,
            last_used=now,
            persona_context=""
        )
        
        logger.info(f"Registered ADK session {session_id} for user {user_id}")

    async def get_or_create_session(self, user_id: str, session_service, app_name: str) -> Tuple[str, bool]:
        """Get existing session or create new one. Returns (session_id, is_new_session)"""
        now = datetime.now()
        
        # Clean up expired sessions
        self._cleanup_expired_sessions(now)
        
        # Check if user has existing session
        existing_session = None
        for session_info in self.sessions.values():
            if session_info.user_id == user_id:
                existing_session = session_info
                break
        
        if existing_session:
            # Check if session needs reset due to token limit
            if existing_session.token_count >= self.max_tokens:
                logger.info(f"Session {existing_session.session_id} hit token limit ({existing_session.token_count}), creating new session with persona preservation")
                return await self._create_new_session_with_persona(user_id, existing_session, session_service, app_name)
            else:
                # Update last used time
                existing_session.last_used = now
                logger.info(f"Using existing session {existing_session.session_id} for user {user_id}")
                return existing_session.session_id, False
        else:
            # Create brand new session
            return await self._create_fresh_session(user_id, session_service, app_name)
    
    async def _create_fresh_session(self, user_id: str, session_service, app_name: str) -> Tuple[str, bool]:
        """Create a completely new session"""
        session = await session_service.create_session(app_name=app_name, user_id=user_id)
        session_id = session.id
        
        now = datetime.now()
        self.sessions[session_id] = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            token_count=0,
            created_at=now,
            last_used=now,
            persona_context=""
        )
        
        logger.info(f"Created fresh session {session_id} for user {user_id}")
        return session_id, True
    
    async def _create_new_session_with_persona(self, user_id: str, old_session: SessionInfo, session_service, app_name: str) -> Tuple[str, bool]:
        """Create new session while preserving context through summarization and vector storage"""
        from .context_manager import context_manager
        
        # Store the old session's conversation in vector database
        old_conversation = f"Session {old_session.session_id} conversation history with {old_session.token_count} tokens"
        if old_session.persona_context:
            old_conversation += f"\nPersona context: {old_session.persona_context}"
        
        # Store conversation chunk for future retrieval
        await context_manager.store_conversation_chunk(
            user_id, 
            old_session.session_id, 
            old_conversation
        )
        
        # Create new session
        session = await session_service.create_session(app_name=app_name, user_id=user_id)
        session_id = session.id
        
        # Get persona context from stored conversations
        persona_context = await context_manager.get_persona_context(user_id)
        persona_tokens = self.count_tokens(persona_context)
        
        now = datetime.now()
        self.sessions[session_id] = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            token_count=persona_tokens,
            created_at=now,
            last_used=now,
            persona_context=persona_context
        )
        
        # Remove old session
        if old_session.session_id in self.sessions:
            del self.sessions[old_session.session_id]
        
        logger.info(f"Created new session {session_id} with context stored in vector DB for user {user_id}")
        return session_id, True
    
    def update_token_count(self, session_id: str, message_tokens: int, response_tokens: int):
        """Update token count for a session"""
        if session_id in self.sessions:
            self.sessions[session_id].token_count += message_tokens + response_tokens
            self.sessions[session_id].last_used = datetime.now()
            logger.debug(f"Session {session_id} token count: {self.sessions[session_id].token_count}")
        else:
            logger.warning(f"Attempted to update token count for unknown session: {session_id}")
    
    def update_persona_context(self, session_id: str, conversation_snippet: str):
        """Update persona context from recent conversation"""
        if session_id in self.sessions:
            persona_info = self.extract_persona_context(conversation_snippet)
            if persona_info:
                self.sessions[session_id].persona_context = persona_info
        else:
            logger.warning(f"Attempted to update persona context for unknown session: {session_id}")
    
    def get_persona_context(self, session_id: str) -> str:
        """Get preserved persona context for session initialization"""
        if session_id in self.sessions:
            return self.sessions[session_id].persona_context
        logger.warning(f"Session {session_id} not found in session manager")
        return ""
    
    def _cleanup_expired_sessions(self, now: datetime):
        """Remove expired sessions"""
        expired_sessions = []
        for session_id, session_info in self.sessions.items():
            if now - session_info.last_used > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            logger.info(f"Removing expired session {session_id}")
            del self.sessions[session_id]
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "token_count": session.token_count,
                "max_tokens": self.max_tokens,
                "token_percentage": (session.token_count / self.max_tokens) * 100,
                "created_at": session.created_at.isoformat(),
                "last_used": session.last_used.isoformat(),
                "has_persona": bool(session.persona_context)
            }
        return {}

# Global session manager instance
session_manager = SessionManager(max_tokens=8000, session_timeout_hours=24)
