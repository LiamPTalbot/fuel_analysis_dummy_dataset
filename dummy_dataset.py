import numpy as np
from datetime import datetime, timedelta
import pandas as pd

# Define ships, engines, and fuel tank mappings
ships = ['QNLZ', 'PWLS']
fuel_tanks = {'FWD DG RU': ['DG1', 'DG2'], 'AFT DG RU': ['DG3', 'DG4']}

# Time frame for the dataset
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 10, 1)

# Normal ranges for fuel quality measurements
density_range = (800, 820)  # kg/m3
water_reaction_range = (0.5, 2.5)  # ml
flash_point_range = (60, 70)  # Celsius
filter_block_range = (1.0, 3.0)  # Filter Blocking Tendency
cloud_point_range = (-10, 5)  # Celsius
sulphur_range = (0.05, 0.3)  # Sulphur %
cfu_range = (10, 100)  # Colony Forming Units per ml
water_content_range = (50, 200)  # mg/kg

# Function to generate failure time based on fuel quality
def generate_failure_time(fuel_quality):
    cfu = max(fuel_quality['Colony Forming Units (CFU/ml)'], 1)
    water_content = max(fuel_quality['Water content (mg/kg)'], 1)
    filter_block = max(fuel_quality['Filter Blocking Tendency'], 1)
    
    # Base failure time (10,000 hours for good fuel)
    base_failure_time = 10000
    degradation_factor = ((cfu / 100) + (water_content / 200) + filter_block / 3) * np.random.uniform(0.8, 1.2)
    
    # Failure time reduces with worse quality
    time_til_failure = max(200, base_failure_time / degradation_factor)
    
    return round(time_til_failure, 2)

# Function to reset fuel quality during refuel or cleaning
def reset_fuel_quality(base_values):
    return {metric: base + np.random.normal(0, deviation)
            for metric, (base, deviation) in base_values.items()}

# Generate the dataset with degradation, periodic cleaning, and refuel
data = []
for ship in ships:
    # Define base fuel quality for the ship's initial refuel
    base_values = {
        'Density': (np.random.uniform(*density_range), 1),
        'Water Reaction Vol Change': (np.random.uniform(*water_reaction_range), 0.1),
        'Flash Point': (np.random.uniform(*flash_point_range), 1),
        'Filter Blocking Tendency': (np.random.uniform(*filter_block_range), 0.2),
        'Cloud Point': (np.random.uniform(*cloud_point_range), 0.5),
        'Sulphur (%)': (np.random.uniform(*sulphur_range), 0.02),
        'Colony Forming Units (CFU/ml)': (np.random.uniform(*cfu_range), 10),
        'Water content (mg/kg)': (np.random.uniform(*water_content_range), 15)
    }
    
    for fuel_tank, engines in fuel_tanks.items():
        for engine in engines:
            # Determine number of pumps per engine
            num_pumps = 16 if engine in ['DG1', 'DG2'] else 12
            for pump_num in range(1, num_pumps + 1):
                current_date = start_date
                fuel_quality = reset_fuel_quality(base_values)  # Initial refuel

                while current_date < end_date:
                    # Apply gradual degradation before calculating time til failure
                    for metric in fuel_quality:
                        fuel_quality[metric] += np.random.normal(0.05, 0.02)

                    # Calculate time until next failure based on degraded fuel quality
                    time_til_failure = generate_failure_time({
                        'Colony Forming Units (CFU/ml)': fuel_quality['Colony Forming Units (CFU/ml)'],
                        'Water content (mg/kg)': fuel_quality['Water content (mg/kg)'],
                        'Filter Blocking Tendency': fuel_quality['Filter Blocking Tendency']
                    })

                    # Calculate the failure date based on hours until failure
                    failure_days = int(time_til_failure / 24)  # Convert hours to days
                    failure_date = current_date + timedelta(days=failure_days)

                    # Check if failure date is within dataset range
                    if failure_date <= end_date:
                        # Append failure report data to dataset
                        data.append([
                            ship, engine, f'{ship}_{engine}', f'{engine}_Pump_{pump_num}', time_til_failure,
                            fuel_tank, failure_date.strftime('%Y-%m-%d'), 
                            round(fuel_quality['Density'], 2), 
                            round(fuel_quality['Water Reaction Vol Change'], 2), 
                            round(fuel_quality['Flash Point'], 2), 
                            round(fuel_quality['Filter Blocking Tendency'], 2), 
                            round(fuel_quality['Cloud Point'], 2), 
                            round(fuel_quality['Sulphur (%)'], 3), 
                            round(fuel_quality['Colony Forming Units (CFU/ml)'], 2), 
                            round(fuel_quality['Water content (mg/kg)'], 2)
                        ])

                        # Update current date to reflect pump maintenance/replacement
                        current_date = failure_date + timedelta(days=1)

                        # Every 4-6 months, reset fuel quality to simulate cleaning/refueling
                        if np.random.rand() < 1/6:  # Approximate every 6th failure
                            fuel_quality = reset_fuel_quality(base_values)
                    else:
                        # If the failure date exceeds the dataset range, end loop for this pump
                        break

# Create DataFrame
columns = ['Ship', 'Engine', 'Engine ID', 'Fuel Pump ID', 'Time Til Failure (hours)', 'Fuel Tank Feed', 'Date', 
           'Density (kg/m3)', 'Water Reaction Vol Change (ml)', 'Flash Point (celsius)', 
           'Filter Blocking Tendency', 'Cloud Point (celsius)', 'Sulphur (%)', 
           'Colony Forming Units (CFU/ml)', 'Water content (mg/kg)']

df_failures = pd.DataFrame(data, columns=columns)

# Save to CSV
csv_output_path = './complete_ship_fuel_analysis.csv'
df_failures.to_csv(csv_output_path, index=False)

print(f"Data has been saved to {csv_output_path}")
