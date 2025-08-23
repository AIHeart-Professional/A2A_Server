import asyncio
import logging
import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
import tiktoken

logger = logging.getLogger(__name__)

@dataclass
class ConversationChunk:
    """A chunk of conversation with metadata"""
    id: str
    user_id: str
    session_id: str
    content: str
    summary: str
    timestamp: datetime
    tokens: int
    embedding: Optional[List[float]] = None

class ContextManager:
    """Manages conversation context with summarization and vector storage"""
    
    def __init__(self, db_path: str = "conversation_context.db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Initialize embedding model for semantic search
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(embedding_model)
        except ImportError:
            logger.warning("sentence-transformers not available, using simple text matching")
            self.embedding_model = None
            
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for context storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_chunks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tokens INTEGER NOT NULL,
                embedding BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON conversation_chunks(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id ON conversation_chunks(session_id)
        ''')
        
        conn.commit()
        conn.close()
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using character estimate")
            return len(text) // 4
    
    async def summarize_conversation_chunk(self, conversation: str) -> str:
        """Summarize a chunk of conversation using a simple approach"""
        # This is a basic summarization - you could enhance with LLM calls
        lines = conversation.split('\n')
        
        # Extract key information
        user_messages = [line for line in lines if line.startswith('User:')]
        agent_messages = [line for line in lines if line.startswith('Agent:')]
        
        # Create summary
        summary_parts = []
        
        if user_messages:
            summary_parts.append(f"User discussed: {'; '.join([msg[5:].strip()[:100] for msg in user_messages[-3:]])}")
        
        if agent_messages:
            # Extract personality traits and key responses
            personality_indicators = []
            for msg in agent_messages:
                msg_lower = msg.lower()
                if any(trait in msg_lower for trait in ['tsundere', 'baka', 'idiot', 'not like', "it's not like"]):
                    personality_indicators.append("tsundere personality")
                if any(emotion in msg_lower for emotion in ['embarrassed', 'flustered', 'annoyed']):
                    personality_indicators.append("emotional responses")
            
            if personality_indicators:
                summary_parts.append(f"Agent showed: {', '.join(set(personality_indicators))}")
            
            summary_parts.append(f"Agent responses: {'; '.join([msg[6:].strip()[:100] for msg in agent_messages[-2:]])}")
        
        return ' | '.join(summary_parts)
    
    async def store_conversation_chunk(self, user_id: str, session_id: str, conversation: str) -> str:
        """Store a conversation chunk with summary and embedding"""
        chunk_id = f"{user_id}_{session_id}_{int(datetime.now().timestamp())}"
        
        # Create summary
        summary = await self.summarize_conversation_chunk(conversation)
        
        # Create embedding for semantic search
        if self.embedding_model:
            embedding = self.embedding_model.encode(f"{summary} {conversation}").tolist()
        else:
            # Fallback to simple hash-based embedding
            embedding = [hash(f"{summary} {conversation}") % 1000 / 1000.0]
        
        # Count tokens
        tokens = self.count_tokens(conversation)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_chunks 
            (id, user_id, session_id, content, summary, timestamp, tokens, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chunk_id,
            user_id,
            session_id,
            conversation,
            summary,
            datetime.now().isoformat(),
            tokens,
            json.dumps(embedding)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored conversation chunk {chunk_id} with {tokens} tokens")
        return chunk_id
    
    async def retrieve_relevant_context(self, user_id: str, query: str, max_chunks: int = 5, max_tokens: int = 2000) -> str:
        """Retrieve relevant conversation context using semantic search"""
        # Create query embedding
        if not self.embedding_model:
            # Fallback to simple text matching without embeddings
            return await self._simple_text_search(user_id, query, max_chunks, max_tokens)
            
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Get all chunks for user
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, summary, content, tokens, embedding, timestamp
            FROM conversation_chunks 
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (user_id,))
        
        chunks = cursor.fetchall()
        conn.close()
        
        if not chunks:
            return ""
        
        # Calculate similarity scores
        scored_chunks = []
        for chunk in chunks:
            chunk_id, summary, content, tokens, embedding_json, timestamp = chunk
            try:
                chunk_embedding = json.loads(embedding_json)
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                scored_chunks.append((similarity, summary, content, tokens, timestamp))
            except Exception as e:
                logger.warning(f"Error calculating similarity for chunk {chunk_id}: {e}")
        
        # Sort by similarity and select top chunks
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Build context within token limit
        context_parts = []
        total_tokens = 0
        
        for similarity, summary, content, tokens, timestamp in scored_chunks[:max_chunks]:
            if total_tokens + tokens <= max_tokens:
                context_parts.append(f"[Previous context - {timestamp[:10]}]: {summary}")
                total_tokens += tokens
            else:
                break
        
        return "\n".join(context_parts)
    
    async def _simple_text_search(self, user_id: str, query: str, max_chunks: int = 5, max_tokens: int = 2000) -> str:
        """Simple text-based search fallback when embeddings aren't available"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent chunks and search by keyword matching
        cursor.execute('''
            SELECT summary, content, tokens, timestamp
            FROM conversation_chunks 
            WHERE user_id = ? AND (
                LOWER(summary) LIKE LOWER(?) OR 
                LOWER(content) LIKE LOWER(?)
            )
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, f'%{query}%', f'%{query}%', max_chunks * 2))
        
        chunks = cursor.fetchall()
        conn.close()
        
        if not chunks:
            # If no keyword matches, return most recent chunks
            return await self._get_recent_context(user_id, max_chunks, max_tokens)
        
        # Build context within token limit
        context_parts = []
        total_tokens = 0
        
        for summary, content, tokens, timestamp in chunks[:max_chunks]:
            if total_tokens + tokens <= max_tokens:
                context_parts.append(f"[Previous context - {timestamp[:10]}]: {summary}")
                total_tokens += tokens
            else:
                break
        
        return "\n".join(context_parts)
    
    async def _get_recent_context(self, user_id: str, max_chunks: int = 5, max_tokens: int = 2000) -> str:
        """Get most recent conversation context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT summary, content, tokens, timestamp
            FROM conversation_chunks 
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, max_chunks))
        
        chunks = cursor.fetchall()
        conn.close()
        
        # Build context within token limit
        context_parts = []
        total_tokens = 0
        
        for summary, content, tokens, timestamp in chunks:
            if total_tokens + tokens <= max_tokens:
                context_parts.append(f"[Previous context - {timestamp[:10]}]: {summary}")
                total_tokens += tokens
            else:
                break
        
        return "\n".join(context_parts)
    
    async def get_persona_context(self, user_id: str) -> str:
        """Get persona-specific context for character consistency"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT summary, content FROM conversation_chunks 
            WHERE user_id = ? 
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (user_id,))
        
        chunks = cursor.fetchall()
        conn.close()
        
        # Extract persona-related information
        persona_traits = []
        for summary, content in chunks:
            # Look for personality indicators in summaries
            if any(trait in summary.lower() for trait in ['tsundere', 'personality', 'character', 'trait']):
                persona_traits.append(summary)
        
        return " | ".join(persona_traits[-3:]) if persona_traits else ""
    
    async def cleanup_old_chunks(self, days_old: int = 30):
        """Clean up old conversation chunks"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM conversation_chunks 
            WHERE timestamp < ?
        ''', (datetime.fromtimestamp(cutoff_date).isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted_count} old conversation chunks")
        return deleted_count
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a user's stored context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*), SUM(tokens), MIN(timestamp), MAX(timestamp)
            FROM conversation_chunks 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return {
                "chunk_count": result[0],
                "total_tokens": result[1],
                "first_conversation": result[2],
                "last_conversation": result[3]
            }
        return {"chunk_count": 0, "total_tokens": 0}

# Global context manager instance
context_manager = ContextManager()
