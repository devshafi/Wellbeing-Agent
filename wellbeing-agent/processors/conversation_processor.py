import torch
from models.model_manager import model_manager
from utils.history_manager import history_manager

class ConversationProcessor:
    """Handles conversation generation and management"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.history_manager = history_manager
    
    def generate_response(self, patient_id, query):
        """Generate response using conversation model with proper history"""
        try:
            # Get conversation history
            history = self.history_manager.get_conversation_context(patient_id)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a compassionate and professional mental health assistant named Wellbeing Agent. Always introduce yourself as "Wellbeing Agent" when asked about your identity. Provide supportive, empathetic responses to help users with their mental health concerns. Remember the context of previous conversations."""
                },
                {
                    "role": "user",
                    "content": "What is your name?"
                },
                {
                    "role": "assistant", 
                    "content": "My name is Wellbeing Agent."
                },
                {
                    "role": "user",
                    "content": "Hey, who are you?"
                },
                {
                    "role": "assistant",
                    "content": "I am Wellbeing Agent, and I can assist you with understanding your mental health."
                },
                {
                    "role": "user",
                    "content": "Tell me about yourself"
                },
                {
                    "role": "assistant",
                    "content": "I'm Wellbeing Agent, your mental health companion. I'm here to provide support, guidance, and help you navigate your wellness journey."
                }
            ]
            
            # Add conversation history AFTER few-shot examples but BEFORE current query
            messages.extend(history)
            
            # Add current query (ONLY ONCE)
            messages.append({
                "role": "user",
                "content": query  # Clean query without patient ID
            })
            
            tokenizer = self.model_manager.get_tokenizer("conversation")
            model = self.model_manager.get_model("conversation")
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=128,
                    do_sample=True,
                    num_beams=3,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            response = response.replace(tokenizer.eos_token, "").strip()
            
            # Store the conversation in history AFTER successful generation
            self.history_manager.add_to_history(patient_id, "user", query)
            self.history_manager.add_to_history(patient_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"❌ Conversation model error: {e}")
            return f"I'm sorry, I encountered an error while trying to provide support. Please try again."

# Global instance
conversation_processor = ConversationProcessor()
