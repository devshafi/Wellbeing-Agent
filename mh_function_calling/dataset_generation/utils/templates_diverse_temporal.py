import random

# Enhanced templates with mixed temporal (70%) and non-temporal (30%) queries
ENHANCED_MENTAL_HEALTH_TEMPLATES = {
    'get_steps_data': [
        # Temporal queries (70%)
        "My depression is making me less active for the past {num_days} days",
        "I'm tracking daily activity for mood correlation over {num_days} days",
        "Agoraphobia is limiting my outdoor movement for {num_days} days",
        "Social isolation is reducing my step count for {num_days} days",
        "I'm too depressed to leave the house much for the past {num_days} days",
        "Seasonal depression is affecting my activity for {num_days} days",
        "My ADHD medication affects my energy levels, show me {num_days} days data",
        "Anxiety makes it hard to go outside for the past {num_days} days",
        "I'm using walking to manage my stress, track {num_days} days",
        "My panic disorder limits my outdoor activities for {num_days} days",
        
        # Non-temporal queries (30%)
        "How active have I been lately?",
        "My therapist wants to see my daily activity",
        "Can you show me my step count?",
        "I need my activity data for my appointment",
        "What do my daily steps look like recently?",
        "Been feeling sluggish - what are my activity levels?",
        "Show me how much I've been walking",
        "My doctor asked for my movement data",
        "I want to see if I'm getting enough activity",
        "Could you check my daily step count?"
    ],
    
    'get_blood_glucose_data': [
        # Temporal queries
        "My psychiatric medication affects my blood sugar for {num_days} days",
        "Stress eating is impacting my glucose levels for the past {num_days} days",
        "I need to monitor diabetes while managing depression for {num_days} days",
        "Anxiety medication may be affecting my glucose for {num_days} days",
        "My mood swings might be related to blood sugar for {num_days} days",
        "Stress is causing glucose spikes for the past {num_days} days",
        "I'm checking if mood stabilizers affect my diabetes for {num_days} days",
        "Panic attacks seem related to blood sugar drops over {num_days} days",
        
        # Non-temporal queries
        "How are my blood sugar levels?",
        "My doctor wants to see my glucose readings",
        "Can you check my blood sugar data?",
        "I need glucose information for my diabetes management",
        "What do my blood sugar patterns look like?",
        "My endocrinologist requested glucose data",
        "Been feeling shaky - what's my blood sugar like?",
        "Show me my recent glucose measurements",
        "I think my medication is affecting my blood sugar",
        "Could you pull my glucose readings?"
    ],
    
    'get_oxygen_saturation_data': [
        # Temporal queries
        "My panic attacks make me feel like I can't breathe for {num_days} days",
        "I'm having anxiety-related breathing issues for the past {num_days} days",
        "Hyperventilation during panic needs monitoring for {num_days} days",
        "I want to check if anxiety affects my oxygen levels over {num_days} days",
        "My therapist suggested monitoring breathing during anxiety for {num_days} days",
        "Panic disorder includes feeling short of breath for {num_days} days",
        "I'm practicing breathing exercises for anxiety, track {num_days} days",
        
        # Non-temporal queries
        "How are my oxygen levels?",
        "I've been feeling short of breath lately",
        "Can you check my oxygen saturation?",
        "My breathing feels off - what do the numbers show?",
        "I need oxygen data for my pulmonologist",
        "Been having breathing issues - what's my SpO2?",
        "Show me my oxygen saturation readings",
        "My anxiety is affecting my breathing",
        "Could you check my blood oxygen levels?",
        "What do my oxygen measurements look like?"
    ],
    
    'get_blood_pressure_data': [
        # Temporal queries
        "My anxiety is causing high blood pressure for {num_days} days",
        "I need to monitor stress impact on my BP for {num_days} days",
        "Panic attacks are affecting my blood pressure for the past {num_days} days",
        "My psychiatrist wants to check medication effects on BP for {num_days} days",
        "Chronic stress is impacting my cardiovascular health for {num_days} days",
        "I want to see if meditation lowers my blood pressure over {num_days} days",
        "Work stress is causing hypertension for the past {num_days} days",
        "ADHD stimulants might be raising my blood pressure for {num_days} days",
        
        # Non-temporal queries
        "How's my blood pressure been?",
        "My cardiologist wants to see my BP readings",
        "Can you check my blood pressure data?",
        "I think my medication is affecting my BP",
        "What do my blood pressure numbers look like?",
        "Been feeling dizzy - what's my blood pressure?",
        "Show me my recent BP measurements",
        "My anxiety might be raising my blood pressure",
        "Could you pull my blood pressure readings?",
        "I need BP data for my doctor visit"
    ],
    
    'get_exercise_session_data': [
        # Temporal queries
        "I'm trying exercise therapy for my depression for {num_days} days",
        "My energy levels are too low to exercise for the past {num_days} days",
        "I want to track if exercise improves my mood over {num_days} days",
        "Depression is making it hard to stay active for {num_days} days",
        "My therapist recommended tracking exercise for anxiety for {num_days} days",
        "I'm using running to manage my stress for the past {num_days} days",
        "Lack of motivation is affecting my workouts for {num_days} days",
        "I need to see if exercise helps my ADHD over {num_days} days",
        
        # Non-temporal queries
        "How have my workouts been?",
        "My trainer wants to see my exercise data",
        "Can you show me my workout sessions?",
        "I need exercise information for my fitness plan",
        "What do my workout patterns look like?",
        "Been struggling with motivation - how's my exercise?",
        "Show me my recent workout sessions",
        "My therapist asked about my exercise routine",
        "Could you check my fitness activity?",
        "I want to see my exercise consistency"
    ],
    
    'get_calories_burned_data': [
        # Temporal queries
        "I'm tracking calorie burn for eating disorder recovery for {num_days} days",
        "My anxiety affects my metabolism and calorie burn for {num_days} days",
        "I need to monitor energy expenditure for weight management over {num_days} days",
        "Depression medication affects my metabolism for the past {num_days} days",
        "I want to balance calorie burn with my mental health for {num_days} days",
        "My eating disorder includes obsessing over calories burned for {num_days} days",
        
        # Non-temporal queries
        "How many calories have I been burning?",
        "My nutritionist wants to see my calorie data",
        "Can you check my calories burned?",
        "I need calorie information for my meal planning",
        "What do my calorie burn patterns look like?",
        "Been trying to lose weight - how's my calorie burn?",
        "Show me my recent calorie expenditure",
        "My dietitian asked for my calorie data",
        "Could you pull my calories burned?",
        "I want to see my energy expenditure"
    ],
    
    'get_distance_data': [
        # Temporal queries
        "I'm tracking walking distance for depression recovery for {num_days} days",
        "My agoraphobia limits how far I can travel for the past {num_days} days",
        "I want to see if distance walked correlates with mood over {num_days} days",
        "Social anxiety affects my willingness to travel for {num_days} days",
        "I'm gradually increasing distance for exposure therapy for {num_days} days",
        "My panic disorder limits my travel range for the past {num_days} days",
        
        # Non-temporal queries
        "How far have I been walking?",
        "My physical therapist wants to see my distance data",
        "Can you check how much distance I've covered?",
        "I need distance information for my mobility assessment",
        "What do my walking distances look like?",
        "Been trying to walk more - how's my distance?",
        "Show me my recent travel distances",
        "My trainer asked about my walking distance",
        "Could you check my movement distance?",
        "I want to see how far I've been going"
    ],
    
    'get_exercise_heart_rate_data': [
        # Temporal queries
        "I need to differentiate exercise HR from anxiety HR for {num_days} days",
        "My panic attacks include rapid heart rate during exercise for {num_days} days",
        "I want to see if exercise helps with anxiety symptoms over {num_days} days",
        "My heart rate spikes trigger anxiety during workouts for {num_days} days",
        "I'm monitoring safe exercise intensity for my anxiety for {num_days} days",
        "My therapist wants me to track exercise heart rate patterns for {num_days} days",
        
        # Non-temporal queries
        "How's my heart rate during exercise?",
        "My trainer wants to see my workout heart rate",
        "Can you check my exercise HR data?",
        "I need heart rate info for my fitness assessment",
        "What does my exercise heart rate look like?",
        "Been worried about my HR during workouts",
        "Show me my heart rate during exercise",
        "My cardiologist asked for exercise HR data",
        "Could you check my workout heart rate?",
        "I want to see my exercise cardiac data"
    ],
    
    'get_power_data': [
        # Temporal queries
        "I'm using cycling power data to track depression recovery for {num_days} days",
        "My energy output reflects my mental state for the past {num_days} days",
        "I want to see if power output correlates with mood over {num_days} days",
        "Depression affects my physical strength and power for {num_days} days",
        "I'm tracking power to motivate myself during low periods for {num_days} days",
        "My bipolar episodes affect my exercise power output for {num_days} days",
        
        # Non-temporal queries
        "How's my power output been?",
        "My cycling coach wants to see my power data",
        "Can you check my exercise power?",
        "I need power information for my training plan",
        "What does my power output look like?",
        "Been feeling weak - how's my power?",
        "Show me my recent power measurements",
        "My trainer asked about my power output",
        "Could you check my cycling power?",
        "I want to see my exercise power data"
    ],
    
    'get_speed_data': [
        # Temporal queries
        "My depression affects my running pace and speed for {num_days} days",
        "I want to track if speed training helps with anxiety for {num_days} days",
        "My energy levels from medication affect my speed for the past {num_days} days",
        "I'm using pace goals to combat depression lethargy for {num_days} days",
        "My mood episodes affect my exercise performance for {num_days} days",
        "ADHD affects my ability to maintain consistent pace for {num_days} days",
        
        # Non-temporal queries
        "How fast have I been running?",
        "My running coach wants to see my speed data",
        "Can you check my pace and speed?",
        "I need speed information for my training",
        "What does my running speed look like?",
        "Been feeling slow - how's my pace?",
        "Show me my recent speed measurements",
        "My trainer asked about my running speed",
        "Could you check my exercise pace?",
        "I want to see my speed data"
    ],
    
    'get_vo2max_data': [
        # Temporal queries
        "I want to track cardiovascular health during depression treatment for {num_days} days",
        "My psychiatric medications might affect my VO2 max for {num_days} days",
        "I'm monitoring fitness levels while managing mental health for {num_days} days",
        "Depression has affected my overall cardiovascular fitness for {num_days} days",
        "I want to see if mental health treatment improves my VO2 max over {num_days} days",
        "My anxiety medications may impact my aerobic capacity for {num_days} days",
        
        # Non-temporal queries
        "How's my cardiovascular fitness?",
        "My cardiologist wants to see my VO2 max",
        "Can you check my aerobic capacity?",
        "I need VO2 max data for my fitness assessment",
        "What does my cardiovascular fitness look like?",
        "Been out of shape - how's my VO2 max?",
        "Show me my recent fitness measurements",
        "My doctor asked about my aerobic capacity",
        "Could you check my VO2 max?",
        "I want to see my cardiovascular data"
    ],
    
    'get_heart_rate_data': [
        # Temporal queries
        "I've been having panic attacks and my heart races for {num_days} days",
        "My anxiety is causing heart palpitations for the past {num_days} days",
        "I need to track stress impact on my heart rate for {num_days} days",
        "My resting heart rate seems high due to anxiety for {num_days} days",
        "Panic disorder is affecting my cardiovascular health for {num_days} days",
        "I want to see if meditation lowers my heart rate over {num_days} days",
        "Stress at work is making my heart race for the past {num_days} days",
        "ADHD stimulants are affecting my heart rate for {num_days} days",
        
        # Non-temporal queries
        "How's my heart rate been?",
        "My cardiologist wants to see my heart rate",
        "Can you check my pulse data?",
        "I need heart rate info for my appointment",
        "What does my heart rate look like?",
        "Been feeling palpitations - what's my HR?",
        "Show me my recent heart rate readings",
        "My anxiety is making my heart race",
        "Could you check my cardiac data?",
        "I want to see my heart rate patterns"
    ],
    
    'get_nutrition_data': [
        # Temporal queries
        "Depression is affecting my eating habits for {num_days} days",
        "I'm tracking nutrition to help manage my mood for {num_days} days",
        "My eating disorder recovery requires meal monitoring for {num_days} days",
        "Anxiety makes it hard to eat properly for the past {num_days} days",
        "I want to see if diet affects my mental health over {num_days} days",
        "Stress eating is impacting my nutrition for {num_days} days",
        "My therapist suggested tracking emotional eating for {num_days} days",
        "Medication side effects are affecting my appetite for {num_days} days",
        
        # Non-temporal queries
        "How's my nutrition been?",
        "My dietitian wants to see my eating data",
        "Can you check my nutritional intake?",
        "I need nutrition info for my meal planning",
        "What do my eating patterns look like?",
        "Been struggling with eating - how's my nutrition?",
        "Show me my recent dietary data",
        "My therapist asked about my eating habits",
        "Could you check my nutritional data?",
        "I want to see my diet information"
    ],
    
    'get_sleep_data': [
        # Temporal queries
        "My depression is affecting my sleep for {num_days} days",
        "I'm having anxiety-related insomnia for the past {num_days} days",
        "My medication is causing sleep issues for {num_days} days",
        "Panic attacks are waking me up for {num_days} days",
        "Racing thoughts are keeping me awake for the past {num_days} days",
        "I'm sleeping too much due to depression for {num_days} days",
        "My bipolar episode is affecting sleep for {num_days} days",
        "PTSD nightmares are disrupting my sleep for {num_days} days",
        
        # Non-temporal queries
        "How well have I been sleeping?",
        "My sleep specialist wants to see my sleep data",
        "Can you check my sleep patterns?",
        "I need sleep info for my sleep study",
        "What does my sleep quality look like?",
        "Been having trouble sleeping lately",
        "Show me my recent sleep data",
        "My therapist asked about my sleep",
        "Could you check my sleep metrics?",
        "I want to see my sleep information"
    ],
    
    'get_weight_data': [
        # Temporal queries
        "My antidepressant is causing weight gain for {num_days} days",
        "Depression is affecting my appetite and weight for the past {num_days} days",
        "I'm monitoring weight changes from mood stabilizers for {num_days} days",
        "Binge eating disorder is impacting my weight for {num_days} days",
        "Anxiety medication side effects include weight changes for {num_days} days",
        "My eating disorder recovery needs weight monitoring for {num_days} days",
        "Stress eating is causing weight fluctuations for the past {num_days} days",
        
        # Non-temporal queries
        "How's my weight been?",
        "My doctor wants to see my weight data",
        "Can you check my weight measurements?",
        "I need weight info for my health assessment",
        "What does my weight trend look like?",
        "Been concerned about my weight lately",
        "Show me my recent weight data",
        "My nutritionist asked about my weight",
        "Could you check my weight readings?",
        "I want to see my weight information"
    ],
    
    'get_body_fat_data': [
        # Temporal queries
        "My psychiatric medications are affecting body composition for {num_days} days",
        "I want to track body fat changes during treatment for {num_days} days",
        "Depression led to muscle loss and fat gain for the past {num_days} days",
        "I'm monitoring body composition for eating disorder recovery for {num_days} days",
        "My antipsychotics are causing metabolic changes for {num_days} days",
        
        # Non-temporal queries
        "How's my body fat percentage?",
        "My trainer wants to see my body composition",
        "Can you check my body fat data?",
        "I need body fat info for my fitness plan",
        "What does my body composition look like?",
        "Been working on body composition",
        "Show me my recent body fat measurements",
        "My nutritionist asked about body fat",
        "Could you check my body composition?",
        "I want to see my body fat data"
    ],
    
    'get_bmr_data': [
        # Temporal queries
        "My psychiatric medications might be affecting my metabolism for {num_days} days",
        "I want to track metabolic changes during treatment for {num_days} days",
        "Depression has affected my energy levels and metabolism for {num_days} days",
        "I need BMR data to understand medication side effects for {num_days} days",
        "My eating disorder recovery includes metabolic monitoring for {num_days} days",
        
        # Non-temporal queries
        "How's my metabolism been?",
        "My nutritionist wants to see my BMR",
        "Can you check my metabolic rate?",
        "I need BMR info for my diet plan",
        "What does my metabolism look like?",
        "Been concerned about my metabolic rate",
        "Show me my recent BMR data",
        "My doctor asked about my metabolism",
        "Could you check my basal metabolic rate?",
        "I want to see my metabolic information"
    ],
    
    'get_height_data': [
        # Temporal queries
        "I need accurate height for BMI calculation during treatment for {num_days} days",
        "My eating disorder recovery includes growth monitoring for {num_days} days",
        "I want consistent height measurements for health tracking over {num_days} days",
        "My treatment team needs accurate body measurements for {num_days} days",
        
        # Non-temporal queries
        "What's my current height?",
        "My doctor needs my height measurement",
        "Can you check my height data?",
        "I need height info for my health records",
        "What does my height measurement show?",
        "Need my height for medical calculations",
        "Show me my height data",
        "My physician asked for my height",
        "Could you check my height measurement?",
        "I want to see my height information"
    ],
    
    'get_stress_data': [
        # Temporal queries
        "My stress levels have been overwhelming for {num_days} days",
        "I need to track stress patterns for anxiety management over {num_days} days",
        "Work stress is affecting my mental health for the past {num_days} days",
        "I want to see if therapy reduces my stress levels over {num_days} days",
        "My panic attacks correlate with high stress for {num_days} days",
        "I'm monitoring stress to adjust my coping strategies for {num_days} days",
        "Chronic stress is impacting my depression for the past {num_days} days",
        "Workplace stress is worsening my anxiety for {num_days} days",
        
        # Non-temporal queries
        "How stressed have I been lately?",
        "My therapist wants to see my stress levels",
        "Can you check my stress data?",
        "I need stress info for my mental health assessment",
        "What do my stress patterns look like?",
        "Been feeling overwhelmed - what's my stress like?",
        "Show me my recent stress measurements",
        "My doctor asked about my stress levels",
        "Could you check my stress readings?",
        "I want to see my stress information"
    ],
    
    'get_body_temperature_data': [
        # Temporal queries
        "My anxiety is causing temperature fluctuations for {num_days} days",
        "I'm having hot flashes from psychiatric medication for {num_days} days",
        "Panic attacks include feeling feverish for the past {num_days} days",
        "My body temperature seems irregular due to stress for {num_days} days",
        "I need to monitor temperature changes with mood episodes over {num_days} days",
        "My antidepressants might be affecting my body temperature for {num_days} days",
        
        # Non-temporal queries
        "How's my body temperature been?",
        "My doctor wants to see my temperature readings",
        "Can you check my body temperature data?",
        "I need temperature info for my health assessment",
        "What do my temperature patterns look like?",
        "Been feeling feverish - what's my temperature?",
        "Show me my recent temperature data",
        "My physician asked about my body temperature",
        "Could you check my temperature readings?",
        "I want to see my temperature information"
    ]
}

# Humanized thinking templates for all functions
HUMANIZED_THINKING_TEMPLATES = {
    'get_steps_data': [
        "This person is asking about their activity levels, probably related to their mental health journey. They mentioned {num_days} days, so I'll get their step data for that period to help them track their movement patterns.",
        
        "Sounds like someone's dealing with depression or anxiety affecting their activity. They gave me a specific timeframe, so I'll pull their step data to help them see their activity patterns.",
        
        "Activity tracking is really important for mental health. The user specified a number of days, so I'll get their step data for that period.",
        
        # Non-temporal thinking
        "They want to see their activity data but didn't specify exactly when. Since they mentioned 'lately', I'll get about a week of step data to show their recent activity patterns."
    ],
    
    'get_blood_glucose_data': [
        "This person seems concerned about their blood sugar, possibly related to medication effects or stress. They mentioned {num_days} days, so I'll get their glucose data for that period.",
        
        "Blood sugar monitoring is crucial, especially when dealing with mental health medications. I'll retrieve their glucose data for the specified timeframe.",
        
        "Looks like they're tracking blood sugar in relation to their mental health treatment. I'll get their glucose readings for the days they mentioned.",
        
        # Non-temporal thinking
        "They need glucose data but didn't specify when exactly. I'll default to a week of data to give them a good overview of recent blood sugar patterns."
    ],
    
    'get_oxygen_saturation_data': [
        "This person is having breathing concerns, likely related to anxiety or panic. They specified {num_days} days, so I'll get their oxygen saturation data for that period.",
        
        "Breathing issues and anxiety often go together. I'll retrieve their SpO2 data for the timeframe they mentioned to help them understand their patterns.",
        
        "Sounds like panic or anxiety affecting their breathing. I'll get their oxygen saturation measurements for the specified days.",
        
        # Non-temporal thinking
        "They're concerned about their breathing but didn't give specific dates. I'll get about a week of oxygen saturation data to show recent patterns."
    ],
    
    'get_blood_pressure_data': [
        "This person is worried about their blood pressure, probably stress or medication related. They mentioned {num_days} days, so I'll get their BP data for that period.",
        
        "Blood pressure and mental health are closely connected. I'll retrieve their BP readings for the timeframe they specified.",
        
        "Sounds like anxiety or stress affecting their blood pressure. I'll get their cardiovascular data for the days they mentioned.",
        
        # Non-temporal thinking
        "They want BP data but didn't specify when. I'll get about a week of blood pressure readings to show recent patterns."
    ],
    
    'get_exercise_session_data': [
        "This person is tracking exercise as part of their mental health management. They specified {num_days} days, so I'll get their workout data for that period.",
        
        "Exercise therapy is great for mental health. I'll retrieve their exercise session data for the timeframe they mentioned.",
        
        "Sounds like they're using exercise to help with depression or anxiety. I'll get their workout information for the specified days.",
        
        # Non-temporal thinking
        "They want to see their exercise data but didn't specify when. I'll get about a week of workout sessions to show recent activity."
    ],
    
    'get_calories_burned_data': [
        "This person is monitoring calorie burn, possibly for eating disorder recovery or weight management. They mentioned {num_days} days, so I'll get their calorie data.",
        
        "Calorie tracking can be part of healthy mental health management. I'll retrieve their calories burned for the specified timeframe.",
        
        "Sounds like they're balancing physical and mental health goals. I'll get their calorie burn data for the days they mentioned.",
        
        # Non-temporal thinking
        "They want calorie data but didn't specify when exactly. I'll get about a week of calorie burn information to show recent patterns."
    ],
    
    'get_distance_data': [
        "This person is tracking their movement distance, likely for exposure therapy or depression recovery. They specified {num_days} days, so I'll get their distance data.",
        
        "Distance tracking can help with agoraphobia or depression treatment. I'll retrieve their travel distance for the timeframe they mentioned.",
        
        "Sounds like they're working on mobility goals for their mental health. I'll get their distance information for the specified days.",
        
        # Non-temporal thinking
        "They want distance data but didn't give specific dates. I'll get about a week of distance measurements to show recent movement patterns."
    ],
    
    'get_exercise_heart_rate_data': [
        "This person wants to understand their heart rate during exercise, probably to differentiate from anxiety symptoms. They mentioned {num_days} days, so I'll get their exercise HR data.",
        
        "Exercise heart rate monitoring is important when dealing with anxiety or panic. I'll retrieve their workout HR data for the specified timeframe.",
        
        "Sounds like they're concerned about heart rate during exercise. I'll get their exercise cardiac data for the days they mentioned.",
        
        # Non-temporal thinking
        "They want exercise heart rate data but didn't specify when. I'll get about a week of workout HR information to show patterns."
    ],
    
    'get_power_data': [
        "This person is tracking exercise power output, possibly to monitor their physical strength during mental health treatment. They specified {num_days} days.",
        
        "Power output can reflect energy levels and mood. I'll retrieve their exercise power data for the timeframe they mentioned.",
        
        "Sounds like they're using power metrics to track their recovery. I'll get their power output for the specified days.",
        
        # Non-temporal thinking
        "They want power data but didn't specify when exactly. I'll get about a week of power measurements to show recent performance."
    ],
    
    'get_speed_data': [
        "This person is monitoring their exercise speed, likely to track how their mental state affects performance. They mentioned {num_days} days.",
        
        "Speed and pace can be affected by depression or medication. I'll retrieve their speed data for the specified timeframe.",
        
        "Sounds like they're tracking pace as part of their mental health journey. I'll get their speed information for the days they mentioned.",
        
        # Non-temporal thinking
        "They want speed data but didn't give specific dates. I'll get about a week of pace measurements to show recent patterns."
    ],
    
    'get_vo2max_data': [
        "This person wants to monitor their cardiovascular fitness during mental health treatment. They specified {num_days} days, so I'll get their VO2 max data.",
        
        "VO2 max can be affected by medications and mental health. I'll retrieve their aerobic capacity data for the timeframe they mentioned.",
        
        "Sounds like they're tracking fitness alongside mental health recovery. I'll get their VO2 max measurements for the specified days.",
        
        # Non-temporal thinking
        "They want VO2 max data but didn't specify when. I'll get about a week of cardiovascular fitness measurements."
    ],
    
    'get_heart_rate_data': [
        "This person is concerned about their heart rate, probably anxiety or panic related. They mentioned {num_days} days, so I'll get their HR data for that period.",
        
        "Heart rate issues often come with anxiety disorders. I'll retrieve their cardiac data for the timeframe they specified.",
        
        "Sounds like palpitations or racing heart from stress. I'll get their heart rate measurements for the days they mentioned.",
        
        # Non-temporal thinking
        "They're worried about their heart rate but didn't specify when exactly. I'll get about a week of HR data to show recent patterns."
    ],
    
    'get_nutrition_data': [
        "This person is tracking their eating habits, likely for mental health or eating disorder management. They mentioned {num_days} days.",
        
        "Nutrition and mental health are closely connected. I'll retrieve their dietary data for the timeframe they specified.",
        
        "Sounds like they're working on healthy eating patterns. I'll get their nutrition information for the specified days.",
        
        # Non-temporal thinking
        "They want nutrition data but didn't specify when. I'll get about a week of dietary information to show recent eating patterns."
    ],
    
    'get_sleep_data': [
        "This person is having sleep issues, which is so common with mental health challenges. They mentioned {num_days} days, so I'll get their sleep data for that period.",
        
        "Sleep problems and mental health often go hand in hand. I'll retrieve their sleep metrics for the timeframe they specified.",
        
        "Sounds like insomnia or sleep disruption from anxiety or depression. I'll get their sleep information for the days they mentioned.",
        
        # Non-temporal thinking
        "They want sleep data but didn't give specific dates. I'll get about a week of sleep metrics to show recent sleep patterns."
    ],
    
    'get_weight_data': [
        "This person is monitoring weight changes, possibly from medication or eating disorder recovery. They mentioned {num_days} days.",
        
        "Weight can be affected by psychiatric medications and mental health. I'll retrieve their weight data for the specified timeframe.",
        
        "Sounds like they're tracking weight as part of their treatment. I'll get their weight measurements for the days they mentioned.",
        
        # Non-temporal thinking
        "They want weight data but didn't specify when exactly. I'll get about a week of weight measurements to show recent trends."
    ],
    
    'get_body_fat_data': [
        "This person wants to track body composition, possibly during treatment or recovery. They specified {num_days} days.",
        
        "Body composition can change with medications and mental health treatment. I'll retrieve their body fat data for the timeframe mentioned.",
        
        "Sounds like they're monitoring body composition changes. I'll get their body fat measurements for the specified days.",
        
        # Non-temporal thinking
        "They want body fat data but didn't specify when. I'll get about a week of body composition measurements."
    ],
    
    'get_bmr_data': [
        "This person wants to track their metabolism, possibly affected by medications. They mentioned {num_days} days.",
        
        "BMR can be influenced by psychiatric medications and mental health. I'll retrieve their metabolic data for the specified timeframe.",
        
        "Sounds like they're concerned about metabolic changes. I'll get their BMR measurements for the days they mentioned.",
        
        # Non-temporal thinking
        "They want BMR data but didn't specify when exactly. I'll get about a week of metabolic rate measurements."
    ],
    
    'get_height_data': [
        "This person needs height measurements, probably for medical calculations or health tracking. They mentioned {num_days} days.",
        
        "Height data is important for BMI and medical dosing. I'll retrieve their height measurements for the specified timeframe.",
        
        "Sounds like they need accurate height for their treatment team. I'll get their height data for the days mentioned.",
        
        # Non-temporal thinking
        "They need height data but didn't specify when. I'll get their most recent height measurements."
    ],
    
    'get_stress_data': [
        "This person is dealing with stress, which is so tough especially with mental health challenges. They mentioned {num_days} days, so I'll get their stress data.",
        
        "Stress tracking is crucial for anxiety and depression management. I'll retrieve their stress levels for the timeframe they specified.",
        
        "Sounds like they're overwhelmed and want to see their stress patterns. I'll get their stress measurements for the specified days.",
        
        # Non-temporal thinking
        "They want stress data but didn't give specific dates. I'll get about a week of stress measurements to show recent patterns."
    ],
    
    'get_body_temperature_data': [
        "This person is concerned about temperature changes, possibly from anxiety or medication effects. They mentioned {num_days} days.",
        
        "Body temperature can be affected by psychiatric medications and stress. I'll retrieve their temperature data for the specified timeframe.",
        
        "Sounds like they're having temperature regulation issues. I'll get their body temperature measurements for the days they mentioned.",
        
        # Non-temporal thinking
        "They want temperature data but didn't specify when exactly. I'll get about a week of temperature readings to show recent patterns."
    ]
}

def generate_mixed_query(function_name: str, include_temporal: bool = None) -> tuple:
    """Generate query with optional temporal info"""
    
    if include_temporal is None:
        include_temporal = random.random() < 0.7  # 70% temporal, 30% non-temporal
    
    templates = ENHANCED_MENTAL_HEALTH_TEMPLATES.get(function_name, [])
    if not templates:
        return None, None
    
    if include_temporal:
        # Filter temporal templates (ones with {num_days})
        temporal_templates = [t for t in templates if '{num_days}' in t]
        if temporal_templates:
            template = random.choice(temporal_templates)
            num_days = random.choice([1, 3, 5, 7, 10, 14, 21, 30])
            query = template.format(num_days=num_days)
            return query, num_days
    
    # Use non-temporal templates
    non_temporal_templates = [t for t in templates if '{num_days}' not in t]
    if non_temporal_templates:
        template = random.choice(non_temporal_templates)
        # Default to 7 days for non-temporal queries
        return template, 7
    
    return None, None

def generate_humanized_thinking(function_name: str, has_temporal: bool, num_days: int = None) -> str:
    """Generate more human-like thinking patterns"""
    
    thinking_templates = HUMANIZED_THINKING_TEMPLATES.get(function_name, [])
    if not thinking_templates:
        return f"The user wants {function_name.replace('get_', '').replace('_data', '')} data. I should help them get this information."
    
    if has_temporal and num_days:
        # Use temporal thinking templates
        temporal_templates = [t for t in thinking_templates if '{num_days}' in t]
        if temporal_templates:
            template = random.choice(temporal_templates)
            return template.format(num_days=num_days)
    
    # Use non-temporal thinking templates
    non_temporal_templates = [t for t in thinking_templates if '{num_days}' not in t]
    if non_temporal_templates:
        return random.choice(non_temporal_templates)
    
    return random.choice(thinking_templates)