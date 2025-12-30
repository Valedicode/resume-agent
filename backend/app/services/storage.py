"""
Storage Abstraction Layer

Defines interfaces for session storage backends (memory, database, etc.).
This allows easy migration from in-memory to database storage without
changing the session manager or API code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class SessionStorage(ABC):
    """
    Abstract base class for session storage backends.
    
    Implementations:
    - MemorySessionStorage: In-memory storage (current, for development)
    - DatabaseSessionStorage: PostgreSQL storage (future, for production)
    - RedisSessionStorage: Redis storage (future, for high-performance caching)
    
    All storage backends must implement these methods to ensure compatibility
    with the SessionManager.
    """
    
    @abstractmethod
    def create_session(
        self,
        session_id: str,
        session_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier (UUID)
            session_type: Type of session ("writer", "supervisor", etc.)
            data: Initial session data
            
        Returns:
            True if created successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dict or None if not found
        """
        pass
    
    @abstractmethod
    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False if session not found
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Add a message to the session's conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role ("user", "assistant", "system")
            content: Message content
            timestamp: Message timestamp (defaults to now)
            
        Returns:
            True if added successfully, False if session not found
        """
        pass
    
    @abstractmethod
    def get_messages(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dicts or None if session not found
        """
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self, ttl_minutes: int) -> int:
        """
        Remove sessions that haven't been accessed recently.
        
        Args:
            ttl_minutes: Time-to-live in minutes
            
        Returns:
            Number of sessions deleted
        """
        pass
    
    @abstractmethod
    def get_session_count(self) -> int:
        """
        Get the total number of active sessions.
        
        Returns:
            Number of sessions
        """
        pass
    
    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists, False otherwise
        """
        pass

