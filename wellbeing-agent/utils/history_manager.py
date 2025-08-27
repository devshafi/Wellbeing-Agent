class HistoryManager:
    """Manages conversation history for patients"""
    
    def __init__(self):
        self.conversation_history = {}  # Store per patient: {patient_id: [messages]}
    
    def add_to_history(self, patient_id, role, content):
        """Add message to conversation history"""
        if patient_id not in self.conversation_history:
            self.conversation_history[patient_id] = []
        
        self.conversation_history[patient_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 10 exchanges (20 messages) to avoid context overflow
        if len(self.conversation_history[patient_id]) > 40:
            self.conversation_history[patient_id] = self.conversation_history[patient_id][-40:] 
    
    def get_conversation_context(self, patient_id, max_history=20):
        """Get recent conversation history for context"""
        if patient_id not in self.conversation_history:
            return []
        
        # Return last N messages (max_history)
        return self.conversation_history[patient_id][-max_history:]
    
    def clear_conversation_history(self, patient_id):
        """Clear conversation history for a specific patient"""
        if patient_id in self.conversation_history:
            del self.conversation_history[patient_id]
            print(f"🗑️ Cleared conversation history for patient {patient_id}")
    
    def get_conversation_summary(self, patient_id):
        """Get a summary of conversation history"""
        if patient_id not in self.conversation_history:
            return "No conversation history found."
        
        history = self.conversation_history[patient_id]
        return f"Conversation history: {len(history)} messages, last message: {history[-1]['content'][:50]}..." if history else "No messages"

# Global instance
history_manager = HistoryManager()
