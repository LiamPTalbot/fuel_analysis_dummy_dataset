import numpy as np
from datetime import datetime
import pandas as pd

# Define ship and fuel tank options
ships = ['QNLZ', 'PWLS']
fuel_tanks = {'FWD DG RU': ['DG1', 'DG2'], 'AFT DG RU': ['DG3', 'DG4']}

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
cumulative_hours = {ship: {engine: {pump: 0 for pump in range(1, 17)} if engine in ['DG1', 'DG2'] else {pump: 0 for pump in range(1, 13)}
                            for engine in ['DG1', 'DG2', 'DG3', 'DG4']}
                    for ship in ships}

for ship in ships:
    for fuel_tank, engines in fuel_tanks.items():
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

        # Create rows for each month and engine
        for i, date in enumerate(date_range):
            for engine in engines:
                # Determine number of pumps based on engine
                num_pumps = 16 if engine in ['DG1', 'DG2'] else 12
                for pump_num in range(1, num_pumps + 1):
                    # Update cumulative hours
                    fuel_quality = {
                        'Colony Forming Units (CFU/ml)': cfu_vals[i],
                        'Water content (mg/kg)': water_content_vals[i],
                        'Filter Blocking Tendency': filter_block_vals[i]
                    }
                    if cumulative_hours[ship][engine][pump_num] == 0 or cumulative_hours[ship][engine][pump_num] >= generate_failure_time(fuel_quality):
                        # Reset failure time on reaching limit
                        time_til_failure = generate_failure_time(fuel_quality)
                        cumulative_hours[ship][engine][pump_num] = 0  # Simulate maintenance/reset on failure
                    else:
                        time_til_failure = None  # No failure this month
                    
                    cumulative_hours[ship][engine][pump_num] += 730  # 730 hours per month on average

                    data.append([
                        ship, engine, f'{ship}_{engine}', f'{engine}_Pump_{pump_num}', time_til_failure,
                        fuel_tank, date.strftime('%Y-%m-%d'), 
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
columns = ['Ship', 'Engine', 'Engine ID', 'Fuel Pump ID', 'Time Til Failure (hours)', 'Fuel Tank Feed', 'Date', 
           'Density (kg/m3)', 'Water Reaction Vol Change (ml)', 'Flash Point (celsius)', 
           'Filter Blocking Tendency', 'Cloud Point (celsius)', 'Sulphur (%)', 
           'Colony Forming Units (CFU/ml)', 'Water content (mg/kg)']

df_complete = pd.DataFrame(data, columns=columns)

# Save to CSV
csv_output_path_complete = './complete_ship_fuel_analysis.csv'
df_complete.to_csv(csv_output_path_complete, index=False)

print(f"Data has been saved to {csv_output_path_complete}")
