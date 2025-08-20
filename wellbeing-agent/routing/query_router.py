import torch
import re
from models.model_manager import model_manager

class QueryRouter:
    """Handles query routing using LLM and rule-based fallback"""
    
    def __init__(self):
        self.model_manager = model_manager
    
    def route_query(self, patient_id, query):
        """Main routing function using LLM"""
        print(f"🎯 Routing query using LLM: {query}")
        
        # Use LLM-based routing
        route_decision = self._llm_route_query(patient_id, query)
        
        print(f"🎯 LLM Routing decision: {route_decision}")
        return route_decision
    
    def _llm_route_query(self, patient_id, query):
        """Enhanced LLM-based routing with multi-modal classification"""
        try:
            # Enhanced few-shot examples for routing
            few_shot_prompt = """You are an intelligent routing system for a mental health assistant. You need to classify user queries into these categories:

1. "CONVERSATION" - for greetings, introductions, general chat, emotional support, mental health advice
2. "FUNCTION_CALLING" - for pure data retrieval, health metrics, information lookup only  
3. "HYBRID" - ONLY when user has specific health symptoms AND would benefit from actual data to provide informed help

Examples:

Query: "Hello, how are you?"
Analysis: Simple greeting, no health concerns
Classification: CONVERSATION

Query: "My name is Sarah, nice to meet you"
Analysis: Introduction, general conversation
Classification: CONVERSATION

Query: "I'm feeling really anxious about my job interview tomorrow"
Analysis: General emotional support needed, no specific symptoms requiring data
Classification: CONVERSATION

Query: "How can I manage stress better?"
Analysis: General advice request, no specific health issues
Classification: CONVERSATION

Query: "Show me my exercise data for the past week"
Analysis: Pure data request, no emotional support needed
Classification: FUNCTION_CALLING

Query: "I can't sleep for two days and I'm really worried"
Analysis: Specific sleep problem with duration, needs sleep data for informed help
Classification: HYBRID

Query: "My heart rate feels high today, should I be concerned?"
Analysis: Specific physiological symptom, needs heart rate data for assessment
Classification: HYBRID

Query: "Get my medication history for this month"
Analysis: Pure data request
Classification: FUNCTION_CALLING

Query: "I feel depressed and nothing seems to help"
Analysis: General emotional issue, needs support not specific data
Classification: CONVERSATION

Query: "I've been having trouble sleeping for a week"
Analysis: Specific sleep issue with duration, sleep data would help provide context
Classification: HYBRID

Now analyze and classify this query:

Query: "{query}"
Analysis: [Think about whether this needs data, emotional support, or both]
Classification:"""

            # Format the prompt
            formatted_prompt = few_shot_prompt.format(query=query)
            
            # Create messages for chat template
            messages = [
                {
                    "role": "system",
                    "content": "You are a precise classification system. Respond with only 'CONVERSATION', 'FUNCTION_CALLING', or 'HYBRID' - nothing else."
                },
                {
                    "role": "user", 
                    "content": formatted_prompt
                }
            ]
            
            tokenizer = self.model_manager.get_tokenizer("router")
            model = self.model_manager.get_model("router")
            
            # Apply chat template
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            
            # Tokenize
            inputs = tokenizer(
                prompt, 
                return_tensors="pt", 
                max_length=2048, 
                truncation=True,
                padding=True
            )
            
            # Move to model device
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Generate classification
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=30,  # Slightly more tokens for analysis
                    temperature=0.1,    # Low temperature for consistent classification
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            # Decode response
            input_length = inputs['input_ids'].shape[1]
            response_tokens = outputs[0][input_length:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True).strip().upper()
            
            print(f"🤖 Enhanced LLM Router Response: '{response}'")
            
            # Parse the response
            if "HYBRID" in response:
                return "hybrid"
            elif "FUNCTION_CALLING" in response or "FUNCTION" in response:
                return "function_calling"
            elif "CONVERSATION" in response:
                return "conversation"
            else:
                # Fallback to rule-based if unclear response
                print(f"⚠️ Unclear LLM response: '{response}', falling back to enhanced rule-based routing")
                return self._enhanced_rule_based_routing(query)
                
        except Exception as e:
            print(f"❌ LLM routing failed: {e}")
            print("🔄 Falling back to enhanced rule-based routing")
            return self._enhanced_rule_based_routing(query)
    
    def _enhanced_rule_based_routing(self, query):
        """Enhanced fallback rule-based routing with hybrid detection"""
        
        function_keywords = [
            "get", "retrieve", "fetch", "show", "display", "find", "search",
            "data", "information", "history", "records", "chart", "report",
            "exercise", "workout", "steps", "sleep", "heart rate", "medication",
            "show me my", "get my", "find my", "what is my"
        ]
        
        # Greeting patterns - always conversation
        greeting_patterns = [
            r"^hello|^hi |^hey|^good morning|^good afternoon|^good evening",
            r"how are you|nice to meet|my name is|i'm |i am ",
            r"^greetings|^salutations|what's up|how's it going"
        ]
        
        conversation_keywords = [
            "feel", "feeling", "anxious", "stressed", "sad", "depressed",
            "help", "support", "advice", "talk", "discuss", "cope",
            "i am", "i'm", "i feel", "i'm feeling", "help me", "worried", "concern"
        ]
        
        # Keywords that suggest hybrid approach needed
        hybrid_patterns = [
            # Health issues that benefit from data context
            r"can't sleep|insomnia|sleep problem|sleeping badly",
            r"heart rate.*high|heart.*racing|palpitations",
            r"mood swings|mood changes|feeling different",
            r"energy.*low|tired all the time|exhausted",
            r"exercise.*not working|workout.*not helping",
            r"medication.*not working|pills.*not helping",
            # Temporal patterns suggesting data analysis needed
            r"for \d+ days?|for \d+ weeks?|lately|recently|past few",
            r"since.*ago|been having.*for",
        ]
        
        query_lower = query.lower()
        
        # Check for greetings first - always route to conversation
        greeting_score = sum(1 for pattern in greeting_patterns 
                            if re.search(pattern, query_lower))
        
        if greeting_score > 0:
            print(f"🎯 Greeting detected, routing to conversation")
            return "conversation"
        
        # Check for hybrid patterns
        hybrid_score = sum(1 for pattern in hybrid_patterns 
                          if re.search(pattern, query_lower))
        
        function_score = sum(1 for keyword in function_keywords 
                            if keyword in query_lower)
        
        conversation_score = sum(1 for keyword in conversation_keywords 
                               if keyword in query_lower)
        
        print(f"🎯 Enhanced routing scores - Hybrid: {hybrid_score}, Function: {function_score}, Conversation: {conversation_score}")
        
        # Decision logic
        if hybrid_score > 0 and conversation_score > 0:
            return "hybrid"
        elif function_score > conversation_score and function_score > 0:
            return "function_calling"
        else:
            return "conversation"

# Global instance
query_router = QueryRouter()
