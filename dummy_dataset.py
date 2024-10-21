import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set a random seed for reproducibility
np.random.seed(42)

# Generate the original random data for Water content and time until failure
water_content = np.random.uniform(1, 100, 500)
time_until_failure = (3000 / water_content) + np.random.normal(0, 50, size=water_content.shape)

# Create DataFrame with the original columns
data = pd.DataFrame({
    'Water Content (ppm)': water_content,
    'Time Until Failure (hours)': time_until_failure
})

# Add 'Ship Name' and 'Fuel Tank' columns
data['Ship Name'] = 'HMS NONSUCH'
data['Fuel Tank'] = np.random.choice(['Fuel Tank 1', 'Fuel Tank 2', 'Fuel Tank 3', 'Fuel Tank 4'], size=len(data))

# Add a 'Date' column for when the sample was taken
start_date = datetime.now() - timedelta(days=30)  # Start date 30 days ago
dates = [start_date + timedelta(days=np.random.randint(0, 30)) for _ in range(len(data))]  # Random date within the last 30 days
data['Date'] = [d.date() for d in pd.to_datetime(dates)]  # Convert to date format (YYYY-MM-DD)

# Round water content and time until failure to 2 significant figures
data['Water Content (ppm)'] = np.round(data['Water Content (ppm)'], 2)
data['Time Until Failure (hours)'] = np.round(data['Time Until Failure (hours)'], 2)

# Define engine IDs and names
engine_mapping = {
    'Engine 1': 'ENG1001',
    'Engine 2': 'ENG1002',
    'Engine 3': 'ENG1003',
    'Engine 4': 'ENG1004'
}

# Generate random failure reports for 4 engines corresponding to 4 fuel tanks
num_reports = 10
failure_reports = []

for _ in range(num_reports):
    # Randomly select an engine (and its corresponding fuel tank)
    engine_index = np.random.randint(0, 4)  # Select engine index from 0 to 3
    engine_name = f'Engine {engine_index + 1}'
    fuel_tank = f'Fuel Tank {engine_index + 1}'
    engine_id = engine_mapping[engine_name]

    # Generate random time until failure and failure date
    time_until_failure = np.random.uniform(50, 3000)  # Random time until failure between 50 and 3000 hours
    failure_date = (datetime.now() - timedelta(hours=time_until_failure)).date()  # Failure date

    # Append the report to the list, ensuring time until failure is non-negative
    failure_reports.append({
        'Engine Name': engine_name,
        'Engine ID': engine_id,  # Consistent engine ID
        'Fuel Pump Location': f'Cyl. {np.random.randint(1, 17)}',  # Randomly chosen cylinder from 1 to 16
        'Fuel Pump Model': "Wartsila",  # Fuel pump model (always Wartsila)
        'Time Until Failure (hours)': max(0, time_until_failure),  # Ensure non-negative
        'Date of Failure': failure_date,
        'Fuel Tank': fuel_tank
    })

# Create a DataFrame from the failure reports
failure_reports_df = pd.DataFrame(failure_reports)

# Merge the data and failure reports based on 'Fuel Tank' and 'Date'
merged_data = pd.merge(data, failure_reports_df, left_on=['Fuel Tank', 'Date'], right_on=['Fuel Tank', 'Date of Failure'], how='left')

# Drop the Time Until Failure_x column, if it exists, to avoid confusion
if 'Time Until Failure (hours)_x' in merged_data.columns:
    merged_data.drop(columns=['Time Until Failure (hours)_x'], inplace=True)

# Rename the water content column to have a suffix
merged_data.rename(columns={'Water Content (ppm)': 'Water Content (ppm)_x'}, inplace=True)

# Add a column for Fuel Tank Feed based on Engine Name
merged_data['Fuel Tank Feed'] = merged_data['Engine Name']

# Rearrange the columns in the specified order
final_columns = [
    'Ship Name',
    'Fuel Tank',
    'Date',
    'Water Content (ppm)_x',
    'Engine Name',
    'Engine ID',
    'Fuel Tank Feed',
    'Fuel Pump Location',
    'Fuel Pump Model',
    'Time Until Failure (hours)',  # Ensure this is the correct column
    'Date of Failure'
]

# Rename the time until failure column to ensure it matches
if 'Time Until Failure (hours)_y' in merged_data.columns:
    merged_data.rename(columns={'Time Until Failure (hours)_y': 'Time Until Failure (hours)'}, inplace=True)

# Reorder the DataFrame to the final column order
merged_data = merged_data[final_columns]

# Create a timestamp for the filename
file_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Define the path to the public directory and ensure it exists
public_directory = os.path.expanduser('./public')  # Save to the public folder in your home directory
os.makedirs(public_directory, exist_ok=True)  # Create the directory if it doesn't exist

# Save the merged DataFrame to the public directory
merged_filename = f'{public_directory}/full_fuel_analysis_with_failures_{file_timestamp}.csv'

# Save the merged data
merged_data.to_csv(merged_filename, index=False)

print(f'Full dataset with failures saved as {merged_filename}')
