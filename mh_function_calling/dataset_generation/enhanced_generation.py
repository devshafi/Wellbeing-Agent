import json
import random
import pandas as pd
from typing import List, Dict, Tuple
import numpy as np

from utils.enhanced_template import (
    MENTAL_HEALTH_EXPRESSIONS,
    TEMPORAL_EXPRESSIONS, 
    NON_TEMPORAL_EXPRESSIONS,
    QUERY_STARTERS,
    DATA_REQUEST_PATTERNS,
    REQUEST_REASONS,
    MEDICAL_REFS,
    FUNCTION_CONDITION_MAP,
    ENHANCED_THINKING_TEMPLATES,
    get_random_mh_expression,
    get_temporal_expression,
    get_non_temporal_expression,
    get_data_type,
    get_relevant_condition,
    extract_time_info,
    extract_non_temporal_word
)

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# ========================================
# ALL 20 HEALTH FUNCTIONS
# ========================================

ALL_HEALTH_FUNCTIONS = [
    'get_steps_data', 'get_blood_glucose_data', 'get_oxygen_saturation_data',
    'get_blood_pressure_data', 'get_exercise_session_data', 'get_calories_burned_data',
    'get_distance_data', 'get_exercise_heart_rate_data', 'get_power_data',
    'get_speed_data', 'get_vo2max_data', 'get_heart_rate_data',
    'get_nutrition_data', 'get_sleep_data', 'get_weight_data',
    'get_body_fat_data', 'get_bmr_data', 'get_height_data',
    'get_stress_data', 'get_body_temperature_data'
]

# ========================================
# DIVERSE QUERY GENERATION
# ========================================

def generate_diverse_temporal_query(function_name: str) -> Dict:
    """Generate highly diverse temporal queries with function + temporal reasoning"""
    
    data_type = get_data_type(function_name)
    condition_category = get_relevant_condition(function_name)
    condition = get_random_mh_expression(condition_category)
    
    # Choose random timeframe
    possible_days = [1, 2, 3, 5, 7, 10, 14, 21, 30]
    days = random.choice(possible_days)
    time_phrase = get_temporal_expression(days)
    
    # Build query with variations
    query_patterns = [
        # Direct approach
        f"{random.choice(QUERY_STARTERS)} {random.choice(DATA_REQUEST_PATTERNS).format(data_type=data_type)} for {time_phrase}",
        
        # Condition-focused
        f"My {condition} is affecting my {data_type} {time_phrase}",
        f"I'm tracking {data_type} to help manage my {condition} over {time_phrase}",
        f"I want to see if my {condition} correlates with {data_type} for {time_phrase}",
        
        # Medical context
        f"{random.choice(MEDICAL_REFS)} wants to see my {data_type} data for {time_phrase}",
        f"I need {data_type} information for my {condition} treatment over {time_phrase}",
        
        # Problem-solving
        f"I'm trying to understand my {data_type} patterns during {condition} episodes over {time_phrase}",
        f"My {condition} symptoms seem connected to {data_type} changes for {time_phrase}",
        
        # Monitoring approach
        f"I've been monitoring {data_type} for {condition} management over {time_phrase}",
        f"Need to track {data_type} changes since my {condition} got worse {time_phrase}",
        
        # Therapy context
        f"My therapist suggested tracking {data_type} for {condition} over {time_phrase}",
        f"I want to correlate {data_type} with my {condition} therapy progress for {time_phrase}"
    ]
    
    query = random.choice(query_patterns)
    
    # Extract actual time info from generated query
    extracted_days, extracted_phrase = extract_time_info(query)
    if extracted_days:
        days = extracted_days
        time_phrase = extracted_phrase
    
    # Generate thinking with BOTH function and temporal reasoning
    thinking_template = random.choice(ENHANCED_THINKING_TEMPLATES['temporal'])
    thinking = thinking_template.format(
        condition=condition,
        data_type=data_type,
        time_phrase=time_phrase,
        num_days=days,
        function_name=function_name  # Added function name
    )
    
    return {
        'query': query,
        'days': days,
        'time_phrase': time_phrase,
        'thinking': thinking,
        'condition': condition,
        'is_temporal': True
    }

def generate_diverse_non_temporal_query(function_name: str) -> Dict:
    """Generate highly diverse non-temporal queries with function + default temporal reasoning"""
    
    data_type = get_data_type(function_name)
    condition_category = get_relevant_condition(function_name)
    condition = get_random_mh_expression(condition_category)
    
    # Randomly decide whether to include a non-temporal word or not
    include_non_temporal = random.choice([True, False])
    
    if include_non_temporal:
        non_temporal_word = get_non_temporal_expression()
        query_patterns = [
            f"How's my {data_type} been {non_temporal_word}?",
            f"What do my {data_type} levels look like {non_temporal_word}?",
            f"I've been struggling with {condition} {non_temporal_word} - show me my {data_type}",
            f"My {condition} has been affecting me {non_temporal_word} - how's my {data_type}?",
            f"Been dealing with {condition} {non_temporal_word} - what's my {data_type} like?",
        ]
        actual_non_temporal_word = non_temporal_word
    else:
        query_patterns = [
            f"{random.choice(QUERY_STARTERS)} check my {data_type} data",
            f"{random.choice(MEDICAL_REFS)} wants to see my {data_type} data",
            f"I need my {data_type} information for my appointment",
            f"Show me my {data_type} readings",
            f"Could you pull up my {data_type} data?",
            f"I want to see my {data_type} measurements",
            f"I need to review my {data_type} patterns for {condition}",
            f"Can you analyze my {data_type} trends?",
            f"What does my {data_type} data tell us about my {condition}?",
            f"Can you check my {data_type} data",
            f"I want to check my {data_type} data",
        ]
        actual_non_temporal_word = None
    
    query = random.choice(query_patterns)
    
    # Extract the actual non-temporal word used (if any)
    detected_word = extract_non_temporal_word(query)
    
    # Generate appropriate thinking based on whether non-temporal words were used
    if detected_word != "without specific timeframe":
        # Use thinking templates that reference the actual word + function reasoning
        thinking_templates = [
            "They mentioned '{actual_word}' and want {data_type} information for their {condition}. Since they're asking specifically about {data_type}, I need to call {function_name}. I'll go with 7 days of data to show current trends.",
            "Since they said '{actual_word}' and need {data_type} data, I should use {function_name} to get those measurements. I'll get about 7 days of {data_type} data to show recent patterns related to their {condition}.",
            "They want {data_type} data '{actual_word}' but didn't specify how far back. For {data_type} specifically, {function_name} is the right function to call. A week (7 days) is usually good for seeing recent {condition}-related patterns."
        ]
        thinking_template = random.choice(thinking_templates)
        thinking = thinking_template.format(
            data_type=data_type,
            actual_word=detected_word,
            condition=condition,
            function_name=function_name  # Added function name
        )
    else:
        # Use thinking templates that don't reference any specific words + function reasoning
        thinking_templates = [
            "They want to see their {data_type} data but didn't specify exactly when. Since they're asking specifically about {data_type}, I need to call {function_name} to get those measurements. Since this seems to be a general request about their {condition}, I'll default to getting a week's worth of data (7 days) to give them a good overview.",
            "This person wants {data_type} information but no specific timeframe was given. The request is for {data_type} data specifically, so {function_name} is the right function to use. I'll get about 7 days of data to show recent patterns related to their {condition}.",
            "{data_type} inquiry without exact dates. Since they need {data_type} measurements, I should call {function_name}. A week of data (7 days) should be helpful for seeing current patterns in relation to their {condition} without being overwhelming.",
            "The user is asking about their {data_type} - no specific timeframe given. For {data_type} data, I need to use {function_name}. For {condition} tracking, a week of recent data (7 days) is usually a good starting point.",
            "No specific time period mentioned, but they want {data_type} data. Since they're asking about {data_type} specifically, {function_name} is the appropriate function. For {data_type} related to {condition}, I'll default to 7 days to show recent patterns without overwhelming them with data.",
            "The patient is requesting {data_type} data for their {condition}. For {data_type} specifically, I need to call {function_name}. Without a specific timeframe, 7 days of recent data will provide a good baseline for assessment.",
            "This is a general {data_type} inquiry in the context of {condition}. Since they want {data_type} data, {function_name} is the appropriate function. A week of data gives a good recent snapshot without being overwhelming."
        ]
        thinking_template = random.choice(thinking_templates)
        thinking = thinking_template.format(
            data_type=data_type,
            condition=condition,
            function_name=function_name  # Added function name
        )
    
    return {
        'query': query,
        'days': 7,  # Default for non-temporal
        'time_phrase': None,
        'thinking': thinking,
        'condition': condition,
        'is_temporal': False,
        'actual_non_temporal_word': detected_word
    }

# ========================================
# SAMPLE GENERATION
# ========================================

def generate_single_sample(function_name: str, is_temporal: bool = True) -> Dict:
    """Generate a single dataset sample"""
    
    # Generate query data
    if is_temporal:
        query_data = generate_diverse_temporal_query(function_name)
    else:
        query_data = generate_diverse_non_temporal_query(function_name)
    
    # Generate patient ID
    patient_formats = ["UID_{}", "P{:03d}", "USER_{}", "ID_{:04d}", "PATIENT_{}"]
    patient_id = random.choice(patient_formats).format(random.randint(100, 9999))
    
    # Create function call
    function_call = {
        "name": function_name,
        "parameters": {
            "patient_id": patient_id,
            "num_days": query_data['days']
        }
    }
    
    response = f"<think>\n{query_data['thinking']}\n</think>\n\n<function>\n{json.dumps(function_call, indent=2)}\n</function>"
    
    return {
        'patient_query': query_data['query'],
        'assistant_response': response,
        'function_name': function_name,
        'patient_id': patient_id,
        'num_days': query_data['days'],
        'has_temporal': query_data['is_temporal'],
        'condition': query_data['condition']
    }

# ========================================
# SCALED DATASET GENERATION
# ========================================

def generate_scaled_dataset(samples_per_function: int = 500, temporal_ratio: float = 0.7) -> List[Dict]:
    """Generate large, diverse dataset with configurable size and ratios"""
    
    dataset = []
    
    print(f"🚀 Generating enhanced diverse dataset...")
    print(f"Functions: {len(ALL_HEALTH_FUNCTIONS)}")
    print(f"Samples per function: {samples_per_function}")
    print(f"Temporal ratio: {temporal_ratio*100:.0f}%")
    print(f"Total target: {len(ALL_HEALTH_FUNCTIONS) * samples_per_function:,} samples")
    print("=" * 60)
    
    for func_idx, function_name in enumerate(ALL_HEALTH_FUNCTIONS, 1):
        print(f"Processing {func_idx:2d}/20: {function_name}")
        
        function_samples = []
        
        # Calculate temporal/non-temporal split
        temporal_count = int(samples_per_function * temporal_ratio)
        non_temporal_count = samples_per_function - temporal_count
        
        # Generate temporal samples
        for i in range(temporal_count):
            sample = generate_single_sample(function_name, is_temporal=True)
            function_samples.append(sample)
        
        # Generate non-temporal samples
        for i in range(non_temporal_count):
            sample = generate_single_sample(function_name, is_temporal=False)
            function_samples.append(sample)
        
        print(f"  ✅ Generated {len(function_samples)} samples ({temporal_count} temporal, {non_temporal_count} non-temporal)")
        dataset.extend(function_samples)
    
    # Shuffle to mix functions
    random.shuffle(dataset)
    
    return dataset

# ========================================
# DATASET ANALYSIS
# ========================================

def analyze_dataset(dataset: List[Dict]) -> Dict:
    """Analyze dataset diversity and statistics"""
    
    analysis = {
        'total_samples': len(dataset),
        'temporal_count': sum(1 for s in dataset if s['has_temporal']),
        'non_temporal_count': sum(1 for s in dataset if not s['has_temporal']),
        'functions': {},
        'conditions': {},
        'day_distribution': {},
        'unique_queries': len(set(s['patient_query'] for s in dataset)),
        'avg_query_length': 0,
        'avg_thinking_length': 0
    }
    
    query_lengths = []
    thinking_lengths = []
    
    # Analyze by function
    for sample in dataset:
        func = sample['function_name']
        if func not in analysis['functions']:
            analysis['functions'][func] = {'total': 0, 'temporal': 0, 'non_temporal': 0}
        
        analysis['functions'][func]['total'] += 1
        if sample['has_temporal']:
            analysis['functions'][func]['temporal'] += 1
        else:
            analysis['functions'][func]['non_temporal'] += 1
        
        # Analyze conditions
        condition = sample['condition']
        analysis['conditions'][condition] = analysis['conditions'].get(condition, 0) + 1
        
        # Analyze day distribution
        days = sample['num_days']
        analysis['day_distribution'][days] = analysis['day_distribution'].get(days, 0) + 1
        
        # Analyze lengths
        query_lengths.append(len(sample['patient_query'].split()))
        
        # Extract thinking from response
        try:
            thinking_part = sample['assistant_response'].split('<think>')[1].split('</think>')[0].strip()
            thinking_lengths.append(len(thinking_part.split()))
        except:
            pass
    
    if query_lengths:
        analysis['avg_query_length'] = np.mean(query_lengths)
    if thinking_lengths:
        analysis['avg_thinking_length'] = np.mean(thinking_lengths)
    
    return analysis

def print_analysis_report(analysis: Dict):
    """Print comprehensive analysis report"""
    
    print("\n" + "="*60)
    print("📊 DATASET ANALYSIS REPORT")
    print("="*60)
    
    # Basic stats
    print(f"Total Samples: {analysis['total_samples']:,}")
    print(f"Unique Queries: {analysis['unique_queries']:,} ({analysis['unique_queries']/analysis['total_samples']*100:.1f}% unique)")
    print(f"Temporal Queries: {analysis['temporal_count']:,} ({analysis['temporal_count']/analysis['total_samples']*100:.1f}%)")
    print(f"Non-temporal Queries: {analysis['non_temporal_count']:,} ({analysis['non_temporal_count']/analysis['total_samples']*100:.1f}%)")
    print(f"Average Query Length: {analysis['avg_query_length']:.1f} words")
    print(f"Average Thinking Length: {analysis['avg_thinking_length']:.1f} words")
    
    # Function distribution
    print(f"\n📋 Function Distribution:")
    for func, stats in sorted(analysis['functions'].items()):
        print(f"  {func}: {stats['total']} ({stats['temporal']} temporal, {stats['non_temporal']} non-temporal)")
    
    # Top conditions
    print(f"\n🏥 Top Mental Health Conditions:")
    sorted_conditions = sorted(analysis['conditions'].items(), key=lambda x: x[1], reverse=True)
    for condition, count in sorted_conditions[:10]:
        print(f"  {condition}: {count:,} ({count/analysis['total_samples']*100:.1f}%)")
    
    # Day distribution
    print(f"\n📅 Day Distribution:")
    sorted_days = sorted(analysis['day_distribution'].items())
    for days, count in sorted_days:
        print(f"  {days:2d} days: {count:,} ({count/analysis['total_samples']*100:.1f}%)")
    
    # Quality metrics
    uniqueness_score = analysis['unique_queries'] / analysis['total_samples'] * 100
    diversity_score = len(analysis['conditions']) / analysis['total_samples'] * 100
    
    print(f"\n🎯 Quality Metrics:")
    print(f"  Uniqueness Score: {uniqueness_score:.1f}% (higher is better)")
    print(f"  Condition Diversity: {len(analysis['conditions'])} unique conditions")
    print(f"  Function Coverage: {len(analysis['functions'])}/20 functions")

# ========================================
# MAIN GENERATION FUNCTIONS
# ========================================

def generate_small_dataset() -> List[Dict]:
    """Generate small dataset: 2,000 samples (100 per function)"""
    return generate_scaled_dataset(samples_per_function=100)

def generate_medium_dataset() -> List[Dict]:
    """Generate medium dataset: 5,000 samples (250 per function)"""
    return generate_scaled_dataset(samples_per_function=250)

def generate_large_dataset() -> List[Dict]:
    """Generate large dataset: 10,000 samples (500 per function)"""
    return generate_scaled_dataset(samples_per_function=500)

def generate_xlarge_dataset() -> List[Dict]:
    """Generate extra-large dataset: 20,000 samples (1,000 per function)"""
    return generate_scaled_dataset(samples_per_function=1000)

def save_dataset(dataset: List[Dict], filename: str = None):
    """Save dataset to CSV file"""
    
    if filename is None:
        filename = f"mh_function_calling_{len(dataset)}_samples_enhanced.csv"
    
    df = pd.DataFrame(dataset)
    filepath = f"/home/jovyan/Works/MSc_Thesis/dataset/{filename}"
    df.to_csv(filepath, index=False)
    
    print(f"\n✅ Dataset saved to: {filename}")
    print(f"📁 Full path: {filepath}")
    return filepath

# ========================================
# SAMPLE DISPLAY
# ========================================

def show_sample_queries(dataset: List[Dict], num_samples: int = 5):
    """Display sample queries for diversity check"""
    
    print(f"\n🔍 SAMPLE QUERIES (showing diversity):")
    print("=" * 60)
    
    # Sample temporal queries
    temporal_samples = [s for s in dataset if s['has_temporal']][:num_samples]
    print("📅 TEMPORAL QUERIES:")
    for i, sample in enumerate(temporal_samples, 1):
        print(f"\n{i}. Function: {sample['function_name']}")
        print(f"   Query: {sample['patient_query']}")
        print(f"   Days: {sample['num_days']}")
        print(f"   Condition: {sample['condition']}")
    
    # Sample non-temporal queries  
    non_temporal_samples = [s for s in dataset if not s['has_temporal']][:num_samples]
    print(f"\n📊 NON-TEMPORAL QUERIES:")
    for i, sample in enumerate(non_temporal_samples, 1):
        print(f"\n{i}. Function: {sample['function_name']}")
        print(f"   Query: {sample['patient_query']}")
        print(f"   Condition: {sample['condition']}")

# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    
    print("🎯 Enhanced Mental Health Function Calling Dataset Generator")
    print("=" * 60)
    print("Available dataset sizes:")
    print("1. Small:  2,000 samples (100 per function)")
    print("2. Medium: 5,000 samples (250 per function)")  
    print("3. Large: 10,000 samples (500 per function)")
    print("4. XL:    20,000 samples (1,000 per function)")
    print("5. Custom: Specify your own size")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        dataset = generate_small_dataset()
    elif choice == '2':
        dataset = generate_medium_dataset()
    elif choice == '3':
        dataset = generate_large_dataset()
    elif choice == '4':
        dataset = generate_xlarge_dataset()
    elif choice == '5':
        try:
            custom_size = int(input("Enter samples per function: "))
            dataset = generate_scaled_dataset(samples_per_function=custom_size)
        except ValueError:
            print("Invalid input. Using medium dataset (250 per function).")
            dataset = generate_medium_dataset()
    else:
        print("Invalid choice. Using medium dataset (250 per function).")
        dataset = generate_medium_dataset()
    
    # Analyze dataset
    analysis = analyze_dataset(dataset)
    print_analysis_report(analysis)
    
    # Show samples
    show_sample_queries(dataset)
    
    # Save dataset
    save_dataset(dataset)
    
    print(f"\n🎯 Dataset Generation Complete!")
    print(f"✅ {len(dataset):,} samples generated with high diversity")
    print(f"🔄 Extensive paraphrasing reduces memorization risk")
    print(f"💡 Natural language patterns improve generalization")
    print(f"🏥 Mental health context maintained throughout")