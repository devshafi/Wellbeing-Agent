import torch
import json
import re
from models.model_manager import model_manager
from utils.history_manager import history_manager
from utils.few_shot_examples import FewShotExamples
from function_registry import function_registry

class HybridProcessor:
    """Handles hybrid queries that need both data and conversation"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.history_manager = history_manager
    
    def process_query(self, patient_id, query):
        """Process hybrid queries that need both data and conversation"""
        print(f"\n🎭 HYBRID PROCESSING PIPELINE")
        print(f"┌─ MISSION: Combine health data with empathetic conversation")
        print(f"├─ Patient needs both factual insights and emotional support")
        print(f"└─ Executing multi-modal analysis...")
        
        # Step 1: Strategic Planning
        print(f"\n📊 SUB-PHASE: DATA STRATEGY")
        print(f"├── Consulting function calling AI to determine data needs...")
        print(f"└── Analyzing query for specific health concerns...")
        
        function_calls = self._get_function_calls_from_model(patient_id, query)
        
        # Step 1.5: Validate that the function calls make sense for available functions
        print(f"\n🔍 SUB-PHASE: DATA VALIDATION")
        valid_functions = list(function_registry.functions.keys())
        valid_function_calls = []
        
        if function_calls:
            print(f"├── Validating proposed data retrievals...")
            for func_call in function_calls:
                function_name = func_call.get("name")
                if function_name in valid_functions:
                    valid_function_calls.append(func_call)
                    print(f"├── ✅ Approved: {function_name}")
                else:
                    print(f"├── ❌ Rejected: {function_name} (unavailable)")
        
        # If no valid function calls, fall back to conversation mode
        if not valid_function_calls:
            print(f"└── 🔄 No valid data sources found")
            print(f"    Switching to pure conversation mode...")
            from processors.conversation_processor import conversation_processor
            return conversation_processor.generate_response(patient_id, query)
        
        print(f"└── ✅ Data strategy validated: {len(valid_function_calls)} sources")
        
        # Step 2: Data Retrieval Execution
        print(f"\n💾 SUB-PHASE: DATA RETRIEVAL")
        print(f"├── Executing approved data retrievals...")
        collected_data = {}
        executed_functions = set()  # Track executed functions to avoid duplicates
        
        for func_call in valid_function_calls:
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
                    
                    print(f"├── 📊 Retrieving: {function_name}")
                    
                    result = function_registry.execute_function(function_name, parameters)
                    executed_functions.add(func_signature)
                    
                    if result["success"]:
                        data_type = function_name.replace("get_", "").replace("_data", "")
                        collected_data[data_type] = result
                        print(f"├── ✅ Success: {data_type} data acquired")
                    else:
                        print(f"├── ❌ Failed: {function_name} - {result.get('error')}")
                        
                except Exception as e:
                    print(f"├── ❌ Error: {func_call} - {e}")
        
        print(f"└── 📊 Data collection complete: {len(collected_data)} datasets")
        
        # Step 3: Therapeutic Response Generation
        print(f"\n💝 SUB-PHASE: THERAPEUTIC RESPONSE")
        print(f"├── Integrating health data with therapeutic insights...")
        print(f"├── Crafting empathetic, data-informed response...")
        
        if collected_data:
            print(f"└── Generating hybrid response with {len(collected_data)} data sources...")
            response = self._generate_data_informed_response(patient_id, query, collected_data)
        else:
            # Fallback to regular conversation if no data could be retrieved
            print(f"└── 🔄 Fallback: Pure conversation mode...")
            from processors.conversation_processor import conversation_processor
            response = conversation_processor.generate_response(patient_id, query)
        
        # Step 4: Prepare return data
        result = {
            "response": response,
            "raw_data": collected_data if collected_data else None
        }
        
        print(f"🎭 HYBRID PROCESSING COMPLETE")
        return result
    
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
                    max_new_tokens=256,
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
            
            print(f"├── 🤖 Function AI Reasoning:")
            lines = response.split('\n')
            for line in lines[:3]:  # Show first few lines of reasoning
                if line.strip():
                    print(f"│   '{line.strip()[:80]}{'...' if len(line) > 80 else ''}'")
            if len(lines) > 3:
                print(f"│   ... (analysis continues)")
            
            # Extract function calls using the same logic as function_calling_processor
            function_calls = self._extract_function_calls(response)
            print(f"└── 📋 AI Proposed: {len(function_calls)} data retrieval operations")
            return function_calls
            
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
                    "get_sleep_data", "get_stress_data", "get_heart_rate_data", "get_mood_data",
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
            
            # Create dynamic system prompt with few-shot examples based on collected data types
            system_prompt_with_examples = FewShotExamples.get_system_prompt_with_examples(list(collected_data.keys()))
            
            messages = [
                {
                    "role": "system",
                    "content": system_prompt_with_examples
                },
            ]
            
            # Add conversation history
            messages.extend(history)
            
            # Add current query with embedded data context
            messages.append({
                "role": "user",
                "content": f"""PATIENT QUERY: {query}

ACTUAL DATA TO ANALYZE:
{data_context}

THERAPEUTIC INSTRUCTIONS: 
1. CONNECT the patient's specific concern ("{query}") to their actual data patterns
2. EMPATHIZE with their emotional state and validate their feelings
3. IDENTIFY meaningful trends that relate to their concern (don't just list daily values)
4. PROVIDE therapeutic insights about how the data relates to their mental health
5. OFFER one concrete coping strategy based on the patterns you observe
6. Use specific dates and values to support your therapeutic analysis
7. Keep response CONCISE (2-3 sentences max) while maintaining empathy

Remember: This is mental health support, not data reporting. Connect their worry to what the data reveals therapeutically and BRIEFLY."""
            })
            
            print(messages)
            
            tokenizer = self.model_manager.get_tokenizer("conversation")
            model = self.model_manager.get_model("conversation")
            
            prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            input_length = inputs['input_ids'].shape[1]
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    do_sample=True,
                    num_beams=3,
                    temperature=0.5,
                    # top_p=0.9,
                    repetition_penalty=1.1,
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
                context_parts.append("Sleep records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    hours = record.get('hours_slept', 0)
                    quality = record.get('quality', 'Unknown')
                    context_parts.append(f"• {date}: {hours} hours, {quality} quality")
                    
            elif data_type == "heart_rate" and isinstance(data, list):
                context_parts.append("Heart rate records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    avg_hr = record.get('avg_heart_rate', 0)
                    max_hr = record.get('max_heart_rate', 0)
                    context_parts.append(f"• {date}: Average {avg_hr} bpm, Max {max_hr} bpm")
                    
            elif data_type == "stress" and isinstance(data, list):
                context_parts.append("Stress level records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    stress_level = record.get('stress_level', 0)
                    context_parts.append(f"• {date}: Stress level {stress_level}/100")
            
            elif data_type == "blood_pressure" and isinstance(data, list):
                context_parts.append("Blood pressure records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    systolic = record.get('systolic', 0)
                    diastolic = record.get('diastolic', 0)
                    category = record.get('category', 'Unknown')
                    context_parts.append(f"• {date}: {systolic}/{diastolic} mmHg ({category})")
            
            elif data_type == "blood_glucose" and isinstance(data, list):
                context_parts.append("Blood glucose records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    fasting = record.get('fasting_glucose', 0)
                    post_meal = record.get('post_meal_glucose', 0)
                    context_parts.append(f"• {date}: Fasting {fasting} mg/dL, Post-meal {post_meal} mg/dL")
            
            elif data_type == "nutrition" and isinstance(data, list):
                context_parts.append("Nutrition records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    calories = record.get('total_calories', 0)
                    protein = record.get('protein_g', 0)
                    carbs = record.get('carbs_g', 0)
                    fat = record.get('fat_g', 0)
                    context_parts.append(f"• {date}: {calories} cal (P:{protein}g C:{carbs}g F:{fat}g)")
            
            elif data_type == "exercise_session" and isinstance(data, list):
                context_parts.append("Exercise session records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    exercise_type = record.get('exercise_type', 'Unknown')
                    duration = record.get('duration_minutes', 0)
                    intensity = record.get('intensity', 'Unknown')
                    context_parts.append(f"• {date}: {exercise_type} - {duration}min ({intensity} intensity)")
            
            elif data_type == "steps" and isinstance(data, list):
                context_parts.append("Activity records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    steps = record.get('total_steps', 0)
                    active_min = record.get('active_minutes', 0)
                    distance = record.get('distance_km', 0)
                    context_parts.append(f"• {date}: {steps:,} steps, {active_min} active min, {distance}km")
            
            elif data_type == "weight" and isinstance(data, list):
                context_parts.append("Weight records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    weight = record.get('weight_kg', 0)
                    trend = record.get('weight_trend', 'Unknown')
                    context_parts.append(f"• {date}: {weight}kg ({trend})")
            
            elif data_type == "body_fat" and isinstance(data, list):
                context_parts.append("Body composition records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    body_fat = record.get('body_fat_percentage', 0)
                    muscle_mass = record.get('muscle_mass_kg', 0)
                    context_parts.append(f"• {date}: {body_fat}% body fat, {muscle_mass}kg muscle mass")
            
            elif data_type == "oxygen_saturation" and isinstance(data, list):
                context_parts.append("Oxygen saturation records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    spo2 = record.get('spo2_percentage', 0)
                    pulse_rate = record.get('pulse_rate', 0)
                    context_parts.append(f"• {date}: {spo2}% SpO2, {pulse_rate} bpm pulse")
            
            elif data_type == "body_temperature" and isinstance(data, list):
                context_parts.append("Body temperature records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    temp_c = record.get('body_temp_celsius', 0)
                    fever_status = record.get('fever_status', 'Unknown')
                    context_parts.append(f"• {date}: {temp_c}°C ({fever_status})")
            
            elif data_type == "calories_burned" and isinstance(data, list):
                context_parts.append("Calorie expenditure records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    total_cal = record.get('total_calories', 0)
                    active_cal = record.get('active_calories', 0)
                    context_parts.append(f"• {date}: {total_cal} total calories, {active_cal} active calories")
            
            elif data_type == "exercise_heart_rate" and isinstance(data, list):
                context_parts.append("Exercise heart rate records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    avg_hr = record.get('avg_exercise_hr', 0)
                    max_hr = record.get('max_exercise_hr', 0)
                    context_parts.append(f"• {date}: Avg exercise HR {avg_hr} bpm, Max {max_hr} bpm")
            
            elif data_type == "vo2max" and isinstance(data, list):
                context_parts.append("VO2 max fitness records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    vo2max = record.get('vo2max_ml_kg_min', 0)
                    fitness_level = record.get('fitness_level', 'Unknown')
                    context_parts.append(f"• {date}: VO2 max {vo2max} ml/kg/min ({fitness_level})")
            
            elif data_type == "distance" and isinstance(data, list):
                context_parts.append("Distance records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    total_distance = record.get('total_distance_km', 0)
                    walking = record.get('walking_distance_km', 0)
                    running = record.get('running_distance_km', 0)
                    context_parts.append(f"• {date}: {total_distance}km total (Walk: {walking}km, Run: {running}km)")
            
            elif data_type == "speed" and isinstance(data, list):
                context_parts.append("Speed/pace records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    avg_speed = record.get('avg_speed_kmh', 0)
                    activity = record.get('activity_type', 'Unknown')
                    pace = record.get('avg_pace_min_km', 'Unknown')
                    context_parts.append(f"• {date}: {avg_speed} km/h avg speed, {pace}/km pace ({activity})")
            
            elif data_type == "power" and isinstance(data, list):
                context_parts.append("Power output records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    avg_power = record.get('avg_power_watts', 0)
                    max_power = record.get('max_power_watts', 0)
                    context_parts.append(f"• {date}: {avg_power}W avg power, {max_power}W max power")
            
            elif data_type == "bmr" and isinstance(data, list):
                context_parts.append("Metabolic rate records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    bmr = record.get('bmr_calories', 0)
                    tdee = record.get('tdee_calories', 0)
                    context_parts.append(f"• {date}: {bmr} BMR calories, {tdee} TDEE calories")
            
            elif data_type == "height" and isinstance(data, list):
                context_parts.append("Height records:")
                for record in data:
                    date = record.get('date', 'Unknown')
                    height_cm = record.get('height_cm', 0)
                    height_ft = record.get('height_feet_inches', 'Unknown')
                    context_parts.append(f"• {date}: {height_cm}cm ({height_ft})")
                    
            else:
                # Fallback for any other data types
                context_parts.append(f"Data records:")
                if isinstance(data, list) and data:
                    # Show key-value pairs for first record as sample
                    sample_record = data[0]
                    for key, value in sample_record.items():
                        context_parts.append(f"• {key}: {value}")
                    if len(data) > 1:
                        context_parts.append(f"... and {len(data)-1} more records")
                else:
                    context_parts.append(f"{json.dumps(data, indent=2)}")
            
            context_parts.append("")  # Empty line between data types
        
        if not context_parts:
            return "No health data available for analysis"
            
        return "\n".join(context_parts)

# Global instance
hybrid_processor = HybridProcessor()
