"""
SQLite-based History Manager for Wellbeing Agent
Persistent conversation storage with modular design
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading

class SQLiteHistoryManager:
    """Manages conversation history using SQLite database"""
    
    def __init__(self, db_path: str = None):
        # Always use absolute path relative to wellbeing-agent directory
        if db_path is None:
            agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(agent_dir, "data", "conversation_history.db")
        
        self.db_path = db_path
        self.lock = threading.Lock()  # Thread safety for concurrent access
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"📁 Created database directory: {db_dir}")
    
    def _initialize_database(self):
        """Initialize SQLite database with conversation tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    metadata TEXT,  -- JSON string for additional data
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    patient_id TEXT NOT NULL,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ended_at DATETIME,
                    total_messages INTEGER DEFAULT 0,
                    session_summary TEXT
                )
            ''')
            
            # Create indexes for better query performance
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_patient_timestamp 
                ON conversations(patient_id, timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_patient_role 
                ON conversations(patient_id, role)
            ''')
            
            conn.commit()
            print(f"✅ SQLite database initialized: {self.db_path}")
    
    def add_to_history(self, patient_id: str, role: str, content: str, 
                      session_id: str = None, metadata: Dict = None):
        """Add message to conversation history in database"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Insert conversation message
                    conn.execute('''
                        INSERT INTO conversations 
                        (patient_id, role, content, session_id, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        patient_id, 
                        role, 
                        content, 
                        session_id or f"{patient_id}_{datetime.now().strftime('%Y%m%d')}",
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    # Clean up old conversations (keep only last 20 pairs = 40 messages)
                    self._cleanup_old_conversations(conn, patient_id)
                    
                    conn.commit()
                    
            except sqlite3.Error as e:
                print(f"❌ Error adding to history: {e}")
    
    def _cleanup_old_conversations(self, conn: sqlite3.Connection, patient_id: str):
        """Keep only the last 20 conversation pairs (40 messages) per patient"""
        # Count total messages for this patient
        cursor = conn.execute('''
            SELECT COUNT(*) FROM conversations WHERE patient_id = ?
        ''', (patient_id,))
        
        total_messages = cursor.fetchone()[0]
        
        # If more than 40 messages, delete oldest ones
        if total_messages > 40:
            messages_to_delete = total_messages - 40
            
            conn.execute('''
                DELETE FROM conversations 
                WHERE patient_id = ? 
                AND id IN (
                    SELECT id FROM conversations 
                    WHERE patient_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            ''', (patient_id, patient_id, messages_to_delete))
            
            print(f"🧹 Cleaned up {messages_to_delete} old messages for patient {patient_id}")
    
    def get_conversation_context(self, patient_id: str, max_history: int = 20) -> List[Dict]:
        """Get recent conversation history for context"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT role, content, timestamp, metadata
                        FROM conversations 
                        WHERE patient_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (patient_id, max_history))
                    
                    messages = []
                    for row in cursor.fetchall():
                        role, content, timestamp, metadata = row
                        message = {
                            "role": role,
                            "content": content,
                            "timestamp": timestamp
                        }
                        
                        if metadata:
                            try:
                                message["metadata"] = json.loads(metadata)
                            except json.JSONDecodeError:
                                pass
                        
                        messages.append(message)
                    
                    # Return in chronological order (oldest first)
                    return list(reversed(messages))
                    
            except sqlite3.Error as e:
                print(f"❌ Error getting conversation context: {e}")
                return []
    
    def add_interaction(self, patient_id: str, user_query: str, agent_response: str, 
                       session_id: str = None, query_metadata: Dict = None, 
                       response_metadata: Dict = None):
        """Add a complete user-agent interaction (convenience method)"""
        
        # Add user message
        self.add_to_history(
            patient_id=patient_id,
            role="user", 
            content=user_query,
            session_id=session_id,
            metadata=query_metadata
        )
        
        # Add agent response
        self.add_to_history(
            patient_id=patient_id,
            role="assistant",
            content=agent_response, 
            session_id=session_id,
            metadata=response_metadata
        )
        
        print(f"💾 Stored interaction for patient {patient_id}")
    
    def clear_conversation_history(self, patient_id: str):
        """Clear conversation history for a specific patient"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        DELETE FROM conversations WHERE patient_id = ?
                    ''', (patient_id,))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    print(f"🗑️ Cleared {deleted_count} messages for patient {patient_id}")
                    return deleted_count
                    
            except sqlite3.Error as e:
                print(f"❌ Error clearing conversation history: {e}")
                return 0
    
    def get_conversation_summary(self, patient_id: str) -> Dict:
        """Get a comprehensive summary of conversation history"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Get basic stats
                    cursor = conn.execute('''
                        SELECT 
                            COUNT(*) as total_messages,
                            COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                            COUNT(CASE WHEN role = 'assistant' THEN 1 END) as agent_responses,
                            MIN(timestamp) as first_message,
                            MAX(timestamp) as last_message
                        FROM conversations 
                        WHERE patient_id = ?
                    ''', (patient_id,))
                    
                    stats = cursor.fetchone()
                    
                    if stats and stats[0] > 0:
                        total_messages, user_messages, agent_responses, first_msg, last_msg = stats
                        
                        # Get last message content
                        cursor = conn.execute('''
                            SELECT content FROM conversations 
                            WHERE patient_id = ? 
                            ORDER BY timestamp DESC 
                            LIMIT 1
                        ''', (patient_id,))
                        
                        last_content = cursor.fetchone()
                        last_content = last_content[0][:100] + "..." if last_content and len(last_content[0]) > 100 else (last_content[0] if last_content else "")
                        
                        return {
                            "total_messages": total_messages,
                            "user_messages": user_messages, 
                            "agent_responses": agent_responses,
                            "conversation_pairs": user_messages,  # Assuming user-agent pairs
                            "first_message_time": first_msg,
                            "last_message_time": last_msg,
                            "last_message_preview": last_content,
                            "status": "active" if total_messages > 0 else "empty"
                        }
                    else:
                        return {
                            "total_messages": 0,
                            "status": "no_history",
                            "message": f"No conversation history found for patient {patient_id}"
                        }
                        
            except sqlite3.Error as e:
                print(f"❌ Error getting conversation summary: {e}")
                return {"error": str(e), "status": "error"}
    
    def get_patients_with_history(self) -> List[str]:
        """Get list of all patients with conversation history"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT DISTINCT patient_id 
                        FROM conversations 
                        ORDER BY patient_id
                    ''')
                    
                    return [row[0] for row in cursor.fetchall()]
                    
            except sqlite3.Error as e:
                print(f"❌ Error getting patients list: {e}")
                return []
    
    def export_conversation_history(self, patient_id: str, format: str = "json") -> Optional[str]:
        """Export conversation history for a patient"""
        conversations = self.get_conversation_context(patient_id, max_history=1000)  # Get all
        
        if not conversations:
            return None
        
        if format.lower() == "json":
            return json.dumps(conversations, indent=2, default=str)
        elif format.lower() == "txt":
            text_output = f"Conversation History for Patient: {patient_id}\n"
            text_output += "=" * 50 + "\n\n"
            
            for msg in conversations:
                timestamp = msg.get("timestamp", "Unknown")
                role = msg["role"].upper()
                content = msg["content"]
                text_output += f"[{timestamp}] {role}: {content}\n\n"
            
            return text_output
        else:
            return json.dumps(conversations, indent=2, default=str)
    
    def get_database_info(self) -> Dict:
        """Get database statistics and information"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Get table info
                    cursor = conn.execute('''
                        SELECT 
                            COUNT(*) as total_messages,
                            COUNT(DISTINCT patient_id) as unique_patients,
                            MIN(timestamp) as oldest_message,
                            MAX(timestamp) as newest_message
                        FROM conversations
                    ''')
                    
                    stats = cursor.fetchone()
                    
                    # Get database file size
                    db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                    
                    return {
                        "database_path": self.db_path,
                        "database_size_mb": round(db_size / (1024 * 1024), 2),
                        "total_messages": stats[0] if stats else 0,
                        "unique_patients": stats[1] if stats else 0,
                        "oldest_message": stats[2] if stats else None,
                        "newest_message": stats[3] if stats else None,
                        "status": "healthy"
                    }
                    
            except sqlite3.Error as e:
                return {
                    "database_path": self.db_path,
                    "error": str(e),
                    "status": "error"
                }

# Create global instance - maintains singleton pattern for backward compatibility
sqlite_history_manager = SQLiteHistoryManager()

# Backward compatibility alias
history_manager = sqlite_history_manager
