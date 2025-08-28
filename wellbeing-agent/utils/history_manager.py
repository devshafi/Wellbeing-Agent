"""
History Manager - Backward Compatible Interface
Now uses SQLite backend for persistent storage
"""

from .sqlite_history_manager import SQLiteHistoryManager

class HistoryManager:
    """Manages conversation history for patients - Updated with SQLite backend"""
    
    def __init__(self):
        # Use SQLite backend for persistence
        self.sqlite_manager = SQLiteHistoryManager()
        print("📁 History Manager initialized with SQLite backend")
    
    def add_to_history(self, patient_id, role, content):
        """Add message to conversation history - Backward compatible method"""
        self.sqlite_manager.add_to_history(patient_id, role, content)
    
    def get_conversation_context(self, patient_id, max_history=20):
        """Get recent conversation history for context - Backward compatible"""
        return self.sqlite_manager.get_conversation_context(patient_id, max_history)
    
    def clear_conversation_history(self, patient_id):
        """Clear conversation history for a specific patient - Backward compatible"""
        return self.sqlite_manager.clear_conversation_history(patient_id)
    
    def get_conversation_summary(self, patient_id):
        """Get a summary of conversation history - Backward compatible"""
        summary = self.sqlite_manager.get_conversation_summary(patient_id)
        
        if summary.get("status") == "no_history":
            return summary["message"]
        elif summary.get("status") == "error":
            return f"Error retrieving history: {summary.get('error', 'Unknown error')}"
        else:
            last_msg = summary.get("last_message_preview", "")
            return f"Conversation history: {summary['total_messages']} messages, last: {last_msg}"
    
    def add_interaction(self, patient_id, user_query, agent_response, metadata=None):
        """Add a complete user-agent interaction - New enhanced method"""
        return self.sqlite_manager.add_interaction(
            patient_id, user_query, agent_response, 
            query_metadata=metadata, response_metadata=metadata
        )
    
    # Additional methods for enhanced functionality
    def get_patients_with_history(self):
        """Get list of all patients with conversation history"""
        return self.sqlite_manager.get_patients_with_history()
    
    def export_conversation(self, patient_id, format="json"):
        """Export conversation history for a patient"""
        return self.sqlite_manager.export_conversation_history(patient_id, format)
    
    def get_database_info(self):
        """Get database statistics"""
        return self.sqlite_manager.get_database_info()

# Global instance - maintains existing interface
history_manager = HistoryManager()
