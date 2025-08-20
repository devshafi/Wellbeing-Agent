from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from function_registry import function_registry
from typing import Dict, Any
import torch
import json
import re

class MultiModelManager:
    _instance = None
    _conversation_model = None
    _function_calling_model = None
    _router_model = None
    _tokenizers = {}
    _loaded_models = set()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultiModelManager, cls).__new__(cls)
        return cls._instance
    
    def load_conversation_model(self, model_path):
        """Load the conversation model"""
        if "conversation" in self._loaded_models:
            print("Conversation model already loaded!")
            return
        
        print("🔄 Loading conversation model...")
        try:
            config = PeftConfig.from_pretrained(model_path)
            print(f"Base model: {config.base_model_name_or_path}")
            
            self._conversation_model = AutoModelForCausalLM.from_pretrained(
                config.base_model_name_or_path,
                device_map={"": 0},
                torch_dtype=torch.bfloat16
            )
            
            self._tokenizers["conversation"] = AutoTokenizer.from_pretrained(model_path)
            print(f"Conversation tokenizer vocab size: {len(self._tokenizers['conversation'])}")
            
            self._conversation_model.resize_token_embeddings(len(self._tokenizers["conversation"]))
            self._conversation_model = PeftModel.from_pretrained(self._conversation_model, model_path)
            self._conversation_model.to(torch.bfloat16)
            self._conversation_model.eval()
            self._loaded_models.add("conversation")
            print("✅ Conversation model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load conversation model: {e}")
            raise e
    
    def load_function_calling_model(self, model_path):
        """Load the function calling model"""
        if "function_calling" in self._loaded_models:
            print("Function calling model already loaded!")
            return
        
        print("🔄 Loading function calling model...")
        try:
            config = PeftConfig.from_pretrained(model_path)
            print(f"Base model: {config.base_model_name_or_path}")
            
            # Use different GPU if available, otherwise same GPU
            device_map = {"": 1} if torch.cuda.device_count() > 1 else {"": 0}
            
            self._function_calling_model = AutoModelForCausalLM.from_pretrained(
                config.base_model_name_or_path,
                device_map=device_map,
                torch_dtype=torch.bfloat16
            )
            
            self._tokenizers["function_calling"] = AutoTokenizer.from_pretrained(model_path)
            print(f"Function calling tokenizer vocab size: {len(self._tokenizers['function_calling'])}")
            
            self._function_calling_model.resize_token_embeddings(len(self._tokenizers["function_calling"]))
            self._function_calling_model = PeftModel.from_pretrained(self._function_calling_model, model_path)
            self._function_calling_model.to(torch.bfloat16)
            self._function_calling_model.eval()
            self._loaded_models.add("function_calling")
            print("✅ Function calling model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to load function calling model: {e}")
            raise e
    
    def load_router_model(self, model_name="meta-llama/Llama-3.2-3B-Instruct"):
        """Load Llama 3.2 3B as router model"""
        if "router" in self._loaded_models:
            print("Router model already loaded!")
            return
        
        print("🔄 Loading Llama 3.2 3B router model...")
        try:
            # Use CPU or different GPU for router to save memory
            device_map = "cpu" if torch.cuda.device_count() <= 2 else {"": 2}
            
            self._router_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=device_map,
                torch_dtype=torch.bfloat16 if device_map != "cpu" else torch.float32
            )
            
            self._tokenizers["router"] = AutoTokenizer.from_pretrained(model_name)
            if self._tokenizers["router"].pad_token is None:
                self._tokenizers["router"].pad_token = self._tokenizers["router"].eos_token
            
            self._router_model.eval()
            self._loaded_models.add("router")
            print("✅ Llama 3.2 3B router model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Router model failed to load: {e}")
            print("Falling back to rule-based routing")
            raise e

class AgenticSystem:
    def __init__(self):
        self.model_manager = MultiModelManager()
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
        if len(self.conversation_history[patient_id]) > 20:
            self.conversation_history[patient_id] = self.conversation_history[patient_id][-20:] 
    
    def get_conversation_context(self, patient_id, max_history=6):
        """Get recent conversation history for context"""
        if patient_id not in self.conversation_history:
            return []
        
        # Return last N messages (max_history)
        return self.conversation_history[patient_id][-max_history:]
        
    def setup_models(self):
        """Initialize all models with your specific paths"""
        
        conversation_model_path = "/home/jovyan/Works/MSc_Thesis/mh_conversation/finetuned_model/llama3.2_3b_mh_conversation_v7"
        function_calling_model_path = "/home/jovyan/Works/MSc_Thesis/mh_function_calling/model_training/finetuned_models/llama3.2_3b_mh_function_calling_v6"
        
        print("🚀 Initializing Agentic Mental Health System...")
        
        try:
            # Load conversation model
            self.model_manager.load_conversation_model(conversation_model_path)
            
            # Load function calling model
            self.model_manager.load_function_calling_model(function_calling_model_path)
            
            # Load Llama 3.2 3B router
            self.model_manager.load_router_model()
            
            print("🎉 All models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Failed to setup models: {e}")
            raise e
    
    def llm_route_query(self, patient_id, query):
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
            
            tokenizer = self.model_manager._tokenizers["router"]
            model = self.model_manager._router_model
            
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
                return self.enhanced_rule_based_routing(query)
                
        except Exception as e:
            print(f"❌ LLM routing failed: {e}")
            print("🔄 Falling back to enhanced rule-based routing")
            return self.enhanced_rule_based_routing(query)
    
    def fallback_rule_based_routing(self, query):
        """Fallback rule-based routing when LLM fails"""
        function_keywords = [
            "get", "retrieve", "fetch", "show", "display", "find", "search",
            "data", "information", "history", "records", "chart", "report",
            "exercise", "workout", "steps", "sleep", "heart rate", "medication",
            "show me my", "get my", "find my", "what is my"
        ]
        
        conversation_keywords = [
            "feel", "feeling", "anxious", "stressed", "sad", "depressed",
            "help", "support", "advice", "talk", "discuss", "cope",
            "i am", "i'm", "i feel", "i'm feeling", "help me"
        ]
        
        query_lower = query.lower()
        
        function_score = sum(1 for keyword in function_keywords if keyword in query_lower)
        conversation_score = sum(1 for keyword in conversation_keywords if keyword in query_lower)
        
        print(f"🎯 Fallback routing scores - Function: {function_score}, Conversation: {conversation_score}")
        
        if function_score > conversation_score and function_score > 0:
            return "function_calling"
        else:
            return "conversation"
    
    def enhanced_rule_based_routing(self, query):
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
    
    def route_query(self, patient_id, query):
        """Main routing function using LLM"""
        print(f"🎯 Routing query using LLM: {query}")
        
        # Use LLM-based routing
        route_decision = self.llm_route_query(patient_id, query)
        
        print(f"🎯 LLM Routing decision: {route_decision}")
        return route_decision
    
    def analyze_query_requirements(self, query):
        """Analyze query to determine what data might be needed for hybrid responses"""
        
        data_mapping = {
            'sleep': {
                'triggers': ['sleep', 'insomnia', 'tired', 'rest', 'night', 'bed', 'wake', 'exhausted'],
                'function': 'get_sleep_data',
                'days': 7
            },
            'heart_rate': {
                'triggers': ['heart', 'pulse', 'racing', 'palpitations', 'chest'],
                'function': 'get_heart_rate_data', 
                'days': 3
            },
            'mood': {
                'triggers': ['mood', 'feeling', 'emotional', 'sad', 'happy', 'depressed', 'anxious'],
                'function': 'get_mood_data',
                'days': 14
            },
            'exercise': {
                'triggers': ['exercise', 'workout', 'activity', 'fitness', 'gym', 'run'],
                'function': 'get_exercise_data',
                'days': 7
            },
            'medication': {
                'triggers': ['medication', 'pills', 'medicine', 'drugs', 'prescription'],
                'function': 'get_medication_data',
                'days': 30
            },
            'steps': {
                'triggers': ['steps', 'walking', 'activity', 'movement'],
                'function': 'get_steps_data',
                'days': 7
            }
        }
        
        query_lower = query.lower()
        detected_needs = []
        
        # Extract time periods from query
        time_matches = re.findall(r'(\d+)\s+(day|week|month)s?', query_lower)
        default_days = 7
        
        if time_matches:
            number, period = time_matches[0]
            if period == 'day':
                default_days = int(number)
            elif period == 'week':
                default_days = int(number) * 7
            elif period == 'month':
                default_days = int(number) * 30
        
        # Check what data types are mentioned
        for data_type, config in data_mapping.items():
            if any(trigger in query_lower for trigger in config['triggers']):
                detected_needs.append({
                    'type': data_type,
                    'function': config['function'],
                    'days': min(default_days, config['days'])  # Don't exceed typical ranges
                })
        
        print(f"🔍 Detected data needs: {detected_needs}")
        
        return {
            'data_needs': detected_needs,
            'query_period': default_days
        }
    
    def process_hybrid_query(self, patient_id, query):
        """Process hybrid queries that need both data and conversation"""
        print(f"🎭 Processing HYBRID query: {query}")
        
        # Step 1: Analyze what data we need
        requirements = self.analyze_query_requirements(query)
        
        # Step 2: Collect relevant data
        collected_data = {}
        for need in requirements['data_needs']:
            try:
                print(f"📊 Fetching {need['type']} data...")
                
                # Execute the function to get data
                result = function_registry.execute_function(
                    need['function'], 
                    {
                        "patient_id": patient_id,
                        "num_days": need['days']
                    }
                )
                
                if result["success"]:
                    collected_data[need['type']] = result
                    print(f"✅ Successfully retrieved {need['type']} data")
                else:
                    print(f"❌ Failed to retrieve {need['type']} data: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Error retrieving {need['type']} data: {e}")
        
        # Step 3: Generate data-informed conversation response
        if collected_data:
            response = self.generate_data_informed_response(patient_id, query, collected_data)
        else:
            # Fallback to regular conversation if no data could be retrieved
            response = self.generate_conversation_response(patient_id, query)
        
        # Step 4: Add data summaries as appendix
        if collected_data:
            response += "\n\n" + "="*50 + "\n**📊 Raw Data Used:**\n"
            for data_type, result in collected_data.items():
                response += f"\n**{data_type.upper()}:**\n{json.dumps(result['data'], indent=2)}\n"
        
        return response
    
    def generate_data_informed_response(self, patient_id, query, collected_data):
        """Generate conversation response informed by collected health data"""
        try:
            # Get conversation history
            history = self.get_conversation_context(patient_id)
            
            # Create data context summary
            data_context = self.create_hybrid_data_context(collected_data)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are Wellbeing Agent, a compassionate mental health assistant. You MUST analyze the provided health data and give personalized responses based on the actual data patterns.

CRITICAL: You have been provided with real user data. You must reference specific data points and patterns from this data in your response.

Raw health data context:
{data_context}

MANDATORY RESPONSE STRUCTURE:
1. First, analyze the data patterns (mention specific values, dates, trends)
2. Then provide empathetic support addressing their specific situation
3. Give personalized recommendations based on their data patterns
4. Be specific about what you observe in their data

Example of good data analysis:
"Looking at your sleep data, I can see quite a bit of variation - you had 7.7 hours on August 14th with excellent quality, but then it dropped to 4.4 hours on August 17th. I notice your sleep hours have been inconsistent, ranging from 4.4 to 8.5 hours, and despite getting good hours recently (8.0 and 8.5), the quality has been poor to fair..."

You MUST reference actual data points and patterns. Do not give generic advice."""
                },
                {
                    "role": "user",
                    "content": "I'm having trouble sleeping. Can you help me understand what's going on?"
                },
                {
                    "role": "assistant",
                    "content": "I can see from your sleep data that you've been experiencing significant inconsistency in your sleep patterns. Looking at the past week, your sleep hours have varied dramatically - from just 4.4 hours on one night to 8.5 hours on another. What's particularly concerning is that even when you're getting adequate hours (like the 8.0 and 8.5 hours recently), the quality is still rating as poor to fair. This suggests the issue might not just be about duration but about sleep quality. The variation in your pattern - going from 4.4 hours to 8.0 hours - indicates your sleep schedule might be quite irregular, which can disrupt your natural circadian rhythm."
                },
            ]
            
            # Add conversation history
            messages.extend(history)
            
            # Add current query
            messages.append({
                "role": "user",
                "content": query
            })
            
            tokenizer = self.model_manager._tokenizers["conversation"]
            model = self.model_manager._conversation_model
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=450,  # Longer for detailed data analysis
                    do_sample=True,
                    temperature=0.8,     # Higher temperature for more detailed analysis
                    top_p=0.95,         # Higher top_p for richer responses
                    repetition_penalty=1.15,  # Higher penalty to avoid generic responses
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            response = response.replace(tokenizer.eos_token, "").strip()
            
            # Store in history
            self.add_to_history(patient_id, "user", query)
            self.add_to_history(patient_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"❌ Data-informed response error: {e}")
            return f"I understand your concern. Let me help you work through this, though I'm having some technical difficulties accessing your data right now."
    
    def create_hybrid_data_context(self, collected_data):
        """Create raw data context from collected data for the conversation model"""
        context_parts = []
        
        for data_type, result in collected_data.items():
            if not result.get("success"):
                continue
                
            # Pass the raw data directly to the model
            data = result["data"]
            context_parts.append(f"{data_type.upper()}_DATA: {json.dumps(data)}")
        
        return "\n".join(context_parts) if context_parts else "No recent data available"
   
    def extract_and_execute_function(self, response: str) -> tuple:
    
        """Extract function calls from response and execute them with flexible pattern matching"""
        try:
            print("🔍 Looking for function calls in response...")
            
            # Method 1: Look for properly tagged function calls
            function_pattern = r'<function>(.*?)</function>'
            function_match = re.search(function_pattern, response, re.DOTALL)
            
            function_call_str = None
            
            if function_match:
                print("✅ Found properly tagged function call")
                function_call_str = function_match.group(1).strip()
            else:
                print("⚠️ No proper function tags found, trying flexible detection...")
                
                # Method 2: Look for JSON-like structure with "name" and "parameters"
                # This pattern looks for the structure even without proper tags
                flexible_patterns = [
                    # Pattern 1: JSON with name and parameters
                    r'"name"\s*:\s*"([^"]+)"[^}]*?"parameters"\s*:\s*\{([^}]+)\}',
                    # Pattern 2: More flexible JSON structure
                    r'\{\s*"name"\s*:\s*"([^"]+)"[^}]*?"parameters"\s*:\s*\{([^}]*?)\}\s*\}',
                    # Pattern 3: Detect any JSON-like structure with name field
                    r'\{\s*"name"\s*:\s*"([^"]+)".*?\}',
                ]
                
                for i, pattern in enumerate(flexible_patterns):
                    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                    if match:
                        print(f"✅ Found function call using pattern {i+1}")
                        
                        if len(match.groups()) >= 2:
                            # Extract name and parameters
                            function_name = match.group(1)
                            parameters_str = match.group(2)
                            
                            # Try to reconstruct valid JSON
                            try:
                                # Clean up parameters string
                                parameters_str = parameters_str.strip()
                                if not parameters_str.startswith('{'):
                                    parameters_str = '{' + parameters_str + '}'
                                
                                parameters = json.loads(parameters_str)
                                
                                function_call_str = json.dumps({
                                    "name": function_name,
                                    "parameters": parameters
                                })
                                print(f"🔧 Reconstructed function call: {function_call_str}")
                                break
                                
                            except json.JSONDecodeError:
                                # Try with simpler parameter extraction
                                print(f"⚠️ Failed to parse parameters, trying simpler extraction...")
                                continue
                        else:
                            # Just function name found
                            function_name = match.group(1)
                            function_call_str = json.dumps({
                                "name": function_name,
                                "parameters": {}
                            })
                            break
                
                # Method 3: Last resort - look for specific function names in text
                if not function_call_str:
                    print("🔍 Trying function name detection...")
                    known_functions = [
                        "get_exercise_data", "get_sleep_data", "get_heart_rate_data",
                        "get_medication_data", "get_mood_data", "get_weight_data",
                        "get_steps_data", "get_health_summary"
                    ]
                    
                    for func_name in known_functions:
                        if func_name in response.lower().replace('_', ' ') or func_name in response:
                            print(f"🎯 Detected function by name: {func_name}")
                            
                            # Try to extract patient_id and num_days from context
                            patient_id_match = re.search(r'"patient_id"\s*:\s*"([^"]+)"', response)
                            num_days_match = re.search(r'"num_days"\s*:\s*(\d+)', response)
                            
                            parameters = {}
                            if patient_id_match:
                                parameters["patient_id"] = patient_id_match.group(1)
                            if num_days_match:
                                parameters["num_days"] = int(num_days_match.group(1))
                            
                            # Default parameters if not found
                            if "patient_id" not in parameters:
                                parameters["patient_id"] = "UID_123"  # Default
                            if "num_days" not in parameters and func_name != "get_health_summary":
                                parameters["num_days"] = 7  # Default
                            
                            function_call_str = json.dumps({
                                "name": func_name,
                                "parameters": parameters
                            })
                            break
            
            if not function_call_str:
                print("❌ No function calls detected")
                return response, None
            
            try:
                # Parse the JSON function call
                function_call = json.loads(function_call_str)
                function_name = function_call.get("name")
                parameters = function_call.get("parameters", {})
                
                print(f"🔧 Executing function: {function_name} with params: {parameters}")
                
                # Execute the function
                result = function_registry.execute_function(function_name, parameters)
                
                if result["success"]:
                    # Format the result nicely
                    formatted_result = self.format_function_result(result)
                    
                    # Replace the function call in the response with the actual result
                    if function_match:
                        # Replace tagged function call
                        enhanced_response = re.sub(
                            function_pattern, 
                            formatted_result, 
                            response, 
                            flags=re.DOTALL
                        )
                    else:
                        # Append result to response since no clear tags to replace
                        enhanced_response = response + "\n\n" + formatted_result
                    
                    return enhanced_response, result
                else:
                    error_message = f"❌ **Function Error**: {result.get('error', 'Unknown error')}"
                    
                    if function_match:
                        enhanced_response = re.sub(
                            function_pattern, 
                            error_message, 
                            response, 
                            flags=re.DOTALL
                        )
                    else:
                        enhanced_response = response + "\n\n" + error_message
                        
                    return enhanced_response, result
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                error_message = f"❌ **JSON Parse Error**: Invalid function call format: {function_call_str}"
                return response + "\n\n" + error_message, None
                
        except Exception as e:
            print(f"❌ Function extraction error: {e}")
            return response, None
   
    def format_function_result(self, result: Dict) -> str:
        """Format function execution result for display"""
        if not result.get("success"):
            return f"❌ **Error**: {result.get('error', 'Unknown error')}"
        
        function_name = result["function"]
        data = result["data"]
        
        # Format based on function type
        if function_name == "get_sleep_data":
            return self.format_sleep_data(data)
        elif function_name == "get_heart_rate_data":
            return self.format_heart_rate_data(data)
        else:
            # Generic formatting
            return f"**📊 {function_name} Results:**\n```json\n{json.dumps(data, indent=2)}\n```"
    
    # Add this method to the AgenticSystem class

    def generate_orchestrator_response(self, patient_id, original_query, function_result):
        """Generate natural language response based on function execution results using conversation model"""
        try:
            if not function_result or not function_result.get("success"):
                return "I apologize, but I wasn't able to retrieve the requested information at this time."
            
            function_name = function_result["function"]
            data = function_result["data"]
            
            # Create a structured summary of the data for the orchestrator
            data_summary = self.create_data_summary(function_name, data)
            
            # Craft a prompt for the conversation model to generate a natural response
            messages = [
                {
                    "role": "system",
                    "content": """You are a compassionate mental health assistant. A user has requested health data, and the system has retrieved it successfully. Your job is to:

    1. Provide a warm, conversational response about their data
    2. Highlight key insights and trends
    3. Offer relevant health advice or encouragement
    4. Keep the response concise but informative (2-3 paragraphs max)
    5. Use a supportive, professional tone

    Do not repeat raw data - instead, interpret and contextualize it for the user."""
                },
                {
                    "role": "user",
                    "content": f"""Patient asked: "{original_query}"

    Retrieved data summary:
    {data_summary}

    Please provide a natural, conversational response interpreting this data for the patient."""
                }
            ]
            
            tokenizer = self.model_manager._tokenizers["conversation"]
            model = self.model_manager._conversation_model
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=400,  # Slightly longer for data interpretation
                    do_sample=True,
                    # temperature=0.7,
                    # top_p=0.9,
                    # repetition_penalty=1.00,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            orchestrator_response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            orchestrator_response = orchestrator_response.replace(tokenizer.eos_token, "").strip()
            
            return orchestrator_response
            
        except Exception as e:
            print(f"❌ Orchestrator response error: {e}")
            return "I've retrieved your data successfully, but I'm having trouble interpreting it right now. Please refer to the detailed information above."

    def create_data_summary(self, function_name, data):
        """Create a structured summary of the data for the orchestrator"""
        
        if function_name == "get_sleep_data":
            avg_sleep = data.get('average_sleep_hours', 0)
            total_records = len(data.get('sleep_records', []))
            recent_quality = [record.get('quality', 'Unknown') for record in data.get('sleep_records', [])[-3:]]
            
            return f"""Sleep Data Analysis:
    - Average sleep duration: {avg_sleep} hours per night
    - Total sleep records: {total_records} days
    - Recent sleep quality: {', '.join(recent_quality)}
    - Sleep pattern trend: {'Consistent' if 7 <= avg_sleep <= 9 else 'Needs attention' if avg_sleep < 7 else 'Excessive'}"""

        elif function_name == "get_heart_rate_data":
            avg_resting = data.get('average_resting_hr', 0)
            total_records = len(data.get('heart_rate_records', []))
            recent_hr = [record.get('resting_hr', 0) for record in data.get('heart_rate_records', [])[-3:]]
            
            return f"""Heart Rate Data Analysis:
    - Average resting heart rate: {avg_resting} bpm
    - Total measurement days: {total_records}
    - Recent resting HR: {', '.join(map(str, recent_hr))} bpm
    - HR status: {'Normal range' if 60 <= avg_resting <= 100 else 'Outside normal range - consider consultation'}"""
        else:
            # Generic summary for unknown function types
            return f"""Data retrieved from {function_name}:
    {json.dumps(data, indent=2)[:500]}..."""

    # Update the generate_function_response method
    def generate_function_response(self, patient_id, query):
        """Generate response using function calling model and orchestrator"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful mental health assistant. When users ask for health data, use the available functions to retrieve the information. Think through your response before choosing a function. Use <think>your reasoning</think> tags to show your thought process, then use <function>json</function> tags to call the appropriate function."""
                },
                {
                    "role": "user",
                    "content": f"Patient ID: {patient_id}\nQuery: {query}"
                }
            ]
            
            tokenizer = self.model_manager._tokenizers["function_calling"]
            model = self.model_manager._function_calling_model
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=0.1,
                    top_p=0.95,
                    repetition_penalty=1.0,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            response = response.replace(tokenizer.eos_token, "").strip()
            
            # Extract and execute any function calls
            enhanced_response, function_result = self.extract_and_execute_function(response)
            
            # If function was executed successfully, generate orchestrator response
            if function_result and function_result.get("success"):
                print("🎭 Generating orchestrator response...")
                orchestrator_response = self.generate_orchestrator_response(patient_id, query, function_result)
                
                # Combine thinking process, function execution, and orchestrator response
                final_response = ""
                
                # Extract thinking process if available
                think_pattern = r'<think>(.*?)</think>'
                think_match = re.search(think_pattern, response, re.DOTALL)
                if think_match:
                    thinking = think_match.group(1).strip()
                    final_response += f"**🤔 Analysis:** {thinking}\n\n"
                
                # Add the orchestrator's natural language response
                final_response += f"**📊 Your Health Data Insights:**\n{orchestrator_response}\n\n"
                
                # Add detailed data as expandable section
                formatted_data = self.format_function_result(function_result)
                final_response += f"**📋 Detailed Information:**\n{formatted_data}"
                
                return final_response
            else:
                # Return the enhanced response as before if no function result
                return enhanced_response
            
        except Exception as e:
            print(f"❌ Function calling model error: {e}")
            return f"I'm sorry, I encountered an error while trying to retrieve the information: {str(e)}"
    
    def format_sleep_data(self, data: Dict) -> str:
        """Format sleep data for display"""
        output = f"**😴 Sleep Data ({data['period']})**\n\n"
        output += f"📈 **Summary:**\n"
        output += f"• Average Sleep: {data['average_sleep_hours']} hours/night\n\n"
        
        if data['sleep_records']:
            output += "📅 **Recent Sleep:**\n"
            for record in data['sleep_records'][-5:]:  # Show last 5
                output += f"• {record['date']}: {record['duration_hours']}h ({record['quality']})\n"
        
        return output
    
    def format_heart_rate_data(self, data: Dict) -> str:
        """Format heart rate data for display"""
        output = f"**❤️ Heart Rate Data ({data['period']})**\n\n"
        output += f"📈 **Summary:**\n"
        output += f"• Average Resting HR: {data['average_resting_hr']} bpm\n\n"
        
        if data['heart_rate_records']:
            output += "📅 **Recent Measurements:**\n"
            for record in data['heart_rate_records'][-5:]:
                output += f"• {record['date']}: Resting {record['resting_hr']} bpm, Max {record['max_hr']} bpm\n"
        
        return output   
   
 
    
    def generate_conversation_response(self, patient_id, query):
        """Generate response using conversation model with proper history"""
        try:
            # Get conversation history
            history = self.get_conversation_context(patient_id)
            
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
            
            tokenizer = self.model_manager._tokenizers["conversation"]
            model = self.model_manager._conversation_model
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=256,
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
            self.add_to_history(patient_id, "user", query)
            self.add_to_history(patient_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"❌ Conversation model error: {e}")
            return f"I'm sorry, I encountered an error while trying to provide support. Please try again."
    
    def process_query(self, patient_id, query):
        """Enhanced processing pipeline with hybrid support"""
        print(f"🤖 Processing query for patient {patient_id}")
        print(f"📝 Query: {query}")
        
        # Step 1: Route the query using enhanced LLM router
        route_decision = self.route_query(patient_id, query)
        print(f"🎯 Final routing decision: {route_decision}")
        
        # Step 2: Generate response based on route
        if route_decision == "hybrid":
            print("🎭 Using HYBRID approach (data + conversation)")
            response = self.process_hybrid_query(patient_id, query)
            
            # Add to history
            self.add_to_history(patient_id, "user", query)
            summary = f"Provided data-informed support for: {query[:50]}..."
            self.add_to_history(patient_id, "assistant", summary)
            
        elif route_decision == "function_calling":
            print("🔧 Using FUNCTION CALLING approach")
            response = self.generate_function_response(patient_id, query)
            
            # Add to history
            self.add_to_history(patient_id, "user", query)
            summary = f"Retrieved data for: {query[:50]}..."
            self.add_to_history(patient_id, "assistant", summary)
            
        else:  # conversation
            print("💬 Using CONVERSATION approach")
            response = self.generate_conversation_response(patient_id, query)
            # History is handled inside generate_conversation_response
        
        # Step 3: Return structured result
        return {
            "route": route_decision,
            "response": response,
            "patient_id": patient_id,
            "query": query
        }

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
agentic_system = AgenticSystem()