import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# Path to the input file
data_file = "parking_history_data.csv"

# Parking names
parking_columns = ["Polinka", "Parking Wrońskiego", "D20 - D21", "GEO LO1 Geocentrum", "Architektura"]

# Path to the output folder
output_folder = "datasets"
os.makedirs(output_folder, exist_ok=True)

# Load data
try:
    data = pd.read_csv(data_file)
except FileNotFoundError:
    print(f"File {data_file} not found.")
    exit()

# Check required columns
required_columns = ['Data', 'Czas'] + parking_columns
if not all(column in data.columns for column in required_columns):
    print(f"The file {data_file} must contain columns: {', '.join(required_columns)}.")
    exit()

# Process date and time into a datetime column
data['Datetime'] = pd.to_datetime(data['Data'] + ' ' + data['Czas'], format='%Y-%m-%d %H:%M', errors='coerce')

# Remove invalid dates
data = data.dropna(subset=['Datetime'])

# Add day of the week and formatted datetime columns
data['day_of_week'] = data['Datetime'].dt.dayofweek + 1  # Monday = 1, Sunday = 7
data['datetime_formatted'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M')

# Remove duplicates
data = data.drop_duplicates(subset=['Data', 'Czas'])

# Exclude weekend measurements (Saturday and Sunday)
data = data[~data['day_of_week'].isin([6, 7])]

# Process data for each parking
for col in parking_columns:
    # Convert to numeric values
data[col] = pd.to_numeric(data[col], errors='coerce')

    # Remove missing values for the current parking
    clean_data = data.dropna(subset=[col])

    # Calculate mean and standard deviation
    mean_spots = clean_data[col].mean()
    std_spots = clean_data[col].std()

    # Remove outliers (3 standard deviations from the mean)
    clean_data = clean_data[(clean_data[col] > mean_spots - 3 * std_spots) &
                            (clean_data[col] < mean_spots + 3 * std_spots)]

    # Replace negative values with 0
    clean_data[col] = clean_data[col].apply(lambda x: max(x, 0))

    # Create a basic DataFrame
    out_data = clean_data[['datetime_formatted', 'day_of_week', col]].rename(columns={
        'datetime_formatted': 'datetime', col: 'spots'
    })

    # Sort the data
    out_data = out_data.sort_values(by=['datetime', 'day_of_week']).reset_index(drop=True)

    # Save to file
    output_file = os.path.join(output_folder, f"{col.replace(' ', '_').lower()}.csv")
    out_data.to_csv(output_file, index=False)

print("Data processing complete. Results saved in the 'datasets' folder.")

# Directory with processed data
parking_files = [
    "polinka.csv",
    "parking_wrońskiego.csv",
    "d20_-_d21.csv",
    # "geo_lo1_geocentrum.csv",
    # "architektura.csv"
]

# Load data from files and combine them
all_data = []
for file in parking_files:
    file_path = os.path.join(output_folder, file)
    if os.path.exists(file_path):
        parking_data = pd.read_csv(file_path)
        parking_data['Parking Location'] = file.replace("_", " ").replace(".csv", "").title()
        all_data.append(parking_data)
    else:
        print(f"File {file} does not exist in the {output_folder} folder.")

# Combine all data into one DataFrame
if not all_data:
    print("No data to visualize.")
    exit()

data_combined = pd.concat(all_data, ignore_index=True)

# Convert the datetime column to datetime type
data_combined['datetime'] = pd.to_datetime(data_combined['datetime'], format='%Y-%m-%d %H:%M', errors='coerce')

# Remove invalid dates
data_combined = data_combined.dropna(subset=['datetime'])

# Create an interactive plot
fig = px.line(
    data_combined,
    x='datetime',
    y='spots',
    color='Parking Location',
    title='Parking Occupancy Over Time',
    labels={'spots': 'Occupancy', 'datetime': 'Time'},
    line_group='Parking Location',
    hover_data={'datetime': '|%Y-%m-%d %H:%M', 'Parking Location': True}
)

# Update the layout of the plot
fig.update_layout(
    xaxis_title='Time',
    yaxis_title='Occupancy',
    xaxis=dict(tickformat="%a\n%b %d"),
    template='plotly_white'
)

# Save the plot as an HTML file
output_file_path = os.path.join(output_folder, 'parking_occupancy_visualization.html')
fig.write_html(output_file_path)

print(f"Interactive plot saved as {output_file_path}. Open this file in a browser to view it.")
