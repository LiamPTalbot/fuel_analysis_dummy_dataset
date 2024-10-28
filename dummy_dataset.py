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
    cfu = max(fuel_quality['Colony Forming Units (CFU/ml)'], 1)  # Avoid zero CFU
    water_content = max(fuel_quality['Water content (mg/kg)'], 1)  # Avoid zero water content
    filter_block = max(fuel_quality['Filter Blocking Tendency'], 1)  # Avoid zero filter block
    
    # Base failure time (10,000 hours for good fuel)
    base_failure_time = 10000
    degradation_factor = ((cfu / 100) + (water_content / 200) + filter_block / 3) * np.random.uniform(0.8, 1.2)
    
    # Failure time reduces with worse quality
    time_til_failure = max(200, base_failure_time / degradation_factor)
    
    return round(time_til_failure, 2)

# Generate the dataset
data = []
for ship in ships:
    for fuel_tank, engines in fuel_tanks.items():
        for engine in engines:
            # Set number of pumps per engine
            num_pumps = 16 if engine in ['DG1', 'DG2'] else 12
            for pump_num in range(1, num_pumps + 1):
                # Initialize failure tracking for each pump
                current_date = start_date
                
                while current_date < end_date:
                    # Randomly generate initial fuel quality values
                    density = np.random.uniform(*density_range)
                    water_reaction = np.random.uniform(*water_reaction_range)
                    flash_point = np.random.uniform(*flash_point_range)
                    filter_block = np.random.uniform(*filter_block_range)
                    cloud_point = np.random.uniform(*cloud_point_range)
                    sulphur = np.random.uniform(*sulphur_range)
                    cfu = np.random.uniform(*cfu_range)
                    water_content = np.random.uniform(*water_content_range)

                    # Pack fuel quality data into dictionary
                    fuel_quality = {
                        'Colony Forming Units (CFU/ml)': cfu,
                        'Water content (mg/kg)': water_content,
                        'Filter Blocking Tendency': filter_block
                    }

                    # Calculate time until next failure based on fuel quality
                    time_til_failure = generate_failure_time(fuel_quality)

                    # Calculate the failure date based on hours until failure
                    failure_days = int(time_til_failure / 24)  # Convert hours to days
                    failure_date = current_date + timedelta(days=failure_days)

                    # Check if failure date is within dataset range
                    if failure_date <= end_date:
                        # Append failure report data to dataset
                        data.append([
                            ship, engine, f'{ship}_{engine}', f'{engine}_Pump_{pump_num}', time_til_failure,
                            fuel_tank, failure_date.strftime('%Y-%m-%d'), 
                            round(density, 2), 
                            round(water_reaction, 2), 
                            round(flash_point, 2), 
                            round(filter_block, 2), 
                            round(cloud_point, 2), 
                            round(sulphur, 3), 
                            round(cfu, 2), 
                            round(water_content, 2)
                        ])

                        # Update the current date to reflect maintenance/replacement
                        current_date = failure_date + timedelta(days=1)
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
csv_output_path = './complete_ship_fuel_failures.csv'
df_failures.to_csv(csv_output_path, index=False)

print(f"Data has been saved to {csv_output_path}")
