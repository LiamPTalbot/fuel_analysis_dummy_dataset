import numpy as np
from datetime import datetime
import pandas as pd

# Re-define ship and fuel tank options
ships = ['QNLZ', 'PWLS']
fuel_tanks = ['FWD DG RU', 'AFT DG RU']

# Date range for the dataset (from Jan 2021 to Oct 2024, monthly data)
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 10, 1)
date_range = pd.date_range(start=start_date, end=end_date, freq='MS')  # Month start frequency

# Function to gradually degrade values
def gradual_degrade(start_value, months, drift=0.01, noise=0.005):
    return np.clip([start_value - (i * drift) + np.random.normal(0, noise) for i in range(months)], 0, None)

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
    
    # Failure time reduces with bad quality
    time_til_failure = max(200, base_failure_time / degradation_factor)
    
    return round(time_til_failure, 2)

# Generate the dataset
data = []
for ship in ships:
    for fuel_tank in fuel_tanks:
        # Initialize starting points for each ship and fuel tank
        density = np.random.uniform(*density_range)
        water_reaction = np.random.uniform(*water_reaction_range)
        flash_point = np.random.uniform(*flash_point_range)
        filter_block = np.random.uniform(*filter_block_range)
        cloud_point = np.random.uniform(*cloud_point_range)
        sulphur = np.random.uniform(*sulphur_range)
        cfu = np.random.uniform(*cfu_range)
        water_content = np.random.uniform(*water_content_range)
        
        # Introduce gradual degradation
        density_vals = gradual_degrade(density, len(date_range), drift=0.5)
        water_reaction_vals = gradual_degrade(water_reaction, len(date_range), drift=0.1)
        flash_point_vals = gradual_degrade(flash_point, len(date_range), drift=0.5)
        filter_block_vals = gradual_degrade(filter_block, len(date_range), drift=0.2)
        cloud_point_vals = gradual_degrade(cloud_point, len(date_range), drift=0.2)
        sulphur_vals = gradual_degrade(sulphur, len(date_range), drift=0.01)
        cfu_vals = gradual_degrade(cfu, len(date_range), drift=5)
        water_content_vals = gradual_degrade(water_content, len(date_range), drift=10)
        
        # Occasionally reset the values to simulate cleaning the fuel tank
        reset_points = np.random.choice(range(len(date_range)), size=3, replace=False)
        for rp in reset_points:
            density_vals[rp] = np.random.uniform(*density_range)
            water_reaction_vals[rp] = np.random.uniform(*water_reaction_range)
            flash_point_vals[rp] = np.random.uniform(*flash_point_range)
            filter_block_vals[rp] = np.random.uniform(*filter_block_range)
            cloud_point_vals[rp] = np.random.uniform(*cloud_point_range)
            sulphur_vals[rp] = np.random.uniform(*sulphur_range)
            cfu_vals[rp] = np.random.uniform(*cfu_range)
            water_content_vals[rp] = np.random.uniform(*water_content_range)

        # Create rows for each month
        for i, date in enumerate(date_range):
            data.append([
                ship, fuel_tank, date.strftime('%Y-%m-%d'), 
                round(density_vals[i], 2), 
                round(water_reaction_vals[i], 2), 
                round(flash_point_vals[i], 2), 
                round(filter_block_vals[i], 2), 
                round(cloud_point_vals[i], 2), 
                round(sulphur_vals[i], 3), 
                round(cfu_vals[i], 2), 
                round(water_content_vals[i], 2)
            ])

# Create DataFrame
columns = ['Ship', 'Fuel Tank', 'Date', 'Density (kg/m3)', 'Water Reaction Vol Change (ml)', 
           'Flash Point (celsius)', 'Filter Blocking Tendency', 'Cloud Point (celsius)', 
           'Sulphur (%)', 'Colony Forming Units (CFU/ml)', 'Water content (mg/kg)']

df = pd.DataFrame(data, columns=columns)

# Generate failure data for all pumps on DG1, DG2 (16 pumps each) and DG3, DG4 (12 pumps each)
failure_data_complete = []
for _, row in df.iterrows():
    ship = row['Ship']
    fuel_tank = row['Fuel Tank']
    
    # Define engines and their pump counts based on fuel tank
    if fuel_tank == 'FWD DG RU':
        engines = {'DG1': 16, 'DG2': 16}  # DG1 and DG2 each have 16 pumps
    else:
        engines = {'DG3': 12, 'DG4': 12}  # DG3 and DG4 each have 12 pumps
    
    # Generate data for each engine and all pumps in that engine
    for engine, num_pumps in engines.items():
        for pump_num in range(1, num_pumps + 1):
            # Generate time til failure based on fuel quality
            time_til_failure = generate_failure_time(row)
            
            # Append the detailed failure data to the dataset
            failure_data_complete.append({
                'Ship': ship,
                'Engine': engine,
                'Engine ID': f'{ship}_{engine}',
                'Fuel Pump ID': f'{engine}_Pump_{pump_num}',
                'Time Til Failure (hours)': time_til_failure,
                'Fuel Tank Feed': fuel_tank
            })

# Convert the complete failure data to a DataFrame
failure_df_complete = pd.DataFrame(failure_data_complete)

# Merge the failure data with the original dataset
merged_df_complete = pd.concat([df.reset_index(drop=True), failure_df_complete.reset_index(drop=True)], axis=1)

# Reorder columns as specified
cols_order_complete = ['Ship', 'Engine', 'Engine ID', 'Fuel Pump ID', 'Time Til Failure (hours)', 'Fuel Tank Feed', 
                       'Fuel Tank', 'Date', 'Density (kg/m3)', 'Water Reaction Vol Change (ml)', 'Flash Point (celsius)', 
                       'Filter Blocking Tendency', 'Cloud Point (celsius)', 'Sulphur (%)', 
                       'Colony Forming Units (CFU/ml)', 'Water content (mg/kg)']

# Reorder the dataframe according to specified column order
reordered_df_complete = merged_df_complete[cols_order_complete]

# Remove the 'Fuel Tank' column and save to CSV
csv_output_path_complete = './complete_ship_fuel_analysis.csv'
reordered_df_complete.to_csv(csv_output_path_complete, index=False)

print(f"Data has been saved to {csv_output_path_complete}")
