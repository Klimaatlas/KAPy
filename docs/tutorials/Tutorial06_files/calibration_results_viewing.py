#Code for comparing output from multipl bias adjustment methods. This is an example for the Ashanti region 
import pandas as pd
import matplotlib.pyplot as plt

# For obs data
data_o = pd.read_csv("./outputs/6.areal_statistics/ensstats/101-scaling_ERA5_Ghana025_no-expt_ensstats.csv")
filter_conditions_o = {'area': 'GH02', 'percentiles': 50}

# Initialize plot
plt.figure(figsize=(12, 6))

# Plot ERA5 data
for indID, color in zip(['GH02'], ['black']):
    filtered_data = data_o[(data_o['area'] == indID) & 
                           (data_o[list(filter_conditions_o.keys())] == pd.Series(filter_conditions_o)).all(axis=1)].copy()
    filtered_data['time'] = pd.to_datetime(filtered_data['time'])
    filtered_data.set_index('time', inplace=True)
    plt.plot(filtered_data.index, filtered_data['mean'], label="ERA5", color=color)

# For CORDEX data
data = pd.read_csv("./outputs/6.areal_statistics/Areal_statistics.csv")
filter_conditions = {'area': 'GH02', 'percentiles': 50,'srcID': 'CORDEX', 'gridID': 'Ghana025','expt': 'rcp85', 'memberID': 'ensstats'}

# Plot CORDEX data for each indID
for indID, color in zip(['101-nocal', '101-scaling', '101-dqm', '101-eqm'], 
                        ['green', 'orange', 'blue', 'red']):
    filtered_data = data[(data['indID'] == indID) & 
                         (data[list(filter_conditions.keys())] == pd.Series(filter_conditions)).all(axis=1)].copy()
    filtered_data['time'] = pd.to_datetime(filtered_data['time'])
    filtered_data.set_index('time', inplace=True)
    plt.plot(filtered_data.index, filtered_data['mean'], label=indID, color=color)

plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Time Series for Different Indicators')
plt.legend()
plt.grid(True)
plt.show()
