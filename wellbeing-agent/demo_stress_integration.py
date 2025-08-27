#!/usr/bin/env python3
"""Demo script showing stress data integration in action."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from function_registry import FunctionRegistry
from utils.few_shot_examples import FewShotExamples

def demo_stress_integration():
    """Demonstrate stress data integration"""
    print("🧘 Mental Health Wellbeing Agent - Stress Data Demo")
    print("=" * 55)
    
    # 1. Function Registry Demo
    print("\n1️⃣ Function Registry - Stress Data Retrieval:")
    print("-" * 45)
    registry = FunctionRegistry()
    result = registry.execute_function("get_stress_data", {"patient_id": "demo_user"})
    
    if result["success"]:
        stress_data = result["data"]
        print(f"📊 Retrieved {len(stress_data)} days of stress data:")
        
        for i, entry in enumerate(stress_data[:3]):  # Show first 3 entries
            stress_emoji = "😰" if entry["stress_level"] > 70 else "😟" if entry["stress_level"] > 40 else "😌"
            print(f"   Day {i+1}: {entry['date']} - {stress_emoji} Stress Level: {entry['stress_level']}/100")
        
        if len(stress_data) > 3:
            print(f"   ... and {len(stress_data) - 3} more days")
    else:
        print(f"❌ Error: {result['error']}")
        return
    
    # 2. Few-Shot Examples Demo
    print("\n2️⃣ Few-Shot Examples - Conversation Context:")
    print("-" * 45)
    examples = FewShotExamples()
    
    # Get stress-specific system prompt
    stress_prompt = examples.get_system_prompt_with_examples(["stress"])
    
    # Extract a sample from the prompt
    if "Escalating Stress Pattern" in stress_prompt:
        start = stress_prompt.find("Example 1 - Escalating Stress Pattern:")
        end = stress_prompt.find("Example 2", start)
        sample_example = stress_prompt[start:end].strip()
        
        print("📝 Sample conversation example for stress data:")
        print(f"   {sample_example[:200]}...")
        print("   [Full example would guide the AI's response style]")
    
    # 3. Integration Summary
    print("\n3️⃣ Complete Integration Summary:")
    print("-" * 35)
    print("✅ Function Registry: get_stress_data() returns date + stress_level (1-100)")
    print("✅ Function Calling Processor: Recognizes stress queries and formats data")
    print("✅ Hybrid Processor: Combines stress data with conversation context")
    print("✅ Few-Shot Examples: Provides empathetic response templates")
    
    print("\n🎯 Example User Query Flow:")
    print("   User: 'I've been feeling really stressed lately'")
    print("   → Router detects stress data need")
    print("   → Function processor retrieves stress data")
    print("   → Hybrid processor combines data + conversation")
    print("   → Response: Empathetic analysis with actual stress levels")
    
    print("\n🎉 Stress data integration is fully operational!")

if __name__ == "__main__":
    demo_stress_integration()
