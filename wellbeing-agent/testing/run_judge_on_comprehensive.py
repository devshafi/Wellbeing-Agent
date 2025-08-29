#!/usr/bin/env python3
"""
Run LLM Judge on the 89-query comprehensive test results
"""

import os
from dotenv import load_dotenv
from llm_judge_evaluation import LLMJudge

def main():
    # Load API key from .env
    load_dotenv('/home/jovyan/Works/MSc_Thesis/.env')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OPENAI_API_KEY found in .env file.")
        return
    
    print("✅ Loaded API key from .env file")
    
    # Path to the 89-query comprehensive results
    csv_path = "/home/jovyan/Works/MSc_Thesis/wellbeing-agent/testing/comprehensive_agent_test_results_20250829_015634.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Comprehensive test results file not found: {csv_path}")
        return
    
    print(f"🔍 Found comprehensive test results: {csv_path}")
    print(f"📊 Using GPT-3.5-turbo for evaluation")
    
    try:
        # Initialize and run evaluation
        judge = LLMJudge(api_key=api_key, model="gpt-3.5-turbo")
        results_path = judge.evaluate_csv_results(csv_path)
        
        print(f"\n🎉 Comprehensive evaluation complete!")
        print(f"📁 Results saved to: {results_path}")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")

if __name__ == "__main__":
    main()
