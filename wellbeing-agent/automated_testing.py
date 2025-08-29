#!/usr/bin/env python3
"""
Automated Testing Script for Wellbeing Agent
Generates mental health queries, processes them, and saves results for evaluation
"""

import sys
import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.wellbeing_agent import wellbeing_agent
from utils.history_manager import history_manager

class AutomatedTester:
    """Automated testing system for the wellbeing agent"""
    
    def __init__(self):
        self.test_queries = [
            {
                "id": 1,
                "category": "Sleep Issues",
                "query": "I've been having trouble sleeping lately. Can you check my sleep data and help me understand what might be wrong?",
                "expected_functions": ["get_sleep_data"],
                "context": "Patient reporting sleep difficulties"
            },
            {
                "id": 2,
                "category": "Stress Management", 
                "query": "I feel really stressed all the time. What do my stress levels look like recently?",
                "expected_functions": ["get_stress_data"],
                "context": "High stress levels reported"
            },
            {
                "id": 3,
                "category": "Physical Activity",
                "query": "I feel like I'm not moving enough during the day. Can you show me my activity data?",
                "expected_functions": ["get_steps_data", "get_exercise_session_data"],
                "context": "Sedentary lifestyle concerns"
            },
            {
                "id": 4,
                "category": "Cardiovascular Health",
                "query": "I've been experiencing rapid heartbeat and I'm worried about my heart health. Can you check my heart rate and blood pressure?",
                "expected_functions": ["get_heart_rate_data", "get_blood_pressure_data"],
                "context": "Cardiovascular concerns"
            },
            {
                "id": 5,
                "category": "Nutrition and Weight",
                "query": "I'm concerned about my eating habits and weight. Can you help me understand my nutrition and weight trends?",
                "expected_functions": ["get_nutrition_data", "get_weight_data"],
                "context": "Nutrition and weight management"
            },
            {
                "id": 6,
                "category": "Diabetes Risk",
                "query": "My family has a history of diabetes and I'm worried about my blood sugar levels. What do my glucose readings show?",
                "expected_functions": ["get_blood_glucose_data"],
                "context": "Diabetes risk assessment"
            },
            {
                "id": 7,
                "category": "Respiratory Issues",
                "query": "I sometimes feel short of breath. Can you check my oxygen levels and see if there's anything concerning?",
                "expected_functions": ["get_oxygen_saturation_data"],
                "context": "Breathing difficulties"
            },
            {
                "id": 8,
                "category": "Overall Wellness",
                "query": "I'm feeling generally unwell and tired. Can you give me a comprehensive overview of my health data?",
                "expected_functions": ["get_sleep_data", "get_stress_data", "get_heart_rate_data", "get_steps_data"],
                "context": "General wellness check"
            },
            {
                "id": 9,
                "category": "Fitness Goals",
                "query": "I want to improve my fitness but don't know where to start. What does my exercise and fitness data tell you?",
                "expected_functions": ["get_vo2max_data", "get_exercise_session_data", "get_calories_burned_data"],
                "context": "Fitness improvement goals"
            },
            {
                "id": 10,
                "category": "Body Composition",
                "query": "I'm concerned about my body composition and metabolism. Can you analyze my body fat and BMR data?",
                "expected_functions": ["get_body_fat_data", "get_bmr_data"],
                "context": "Body composition analysis"
            }
        ]
        
        self.patient_id = "TEST_PATIENT_001"
        self.results = []
        
    def setup_agent(self):
        """Initialize the wellbeing agent"""
        print("🚀 Setting up Wellbeing Agent for automated testing...")
        try:
            wellbeing_agent.setup_models()
            print("✅ Agent setup complete!")
            return True
        except Exception as e:
            print(f"❌ Failed to setup agent: {e}")
            return False
    
    def process_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single test query"""
        print(f"\n🔄 Processing Query {test_case['id']}: {test_case['category']}")
        
        try:
            # Process the query through the agent
            response = wellbeing_agent.process_request(
                message=test_case['query'],
                patient_id=self.patient_id
            )
            
            # Extract key information
            result = {
                "query_id": test_case['id'],
                "category": test_case['category'],
                "query": test_case['query'],
                "expected_functions": test_case['expected_functions'],
                "context": test_case['context'],
                "agent_response": response.get('response', ''),
                "functions_called": response.get('functions_called', []),
                "function_results": response.get('function_results', {}),
                "processing_time": response.get('processing_time', 0),
                "timestamp": datetime.now().isoformat(),
                "success": response.get('success', False)
            }
            
            print(f"✅ Query {test_case['id']} processed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error processing query {test_case['id']}: {e}")
            return {
                "query_id": test_case['id'],
                "category": test_case['category'],
                "query": test_case['query'],
                "expected_functions": test_case['expected_functions'],
                "context": test_case['context'],
                "agent_response": f"ERROR: {str(e)}",
                "functions_called": [],
                "function_results": {},
                "processing_time": 0,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def run_all_tests(self):
        """Run all test queries"""
        print("🧪 Starting automated testing...")
        
        for test_case in self.test_queries:
            result = self.process_query(test_case)
            self.results.append(result)
        
        print(f"\\n🎉 Completed {len(self.results)} test queries!")
    
    def save_results_to_csv(self, filename: str = None):
        """Save results to CSV file for LLM judge evaluation"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"automated_test_results_{timestamp}.csv"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # CSV headers for LLM judge evaluation
        headers = [
            'query_id',
            'category', 
            'user_query',
            'agent_response',
            'expected_functions',
            'actual_functions_called',
            'context',
            'success',
            'processing_time',
            'timestamp',
            'function_results_summary'
        ]
        
        print(f"💾 Saving results to: {filepath}")
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for result in self.results:
                # Prepare function results summary
                func_summary = ""
                if result.get('function_results'):
                    summaries = []
                    for func_name, func_data in result['function_results'].items():
                        if isinstance(func_data, dict) and func_data.get('success'):
                            data_points = len(func_data.get('data', []))
                            summaries.append(f"{func_name}: {data_points} records")
                    func_summary = "; ".join(summaries)
                
                writer.writerow({
                    'query_id': result['query_id'],
                    'category': result['category'],
                    'user_query': result['query'],
                    'agent_response': result['agent_response'],
                    'expected_functions': ', '.join(result['expected_functions']),
                    'actual_functions_called': ', '.join(result.get('functions_called', [])),
                    'context': result['context'],
                    'success': result['success'],
                    'processing_time': result['processing_time'],
                    'timestamp': result['timestamp'],
                    'function_results_summary': func_summary
                })
        
        print(f"✅ Results saved successfully!")
        print(f"📊 Summary: {len(self.results)} queries processed")
        
        # Print quick summary
        successful = sum(1 for r in self.results if r['success'])
        print(f"✅ Successful: {successful}/{len(self.results)}")
        print(f"❌ Failed: {len(self.results) - successful}/{len(self.results)}")
        
        return filepath
    
    def generate_evaluation_prompt(self) -> str:
        """Generate a sample prompt for LLM judge evaluation"""
        prompt = '''
# LLM Judge Evaluation Prompt for Wellbeing Agent

Please evaluate each agent response based on the following criteria:

## Evaluation Criteria (Score 1-5 for each):

1. **Relevance**: Does the response address the user's mental health query appropriately?
2. **Function Usage**: Are the correct health data functions called based on the query?
3. **Data Interpretation**: Does the agent properly interpret and explain the health data?
4. **Therapeutic Value**: Does the response provide helpful mental health support?
5. **Completeness**: Does the response fully address the user's concerns?

## Scoring Guide:
- 5: Excellent - Exceeds expectations
- 4: Good - Meets expectations well
- 3: Satisfactory - Meets basic expectations
- 2: Below Average - Some issues present
- 1: Poor - Significant problems

## Output Format:
For each query, provide:
- Overall Score (1-5)
- Individual criterion scores
- Brief justification
- Suggestions for improvement

This CSV contains {num_queries} mental health queries with agent responses for evaluation.
        '''.strip()
        
        return prompt.format(num_queries=len(self.test_queries))

def main():
    """Main execution function"""
    tester = AutomatedTester()
    
    # Setup the agent
    if not tester.setup_agent():
        print("Failed to setup agent. Exiting...")
        return
    
    # Run all tests
    tester.run_all_tests()
    
    # Save results
    csv_file = tester.save_results_to_csv()
    
    # Generate evaluation prompt
    eval_prompt = tester.generate_evaluation_prompt()
    prompt_file = csv_file.replace('.csv', '_evaluation_prompt.txt')
    
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(eval_prompt)
    
    print(f"\\n📋 Evaluation prompt saved to: {prompt_file}")
    print("\\n🎯 Ready for LLM judge evaluation!")

if __name__ == "__main__":
    main()
