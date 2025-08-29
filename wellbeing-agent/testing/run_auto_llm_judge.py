#!/usr/bin/env python3
"""
Auto LLM Judge Evaluation Script
Automatically uses API key from .env file and GPT-3.5-turbo
"""

import os
import sys
from dotenv import load_dotenv
from llm_judge_evaluation import LLMJudge

def run_evaluation_auto():
    """
    Run LLM judge evaluation with API key from .env file
    """
    # Load environment variables from .env file
    load_dotenv('/home/jovyan/Works/MSc_Thesis/.env')
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OPENAI_API_KEY found in .env file.")
        return
    
    print(f"✅ Loaded API key from .env file")
    
    # Path to the generated test results
    csv_path = "/home/jovyan/Works/MSc_Thesis/wellbeing-agent/testing/automated_agent_test_results_20250829_001147.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Test results file not found: {csv_path}")
        print("Please run the automated testing first.")
        return
    
    print(f"🔍 Found test results: {csv_path}")
    
    # Use GPT-3.5-turbo as requested
    model = "gpt-3.5-turbo"
    print(f"📊 Using model: {model}")
    
    try:
        # Initialize and run evaluation
        judge = LLMJudge(api_key=api_key, model=model)
        results_path = judge.evaluate_csv_results(csv_path)
        
        print(f"\n🎉 Evaluation complete!")
        print(f"📁 Results saved to: {results_path}")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    run_evaluation_auto()
