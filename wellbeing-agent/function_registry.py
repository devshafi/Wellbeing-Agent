import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

class FunctionRegistry:
    """Registry of available functions for the mental health assistant"""
    
    def __init__(self):
        self.functions = {
            
            "get_sleep_data": self.get_sleep_data,
            "get_heart_rate_data": self.get_heart_rate_data,
            "get_stress_data": self.get_stress_data,           
        
        }
    
    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function by name with parameters"""
        try:
            if function_name not in self.functions:
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not found. Available functions: {list(self.functions.keys())}"
                }
            
            # Call the function with parameters
            result = self.functions[function_name](**parameters)
            return {
                "success": True,
                "function": function_name,
                "parameters": parameters,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "function": function_name,
                "parameters": parameters,
                "error": str(e)
            }
    
  
    def get_sleep_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get simple sleep data for the specified number of days"""
        sleep_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)  # Most recent day last
            sleep_record = {
                "date": date.strftime("%Y-%m-%d"),
                "hours_slept": round(random.uniform(4.0, 5.0), 1),
                "quality": random.choice(["Poor"])
            }
            sleep_records.append(sleep_record)
        
        return sleep_records
    
    def get_heart_rate_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get simple heart rate data for the specified number of days"""
        hr_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)  # Most recent day last
            hr_record = {
                "date": date.strftime("%Y-%m-%d"),
                "avg_heart_rate": random.randint(65, 95),
                "max_heart_rate": random.randint(120, 170)
            }
            hr_records.append(hr_record)
        
        return hr_records
    
    def get_stress_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get stress level data for the specified number of days
        
        Args:
            patient_id: ID of the patient
            num_days: Number of days to retrieve data for (default: 7)
            
        Returns:
            List of stress records with date and stress_level (1-100)
        """
        stress_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)  # Most recent day last
            stress_record = {
                "date": date.strftime("%Y-%m-%d"),
                "stress_level": random.randint(1, 100)  # Stress level from 1-100
            }
            stress_records.append(stress_record)
        
        return stress_records
    
  
   
   
# Global instance
function_registry = FunctionRegistry()