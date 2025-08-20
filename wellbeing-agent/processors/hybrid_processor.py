import torch
import json
import re
from models.model_manager import model_manager
from utils.history_manager import history_manager
from function_registry import function_registry

class HybridProcessor:
    """Handles hybrid queries that need both data and conversation"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.history_manager = history_manager
    
    def process_query(self, patient_id, query):
        """Process hybrid queries that need both data and conversation"""
        print(f"🎭 Processing HYBRID query: {query}")
        
        # Step 1: Use function calling model to determine what data we need
        function_calls = self._get_function_calls_from_model(patient_id, query)
        
        # Step 2: Execute the function calls to collect relevant data
        collected_data = {}
        executed_functions = set()  # Track executed functions to avoid duplicates
        
        if function_calls:
            for func_call in function_calls:
                try:
                    function_name = func_call.get("name")
                    parameters = func_call.get("parameters", {})
                    
                    # Skip if we already executed this function
                    func_signature = f"{function_name}_{json.dumps(parameters, sort_keys=True)}"
                    if func_signature in executed_functions:
                        print(f"⚠️ Skipping duplicate function call: {function_name}")
                        continue
                        
                    # Ensure patient_id is included
                    if "patient_id" not in parameters:
                        parameters["patient_id"] = patient_id
                    
                    print(f"📊 Executing function: {function_name} with params: {parameters}")
                    
                    result = function_registry.execute_function(function_name, parameters)
                    executed_functions.add(func_signature)
                    
                    if result["success"]:
                        data_type = function_name.replace("get_", "").replace("_data", "")
                        collected_data[data_type] = result
                        print(f"✅ Successfully retrieved {data_type} data")
                    else:
                        print(f"❌ Failed to retrieve data from {function_name}: {result.get('error')}")
                        
                except Exception as e:
                    print(f"❌ Error executing function call {func_call}: {e}")
        
        # Step 3: Generate data-informed conversation response
        if collected_data:
            response = self._generate_data_informed_response(patient_id, query, collected_data)
        else:
            # Fallback to regular conversation if no data could be retrieved
            from processors.conversation_processor import conversation_processor
            response = conversation_processor.generate_response(patient_id, query)
        
        # Step 4: Add data summaries as appendix
        if collected_data:
            response += "\n\n" + "="*50 + "\n**📊 Raw Data Used:**\n"
            for data_type, result in collected_data.items():
                response += f"\n**{data_type.upper()}:**\n{json.dumps(result['data'], indent=2)}\n"
        
        return response
    
    def _get_function_calls_from_model(self, patient_id, query):
        """Use function calling model to determine what data we need"""
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
            
            tokenizer = self.model_manager.get_tokenizer("function_calling")
            model = self.model_manager.get_model("function_calling")
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
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
            
            print(f"🔧 Function calling model response: {response}")
            
            # Extract function calls using the same logic as function_calling_processor
            return self._extract_function_calls(response)
            
        except Exception as e:
            print(f"❌ Error getting function calls from model: {e}")
            return []
    
    def _extract_function_calls(self, response):
        """Extract function calls from model response"""
        function_calls = []
        
        try:
            # Method 1: Look for properly tagged function calls
            function_pattern = r'<function>(.*?)</function>'
            function_matches = re.findall(function_pattern, response, re.DOTALL)
            
            for match in function_matches:
                try:
                    function_call = json.loads(match.strip())
                    function_calls.append(function_call)
                    print(f"✅ Extracted function call: {function_call}")
                except json.JSONDecodeError:
                    continue
            
            # Method 2: Flexible JSON detection if no proper tags
            if not function_calls:
                print("🔍 Trying flexible function detection...")
                flexible_patterns = [
                    r'"name"\s*:\s*"([^"]+)"[^}]*?"parameters"\s*:\s*\{([^}]+)\}',
                    r'\{\s*"name"\s*:\s*"([^"]+)"[^}]*?"parameters"\s*:\s*\{([^}]*?)\}\s*\}',
                ]
                
                found_functions = set()  # Track found functions to avoid duplicates
                
                for pattern in flexible_patterns:
                    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                    for match in matches:
                        try:
                            function_name = match[0]
                            
                            # Skip if we already found this function
                            if function_name in found_functions:
                                continue
                                
                            parameters_str = match[1]
                            
                            if not parameters_str.startswith('{'):
                                parameters_str = '{' + parameters_str + '}'
                            
                            parameters = json.loads(parameters_str)
                            
                            function_calls.append({
                                "name": function_name,
                                "parameters": parameters
                            })
                            found_functions.add(function_name)
                            print(f"✅ Extracted function call: {function_name}")
                        except (json.JSONDecodeError, IndexError):
                            continue
                            
            # Method 3: Last resort - look for known function names
            if not function_calls:
                print("🔍 Trying function name detection...")
                known_functions = [
                    "get_sleep_data", "get_heart_rate_data", "get_mood_data",
                    "get_exercise_data", "get_medication_data", "get_steps_data",
                    "get_weight_data", "get_health_summary"
                ]
                
                for func_name in known_functions:
                    if func_name in response.lower().replace('_', ' ') or func_name in response:
                        print(f"🎯 Detected function by name: {func_name}")
                        
                        # Default parameters
                        parameters = {"num_days": 7}
                        if func_name == "get_health_summary":
                            parameters = {}
                        
                        function_calls.append({
                            "name": func_name,
                            "parameters": parameters
                        })
                        break  # Only add one function in this fallback
            
            # Final deduplication step
            unique_calls = []
            seen_functions = set()
            
            for call in function_calls:
                func_name = call.get("name")
                if func_name not in seen_functions:
                    unique_calls.append(call)
                    seen_functions.add(func_name)
            
            print(f"📋 Final extracted function calls: {unique_calls}")
            return unique_calls
            
        except Exception as e:
            print(f"❌ Function call extraction error: {e}")
            return []

    def _generate_data_informed_response(self, patient_id, query, collected_data):
        """Generate conversation response informed by collected health data"""
        try:
            # Get conversation history
            history = self.history_manager.get_conversation_context(patient_id)
            
            # Create data context summary
            data_context = self._create_data_context(collected_data)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a mental health assistant who analyzes actual health data. When provided with user data, you must reference specific dates, values, and patterns from that data in your response. Do not give generic advice - analyze the actual data provided and give personalized insights."""
                },
                {
                    "role": "user", 
                    "content": """I've been having trouble sleeping lately.

My recent health data shows:
=== SLEEP DATA ===
Recent sleep records:
• 2025-08-15: 4.2 hours, Poor quality
• 2025-08-16: 4.8 hours, Poor quality
• 2025-08-17: 7.1 hours, Fair quality

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
                },
                {
                    "role": "assistant",
                    "content": """Looking at your sleep data from August 15-17, I can see a clear pattern that explains your troubles. You had significantly insufficient sleep on August 15th and 16th with only 4.2 and 4.8 hours respectively, both rated as poor quality. While you managed to get closer to adequate sleep on August 17th with 7.1 hours, the quality was still only fair.

This pattern shows you're experiencing both sleep duration issues and sleep quality problems. The consecutive nights of under 5 hours sleep would definitely leave you feeling sleep-deprived and struggling. Even when you did get more hours, the poor to fair quality suggests your sleep isn't restorative."""
                },
            ]
            
            # Add conversation history
            messages.extend(history)
            
            # Add current query with embedded data context
            messages.append({
                "role": "user",
                "content": f"""Query: {query}

My recent health data shows:
{data_context}

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
            })
            
            tokenizer = self.model_manager.get_tokenizer("conversation")
            model = self.model_manager.get_model("conversation")
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=300,
                    do_sample=True,
                    temperature=0.1,     # Very low temperature for focused responses
                    top_p=0.8,          # Lower top_p to stay focused
                    repetition_penalty=1.3,  # Higher penalty to avoid repetitive generic phrases
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            response = response.replace(tokenizer.eos_token, "").strip()
            
            # Store in history
            self.history_manager.add_to_history(patient_id, "user", query)
            self.history_manager.add_to_history(patient_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"❌ Data-informed response error: {e}")
            return f"I understand your concern. Let me help you work through this, though I'm having some technical difficulties accessing your data right now."
    
    def _create_data_context(self, collected_data):
        """Create comprehensive data context for the conversation model"""
        context_parts = []
        
        for data_type, result in collected_data.items():
            if not result.get("success"):
                continue
                
            data = result["data"]
            context_parts.append(f"=== {data_type.upper()} DATA ===")
            
            if data_type == "sleep" and isinstance(data, list):
                context_parts.append("Recent sleep records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    hours = record.get('hours_slept', 0)
                    quality = record.get('quality', 'Unknown')
                    context_parts.append(f"• {date}: {hours} hours, {quality} quality")
                    
            elif data_type == "heart_rate" and isinstance(data, list):
                context_parts.append("Recent heart rate data:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    avg_hr = record.get('avg_heart_rate', 0)
                    context_parts.append(f"• {date}: Average {avg_hr} bpm")
            else:
                # Fallback for other data types
                context_parts.append(f"Raw data: {json.dumps(data, indent=2)}")
            
            context_parts.append("")  # Empty line between data types
        
        if not context_parts:
            return "No health data available for analysis"
            
        return "\n".join(context_parts)

# Global instance
hybrid_processor = HybridProcessor()
