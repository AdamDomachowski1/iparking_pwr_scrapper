#!/usr/bin/env python
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# ---------------------------
# PART 0: Remove previously generated output files (if they exist)
# ---------------------------
output_folder = "datasets"
# List of output files to remove (processed CSV files and the interactive HTML file)
files_to_remove = [
    os.path.join(output_folder, "polinka.csv"),
    os.path.join(output_folder, "parking_wrońskiego.csv"),
    os.path.join(output_folder, "d20_-_d21.csv"),
    os.path.join(output_folder, "parking_occupancy_visualization.html")
]

for file_path in files_to_remove:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed existing file: {file_path}")

# ---------------------------
# PART 1: Process raw parking history data and create processed CSV files
# ---------------------------
data_file = "parking_history_data.csv"
# List of parking location columns
parking_columns = ["Polinka", "Parking Wrońskiego", "D20 - D21", "GEO LO1 Geocentrum", "Architektura"]

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load raw data from the CSV file
try:
    data = pd.read_csv(data_file)
except FileNotFoundError:
    print(f"File {data_file} not found.")
    exit()

# Check if required columns exist in the data
required_columns = ['Data', 'Czas'] + parking_columns
if not all(column in data.columns for column in required_columns):
    print(f"The file {data_file} must contain the columns: {', '.join(required_columns)}.")
    exit()

# Process date and time into a single datetime column
data['Datetime'] = pd.to_datetime(data['Data'] + ' ' + data['Czas'], format='%Y-%m-%d %H:%M', errors='coerce')
data = data.dropna(subset=['Datetime'])
data['day_of_week'] = data['Datetime'].dt.dayofweek + 1  # Monday=1, Sunday=7
data['datetime_formatted'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M')
data = data.drop_duplicates(subset=['Data', 'Czas'])
# Exclude weekend measurements (Saturday=6 and Sunday=7)
data = data[~data['day_of_week'].isin([6, 7])]

# Process each parking column: clean data, remove outliers, and save as a new CSV file
for col in parking_columns:
    data[col] = pd.to_numeric(data[col], errors='coerce')
    clean_data = data.dropna(subset=[col])
    
    # Calculate mean and standard deviation for outlier removal
    mean_spots = clean_data[col].mean()
    std_spots = clean_data[col].std()
    clean_data = clean_data[(clean_data[col] > mean_spots - 3 * std_spots) &
                            (clean_data[col] < mean_spots + 3 * std_spots)]
    
    # Replace any negative values with 0
    clean_data[col] = clean_data[col].apply(lambda x: max(x, 0))
    
    # Prepare a basic DataFrame with formatted datetime and spots columns
    out_data = clean_data[['datetime_formatted', 'day_of_week', col]].rename(columns={
        'datetime_formatted': 'datetime', col: 'spots'
    })
    out_data = out_data.sort_values(by=['datetime', 'day_of_week']).reset_index(drop=True)
    
    # Save the processed data to CSV
    output_file = os.path.join(output_folder, f"{col.replace(' ', '_').lower()}.csv")
    out_data.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

print("Data processing complete. Processed files saved in the 'datasets' folder.")

# ---------------------------
# PART 2: Basic analysis of each CSV file in the output folder
# ---------------------------
# List all CSV files in the output folder
csv_files = [file for file in os.listdir(output_folder) if file.endswith('.csv')]
for file_name in csv_files:
    file_path = os.path.join(output_folder, file_name)
    print(f"\nAnalyzing file: {file_path}")
    try:
        df = pd.read_csv(file_path)
        if 'spots' in df.columns:
            # Count records where spots equals 0
            zero_spots_count = (df['spots'] == 0).sum()
            total_records = len(df)
            zero_spots_percentage = (zero_spots_count / total_records) * 100
            max_spots = df['spots'].max()
            
            print(f"Number of records where spots = 0: {zero_spots_count}")
            print(f"Total number of records: {total_records}")
            print(f"Percentage of records where spots = 0: {zero_spots_percentage:.2f}%")
            print(f"Maximum number of spots: {max_spots}")
        else:
            print("The 'spots' column does not exist in the data.")
    except Exception as e:
        print(f"Error while processing file {file_name}: {e}")
    print("-" * 40)

# ---------------------------
# PART 3: Generate heatmaps for selected parking CSV files
# ---------------------------
# Define the list of files and their corresponding parking names for analysis
files_to_analyze = [
    (os.path.join(output_folder, f"{col.replace(' ', '_').lower()}.csv"), col)
    for col in parking_columns
]

for file_path, parking_name in files_to_analyze:
    try:
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['month_year'] = df['datetime'].dt.to_period('M')
        df['day_name'] = df['datetime'].dt.day_name(locale='pl_PL')
        df = df[df['month_year'].dt.month != 1]
        df['is_problem'] = df['spots'] == 0

        problem_analysis = df.groupby(['month_year', 'day_name'])['is_problem'].mean() * 100
        problem_analysis_df = problem_analysis.unstack(level=-1).fillna(0)
        ordered_days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
        problem_analysis_df = problem_analysis_df.reindex(columns=ordered_days)

        plt.figure(figsize=(10, 6))
        sns.heatmap(problem_analysis_df.T, annot=True, fmt=".1f", cmap="Reds",
                    cbar_kws={'label': 'Percentage of problematic cases (%)'})
        plt.title(f"Heatmap of problem occurrence - {parking_name}")
        plt.xlabel("Month")
        plt.ylabel("Day of the week")
        plt.tight_layout()
        plt.show()

        print(f"\nProblem analysis for {parking_name}:")
        print(problem_analysis_df)
    except Exception as e:
        print(f"Error processing heatmap for {parking_name}: {e}")

# ---------------------------
# PART 4: Combine processed CSV files and create an interactive Plotly line chart
# ---------------------------
# List of processed parking CSV files to combine
parking_files = [f"{col.replace(' ', '_').lower()}.csv" for col in parking_columns]

all_data = []
for file in parking_files:
    file_path = os.path.join(output_folder, file)
    if os.path.exists(file_path):
        parking_data = pd.read_csv(file_path)
        parking_data['Parking Location'] = file.replace("_", " ").replace(".csv", "").title()
        all_data.append(parking_data)
    else:
        print(f"File {file} does not exist in the {output_folder} folder.")

if not all_data:
    print("No data available to create an interactive plot.")
    exit()

data_combined = pd.concat(all_data, ignore_index=True)
data_combined['datetime'] = pd.to_datetime(data_combined['datetime'], format='%Y-%m-%d %H:%M', errors='coerce')
data_combined = data_combined.dropna(subset=['datetime'])

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

# Save the interactive plot as an HTML file
html_output = os.path.join(output_folder, 'parking_occupancy_visualization.html')
fig.write_html(html_output)
print(f"\nInteractive plot saved as {html_output}. Open this file in a browser to view it.")
