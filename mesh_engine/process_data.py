import pandas as pd
from pathlib import Path

# This finds the folder where THIS script is saved
base_path = Path(__file__).resolve().parent.parent
data_file = base_path / "data" / "FileList.csv"

print(f"Searching for data at: {data_file}")

# 1. Load the patient index safely
try:
    df = pd.read_csv(data_file)
    print(" Successfully loaded FileList.csv!")
    
    # 2. Find test cases
    healthy_patient = df[df['EF'] > 60].iloc[0]
    damaged_patient = df[df['EF'] < 35].iloc[0]

    print(f"\n--- Project Test Cases ---")
    print(f"HEALTHY: File {healthy_patient['FileName']} | EF: {healthy_patient['EF']}%")
    print(f"DAMAGED: File {damaged_patient['FileName']} | EF: {damaged_patient['EF']}%")

except FileNotFoundError:
    print("❌ ERROR: FileList.csv not found! Please check your /data folder.")
except Exception as e:
    print(f"❌ ERROR: {e}")