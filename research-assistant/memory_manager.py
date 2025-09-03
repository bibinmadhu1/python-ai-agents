from typing import Dict, List, Tuple

class MemoryManager:
    def __init__(self, max_history_per_session: int = 10):
        """
        Initialize memory manager for conversation history
        
        Args:
            max_history_per_session: Maximum number of exchanges to remember per session
        """
        self.conversation_history = {}
        self.max_history = max_history_per_session
    
    def get_context(self, session_id: str) -> str:
        """
        Get conversation context for a session
        
        Args:
            session_id: The session identifier
            
        Returns:
            Context string from previous conversation
        """
        if session_id not in self.conversation_history:
            return ""
        
        # Get last few exchanges for context
        context_exchanges = self.conversation_history[session_id][-self.max_history:]
        return "\n".join([f"Q: {q}\nA: {a}" for q, a in context_exchanges])
    
    def add_exchange(self, session_id: str, query: str, response: str):
        """
        Add a question-answer exchange to the conversation history
        
        Args:
            session_id: The session identifier
            query: The user's query
            response: The AI's response
        """
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append((query, response))
        
        # Trim history if it exceeds the maximum
        if len(self.conversation_history[session_id]) > self.max_history:
            self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history:]
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a specific session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]