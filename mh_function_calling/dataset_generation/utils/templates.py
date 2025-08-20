import re
import random
import json

# Time extraction patterns and their corresponding days
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

# Complete templates for ALL 20 functions
DIVERSE_MENTAL_HEALTH_TEMPLATES = {
    'get_steps_data': {
        'temporal': [
            "My depression is making me less active for the past week",
            "I'm tracking daily activity for mood correlation over the last 14 days", 
            "Agoraphobia is limiting my outdoor movement for three weeks",
            "I want to see if activity affects my anxiety for the last 10 days",
            "Social isolation is reducing my step count since last Monday",
            "My therapist wants to monitor my daily functioning over the past fortnight",
            "I'm too depressed to leave the house much for the last month",
            "Seasonal depression is affecting my activity for 21 days",
            "I need motivation to increase daily movement, check past seven days",
            "My ADHD medication affects my energy levels over the last couple of weeks",
            "Anxiety makes it hard to go outside for the past few days",
            "I'm using walking to manage my stress since 5 days ago",
            "My panic disorder limits my outdoor activities for the past 2 weeks",
            "I want to track if movement helps my mood over 7 days",
            "My energy is very low due to depression for the past business week"
        ],
        'non_temporal': [
            "How active have I been lately?",
            "My therapist wants to see my daily activity levels",
            "Can you show me my step count data?",
            "I need my activity information for my appointment",
            "What do my daily steps look like recently?",
            "Been feeling sluggish - what are my activity levels?",
            "Show me how much I've been walking"
        ]
    },
    
    'get_blood_glucose_data': {
        'temporal': [
            "My psychiatric medication affects my blood sugar for the past week",
            "Stress eating is impacting my glucose levels over the last 14 days",
            "I need to monitor diabetes while managing depression for three weeks", 
            "Anxiety medication may be affecting my glucose for 10 days",
            "My mood swings might be related to blood sugar since last Monday",
            "Stress is causing glucose spikes for the past fortnight",
            "I'm checking if mood stabilizers affect my diabetes over the last month",
            "Panic attacks seem related to blood sugar drops for 21 days",
            "My eating disorder is affecting glucose control for the past seven days",
            "I need glucose data for my psychiatrist from the last couple of weeks",
            "Antipsychotics may be causing diabetes risk over the past few days",
            "I want to see if therapy reduces stress-related glucose since 5 days ago",
            "My binge eating episodes correlate with glucose for the past 2 weeks",
            "Depression medications might affect my blood sugar over 7 days",
            "I'm monitoring glucose changes during treatment for the past business week"
        ],
        'non_temporal': [
            "How are my blood sugar levels?",
            "My endocrinologist wants to see my glucose readings",
            "Can you check my blood glucose data?",
            "I need glucose information for my diabetes management",
            "What do my blood sugar patterns look like?",
            "Been feeling shaky - what's my blood sugar like?",
            "Show me my recent glucose measurements"
        ]
    },
    
    'get_oxygen_saturation_data': {
        'temporal': [
            "My panic attacks make me feel like I can't breathe for the past week",
            "I'm having anxiety-related breathing issues over the last 14 days",
            "Hyperventilation during panic needs monitoring for three weeks",
            "I want to check if anxiety affects my oxygen levels for 10 days",
            "My therapist suggested monitoring breathing during anxiety since last Monday",
            "Panic disorder includes feeling short of breath for the past fortnight",
            "I'm practicing breathing exercises for anxiety over the last month",
            "PTSD episodes affect my breathing patterns for 21 days",
            "I need to differentiate panic from actual oxygen issues for the past seven days",
            "My anxiety makes me hyperventilate since the last couple of weeks",
            "Breathing problems during stress for the past few days",
            "I want to track oxygen levels during panic attacks since 5 days ago",
            "My respiratory issues might be anxiety-related for the past 2 weeks",
            "Shortness of breath from panic disorder over 7 days",
            "I'm monitoring breathing patterns for therapy for the past business week"
        ],
        'non_temporal': [
            "How are my oxygen levels?",
            "I've been feeling short of breath lately",
            "Can you check my oxygen saturation?",
            "My breathing feels off - what do the numbers show?",
            "I need oxygen data for my pulmonologist",
            "Been having breathing issues - what's my SpO2?",
            "Show me my oxygen saturation readings"
        ]
    },
    
    'get_blood_pressure_data': {
        'temporal': [
            "My anxiety is causing high blood pressure for the past week",
            "I need to monitor stress impact on my BP over the last 14 days",
            "Panic attacks are affecting my blood pressure for three weeks",
            "My psychiatrist wants to check medication effects on BP for 10 days",
            "Chronic stress is impacting my cardiovascular health since last Monday",
            "I want to see if meditation lowers my blood pressure for the past fortnight",
            "My anxiety medication may be affecting my BP over the last month",
            "Work stress is causing hypertension for 21 days",
            "I need to track if therapy reduces my blood pressure for the past seven days",
            "My panic disorder includes BP spikes since the last couple of weeks",
            "ADHD stimulants might be raising my blood pressure for the past few days",
            "I'm monitoring cardiovascular effects of psychiatric meds since 5 days ago",
            "Stress-related hypertension concerns for the past 2 weeks",
            "My heart rate and BP seem connected to anxiety over 7 days",
            "I want to correlate BP with panic episodes for the past business week"
        ],
        'non_temporal': [
            "How's my blood pressure been?",
            "My cardiologist wants to see my BP readings",
            "Can you check my blood pressure data?",
            "I think my medication is affecting my BP",
            "What do my blood pressure numbers look like?",
            "Been feeling dizzy - what's my blood pressure?",
            "Show me my recent BP measurements"
        ]
    },
    
    'get_exercise_session_data': {
        'temporal': [
            "I'm trying exercise therapy for my depression for the past week",
            "My energy levels are too low to exercise over the last 14 days",
            "I want to track if exercise improves my mood for three weeks",
            "Depression is making it hard to stay active for 10 days",
            "My therapist recommended tracking exercise for anxiety since last Monday",
            "I'm using running to manage my stress for the past fortnight",
            "Lack of motivation is affecting my workouts over the last month",
            "I need to see if exercise helps my ADHD for 21 days",
            "My bipolar energy affects my exercise patterns for the past seven days",
            "I'm too anxious to go to the gym since the last couple of weeks",
            "Exercise is part of my depression treatment plan for the past few days",
            "I'm tracking workout consistency for mood management since 5 days ago",
            "Social anxiety makes group fitness difficult for the past 2 weeks",
            "I want to correlate exercise with sleep quality over 7 days",
            "My medication affects my exercise performance for the past business week"
        ],
        'non_temporal': [
            "How have my workouts been?",
            "My trainer wants to see my exercise data",
            "Can you show me my workout sessions?",
            "I need exercise information for my fitness plan",
            "What do my workout patterns look like?",
            "Been struggling with motivation - how's my exercise?",
            "Show me my recent workout sessions"
        ]
    },
    
    'get_calories_burned_data': {
        'temporal': [
            "I'm tracking calorie burn for eating disorder recovery for the past week",
            "My anxiety affects my metabolism and calorie burn over the last 14 days",
            "I need to monitor energy expenditure for weight management for three weeks",
            "Depression medication affects my metabolism for 10 days",
            "I want to balance calorie burn with my mental health since last Monday",
            "My eating disorder includes obsessing over calories burned for the past fortnight",
            "I'm using calorie data to manage stress eating over the last month",
            "My therapist wants me to track calorie burn patterns for 21 days",
            "Binge eating episodes affect my calorie balance for the past seven days",
            "I need healthy relationship with calorie tracking since the last couple of weeks",
            "My medication side effects include metabolic changes for the past few days",
            "I want to see if therapy affects my calorie burn since 5 days ago",
            "Stress eating patterns need monitoring for the past 2 weeks",
            "My body image issues relate to calorie obsession over 7 days",
            "I'm balancing recovery with healthy calorie awareness for the past business week"
        ],
        'non_temporal': [
            "How many calories have I been burning?",
            "My nutritionist wants to see my calorie data",
            "Can you check my calories burned?",
            "I need calorie information for my meal planning",
            "What do my calorie burn patterns look like?",
            "Been trying to lose weight - how's my calorie burn?",
            "Show me my recent calorie expenditure"
        ]
    },
    
    'get_distance_data': {
        'temporal': [
            "I'm tracking walking distance for depression recovery for the past week",
            "My agoraphobia limits how far I can travel over the last 14 days",
            "I want to see if distance walked correlates with mood for three weeks",
            "Social anxiety affects my willingness to travel for 10 days",
            "I'm gradually increasing distance for exposure therapy since last Monday",
            "My panic disorder limits my travel range for the past fortnight",
            "I'm using distance goals for depression motivation over the last month",
            "PTSD makes me avoid certain routes and distances for 21 days",
            "I want to track progress in overcoming avoidance for the past seven days",
            "My therapist suggested monitoring distance for agoraphobia since the last couple of weeks",
            "Anxiety makes me stay close to home for the past few days",
            "I'm building confidence to travel further since 5 days ago",
            "My safe zones are expanding with therapy for the past 2 weeks",
            "Distance challenges help with exposure therapy over 7 days",
            "I want to measure my mobility progress for the past business week"
        ],
        'non_temporal': [
            "How far have I been walking?",
            "My physical therapist wants to see my distance data",
            "Can you check how much distance I've covered?",
            "I need distance information for my mobility assessment",
            "What do my walking distances look like?",
            "Been trying to walk more - how's my distance?",
            "Show me my recent travel distances"
        ]
    },
    
    'get_exercise_heart_rate_data': {
        'temporal': [
            "I need to differentiate exercise HR from anxiety HR for the past week",
            "My panic attacks include rapid heart rate during exercise over the last 14 days",
            "I want to see if exercise helps with anxiety symptoms for three weeks",
            "My heart rate spikes trigger anxiety during workouts for 10 days",
            "I'm monitoring safe exercise intensity for my anxiety since last Monday",
            "My therapist wants me to track exercise heart rate patterns for the past fortnight",
            "I need to manage exercise-induced anxiety over the last month",
            "My ADHD medication affects my exercise heart rate for 21 days",
            "I want to build confidence in exercise despite anxiety for the past seven days",
            "I'm tracking if regular exercise lowers resting anxiety since the last couple of weeks",
            "Exercise heart rate spikes worry me for the past few days",
            "I want to ensure safe workout intensity since 5 days ago",
            "My cardiac anxiety needs exercise HR monitoring for the past 2 weeks",
            "I'm learning to trust my body during exercise over 7 days",
            "Heart rate training zones for anxiety management for the past business week"
        ],
        'non_temporal': [
            "How's my heart rate during exercise?",
            "My trainer wants to see my workout heart rate",
            "Can you check my exercise HR data?",
            "I need heart rate info for my fitness assessment",
            "What does my exercise heart rate look like?",
            "Been worried about my HR during workouts",
            "Show me my heart rate during exercise"
        ]
    },
    
    'get_power_data': {
        'temporal': [
            "I'm using cycling power data to track depression recovery for the past week",
            "My energy output reflects my mental state over the last 14 days",
            "I want to see if power output correlates with mood for three weeks",
            "Depression affects my physical strength and power for 10 days",
            "I'm tracking power to motivate myself during low periods since last Monday",
            "My bipolar episodes affect my exercise power output for the past fortnight",
            "I need objective measures of my physical capability over the last month",
            "My ADHD medication affects my exercise performance for 21 days",
            "Power data helps me understand my energy cycles for the past seven days",
            "I want to see if therapy improves my physical strength since the last couple of weeks",
            "My medication changes might affect power output for the past few days",
            "I'm using power metrics to track recovery progress since 5 days ago",
            "Low energy from depression affects my cycling power for the past 2 weeks",
            "I want to correlate power with mood episodes over 7 days",
            "My fitness goals need power monitoring for the past business week"
        ],
        'non_temporal': [
            "How's my power output been?",
            "My cycling coach wants to see my power data",
            "Can you check my exercise power?",
            "I need power information for my training plan",
            "What does my power output look like?",
            "Been feeling weak - how's my power?",
            "Show me my recent power measurements"
        ]
    },
    
    'get_speed_data': {
        'temporal': [
            "My depression affects my running pace and speed for the past week",
            "I want to track if speed training helps with anxiety over the last 14 days",
            "My energy levels from medication affect my speed for three weeks",
            "I'm using pace goals to combat depression lethargy for 10 days",
            "My mood episodes affect my exercise performance since last Monday",
            "I want to see speed patterns during different mental states for the past fortnight",
            "ADHD affects my ability to maintain consistent pace over the last month",
            "I'm tracking speed to measure treatment effectiveness for 21 days",
            "My running pace reflects my mental state for the past seven days",
            "I want to see if therapy improves my athletic performance since the last couple of weeks",
            "Medication side effects might affect my running speed for the past few days",
            "I'm using speed goals for motivation since 5 days ago",
            "My anxiety affects my ability to push pace for the past 2 weeks",
            "I want to correlate running speed with mood over 7 days",
            "Speed training helps with confidence building for the past business week"
        ],
        'non_temporal': [
            "How fast have I been running?",
            "My running coach wants to see my speed data",
            "Can you check my pace and speed?",
            "I need speed information for my training",
            "What does my running speed look like?",
            "Been feeling slow - how's my pace?",
            "Show me my recent speed measurements"
        ]
    },
    
    'get_vo2max_data': {
        'temporal': [
            "I want to track cardiovascular health during depression treatment for the past week",
            "My psychiatric medications might affect my VO2 max over the last 14 days",
            "I'm monitoring fitness levels while managing mental health for three weeks",
            "Depression has affected my overall cardiovascular fitness for 10 days",
            "I want to see if mental health treatment improves my VO2 max since last Monday",
            "My anxiety medications may impact my aerobic capacity for the past fortnight",
            "I'm tracking fitness recovery alongside mental health recovery over the last month",
            "My sedentary lifestyle from depression affected my VO2 max for 21 days",
            "I want to measure cardiovascular improvements for the past seven days",
            "My fitness goals include VO2 max monitoring since the last couple of weeks",
            "Medication effects on aerobic capacity concern me for the past few days",
            "I'm tracking cardio fitness during therapy since 5 days ago",
            "My exercise tolerance needs VO2 max assessment for the past 2 weeks",
            "I want to see if activity levels improve my aerobic fitness over 7 days",
            "Cardiovascular health monitoring during treatment for the past business week"
        ],
        'non_temporal': [
            "How's my cardiovascular fitness?",
            "My cardiologist wants to see my VO2 max",
            "Can you check my aerobic capacity?",
            "I need VO2 max data for my fitness assessment",
            "What does my cardiovascular fitness look like?",
            "Been out of shape - how's my VO2 max?",
            "Show me my recent fitness measurements"
        ]
    },
    
    'get_heart_rate_data': {
        'temporal': [
            "I've been having panic attacks and my heart races for the past week",
            "My anxiety is causing heart palpitations over the last 14 days",
            "I need to track stress impact on my heart rate for three weeks",
            "My resting heart rate seems high due to anxiety for 10 days",
            "Panic disorder is affecting my cardiovascular health since last Monday",
            "I want to see if meditation lowers my heart rate for the past fortnight",
            "My therapist suggested monitoring HR during anxiety over the last month",
            "Stress at work is making my heart race for 21 days",
            "I need to differentiate anxiety from heart problems for the past seven days",
            "My panic symptoms include rapid heartbeat since the last couple of weeks",
            "ADHD stimulants are affecting my heart rate for the past few days",
            "I'm tracking heart rate variability for stress management since 5 days ago",
            "My antidepressants might be affecting my heart rate for the past 2 weeks",
            "I want to monitor cardiovascular effects of my medications over 7 days",
            "Heart palpitations from anxiety need monitoring for the past business week"
        ],
        'non_temporal': [
            "How's my heart rate been?",
            "My cardiologist wants to see my heart rate",
            "Can you check my pulse data?",
            "I need heart rate info for my appointment",
            "What does my heart rate look like?",
            "Been feeling palpitations - what's my HR?",
            "Show me my recent heart rate readings"
        ]
    },
    
    'get_nutrition_data': {
        'temporal': [
            "Depression is affecting my eating habits for the past week",
            "I'm tracking nutrition to help manage my mood over the last 14 days",
            "My eating disorder recovery requires meal monitoring for three weeks",
            "Anxiety makes it hard to eat properly for 10 days",
            "I want to see if diet affects my mental health since last Monday",
            "Stress eating is impacting my nutrition for the past fortnight",
            "My therapist suggested tracking emotional eating over the last month",
            "Medication side effects are affecting my appetite for 21 days",
            "I'm using nutrition to support my mental health treatment for the past seven days",
            "Binge eating episodes need to be tracked since the last couple of weeks",
            "My depression makes me forget to eat for the past few days",
            "I want to establish healthy eating patterns since 5 days ago",
            "My anxiety medication affects my appetite for the past 2 weeks",
            "I'm monitoring nutrition for eating disorder recovery over 7 days",
            "Emotional eating patterns need assessment for the past business week"
        ],
        'non_temporal': [
            "How's my nutrition been?",
            "My dietitian wants to see my eating data",
            "Can you check my nutritional intake?",
            "I need nutrition info for my meal planning",
            "What do my eating patterns look like?",
            "Been struggling with eating - how's my nutrition?",
            "Show me my recent dietary data"
        ]
    },
    
    'get_sleep_data': {
        'temporal': [
            "My depression is affecting my sleep for the past week",
            "I'm having anxiety-related insomnia over the last 14 days",
            "My medication is causing sleep issues for three weeks",
            "Panic attacks are waking me up for 10 days",
            "My therapist wants to see my sleep patterns since last Monday",
            "Racing thoughts are keeping me awake for the past fortnight",
            "I'm sleeping too much due to depression over the last month",
            "My bipolar episode is affecting sleep for 21 days",
            "PTSD nightmares are disrupting my sleep for the past seven days",
            "Anxiety meds aren't helping my sleep since the last couple of weeks",
            "I need to track sleep quality for mood management for the past few days",
            "My sleep schedule is completely disrupted since 5 days ago",
            "I want to see if sleep affects my anxiety levels for the past 2 weeks",
            "My antidepressants are causing vivid dreams over 7 days",
            "I'm using sleep data to adjust my medication timing for the past business week"
        ],
        'non_temporal': [
            "How well have I been sleeping?",
            "My sleep specialist wants to see my sleep data",
            "Can you check my sleep patterns?",
            "I need sleep info for my sleep study",
            "What does my sleep quality look like?",
            "Been having trouble sleeping lately",
            "Show me my recent sleep data"
        ]
    },
    
    'get_weight_data': {
        'temporal': [
            "My antidepressant is causing weight gain for the past week",
            "Depression is affecting my appetite and weight over the last 14 days",
            "I'm monitoring weight changes from mood stabilizers for three weeks",
            "Binge eating disorder is impacting my weight for 10 days",
            "Anxiety medication side effects include weight changes since last Monday",
            "My eating disorder recovery needs weight monitoring for the past fortnight",
            "Stress eating is causing weight fluctuations over the last month",
            "I need to track if therapy helps with emotional eating for 21 days",
            "My psychiatrist wants to monitor medication effects for the past seven days",
            "Body dysmorphia makes weight tracking important since the last couple of weeks",
            "I'm gaining weight from psychiatric medications for the past few days",
            "Depression affected my appetite and weight loss since 5 days ago",
            "I want to manage weight while treating mental health for the past 2 weeks",
            "My eating patterns are tied to my mood episodes over 7 days",
            "Weight monitoring during medication adjustment for the past business week"
        ],
        'non_temporal': [
            "How's my weight been?",
            "My doctor wants to see my weight data",
            "Can you check my weight measurements?",
            "I need weight info for my health assessment",
            "What does my weight trend look like?",
            "Been concerned about my weight lately",
            "Show me my recent weight data"
        ]
    },
    
    'get_body_fat_data': {
        'temporal': [
            "My psychiatric medications are affecting body composition for the past week",
            "I want to track body fat changes during treatment over the last 14 days",
            "Depression led to muscle loss and fat gain for three weeks",
            "I'm monitoring body composition for eating disorder recovery for 10 days",
            "My antipsychotics are causing metabolic changes since last Monday",
            "I need body fat data for my treatment team for the past fortnight",
            "Body dysmorphia makes accurate body composition important over the last month",
            "I want to see if exercise therapy improves body composition for 21 days",
            "My metabolism changes might affect body fat for the past seven days",
            "I'm tracking body composition goals since the last couple of weeks",
            "Medication side effects include body fat changes for the past few days",
            "I want to monitor healthy body composition since 5 days ago",
            "My fitness goals include body fat monitoring for the past 2 weeks",
            "I need objective body composition data over 7 days",
            "Body fat tracking during treatment for the past business week"
        ],
        'non_temporal': [
            "How's my body fat percentage?",
            "My trainer wants to see my body composition",
            "Can you check my body fat data?",
            "I need body fat info for my fitness plan",
            "What does my body composition look like?",
            "Been working on body composition",
            "Show me my recent body fat measurements"
        ]
    },
    
    'get_bmr_data': {
        'temporal': [
            "My psychiatric medications might be affecting my metabolism for the past week",
            "I want to track metabolic changes during treatment over the last 14 days",
            "Depression has affected my energy levels and metabolism for three weeks",
            "I need BMR data to understand medication side effects for 10 days",
            "My eating disorder recovery includes metabolic monitoring since last Monday",
            "I want to see if therapy affects my metabolic rate for the past fortnight",
            "Antipsychotics may be slowing my metabolism over the last month",
            "I'm tracking BMR for weight management during treatment for 21 days",
            "My energy levels correlate with metabolic rate for the past seven days",
            "I want to monitor metabolism during medication changes since the last couple of weeks",
            "BMR changes from psychiatric medications for the past few days",
            "I'm tracking metabolic health since 5 days ago",
            "My weight management needs BMR monitoring for the past 2 weeks",
            "I want to see if activity affects my metabolism over 7 days",
            "Metabolic rate tracking during treatment for the past business week"
        ],
        'non_temporal': [
            "How's my metabolism been?",
            "My nutritionist wants to see my BMR",
            "Can you check my metabolic rate?",
            "I need BMR info for my diet plan",
            "What does my metabolism look like?",
            "Been concerned about my metabolic rate",
            "Show me my recent BMR data"
        ]
    },
    
    'get_height_data': {
        'temporal': [
            "I need accurate height for BMI calculation during treatment for the past week",
            "My eating disorder recovery includes growth monitoring over the last 14 days",
            "I want consistent height measurements for health tracking for three weeks",
            "My treatment team needs accurate body measurements for 10 days",
            "I'm tracking physical health alongside mental health since last Monday",
            "Height data is needed for medication dosing calculations for the past fortnight",
            "My growth patterns need monitoring during recovery over the last month",
            "I want to ensure accurate height measurements for 21 days",
            "My medical team requires precise height data for the past seven days",
            "I'm monitoring physical development since the last couple of weeks",
            "Height measurements for health assessments for the past few days",
            "I need consistent height tracking since 5 days ago",
            "My treatment requires accurate height data for the past 2 weeks",
            "I want to monitor physical health metrics over 7 days",
            "Height tracking for medical calculations for the past business week"
        ],
        'non_temporal': [
            "What's my current height?",
            "My doctor needs my height measurement",
            "Can you check my height data?",
            "I need height info for my health records",
            "What does my height measurement show?",
            "Need my height for medical calculations",
            "Show me my height data"
        ]
    },
    
    'get_stress_data': {
        'temporal': [
            "My stress levels have been overwhelming for the past week",
            "I need to track stress patterns for anxiety management over the last 14 days",
            "Work stress is affecting my mental health for three weeks",
            "I want to see if therapy reduces my stress levels for 10 days",
            "My panic attacks correlate with high stress since last Monday",
            "I'm monitoring stress to adjust my coping strategies for the past fortnight",
            "Chronic stress is impacting my depression over the last month",
            "My therapist wants to see my stress data for 21 days",
            "I need to identify stress triggers for the past seven days",
            "My medication changes might affect stress levels since the last couple of weeks",
            "I'm tracking daily stress for PTSD management for the past few days",
            "Workplace stress is worsening my anxiety since 5 days ago",
            "I want to correlate stress with sleep quality for the past 2 weeks",
            "My stress eating patterns need monitoring over 7 days",
            "I'm using mindfulness to manage stress for the past business week"
        ],
        'non_temporal': [
            "How stressed have I been lately?",
            "My therapist wants to see my stress levels",
            "Can you check my stress data?",
            "I need stress info for my mental health assessment",
            "What do my stress patterns look like?",
            "Been feeling overwhelmed - what's my stress like?",
            "Show me my recent stress measurements"
        ]
    },
    
    'get_body_temperature_data': {
        'temporal': [
            "My anxiety is causing temperature fluctuations for the past week",
            "I'm having hot flashes from psychiatric medication over the last 14 days",
            "Panic attacks include feeling feverish for three weeks",
            "My body temperature seems irregular due to stress for 10 days",
            "I need to monitor temperature changes with mood episodes since last Monday",
            "My antidepressants might be affecting my body temperature for the past fortnight",
            "I'm tracking temperature for medication side effect monitoring over the last month",
            "Anxiety makes me feel hot and cold for 21 days",
            "My bipolar episodes include temperature regulation issues for the past seven days",
            "I want to see if stress affects my body temperature since the last couple of weeks",
            "My panic disorder includes feeling overheated for the past few days",
            "I'm monitoring temperature changes during anxiety attacks since 5 days ago",
            "My psychiatric medications cause night sweats for the past 2 weeks",
            "I need temperature data for my treatment team over 7 days",
            "My mood stabilizers might be affecting temperature regulation for the past business week"
        ],
        'non_temporal': [
            "How's my body temperature been?",
            "My doctor wants to see my temperature readings",
            "Can you check my body temperature data?",
            "I need temperature info for my health assessment",
            "What do my temperature patterns look like?",
            "Been feeling feverish - what's my temperature?",
            "Show me my recent temperature data"
        ]
    }
}

# Proper thinking templates that align with query type
ALIGNED_THINKING_TEMPLATES = {
    'temporal': [
        "This person is asking about {data_type} over a specific time period. They mentioned '{time_phrase}', so I'll get their {data_type} data for {num_days} days to help them see the patterns during that timeframe.",
        
        "The user wants to track {data_type} for a defined period. Based on their request for '{time_phrase}', I'll retrieve {num_days} days of {data_type} data to give them the information they need.",
        
        "This appears to be {data_type} monitoring for a specific duration. They specified '{time_phrase}', so I need to get their {data_type} measurements for {num_days} days.",
        
        "Someone's tracking their {data_type} over '{time_phrase}'. I'll retrieve {num_days} days of {data_type} data to help them understand their patterns during that specific period."
    ],
    
    'non_temporal': [
        "They want to see their {data_type} data but didn't specify exactly when. Since they mentioned 'lately' or 'recently', I'll default to getting a week's worth of data to give them a good overview of their recent {data_type} patterns.",
        
        "This person wants {data_type} information but no specific timeframe was given. I'll get about 7 days of {data_type} data to show recent patterns.",
        
        "{data_type} inquiry without exact dates. A week of data should be helpful for seeing current {data_type} patterns without being overwhelming."
    ]
}

def extract_time_info(query: str) -> tuple:
    """Extract time information from natural language query"""
    for pattern, extractor in TIME_PATTERNS.items():
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            days = extractor(match)
            return days, match.group(0)
    return None, None

def generate_sample(function_name: str, template_type: str) -> dict:
    """Generate a single sample with proper thinking alignment"""
    
    if function_name not in DIVERSE_MENTAL_HEALTH_TEMPLATES:
        return None
    
    templates = DIVERSE_MENTAL_HEALTH_TEMPLATES[function_name][template_type]
    query = random.choice(templates)
    
    data_type = function_name.replace('get_', '').replace('_data', '').replace('_', ' ')
    
    if template_type == 'temporal':
        days, time_phrase = extract_time_info(query)
        if days is None:
            days, time_phrase = 7, "the specified period"
        
        thinking_template = random.choice(ALIGNED_THINKING_TEMPLATES['temporal'])
        thinking = thinking_template.format(
            data_type=data_type,
            time_phrase=time_phrase,
            num_days=days
        )
    else:
        days = 7  # Default for non-temporal
        thinking_template = random.choice(ALIGNED_THINKING_TEMPLATES['non_temporal'])
        thinking = thinking_template.format(data_type=data_type)
    
    # Generate patient ID
    patient_formats = ["UID_{}", "P{:03d}", "USER_{}", "ID_{:04d}", "PATIENT_{}"]
    patient_id = random.choice(patient_formats).format(random.randint(100, 9999))
    
    # Create function call
    function_call = {
        "name": function_name,
        "parameters": {
            "patient_id": patient_id,
            "num_days": days
        }
    }
    
    response = f"<think>\n{thinking}\n</think>\n\n<function>\n{json.dumps(function_call, indent=2)}\n</function>"
    
    return {
        'patient_query': query,
        'assistant_response': response,
        'function_name': function_name,
        'patient_id': patient_id,
        'num_days': days,
        'has_temporal': template_type == 'temporal'
    }

def generate_complete_dataset():
    """Generate complete dataset: 15 temporal + 7 non-temporal for each of 20 functions"""
    
    all_functions = list(DIVERSE_MENTAL_HEALTH_TEMPLATES.keys())
    dataset = []
    
    print("Generating dataset for all 20 functions...")
    print("Each function: 15 temporal + 7 non-temporal = 22 samples")
    print("Total: 440 samples")
    print()
    
    for function_name in all_functions:
        function_samples = []
        
        # Generate 15 temporal samples
        for i in range(15):
            sample = generate_sample(function_name, 'temporal')
            if sample:
                function_samples.append(sample)
        
        # Generate 7 non-temporal samples  
        for i in range(7):
            sample = generate_sample(function_name, 'non_temporal')
            if sample:
                function_samples.append(sample)
        
        # Count distribution
        temporal_count = sum(1 for s in function_samples if s['has_temporal'])
        non_temporal_count = len(function_samples) - temporal_count
        
        print(f"{function_name}: {temporal_count} temporal, {non_temporal_count} non-temporal")
        
        dataset.extend(function_samples)
    
    # Shuffle to mix functions
    random.shuffle(dataset)
    
    # Final statistics
    total_temporal = sum(1 for sample in dataset if sample['has_temporal'])
    total_non_temporal = len(dataset) - total_temporal
    
    print(f"\nFinal Dataset Statistics:")
    print(f"Total samples: {len(dataset)}")
    print(f"Temporal queries: {total_temporal} ({total_temporal/len(dataset)*100:.1f}%)")
    print(f"Non-temporal queries: {total_non_temporal} ({total_non_temporal/len(dataset)*100:.1f}%)")
    
    return dataset

if __name__ == "__main__":
    dataset = generate_complete_dataset()
    
    # Save to CSV
    import pandas as pd
    df = pd.DataFrame(dataset)
    df.to_csv('/home/jovyan/Works/MSc_Thesis/dataset/mh_function_calling_dataset_v3.csv', index=False)
    print("\n✅ Dataset saved to mh_function_calling_dataset_v3.csv")