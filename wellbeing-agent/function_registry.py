import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

class FunctionRegistry:
    """Registry of available functions for the mental health assistant"""
    
    def __init__(self):
        self.functions = {
            # Basic health data
            "get_steps_data": self.get_steps_data,
            "get_sleep_data": self.get_sleep_data,
            "get_heart_rate_data": self.get_heart_rate_data,
            "get_stress_data": self.get_stress_data,
            
            # Blood and circulation
            "get_blood_glucose_data": self.get_blood_glucose_data,
            "get_oxygen_saturation_data": self.get_oxygen_saturation_data,
            "get_blood_pressure_data": self.get_blood_pressure_data,
            
            # Exercise and fitness
            "get_exercise_session_data": self.get_exercise_session_data,
            "get_calories_burned_data": self.get_calories_burned_data,
            "get_distance_data": self.get_distance_data,
            "get_exercise_heart_rate_data": self.get_exercise_heart_rate_data,
            "get_power_data": self.get_power_data,
            "get_speed_data": self.get_speed_data,
            "get_vo2max_data": self.get_vo2max_data,
            
            # Nutrition and body composition
            "get_nutrition_data": self.get_nutrition_data,
            "get_weight_data": self.get_weight_data,
            "get_body_fat_data": self.get_body_fat_data,
            "get_bmr_data": self.get_bmr_data,
            "get_height_data": self.get_height_data,
            
            # Additional health metrics
            "get_body_temperature_data": self.get_body_temperature_data,
            
            # Aliases for common queries
            "get_activity_data": self.get_steps_data,  # Alias for steps/activity
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
                "hours_slept": round(random.uniform(3.5, 5.5), 1),  # Poor sleep duration
                "quality": random.choice(["Poor", "Very Poor", "Restless"])
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
                "avg_heart_rate": random.randint(85, 110),  # Elevated resting HR
                "max_heart_rate": random.randint(160, 200)  # High maximum HR
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
                "stress_level": random.randint(65, 95)  # High stress levels (65-95/100)
            }
            stress_records.append(stress_record)
        
        return stress_records
    
    def get_steps_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get daily step count and activity patterns"""
        steps_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            steps_record = {
                "date": date.strftime("%Y-%m-%d"),
                "total_steps": random.randint(1200, 4500),  # Low activity levels
                "active_minutes": random.randint(5, 25),    # Very low active time
                "distance_km": round(random.uniform(0.8, 3.5), 2)  # Short distances
            }
            steps_records.append(steps_record)
        
        return steps_records
    
    def get_blood_glucose_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get blood sugar levels and glucose monitoring data"""
        glucose_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            glucose_record = {
                "date": date.strftime("%Y-%m-%d"),
                "fasting_glucose": round(random.uniform(110, 140), 1),  # Elevated/pre-diabetic range
                "post_meal_glucose": round(random.uniform(160, 220), 1), # High post-meal levels
                "hba1c_percentage": round(random.uniform(6.5, 8.5), 1)  # Diabetic range
            }
            glucose_records.append(glucose_record)
        
        return glucose_records
    
    def get_oxygen_saturation_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve blood oxygen saturation levels (SpO2)"""
        oxygen_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            oxygen_record = {
                "date": date.strftime("%Y-%m-%d"),
                "spo2_percentage": round(random.uniform(88, 94), 1),  # Below normal range
                "pulse_rate": random.randint(85, 120),  # Elevated pulse
                "measurement_time": f"{random.randint(6, 23):02d}:{random.randint(0, 59):02d}"
            }
            oxygen_records.append(oxygen_record)
        
        return oxygen_records
    
    def get_blood_pressure_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get systolic and diastolic blood pressure readings"""
        bp_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            bp_record = {
                "date": date.strftime("%Y-%m-%d"),
                "systolic": random.randint(140, 180),  # High blood pressure
                "diastolic": random.randint(90, 110),  # High diastolic
                "pulse_pressure": 0,  # Will calculate
                "category": ""  # Will determine based on readings
            }
            # Calculate pulse pressure
            bp_record["pulse_pressure"] = bp_record["systolic"] - bp_record["diastolic"]
            
            # Categorize blood pressure (will be high given the ranges)
            if bp_record["systolic"] < 120 and bp_record["diastolic"] < 80:
                bp_record["category"] = "Normal"
            elif bp_record["systolic"] < 130 and bp_record["diastolic"] < 80:
                bp_record["category"] = "Elevated"
            elif bp_record["systolic"] < 140 and bp_record["diastolic"] < 90:
                bp_record["category"] = "Stage 1 Hypertension"
            else:
                bp_record["category"] = "Stage 2 Hypertension"
            
            bp_records.append(bp_record)
        
        return bp_records
    
    def get_exercise_session_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve workout sessions and exercise activities"""
        exercise_records = []
        
        exercise_types = ["Light Walking", "Gentle Yoga", "Stretching"]  # Limited exercise types
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            # Low chance of exercise, indicating sedentary lifestyle
            if random.random() > 0.7:  # 30% chance of any exercise
                exercise_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "exercise_type": random.choice(exercise_types),
                    "duration_minutes": random.randint(5, 20),  # Very short sessions
                    "intensity": random.choice(["Low", "Very Low"]),  # Low intensity only
                    "calories_burned": random.randint(25, 80)  # Minimal calorie burn
                }
                exercise_records.append(exercise_record)
        
        return exercise_records
    
    def get_calories_burned_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get total calories burned during activities"""
        calories_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            calories_record = {
                "date": date.strftime("%Y-%m-%d"),
                "total_calories": random.randint(1400, 2000),  # Lower total burn
                "active_calories": random.randint(50, 200),    # Very low active calories
                "basal_calories": random.randint(1300, 1600),  # Lower basal rate
                "exercise_calories": random.randint(0, 100)    # Minimal exercise calories
            }
            calories_records.append(calories_record)
        
        return calories_records
    
    def get_distance_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve distance traveled during exercise"""
        distance_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            distance_record = {
                "date": date.strftime("%Y-%m-%d"),
                "total_distance_km": round(random.uniform(0.2, 2.0), 2),   # Very short distances
                "walking_distance_km": round(random.uniform(0.2, 1.5), 2), # Limited walking
                "running_distance_km": round(random.uniform(0, 0.5), 2),   # Minimal/no running
                "cycling_distance_km": round(random.uniform(0, 1.0), 2)    # Very little cycling
            }
            distance_records.append(distance_record)
        
        return distance_records
    
    def get_exercise_heart_rate_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get heart rate data during workouts"""
        exercise_hr_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            exercise_hr_record = {
                "date": date.strftime("%Y-%m-%d"),
                "avg_exercise_hr": random.randint(120, 180),
                "max_exercise_hr": random.randint(160, 200),
                "min_exercise_hr": random.randint(100, 140),
                "heart_rate_zones": {
                    "zone1_minutes": random.randint(0, 20),  # Recovery
                    "zone2_minutes": random.randint(0, 30),  # Aerobic base
                    "zone3_minutes": random.randint(0, 25),  # Aerobic
                    "zone4_minutes": random.randint(0, 15),  # Threshold
                    "zone5_minutes": random.randint(0, 10)   # Anaerobic
                }
            }
            exercise_hr_records.append(exercise_hr_record)
        
        return exercise_hr_records
    
    def get_power_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve power output during exercise sessions"""
        power_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            if random.random() > 0.5:  # 50% chance of power data (cycling/rowing)
                power_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "avg_power_watts": random.randint(150, 300),
                    "max_power_watts": random.randint(250, 500),
                    "normalized_power": random.randint(160, 320),
                    "power_duration_minutes": random.randint(20, 120)
                }
                power_records.append(power_record)
        
        return power_records
    
    def get_speed_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get speed and pace data during activities"""
        speed_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            speed_record = {
                "date": date.strftime("%Y-%m-%d"),
                "avg_speed_kmh": round(random.uniform(5.0, 25.0), 2),
                "max_speed_kmh": round(random.uniform(10.0, 35.0), 2),
                "avg_pace_min_km": f"{random.randint(3, 8)}:{random.randint(0, 59):02d}",
                "activity_type": random.choice(["Running", "Cycling", "Walking", "Swimming"])
            }
            speed_records.append(speed_record)
        
        return speed_records
    
    def get_vo2max_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve VO2 max and cardiorespiratory fitness data"""
        vo2max_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            if random.random() > 0.8:  # 20% chance (VO2 max not measured daily)
                vo2max_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "vo2max_ml_kg_min": round(random.uniform(20.0, 35.0), 1),  # Poor fitness range
                    "fitness_level": "",
                    "estimated_fitness_age": random.randint(45, 70)  # Poor fitness age
                }
                
                # Determine fitness level based on VO2 max (will be poor given range)
                vo2max_val = vo2max_record["vo2max_ml_kg_min"]
                if vo2max_val < 35:
                    vo2max_record["fitness_level"] = "Poor"
                elif vo2max_val < 45:
                    vo2max_record["fitness_level"] = "Fair"
                elif vo2max_val < 55:
                    vo2max_record["fitness_level"] = "Good"
                else:
                    vo2max_record["fitness_level"] = "Excellent"
                
                vo2max_records.append(vo2max_record)
        
        return vo2max_records
    
    def get_nutrition_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve dietary intake and nutritional information"""
        nutrition_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            nutrition_record = {
                "date": date.strftime("%Y-%m-%d"),
                "total_calories": random.randint(1200, 1800),  # Low calorie intake
                "protein_g": random.randint(25, 50),           # Insufficient protein
                "carbs_g": random.randint(200, 300),           # High carbs (processed foods)
                "fat_g": random.randint(60, 100),              # High fat intake
                "fiber_g": random.randint(5, 15),              # Low fiber
                "sugar_g": random.randint(60, 120),            # Very high sugar
                "sodium_mg": random.randint(3000, 4500),       # Excessive sodium
                "water_liters": round(random.uniform(0.5, 1.5), 1)  # Dehydration
            }
            nutrition_records.append(nutrition_record)
        
        return nutrition_records
    
    def get_weight_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve body weight measurements and trends"""
        weight_records = []
        base_weight = random.uniform(55.0, 95.0)  # Base weight for consistency
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            # Small daily variations around base weight
            weight_record = {
                "date": date.strftime("%Y-%m-%d"),
                "weight_kg": round(base_weight + random.uniform(-0.8, 0.8), 1),
                "weight_trend": random.choice(["Stable", "Increasing", "Decreasing"]),
                "measurement_time": f"{random.randint(6, 10):02d}:{random.randint(0, 59):02d}"
            }
            weight_records.append(weight_record)
        
        return weight_records
    
    def get_body_fat_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get body fat percentage and composition data"""
        body_fat_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            if random.random() > 0.7:  # 30% chance (body fat not measured daily)
                body_fat_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "body_fat_percentage": round(random.uniform(25.0, 40.0), 1),  # High body fat
                    "muscle_mass_kg": round(random.uniform(20.0, 30.0), 1),       # Low muscle mass
                    "bone_mass_kg": round(random.uniform(2.0, 3.0), 1),          # Lower bone mass
                    "visceral_fat_level": random.randint(10, 20)                 # High visceral fat
                }
                body_fat_records.append(body_fat_record)
        
        return body_fat_records
    
    def get_bmr_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve basal metabolic rate measurements"""
        bmr_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            bmr_record = {
                "date": date.strftime("%Y-%m-%d"),
                "bmr_calories": random.randint(1200, 2200),
                "rmr_calories": random.randint(1300, 2400),  # Resting metabolic rate
                "tdee_calories": random.randint(1800, 3500)   # Total daily energy expenditure
            }
            bmr_records.append(bmr_record)
        
        return bmr_records
    
    def get_height_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get height measurements and growth tracking"""
        height_records = []
        base_height = random.uniform(150.0, 190.0)  # Base height in cm
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            if random.random() > 0.9:  # 10% chance (height rarely changes)
                height_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "height_cm": round(base_height + random.uniform(-0.2, 0.2), 1),
                    "height_feet_inches": self._cm_to_feet_inches(base_height)
                }
                height_records.append(height_record)
        
        return height_records
    
    def get_body_temperature_data(self, patient_id: str, num_days: int = 7) -> List[Dict[str, Any]]:
        """Get body temperature readings and thermal regulation data"""
        temp_records = []
        
        for i in range(num_days):
            date = datetime.now() - timedelta(days=num_days-1-i)
            temp_record = {
                "date": date.strftime("%Y-%m-%d"),
                "body_temp_celsius": round(random.uniform(36.1, 37.8), 1),
                "body_temp_fahrenheit": 0,  # Will calculate
                "measurement_site": random.choice(["Oral", "Forehead", "Ear", "Wrist"]),
                "fever_status": ""
            }
            
            # Convert to Fahrenheit
            temp_record["body_temp_fahrenheit"] = round((temp_record["body_temp_celsius"] * 9/5) + 32, 1)
            
            # Determine fever status
            if temp_record["body_temp_celsius"] < 37.0:
                temp_record["fever_status"] = "Normal"
            elif temp_record["body_temp_celsius"] < 38.0:
                temp_record["fever_status"] = "Low-grade fever"
            else:
                temp_record["fever_status"] = "Fever"
            
            temp_records.append(temp_record)
        
        return temp_records
    
    def _cm_to_feet_inches(self, cm: float) -> str:
        """Convert centimeters to feet and inches format"""
        total_inches = cm / 2.54
        feet = int(total_inches // 12)
        inches = round(total_inches % 12, 1)
        return f"{feet}' {inches}\""

   
# Global instance
function_registry = FunctionRegistry()