#!/usr/bin/env python3
"""
Comprehensive Automated Agent Testing System
Creates 100 mental health queries based on 20 health functions
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the wellbeing-agent directory to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from core.wellbeing_agent import wellbeing_agent

class ComprehensiveTester:
    def __init__(self):
        self.agent_ready = False

    def setup_agent(self):
        """Initialize and prepare the wellbeing agent models (once)."""
        if self.agent_ready:
            return True
        try:
            print("🚀 Setting up Wellbeing Agent (models)...")
            wellbeing_agent.setup_models()
            self.agent_ready = True
            print("✅ Agent setup complete!")
            return True
        except Exception as e:
            print(f"❌ Agent setup failed: {e}")
            return False
        
    def create_100_test_queries(self):
        """Create 100 comprehensive mental health queries based on health functions"""
        
        # Original 10 queries
        original_queries = [
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
        
        # 90 additional queries (4-5 per health function)
        health_function_queries = [
            # Sleep-related queries (5)
            "I barely get 3 hours of sleep and it's destroying my mental health. Can you analyze my sleep patterns?",
            "My insomnia is making my anxiety unbearable. What do my sleep metrics show?",
            "I keep waking up exhausted despite trying to sleep more. Can you check my sleep quality data?",
            "My sleep schedule is completely messed up and I feel depressed. Can you help me understand my sleep patterns?",
            "I'm desperate for better sleep because I feel terrible all the time. What does my sleep data reveal?",
            
            # Heart Rate queries (5)
            "My resting heart rate feels elevated and it's causing me anxiety. Can you check my heart rate data?",
            "I constantly worry about my heart rate being abnormal. What do my recent readings show?",
            "My heart rate spikes with stress and it scares me. Can you analyze my heart rate patterns?",
            "I feel like my heart is always racing and it's exhausting. What does my heart rate data indicate?",
            "My heart rate during exercise worries me. Can you review my cardiovascular data?",
            
            # Nutrition queries (5)
            "My eating habits are terrible and it's affecting my mental health. Can you analyze my nutrition data?",
            "I feel guilty about my poor food choices. What does my nutritional intake look like?",
            "My diet is making my depression worse. Can you review my nutrition patterns?",
            "I'm stressed about not eating healthily enough. What do my nutrition metrics show?",
            "I'm emotional eating and feel out of control. Can you help me understand my eating patterns?",
            
            # Activity/Steps queries (5)
            "I barely walk anymore and it's affecting my mood severely. Can you check my activity levels?",
            "My low step count is making me feel worthless. What does my activity data show?",
            "I'm anxious about how sedentary I've become. Can you analyze my movement patterns?",
            "I feel guilty about my lack of physical activity. What do my step counts reveal?",
            "My inactivity is making me depressed. Can you review my daily movement data?",
            
            # Weight queries (5)
            "My weight gain is severely impacting my self-esteem. Can you look at my weight trends?",
            "I feel depressed about my weight changes. What does my weight data show?",
            "My weight struggles are making me feel like a failure. Can you analyze my weight patterns?",
            "I'm anxious about my weight all the time. What do my recent measurements indicate?",
            "My weight is affecting every aspect of my mental health. Can you help me understand the trends?",
            
            # Blood Pressure queries (4)
            "My high blood pressure is giving me severe health anxiety. What do my readings show?",
            "I'm terrified about stroke risk because of my blood pressure. Can you review my BP data?",
            "The stress about my blood pressure is making it worse. What are my recent measurements?",
            "My blood pressure readings are causing me to panic. Can you help me interpret them?",
            
            # Exercise Performance queries (5)
            "I haven't exercised in weeks and feel terrible about myself. Can you check my fitness data?",
            "My lack of workouts is making my depression worse. What does my exercise data show?",
            "I feel ashamed of how out of shape I've become. Can you analyze my fitness metrics?",
            "Exercise feels impossible when I'm this depressed. What do my activity levels show?",
            "I can't perform like I used to and it's discouraging. Can you review my exercise data?",
            
            # Body Composition queries (4)
            "My body fat percentage is making me feel disgusted with myself. Can you check my composition data?",
            "I'm obsessing over my body composition and it's unhealthy. What do my metrics show?",
            "My body fat levels are destroying my confidence. Can you analyze my body composition?",
            "I feel hopeless about my body composition changes. What does the data reveal?",
            
            # Energy/BMR queries (4)
            "My low metabolism is making me feel frustrated. Can you check my BMR data?",
            "I worry my metabolism means I'll never lose weight. What does my BMR show?",
            "I feel like my slow metabolism is working against me. Can you analyze my metabolic data?",
            "My energy levels are terrible and I feel hopeless. What do my metabolism metrics indicate?",
            
            # Blood Glucose queries (4)
            "My blood sugar feels unstable and it's affecting my anxiety. Can you check my glucose data?",
            "I'm worried about my glucose readings and diabetes risk. What do my levels show?",
            "Blood sugar spikes are making me panic. Can you analyze my glucose patterns?",
            "My energy crashes from blood sugar make me feel hopeless. What does my glucose data reveal?",
            
            # Stress queries (5)
            "My stress levels are through the roof and I can't cope. Can you check my stress data?",
            "I feel overwhelmed by constant stress. What do my stress metrics show?",
            "My stress is affecting everything in my life. Can you analyze my stress patterns?",
            "I can't manage my stress anymore and feel burned out. What does my stress data indicate?",
            "My chronic stress is making me physically ill. Can you review my stress levels?",
            
            # VO2/Fitness queries (4)
            "My VO2 max results show I'm in terrible shape. Can you help me understand my fitness data?",
            "I'm worried about my cardiovascular fitness being so poor. What does my VO2 data show?",
            "My fitness level is making me anxious about my health. Can you analyze my cardio metrics?",
            "I feel hopeless about my fitness after seeing my results. What do my fitness measurements indicate?",
            
            # Blood Oxygen queries (4)
            "I feel like I can't breathe properly and it's causing panic. Can you check my oxygen data?",
            "My oxygen levels worry me constantly. What do my readings show?",
            "I'm concerned about shortness of breath affecting my life. Can you analyze my oxygen metrics?",
            "Low oxygen feelings make me think something's wrong. What does my oxygen data reveal?",
            
            # Temperature queries (4)
            "I constantly feel feverish and it's making me anxious. Can you check my temperature data?",
            "My body temperature fluctuations worry me. What do my readings show?",
            "I feel cold all the time and wonder if something's wrong. Can you analyze my temperature patterns?",
            "My temperature irregularities are causing health anxiety. What does my temperature data indicate?",
            
            # Distance/Speed queries (4)
            "I can't run as far as I used to and it's depressing. Can you check my exercise distance data?",
            "My declining performance is making me feel weak. What do my workout distances show?",
            "I'm so much slower than before and it's affecting my mood. Can you analyze my exercise speed?",
            "My poor performance is making me want to give up. What do my exercise metrics reveal?",
            
            # Power/Strength queries (4)
            "My declining strength is really discouraging. Can you check my exercise power data?",
            "I feel weak and it's affecting my confidence badly. What do my power metrics show?",
            "My low power during workouts makes me feel pathetic. Can you analyze my strength data?",
            "I'm frustrated with how much strength I've lost. What do my power measurements indicate?",
            
            # Calories queries (4)
            "I'm obsessing over calories and it's becoming unhealthy. Can you check my calorie data?",
            "I feel guilty when I don't burn enough calories. What do my activity metrics show?",
            "My calorie concerns are becoming an anxiety trigger. Can you analyze my calorie burn patterns?",
            "I'm stressed about not being active enough. What does my calorie data reveal?",
            
            # Height/Body Image queries (4)
            "I feel insecure about my height in social situations. Can you help me understand my body metrics?",
            "My height makes me feel inadequate and affects confidence. What do my measurements show?",
            "I'm self-conscious about my physical appearance. Can you review my body composition data?",
            "I feel uncomfortable in my body. What do my physical health metrics indicate?"
        ]
        
        # Combine all queries
        all_queries = original_queries + health_function_queries

        # If fewer than 100, pad with additional health-function-based prompts
        if len(all_queries) < 100:
            pad_queries = [
                # Additional sleep-focused
                "My fragmented sleep is making me irritable and hopeless. Can you look at my sleep stages?",
                "I nap during the day because nights are awful. What does my weekly sleep data show?",
                # Additional stress-focused
                "I wake up stressed and go to bed stressed. Can you analyze my stress patterns this week?",
                "My stress spikes randomly and it's scaring me. What do my stress readings show?",
                # Additional heart rate-focused
                "My heart rate jumps even when sitting. Can you check resting HR trends?",
                "I get palpitations with minor activity. What do my HR patterns suggest?",
                # Additional blood pressure-focused
                "Seeing high BP readings makes me panic. Can you put my BP data in context?",
                "My BP is high at night and it's worrying me. Can you review nocturnal readings?",
                # Additional activity/steps-focused
                "On most days I barely move. What do my step trends say about my routine?",
                "I want to walk more but feel stuck. Can you check my daily movement profile?",
                # Additional nutrition-focused
                "I skip meals then overeat at night. What does my nutrition data show?",
                "Sugar cravings are out of control. Can you review my macro balance?",
                # Additional weight/body comp
                "My weight fluctuates and it stresses me. What do my weekly changes indicate?",
                "I'm avoiding mirrors because of body fat. Can you analyze my body comp trend?",
                # Additional VO2/fitness
                "Climbing stairs leaves me winded. What does my VO2 fitness say about this?",
                "I feel deconditioned after a tough month. Can you assess my cardio fitness?",
                # Additional calories/bmr/energy
                "I feel drained by midday. What do my BMR/TDEE patterns suggest?",
                "I can't keep energy steady. Can you relate my calorie burn to fatigue?",
                # Additional oxygen/temp
                "I feel breathless at random. What do my oxygen levels show lately?",
                "I get chills and heat waves. Can you analyze my body temperature records?",
            ]
            # Extend until we reach 100
            for q in pad_queries:
                if len(all_queries) >= 100:
                    break
                all_queries.append(q)

        return all_queries[:100]  # Ensure exactly 100 queries
    
    def run_comprehensive_testing(self):
        """Run 100 comprehensive tests and save results"""
        
        print("🚀 COMPREHENSIVE WELLBEING AGENT TESTING")
        print("=" * 60)
        print(f"📊 Total Tests: 100")
        print(f"🎯 Coverage: All 20 health functions")
        print(f"🧠 Focus: Mental health perspectives")
        print()
        
        # Ensure agent is initialized
        if not self.setup_agent():
            raise RuntimeError("Agent setup failed; cannot run tests.")

        # Get all 100 queries
        test_queries = self.create_100_test_queries()
        
        results = []
        successful_tests = 0
        
        # Run tests
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 Test {i}/100:")
            print(f"📝 Testing query: {query[:80]}...")
            
            try:
                # Generate unique patient ID
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                patient_id = f"COMPREHENSIVE_TEST_{timestamp}_{i:03d}"
                
                # Process query through the agent (note: param order patient_id, query)
                result = wellbeing_agent.process_query(patient_id, query)

                # Extract response fields
                response_text = result.get("response", "")
                route = result.get("route", "unknown")
                
                results.append({
                    'test_id': i,
                    'patient_id': patient_id,
                    'query': query,
                    'response': response_text,
                    'route': route,
                    'success': True,
                    'error': '',
                    'timestamp': datetime.now().isoformat()
                })
                
                successful_tests += 1
                print(f"✅ Success: Test {i} completed")
                
            except Exception as e:
                print(f"❌ Error in test {i}: {str(e)}")
                results.append({
                    'test_id': i,
                    'patient_id': f"COMPREHENSIVE_TEST_{timestamp}_{i:03d}",
                    'query': query,
                    'response': f"Error: {str(e)}",
                    'route': 'error',
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_agent_test_results_{timestamp}.csv"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        df = pd.DataFrame(results)
        df.to_csv(filepath, index=False)
        
        # Print summary
        print(f"\n📊 TESTING COMPLETE")
        print(f"=" * 40)
        print(f"📈 Total tests: {len(results)}")
        print(f"✅ Successful: {successful_tests}/{len(results)}")
        print(f"❌ Failed: {len(results) - successful_tests}/{len(results)}")
        print(f"📁 Results saved to: {filepath}")
        print()
        
        if successful_tests > 0:
            print(f"🎯 SUCCESS RATE: {(successful_tests/len(results)*100):.1f}%")
            print(f"📋 This CSV file is ready for LLM judge evaluation!")
        
        return filepath

def main():
    tester = ComprehensiveTester()
    results_file = tester.run_comprehensive_testing()
    return results_file

if __name__ == "__main__":
    main()
