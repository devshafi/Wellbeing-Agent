import re
import random

# ========================================
# MENTAL HEALTH EXPRESSION VARIATIONS
# ========================================

MENTAL_HEALTH_EXPRESSIONS = {
    'anxiety': [
        "anxiety", "stress", "worry", "nervousness", "panic", "fear", "unease", 
        "apprehension", "tension", "restlessness", "jitters", "anxiousness",
        "overwhelming worry", "constant fear", "racing thoughts", "panic episodes",
        "severe anxiety", "chronic stress", "social anxiety", "generalized anxiety",
        "anxiety attacks", "feeling on edge", "nervous energy", "worried state",
        "panic disorder symptoms", "stress responses", "fight-or-flight response"
    ],
    
    'depression': [
        "depression", "low mood", "sadness", "melancholy", "despair", "hopelessness",
        "feeling down", "depressive symptoms", "major depression", "mood disorder",
        "feeling blue", "emotional numbness", "persistent sadness", "deep sadness",
        "clinical depression", "depressive episode", "seasonal depression", "mood swings",
        "feeling empty", "loss of interest", "anhedonia", "depressed state",
        "overwhelming sadness", "chronic depression", "bipolar depression"
    ],
    
    'stress': [
        "stress", "pressure", "strain", "tension", "overwhelm", "burnout",
        "chronic stress", "acute stress", "work stress", "life stress", "daily stress",
        "stress overload", "feeling overwhelmed", "high pressure", "stress levels",
        "psychological stress", "emotional stress", "mental strain", "stress response",
        "traumatic stress", "post-traumatic stress", "ongoing pressure", "intense pressure"
    ],
    
    'panic': [
        "panic attacks", "panic episodes", "panic disorder", "sudden panic", "panic symptoms",
        "intense fear", "overwhelming panic", "panic responses", "acute panic",
        "panic reactions", "fear episodes", "terror attacks", "anxiety attacks",
        "sudden anxiety", "panic-like symptoms", "fear responses", "panic states"
    ],
    
    'mood_issues': [
        "mood swings", "emotional instability", "mood episodes", "bipolar symptoms",
        "manic episodes", "hypomanic states", "mood disorder", "emotional dysregulation",
        "mood fluctuations", "emotional ups and downs", "unstable moods", "mood cycles"
    ]
}

# ========================================
# TEMPORAL EXPRESSION VARIATIONS
# ========================================

TEMPORAL_EXPRESSIONS = {
    1: [
        "yesterday", "the last day", "since yesterday", "past 24 hours", "today",
        "over the last day", "in the past day", "since this morning", "all day today",
        "throughout yesterday", "over yesterday", "during the last 24 hours"
    ],
    
    2: [
        "past couple days", "last 2 days", "couple of days ago", "past 48 hours",
        "these past 2 days", "over the last couple of days", "since 2 days ago",
        "for the past two days", "during these 2 days", "over 48 hours"
    ],
    
    3: [
        "past few days", "last 3 days", "few days back", "past 72 hours",
        "these past few days", "over the last 3 days", "since few days ago",
        "for the past three days", "during these few days", "over the last several days"
    ],
    
    5: [
        "past 5 days", "last workweek", "since Monday", "past business week",
        "over the work week", "this work week", "during the weekdays",
        "for the past 5 days", "since last Monday", "over 5 days"
    ],
    
    7: [
        "past week", "last 7 days", "this week", "since last week", "past seven days",
        "a week ago", "over the last week", "during this week", "for the past week",
        "since a week ago", "throughout the week", "over seven days", "this past week",
        "during the last 7 days", "over the course of a week", "since the beginning of the week"
    ],
    
    10: [
        "past 10 days", "last 10 days", "since 10 days ago", "past week and a half",
        "over the last 10 days", "for 10 days now", "during these 10 days",
        "since a week and a half ago", "over a week and a half"
    ],
    
    14: [
        "past 2 weeks", "last fortnight", "past 14 days", "couple of weeks",
        "past two weeks", "last 2 weeks", "over the last fortnight", "these past 2 weeks",
        "for the past two weeks", "since 2 weeks ago", "during the last 2 weeks",
        "over two weeks", "throughout the fortnight", "over 14 days"
    ],
    
    21: [
        "past 3 weeks", "last 21 days", "since 3 weeks ago", "past three weeks",
        "over the last 3 weeks", "for 3 weeks now", "during these 3 weeks",
        "throughout the last 3 weeks", "over three weeks", "since three weeks ago"
    ],
    
    30: [
        "past month", "last 30 days", "since last month", "past four weeks",
        "a month ago", "over the last month", "this past month", "during the month",
        "for the past month", "throughout the month", "over 30 days", "since a month ago",
        "over the course of a month", "during the last 30 days", "for a full month"
    ]
}

# Non-temporal expressions for recent queries
NON_TEMPORAL_EXPRESSIONS = [
    "lately", "recently", "these days", "nowadays", "of late", "in recent times",
    "as of late", "in the recent past", "currently", "at present", "right now",
    "these recent days", "in recent weeks", "over recent time", "in the near past"
]

# ========================================
# QUERY STRUCTURE VARIATIONS
# ========================================

QUERY_STARTERS = [
    "I need to", "I want to", "Can you", "Could you", "Please", "I'd like to",
    "Help me", "Show me", "I'm trying to", "I'm looking to", "I require",
    "I'm hoping to", "Would you", "I'm interested in", "I'm seeking",
    "I need help with", "I'm requesting", "I would like", "Let me"
]

DATA_REQUEST_PATTERNS = [
    "track {data_type}", "monitor {data_type}", "check {data_type}", "see {data_type}",
    "review {data_type}", "analyze {data_type}", "examine {data_type}", "look at {data_type}",
    "get {data_type} data", "retrieve {data_type} information", "access {data_type} records",
    "pull up {data_type} metrics", "view {data_type} patterns", "understand {data_type} trends"
]

REQUEST_REASONS = [
    "to help manage my {condition}", "for my {condition} treatment", "because of my {condition}",
    "to track my {condition} progress", "for my therapy sessions", "for my doctor appointment",
    "to understand my {condition} patterns", "to adjust my treatment plan",
    "to discuss with my therapist", "for my mental health assessment",
    "to monitor treatment effects", "to identify triggers for my {condition}"
]

MEDICAL_REFS = [
    "my therapist", "my psychiatrist", "my doctor", "my physician", "my counselor",
    "my psychologist", "my mental health provider", "my treatment team",
    "my healthcare provider", "my specialist", "my clinician"
]

# ========================================
# TIME EXTRACTION PATTERNS
# ========================================

TIME_PATTERNS = {
    # Day patterns
    r'(\d+)\s*days?': lambda m: int(m.group(1)),
    r'past\s+(\d+)\s*days?': lambda m: int(m.group(1)),
    r'last\s+(\d+)\s*days?': lambda m: int(m.group(1)),
    r'since\s+(\d+)\s*days?\s+ago': lambda m: int(m.group(1)),
    
    # Week patterns  
    r'past\s+week|last\s+week|this\s+week|since\s+last\s+week|past\s+seven\s+days': lambda m: 7,
    r'past\s+(\d+)\s*weeks?': lambda m: int(m.group(1)) * 7,
    r'last\s+(\d+)\s*weeks?': lambda m: int(m.group(1)) * 7,
    r'couple\s+of\s+weeks|past\s+two\s+weeks|last\s+two\s+weeks': lambda m: 14,
    r'past\s+three\s+weeks|last\s+three\s+weeks': lambda m: 21,
    r'fortnight|past\s+fortnight|last\s+fortnight': lambda m: 14,
    
    # Month patterns
    r'past\s+month|last\s+month|since\s+last\s+month': lambda m: 30,
    r'past\s+four\s+weeks': lambda m: 28,
    
    # Special patterns
    r'yesterday|since\s+yesterday': lambda m: 1,
    r'couple\s+of\s+days|past\s+couple\s+days': lambda m: 2,
    r'few\s+days|past\s+few\s+days': lambda m: 3,
    r'workweek|business\s+week|since\s+Monday': lambda m: 5,
    r'week\s+and\s+a\s+half': lambda m: 10,
}

# ========================================
# FUNCTION-CONDITION MAPPINGS
# ========================================

FUNCTION_CONDITION_MAP = {
    'get_steps_data': ['depression', 'anxiety', 'mood_issues'],
    'get_blood_glucose_data': ['stress', 'anxiety', 'depression'],
    'get_oxygen_saturation_data': ['anxiety', 'panic'],
    'get_blood_pressure_data': ['anxiety', 'stress', 'panic'],
    'get_exercise_session_data': ['depression', 'anxiety', 'mood_issues'],
    'get_calories_burned_data': ['depression', 'anxiety', 'stress'],
    'get_distance_data': ['depression', 'anxiety', 'panic'],
    'get_exercise_heart_rate_data': ['anxiety', 'panic', 'stress'],
    'get_power_data': ['depression', 'mood_issues', 'anxiety'],
    'get_speed_data': ['depression', 'anxiety', 'mood_issues'],
    'get_vo2max_data': ['depression', 'anxiety', 'stress'],
    'get_heart_rate_data': ['anxiety', 'panic', 'stress'],
    'get_nutrition_data': ['depression', 'anxiety', 'stress'],
    'get_sleep_data': ['anxiety', 'depression', 'mood_issues'],
    'get_weight_data': ['depression', 'anxiety', 'stress'],
    'get_body_fat_data': ['depression', 'anxiety', 'mood_issues'],
    'get_bmr_data': ['depression', 'anxiety', 'stress'],
    'get_height_data': ['anxiety', 'depression', 'stress'],
    'get_stress_data': ['stress', 'anxiety', 'panic'],
    'get_body_temperature_data': ['anxiety', 'panic', 'stress']
}

# ========================================
# ENHANCED THINKING TEMPLATES WITH FUNCTION REASONING
# ========================================

ENHANCED_THINKING_TEMPLATES = {
    'temporal': [
        # Function + Temporal reasoning
        "The user is dealing with {condition} and wants to track their {data_type} over {time_phrase}. Since they're asking about {data_type}, I need to call {function_name} to get that specific health metric. They mentioned {time_phrase}, which translates to {num_days} days, so I'll retrieve that timeframe to help them see patterns.",
        
        "This person is monitoring their {data_type} for {condition} management. The request is specifically about {data_type} data, so {function_name} is the appropriate function to call. They specified {time_phrase} ({num_days} days), so I'll pull that exact timeframe to give them the information they need.",
        
        "Someone's asking about {data_type} in relation to their {condition}. Since they need {data_type} measurements, I should use {function_name} to retrieve that data. The timeframe they mentioned is {time_phrase}, which equals {num_days} days of data.",
        
        "This appears to be a {data_type} monitoring request for mental health purposes. The user specifically wants {data_type} information, so {function_name} is the correct function to use. They requested data for {time_phrase}, so I need to get {num_days} days worth of measurements.",
        
        "The user is asking for {data_type} data over {time_phrase} - that's {num_days} days. Since they specifically mentioned {data_type}, I need to call {function_name} to get those measurements. This seems related to their {condition}, so this data will help them understand their patterns.",
        
        "I can see they want {data_type} information for a specific period: {time_phrase}. For {data_type} data, I need to use {function_name}. That timeframe works out to {num_days} days, which should give them good insights for managing their {condition}.",
        
        "The patient is requesting {data_type} data for {time_phrase} ({num_days} days) in the context of their {condition}. Since they specifically need {data_type} measurements, {function_name} is the right function to call. I'll retrieve this timeframe to support their health monitoring.",
        
        "This is a {data_type} data request for {condition} management spanning {time_phrase}. The user specifically wants {data_type} information, so I should use {function_name} to get {num_days} days of data to help them track their symptoms and patterns.",
        
        "They're asking about {data_type} as part of their {condition} care plan for {time_phrase}. Since the request is specifically for {data_type} data, {function_name} is the appropriate function. That's {num_days} days - I'll pull that data to help them with their health monitoring.",
        
        "The user wants to understand their {data_type} patterns over {time_phrase} in relation to their {condition}. For {data_type} data specifically, I need to call {function_name}. I'll retrieve {num_days} days of data to give them the insights they're looking for.",
        
        "This person is working on managing their {condition} and needs {data_type} data for {time_phrase}. Since they're asking about {data_type} specifically, {function_name} is the correct function to use. I'll get them {num_days} days of information to support their health journey.",
        
        "Someone's tracking {data_type} in relation to their {condition} over {time_phrase}. The request is specifically about {data_type}, so I should call {function_name} to get those measurements. That timeframe ({num_days} days) will give them the information they need for their health management."
    ],
    
    'non_temporal': [
        # Function + Default temporal reasoning
        "They want to see their {data_type} data but didn't specify exactly when. Since they're asking specifically about {data_type}, I need to call {function_name} to get those measurements. Since this seems to be a general request about their {condition}, I'll default to getting a week's worth of data (7 days) to give them a good overview.",
        
        "This person wants {data_type} information but no specific timeframe was given. The request is for {data_type} data specifically, so {function_name} is the right function to use. I'll get about 7 days of data to show recent patterns related to their {condition}.",
        
        "{data_type} inquiry without exact dates. Since they need {data_type} measurements, I should call {function_name}. A week of data (7 days) should be helpful for seeing current patterns in relation to their {condition} without being overwhelming.",
        
        "The user is asking about their {data_type} - no specific timeframe given. For {data_type} data, I need to use {function_name}. For {condition} tracking, a week of recent data (7 days) is usually a good starting point.",
        
        "No specific time period mentioned, but they want {data_type} data. Since they're asking about {data_type} specifically, {function_name} is the appropriate function. For {data_type} related to {condition}, I'll default to 7 days to show recent patterns without overwhelming them with data.",
        
        "They want {data_type} data but didn't specify how far back. The request is specifically for {data_type}, so I should call {function_name}. A week (7 days) is usually good for seeing recent {condition}-related patterns.",
        
        "This appears to be a general {data_type} request for their {condition}. Since they need {data_type} measurements, {function_name} is the correct function to use. I'll go with 7 days of data - that's enough to show trends without being too much.",
        
        "The patient is requesting {data_type} data for their {condition}. For {data_type} specifically, I need to call {function_name}. Without a specific timeframe, 7 days of recent data will provide a good baseline for assessment.",
        
        "This is a general {data_type} inquiry in the context of {condition}. Since they want {data_type} data, {function_name} is the appropriate function. A week of data gives a good recent snapshot without being overwhelming.",
        
        # CONDITIONAL: Only use when actual non-temporal words are detected
        "They mentioned '{actual_word}' and want {data_type} information for their {condition}. Since they're asking specifically about {data_type}, I need to call {function_name}. I'll go with 7 days of data to show current trends.",
        
        "Since they said '{actual_word}' and need {data_type} data, I should use {function_name} to get those measurements. I'll get about 7 days of {data_type} data to show recent patterns related to their {condition}.",
        
        "They want {data_type} data '{actual_word}' but didn't specify how far back. For {data_type} specifically, {function_name} is the right function to call. A week (7 days) is usually good for seeing recent {condition}-related patterns."
    ]
}

# ========================================
# HELPER FUNCTIONS
# ========================================

def get_random_mh_expression(category: str) -> str:
    """Get a random mental health expression from category"""
    return random.choice(MENTAL_HEALTH_EXPRESSIONS.get(category, [category]))

def get_temporal_expression(days: int) -> str:
    """Get random temporal expression for given days"""
    if days in TEMPORAL_EXPRESSIONS:
        return random.choice(TEMPORAL_EXPRESSIONS[days])
    else:
        # Fallback for custom days
        return f"past {days} days"

def get_non_temporal_expression() -> str:
    """Get random non-temporal expression"""
    return random.choice(NON_TEMPORAL_EXPRESSIONS)

# Add this function to detect actual non-temporal words used
def extract_non_temporal_word(query: str) -> str:
    """Extract actual non-temporal word used in query, or return generic if none found"""
    
    query_lower = query.lower()
    
    # Check for actual non-temporal expressions in the query
    for expression in NON_TEMPORAL_EXPRESSIONS:
        if expression in query_lower:
            return expression
    
    # If no explicit non-temporal word found, return a generic default
    return "without specific timeframe"

def get_data_type(function_name: str) -> str:
    """Extract data type from function name"""
    return function_name.replace('get_', '').replace('_data', '').replace('_', ' ')

def get_relevant_condition(function_name: str) -> str:
    """Get relevant condition for function"""
    conditions = FUNCTION_CONDITION_MAP.get(function_name, ['anxiety'])
    return random.choice(conditions)

def extract_time_info(query: str) -> tuple:
    """Extract time information from natural language query"""
    for pattern, extractor in TIME_PATTERNS.items():
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            days = extractor(match)
            return days, match.group(0)
    return None, None