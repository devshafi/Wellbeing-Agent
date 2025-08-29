"""
Automated Testing for Wellbeing Agent
Generates mental health queries and collects agent responses for evaluation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import json
from datetime import datetime
from core.wellbeing_agent import wellbeing_agent
from utils.history_manager import history_manager

class AgentTester:
    def __init__(self):
        self.test_queries = [
            "I've been feeling really anxious lately and having trouble sleeping. Can you check my recent sleep data and help me understand what's going on?",
            
            "My stress levels seem really high this week. Could you look at my stress data and suggest some coping strategies?",
            
            "I'm worried about my heart rate - it feels like it's racing all the time. Can you check my heart rate data and tell me if I should be concerned?",
            
            "I've been eating poorly and feeling sluggish. Can you review my nutrition data and help me make better food choices?",
            
            "I feel like I'm not getting enough exercise and it's affecting my mood. Can you look at my activity data and suggest a plan?",
            
            "My blood pressure has been concerning me. Can you check my recent readings and explain what they mean for my health?",
            
            "I'm having trouble managing my weight and it's making me depressed. Can you look at my weight data and provide some guidance?",
            
            "I feel tired all the time despite trying to sleep more. Can you check my sleep patterns and energy levels?",
            
            "I'm concerned about my overall fitness and how it might be affecting my mental health. Can you assess my fitness data?",
            
            "I've been feeling overwhelmed and want to understand how my physical health might be contributing to my mental state. Can you do a comprehensive health review?"
        ]
        
    def setup_agent(self):
        """Initialize the wellbeing agent"""
        print("🚀 Setting up Wellbeing Agent for testing...")
        try:
            wellbeing_agent.setup_models()
            print("✅ Agent setup complete!")
            return True
        except Exception as e:
            print(f"❌ Agent setup failed: {e}")
            return False
    
    def test_agent_response(self, query, patient_id="TEST_001"):
        """Get agent response for a single query"""
        try:
            print(f"📝 Testing query: {query[:50]}...")
            
            # Use the wellbeing agent's process_query method
            result = wellbeing_agent.process_query(patient_id, query)
            
            # Extract the response
            response = result.get("response", "")
            route = result.get("route", "unknown")
            
            # Format response similar to the gradio interface
            route_indicators = {
                "conversation": "💬 **Conversation Mode**",
                "function_calling": "🔧 **Data Retrieval Mode**", 
                "hybrid": "🎭 **Hybrid Response** (Data + Conversation)"
            }
            
            route_indicator = route_indicators.get(route.lower(), f"🤖 **{route.upper()} Mode**")
            formatted_response = f"{route_indicator}\n\n{response}"
            
            # Note: Skip history storage for testing purposes
            
            return {
                "success": True,
                "response": formatted_response,
                "route": route,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "route": None,
                "error": str(e)
            }
    
    def run_automated_tests(self):
        """Run all test queries and collect responses"""
        # Setup agent
        if not self.setup_agent():
            return None
            
        results = []
        patient_id = f"AUTOMATED_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n🧪 Running automated tests with patient ID: {patient_id}")
        print("=" * 70)
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n🔍 Test {i}/10:")
            
            # Get agent response
            result = self.test_agent_response(query, patient_id)
            
            # Store result
            test_result = {
                "test_id": i,
                "patient_id": patient_id,
                "query": query,
                "response": result["response"] if result["success"] else None,
                "route": result["route"] if result["success"] else None,
                "success": result["success"],
                "error": result["error"],
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            
            # Print status
            if result["success"]:
                response_preview = result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
                print(f"✅ Success: {response_preview}")
            else:
                print(f"❌ Failed: {result['error']}")
        
        return results
    
    def save_results_to_csv(self, results):
        """Save test results to CSV file"""
        if not results:
            print("❌ No results to save")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"automated_agent_test_results_{timestamp}.csv"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # CSV headers
        headers = ["test_id", "patient_id", "query", "response", "route", "success", "error", "timestamp"]
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for result in results:
                    writer.writerow(result)
            
            print(f"\n📊 Results saved to: {filepath}")
            print(f"📈 Total tests: {len(results)}")
            successful_tests = sum(1 for r in results if r['success'])
            print(f"✅ Successful: {successful_tests}/{len(results)}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return None
    
    def run_full_test_suite(self):
        """Run complete automated testing suite"""
        print("🤖 WELLBEING AGENT AUTOMATED TESTING")
        print("=" * 50)
        
        # Run tests
        results = self.run_automated_tests()
        
        if results:
            # Save results
            csv_file = self.save_results_to_csv(results)
            
            # Print summary
            print("\n📋 TEST SUMMARY:")
            print("=" * 30)
            for i, result in enumerate(results, 1):
                status = "✅" if result['success'] else "❌"
                query_preview = result['query'][:40] + "..."
                print(f"{status} Test {i}: {query_preview}")
            
            return csv_file
        else:
            print("❌ Testing failed - no results generated")
            return None

if __name__ == "__main__":
    tester = AgentTester()
    csv_file = tester.run_full_test_suite()
    
    if csv_file:
        print(f"\n🎉 Testing complete! Results saved to: {csv_file}")
        print("📝 This CSV file is ready for LLM judge evaluation.")
    else:
        print("\n💥 Testing failed!")
