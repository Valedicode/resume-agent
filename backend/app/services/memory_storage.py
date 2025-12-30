"""
In-Memory Session Storage

Thread-safe in-memory storage implementation for development and testing.
In production, this should be replaced with DatabaseSessionStorage.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from threading import Lock

from app.services.storage import SessionStorage


class MemorySessionStorage(SessionStorage):
    """
    Thread-safe in-memory session storage.
    
    **Use Cases:**
    - Development and local testing
    - Unit tests
    - Small deployments
    
    **Limitations:**
    - Data lost on server restart
    - Not suitable for horizontal scaling
    - Memory usage grows with sessions
    
    **For Production:**
    Use DatabaseSessionStorage for persistence and scalability.
    """
    
    def __init__(self):
        """Initialize in-memory storage with thread lock."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def create_session(
        self,
        session_id: str,
        session_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Create a new session in memory.
        
        Args:
            session_id: Unique session identifier
            session_type: Type of session
            data: Initial session data
            
        Returns:
            True if created, False if session_id already exists
        """
        with self._lock:
            if session_id in self._sessions:
                return False
            
            # Store session with metadata
            self._sessions[session_id] = {
                "session_id": session_id,
                "session_type": session_type,
                "created_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow(),
                "messages": [],
                **data  # Merge in initial data
            }
            
            return True
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session from memory.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        with self._lock:
            session = self._sessions.get(session_id)
            
            if session is None:
                return None
            
            # Update last accessed timestamp
            session["last_accessed"] = datetime.utcnow()
            
            # Return a copy to prevent external modifications
            return dict(session)
    
    def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data in memory.
        
        Args:
            session_id: Session identifier
            updates: Fields to update
            
        Returns:
            True if updated, False if session not found
        """
        with self._lock:
            if session_id not in self._sessions:
                return False
            
            session = self._sessions[session_id]
            
            # Update fields
            for key, value in updates.items():
                # Skip protected metadata fields
                if key in ["session_id", "created_at"]:
                    continue
                
                # Special handling for messages (append instead of replace)
                if key == "messages" and isinstance(value, list):
                    if "messages" not in session:
                        session["messages"] = []
                    session["messages"].extend(value)
                else:
                    # Don't overwrite existing data with None
                    if value is None and key in session:
                        continue
                    session[key] = value
            
            # Update timestamp
            session["last_accessed"] = datetime.utcnow()
            
            return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session from memory.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Add message to session conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role
            content: Message content
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            True if added, False if session not found
        """
        with self._lock:
            if session_id not in self._sessions:
                return False
            
            session = self._sessions[session_id]
            
            # Ensure messages list exists
            if "messages" not in session:
                session["messages"] = []
            
            # Add message
            session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": (timestamp or datetime.utcnow()).isoformat()
            })
            
            # Update last accessed
            session["last_accessed"] = datetime.utcnow()
            
            return True
    
    def get_messages(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get conversation history from session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages or None if session not found
        """
        with self._lock:
            if session_id not in self._sessions:
                return None
            
            session = self._sessions[session_id]
            messages = session.get("messages", [])
            
            # Return a copy
            return list(messages)
    
    def cleanup_expired_sessions(self, ttl_minutes: int) -> int:
        """
        Remove expired sessions from memory.
        
        Args:
            ttl_minutes: Time-to-live in minutes
            
        Returns:
            Number of sessions deleted
        """
        with self._lock:
            now = datetime.utcnow()
            ttl = timedelta(minutes=ttl_minutes)
            
            expired_ids = [
                sid for sid, session in self._sessions.items()
                if now - session["last_accessed"] > ttl
            ]
            
            for sid in expired_ids:
                del self._sessions[sid]
            
            return len(expired_ids)
    
    def get_session_count(self) -> int:
        """
        Get number of active sessions.
        
        Returns:
            Session count
        """
        with self._lock:
            return len(self._sessions)
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if exists, False otherwise
        """
        with self._lock:
            return session_id in self._sessions

