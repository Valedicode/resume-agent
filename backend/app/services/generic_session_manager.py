"""
Generic Session Manager

Unified session manager that works with any storage backend.
Supports multiple session types (writer, supervisor, future agents).
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import timedelta

from app.services.storage import SessionStorage


class GenericSessionManager:
    """
    Generic session manager with pluggable storage backend.
    
    **Features:**
    - Works with any storage implementation (memory, database, Redis)
    - Supports multiple session types
    - Flexible session data structure
    - Conversation message management
    - Automatic expiration
    
    **Session Types:**
    - "writer": Writer agent conversations
    - "supervisor": Supervisor agent workflows (legacy, will be removed)
    - Custom types as needed
    
    **Usage:**
    ```python
    # Development: In-memory storage
    storage = MemorySessionStorage()
    manager = GenericSessionManager(storage, ttl_minutes=60)
    
    # Production: Database storage
    storage = DatabaseSessionStorage(db_session)
    manager = GenericSessionManager(storage, ttl_minutes=120)
    ```
    """
    
    def __init__(
        self,
        storage: SessionStorage,
        ttl_minutes: int = 60
    ):
        """
        Initialize session manager.
        
        Args:
            storage: Storage backend implementation
            ttl_minutes: Session time-to-live in minutes (default: 60)
        """
        self.storage = storage
        self.ttl = timedelta(minutes=ttl_minutes)
        self.ttl_minutes = ttl_minutes
    
    def create_session(
        self,
        session_type: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session.
        
        Args:
            session_type: Type of session ("writer", "supervisor", etc.)
            initial_data: Optional initial session data
            
        Returns:
            session_id: Unique session identifier (UUID)
            
        Example:
            ```python
            # Writer session
            session_id = manager.create_session(
                session_type="writer",
                initial_data={
                    "cv_data": cv_dict,
                    "job_data": job_dict,
                    "mode": "job_tailoring"
                }
            )
            
            # Empty session
            session_id = manager.create_session("supervisor")
            ```
        """
        session_id = str(uuid.uuid4())
        data = initial_data or {}
        
        self.storage.create_session(
            session_id=session_id,
            session_type=session_type,
            data=data
        )
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dict or None if not found/expired
        """
        return self.storage.get_session(session_id)
    
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
            True if successful, False if session not found
        """
        return self.storage.update_session(session_id, updates)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete_session(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role ("user", "assistant", "system")
            content: Message content
            
        Returns:
            True if added, False if session not found
        """
        return self.storage.add_message(session_id, role, content)
    
    def get_messages(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dicts or None if session not found
        """
        return self.storage.get_messages(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if exists, False otherwise
        """
        return self.storage.session_exists(session_id)
    
    def get_session_count(self) -> int:
        """
        Get the number of active sessions.
        
        Returns:
            Session count
        """
        return self.storage.get_session_count()
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Should be called periodically (e.g., via background task).
        
        Returns:
            Number of sessions cleaned up
        """
        return self.storage.cleanup_expired_sessions(self.ttl_minutes)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata without full conversation history.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session info dict or None if not found
        """
        session = self.get_session(session_id)
        if session is None:
            return None
        
        return {
            "session_id": session.get("session_id"),
            "session_type": session.get("session_type"),
            "created_at": session.get("created_at").isoformat() if session.get("created_at") else None,
            "last_accessed": session.get("last_accessed").isoformat() if session.get("last_accessed") else None,
            "message_count": len(session.get("messages", [])),
            # Add type-specific fields
            "mode": session.get("mode"),  # For writer sessions
            "has_cv_data": session.get("cv_data") is not None,
            "has_job_data": session.get("job_data") is not None,
        }


# Global manager instance
_session_manager: Optional[GenericSessionManager] = None


def get_session_manager() -> GenericSessionManager:
    """
    Get the global session manager instance.
    
    Uses dependency injection pattern for FastAPI.
    Creates manager with in-memory storage by default.
    
    Returns:
        GenericSessionManager singleton
    """
    global _session_manager
    
    if _session_manager is None:
        # Default: in-memory storage for development
        from app.services.memory_storage import MemorySessionStorage
        storage = MemorySessionStorage()
        _session_manager = GenericSessionManager(storage, ttl_minutes=60)
    
    return _session_manager


def reset_session_manager():
    """
    Reset the session manager (useful for testing).
    """
    global _session_manager
    _session_manager = None


def configure_session_manager(storage: SessionStorage, ttl_minutes: int = 60):
    """
    Configure the global session manager with custom storage.
    
    Call this during application startup to use database storage:
    ```python
    @app.on_event("startup")
    async def startup():
        db_storage = DatabaseSessionStorage(db_session)
        configure_session_manager(db_storage, ttl_minutes=120)
    ```
    
    Args:
        storage: Storage backend implementation
        ttl_minutes: Session time-to-live
    """
    global _session_manager
    _session_manager = GenericSessionManager(storage, ttl_minutes)

