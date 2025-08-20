"""
Few-shot examples for different health data types to guide the conversation model
in providing data-informed responses.
"""

class FewShotExamples:
    """Manages few-shot examples for different health data types"""
    
    @staticmethod
    def get_examples_for_data_types(data_types):
        """
        Get appropriate few-shot examples based on collected data types
        
        Args:
            data_types (list): List of data types (e.g., ['sleep', 'heart_rate'])
            
        Returns:
            list: List of message dictionaries for few-shot examples
        """
        # Priority order for which example to use if multiple data types are present
        priority_order = ["sleep", "heart_rate", "mood", "exercise", "medication"]
        
        # Find the highest priority data type that we have
        selected_type = None
        for data_type in priority_order:
            if data_type in data_types:
                selected_type = data_type
                break
        
        # If no priority match, use the first available data type
        if not selected_type and data_types:
            selected_type = data_types[0]
        
        # Generate appropriate example based on selected data type
        return FewShotExamples._get_example_by_type(selected_type)
    
    @staticmethod
    def _get_example_by_type(data_type):
        """Get few-shot example for a specific data type"""
        
        examples_map = {
            "sleep": FewShotExamples._get_sleep_example(),
            "heart_rate": FewShotExamples._get_heart_rate_example(),
            "mood": FewShotExamples._get_mood_example(),
            "exercise": FewShotExamples._get_exercise_example(),
            "medication": FewShotExamples._get_medication_example(),
        }
        
        return examples_map.get(data_type, FewShotExamples._get_generic_example())
    
    @staticmethod
    def _get_sleep_example():
        """Few-shot example for sleep data analysis"""
        return [
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
            }
        ]
    
    @staticmethod
    def _get_heart_rate_example():
        """Few-shot example for heart rate data analysis"""
        return [
            {
                "role": "user",
                "content": """I'm worried about my heart rate lately.

My recent health data shows:
=== HEART_RATE DATA ===
Recent heart rate data:
• 2025-08-15: Average 95 bpm
• 2025-08-16: Average 88 bpm
• 2025-08-17: Average 102 bpm

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
            },
            {
                "role": "assistant", 
                "content": """Looking at your heart rate data from August 15-17, I can see some concerning variations. Your heart rate has been fluctuating significantly - from 88 bpm on August 16th to 102 bpm on August 17th, with 95 bpm on August 15th.

The reading of 102 bpm on August 17th is notably elevated and could indicate stress, anxiety, or physical strain. The variation from 88 to 102 bpm over just a few days suggests your cardiovascular system may be responding to some form of stress or changes in your routine."""
            }
        ]
    
    @staticmethod
    def _get_mood_example():
        """Few-shot example for mood data analysis"""
        return [
            {
                "role": "user",
                "content": """I've been feeling off emotionally recently.

My recent health data shows:
=== MOOD DATA ===
Recent mood records:
• 2025-08-15: Mood score 3/10, Anxious
• 2025-08-16: Mood score 4/10, Stressed
• 2025-08-17: Mood score 2/10, Depressed

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
            },
            {
                "role": "assistant",
                "content": """Looking at your mood data from August 15-17, I can see a concerning pattern of persistent low mood scores. Your mood has been consistently low, ranging from 2-4 out of 10, with August 17th showing the lowest score of 2 with feelings of depression.

The progression from anxious (Aug 15) to stressed (Aug 16) to depressed (Aug 17) suggests your emotional state has been deteriorating over these three days. These consistently low scores indicate you're experiencing significant emotional distress that may benefit from additional support."""
            }
        ]
    
    @staticmethod
    def _get_exercise_example():
        """Few-shot example for exercise data analysis"""
        return [
            {
                "role": "user",
                "content": """I haven't been feeling motivated to exercise.

My recent health data shows:
=== EXERCISE DATA ===
Recent exercise records:
• 2025-08-15: 0 minutes, No activity
• 2025-08-16: 15 minutes, Light walking
• 2025-08-17: 0 minutes, No activity

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
            },
            {
                "role": "assistant",
                "content": """Looking at your exercise data from August 15-17, I can see a pattern of very low activity levels. You had no recorded exercise on August 15th and 17th, with only 15 minutes of light walking on August 16th.

This minimal activity level over three days suggests you're going through a period of low motivation or energy. The brief walking session on August 16th shows you did make some effort, which is positive, but the overall pattern indicates you might benefit from starting with very small, manageable activities to rebuild your exercise routine."""
            }
        ]
    
    @staticmethod
    def _get_medication_example():
        """Few-shot example for medication data analysis"""
        return [
            {
                "role": "user",
                "content": """I'm concerned about my medication routine.

My recent health data shows:
=== MEDICATION DATA ===
Recent medication records:
• 2025-08-15: Sertraline 50mg - Taken
• 2025-08-16: Sertraline 50mg - Missed
• 2025-08-17: Sertraline 50mg - Taken

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
            },
            {
                "role": "assistant",
                "content": """Looking at your medication data from August 15-17, I can see you missed your Sertraline dose on August 16th but took it on the other days. Missing doses of antidepressants like Sertraline can affect your mood stability and overall wellbeing.

While you've been mostly consistent (taking it 2 out of 3 days), it's important to maintain daily consistency with Sertraline for optimal effectiveness. The missed dose on August 16th might contribute to any mood fluctuations you're experiencing."""
            }
        ]
    
    @staticmethod
    def _get_generic_example():
        """Generic few-shot example for other data types"""
        return [
            {
                "role": "user", 
                "content": """I have some health concerns lately.

My recent health data shows specific patterns and values.

Please analyze my actual data and provide personalized insights based on the specific patterns you can see."""
            },
            {
                "role": "assistant",
                "content": """Looking at your health data, I can see specific patterns in the values and dates provided. Let me analyze these specific data points and trends to give you personalized insights based on what the data actually shows about your health patterns."""
            }
        ]
