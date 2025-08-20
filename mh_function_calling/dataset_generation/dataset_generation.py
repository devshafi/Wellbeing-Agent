
import json
import random
from itertools import product

from utils.utils import load_health_functions, save_samples_to_csv
from utils.templates import MENTAL_HEALTH_QUERY_TEMPLATES, MENTAL_HEALTH_THINKING_TEMPLATES


def generate_dataset_sample(function_data, query_template, thinking_template):
    """Generate a single dataset sample with simplified parameters"""
    
    # Generate random number of days (realistic range for health monitoring)
    num_days_options = [1, 3, 5, 7, 10, 14, 15, 21, 28, 30]
    num_days = random.choice(num_days_options)
    
    # Fill in query template with number of days
    filled_query = query_template.replace('{num_days}', str(num_days))
    
    # Generate patient ID
    patient_id = f"UID_{random.randint(100, 999)}"
    
    # Create simplified function arguments - ONLY patient_id and num_days
    function_args = {
        "patient_id": patient_id,
        "num_days": num_days
    }
    
    # Generate thinking process
    thinking = thinking_template
    
    # Create the complete response with function call
    function_call = {
        "name": function_data['function_name'],
        "parameters": function_args
    }
    
    response = f"<think>\n{thinking}\n</think>\n\n<function>\n{json.dumps(function_call, indent=2)}\n</function>"
    
    return {
        "patient_query": filled_query,
        "assistant_response": response,
        "function_name": function_data['function_name'],
        "patient_id": patient_id,
        "num_days": num_days
    }
    
def generate_complete_dataset(csv_path, samples_per_function=180):
    """Generate complete dataset with simplified parameters"""
    
    functions = load_health_functions(csv_path)
    all_samples = []
    
    for function_data in functions:
        function_name = function_data['function_name']
        print(f"Generating {samples_per_function} samples for {function_name}...")
        
        #Get templates for this function
        query_templates = MENTAL_HEALTH_QUERY_TEMPLATES.get(function_name, [f"Can you get {function_name} data for me for the past {{num_days}} days?"])

        thinking_templates = MENTAL_HEALTH_THINKING_TEMPLATES.get(function_name, [f"I need to retrieve {function_name} data for mental health analysis for the specified time period."])
        
        for i in range(samples_per_function):
            # Randomly select templates
            query_template = random.choice(query_templates)
            thinking_template = random.choice(thinking_templates)
            
            # Generate sample
            sample = generate_dataset_sample(
                function_data, 
                query_template,  
                thinking_template
            )
            
            all_samples.append(sample)
    

    return all_samples



if __name__ == "__main__":
    print("Generating mental health function calling dataset")
    raw_dataset = generate_complete_dataset('mh_function_calling/dataset_generation/health_functions.csv', samples_per_function=200)
    print(len(raw_dataset))
    save_samples_to_csv(raw_dataset,"dataset/mh_function_calling_dataset.csv")

