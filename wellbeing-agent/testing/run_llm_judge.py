#!/usr/bin/env python3
"""
Quick LLM Judge Evaluation Script
Run this after providing your OpenAI API key
"""

import os
import sys
from llm_judge_evaluation import LLMJudge

def run_evaluation():
    """
    Run LLM judge evaluation with user-provided API key
    """
    # Get API key from user
    api_key = input("Please enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Path to the generated test results
    csv_path = "/home/jovyan/Works/MSc_Thesis/wellbeing-agent/testing/automated_agent_test_results_20250829_001147.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Test results file not found: {csv_path}")
        print("Please run the automated testing first.")
        return
    
    print(f"🔍 Found test results: {csv_path}")
    
    # Choose model
    print("\nSelect OpenAI model:")
    print("1. GPT-4 (recommended, more expensive)")
    print("2. GPT-3.5-turbo (faster, cheaper)")
    
    model_choice = input("Enter choice (1 or 2, default: 1): ").strip() or "1"
    
    if model_choice == "2":
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4"
    
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
    run_evaluation()
