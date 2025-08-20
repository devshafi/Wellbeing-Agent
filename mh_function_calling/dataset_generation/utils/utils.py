import pandas as pd
import csv

def load_health_functions(csv_path):
    """Load functions from your health_functions.csv"""
    functions = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            functions.append({
                'health_data': row['Health Data'],
                'datatype': row['DataType'], 
                'function_name': row['Function'],
                'description': row['Description']
            })
    return functions

def save_samples_to_csv(all_samples, filename='mental_health_dataset.csv'):
    """Save all samples to CSV file"""
    
    # Convert samples to DataFrame
    df = pd.DataFrame(all_samples)
    
    # Save to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"✅ Saved {len(all_samples)} samples to {filename}")
    