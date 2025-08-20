import torch
import json
import re
from models.model_manager import model_manager
from utils.history_manager import history_manager
from function_registry import function_registry

class FunctionCallingProcessor:
    """Handles function calling and data retrieval"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.history_manager = history_manager
    
    def process_query(self, patient_id, query):
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
            
            
            tokenizer = self.model_manager.get_tokenizer("function_calling")
            model = self.model_manager.get_model("function_calling")
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=0.01,
                    top_p=0.95,
                    repetition_penalty=1.0,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            response = response.replace(tokenizer.eos_token, "").strip()
            
            
            # Extract and execute any function calls
            enhanced_response, function_result = self._extract_and_execute_function(response)
            
            # If function was executed successfully, generate orchestrator response
            if function_result and function_result.get("success"):
                print("🎭 Generating orchestrator response...")
                orchestrator_response = self._generate_orchestrator_response(patient_id, query, function_result)
                
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
                formatted_data = self._format_function_result(function_result)
                final_response += f"**📋 Detailed Information:**\n{formatted_data}"
                
                # Add to history
                self.history_manager.add_to_history(patient_id, "user", query)
                summary = f"Retrieved data for: {query[:50]}..."
                self.history_manager.add_to_history(patient_id, "assistant", summary)
                
                return final_response
            else:
                # Return the enhanced response as before if no function result
                return enhanced_response
            
        except Exception as e:
            print(f"❌ Function calling model error: {e}")
            return f"I'm sorry, I encountered an error while trying to retrieve the information: {str(e)}"
    
    def _extract_and_execute_function(self, response: str) -> tuple:
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
                flexible_patterns = [
                    r'"name"\s*:\s*"([^"]+)"[^}]*?"parameters"\s*:\s*\{([^}]+)\}',
                    r'\{\s*"name"\s*:\s*"([^"]+)"[^}]*?"parameters"\s*:\s*\{([^}]*?)\}\s*\}',
                    r'\{\s*"name"\s*:\s*"([^"]+)".*?\}',
                ]
                
                for i, pattern in enumerate(flexible_patterns):
                    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                    if match:
                        print(f"✅ Found function call using pattern {i+1}")
                        
                        if len(match.groups()) >= 2:
                            function_name = match.group(1)
                            parameters_str = match.group(2)
                            
                            try:
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
                                continue
                        else:
                            function_name = match.group(1)
                            function_call_str = json.dumps({
                                "name": function_name,
                                "parameters": {}
                            })
                            break
                
                # Method 3: Last resort - look for specific function names
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
                            
                            parameters = {"patient_id": "UID_123"}
                            if func_name != "get_health_summary":
                                parameters["num_days"] = 7
                            
                            function_call_str = json.dumps({
                                "name": func_name,
                                "parameters": parameters
                            })
                            break
            
            if not function_call_str:
                print("❌ No function calls detected")
                return response, None
            
            try:
                # Parse and execute the function call
                function_call = json.loads(function_call_str)
                function_name = function_call.get("name")
                parameters = function_call.get("parameters", {})
                
                print(f"🔧 Executing function: {function_name} with params: {parameters}")
                
                result = function_registry.execute_function(function_name, parameters)
                
                if result["success"]:
                    formatted_result = self._format_function_result(result)
                    
                    if function_match:
                        enhanced_response = re.sub(
                            function_pattern, 
                            formatted_result, 
                            response, 
                            flags=re.DOTALL
                        )
                    else:
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
    
    def _generate_orchestrator_response(self, patient_id, original_query, function_result):
        """Generate natural language response based on function execution results"""
        try:
            if not function_result or not function_result.get("success"):
                return "I apologize, but I wasn't able to retrieve the requested information at this time."
            
            function_name = function_result["function"]
            data = function_result["data"]
            
            # Create a structured summary of the data
            data_summary = self._create_data_summary(function_name, data)
            
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
            
            tokenizer = self.model_manager.get_tokenizer("conversation")
            model = self.model_manager.get_model("conversation")
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=400,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            response_tokens = outputs[0][input_length:]
            orchestrator_response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            orchestrator_response = orchestrator_response.replace(tokenizer.eos_token, "").strip()
            
            return orchestrator_response
            
        except Exception as e:
            print(f"❌ Orchestrator response error: {e}")
            return "I've retrieved your data successfully, but I'm having trouble interpreting it right now."
    
    def _create_data_summary(self, function_name, data):
        """Create a structured summary of the data"""
        if function_name == "get_sleep_data":
            if isinstance(data, list):
                total_hours = sum(record.get('hours_slept', 0) for record in data)
                avg_hours = total_hours / len(data) if data else 0
                qualities = [record.get('quality', 'Unknown') for record in data[-3:]]
                return f"Sleep Data: {len(data)} days, average {avg_hours:.1f}h/night, recent quality: {', '.join(qualities)}"
            else:
                avg_sleep = data.get('average_sleep_hours', 0)
                return f"Sleep Data: Average {avg_sleep}h/night"
        
        elif function_name == "get_heart_rate_data":
            if isinstance(data, list):
                avg_hr = sum(record.get('avg_heart_rate', 0) for record in data) / len(data) if data else 0
                return f"Heart Rate Data: {len(data)} days, average {avg_hr:.0f} bpm"
            else:
                avg_resting = data.get('average_resting_hr', 0)
                return f"Heart Rate Data: Average resting {avg_resting} bpm"
        else:
            return f"Data retrieved from {function_name}: {str(data)[:200]}..."
    
    def _format_function_result(self, result):
        """Format function execution result for display"""
        if not result.get("success"):
            return f"❌ **Error**: {result.get('error', 'Unknown error')}"
        
        function_name = result["function"]
        data = result["data"]
        
        if function_name == "get_sleep_data":
            return f"**😴 Sleep Data:**\n```json\n{json.dumps(data, indent=2)}\n```"
        elif function_name == "get_heart_rate_data":
            return f"**❤️ Heart Rate Data:**\n```json\n{json.dumps(data, indent=2)}\n```"
        else:
            return f"**📊 {function_name} Results:**\n```json\n{json.dumps(data, indent=2)}\n```"

# Global instance
function_calling_processor = FunctionCallingProcessor()
