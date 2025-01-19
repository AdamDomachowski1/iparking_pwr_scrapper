import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create folders for diagrams and reports
output_folder_diagrams = "diagrams"
output_folder_reports = "reports"
os.makedirs(output_folder_diagrams, exist_ok=True)
os.makedirs(output_folder_reports, exist_ok=True)

# List of files to analyze
files = [
    ('datasets/d20_-_d21.csv', 'Parking D20-D21'),
    ('datasets/parking_wrońskiego.csv', 'Parking Wrońskiego'),
    ('datasets/polinka.csv', 'Parking Polinka')
]

# Order of weekdays
ordered_days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']

# Loop to process data for each file
for file_path, parking_name in files:
    # Load the data
    data = pd.read_csv(file_path)
    
    # Convert the 'datetime' column to datetime format
    data['datetime'] = pd.to_datetime(data['datetime'])
    
    # Add columns for hour, day of the week, and month
    data['hour'] = data['datetime'].dt.hour
    data['minute'] = data['datetime'].dt.minute
    data['time'] = data['hour'] + data['minute'] / 60  # Hour in decimal format
    data['time_hhmm'] = data['datetime'].dt.strftime('%H:%M')  # Format hh:mm
    data['day_name'] = pd.Categorical(data['datetime'].dt.day_name(locale='pl_PL'), categories=ordered_days, ordered=True)
    data['month_year'] = data['datetime'].dt.to_period('M')
    data['month'] = data['datetime'].dt.month  # Month number

    # Remove data from January
    data = data[data['month'] != 1]
    
    # Analyze hours when the parking is fully occupied
    data['is_full'] = data['spots'] == 0  # True if the parking is full

    # Create a textual report for the parking lot
    report_lines = [f"Report for {parking_name}\n", "="*40 + "\n"]

    for month in data['month_year'].unique():
        month_data = data[data['month_year'] == month]
        full_duration = month_data.groupby(['time_hhmm', 'day_name'])['is_full'].sum().unstack(level=1)

        # Get times present in the data
        unique_times = full_duration.index
        full_hours = [time for time in unique_times if time.endswith(":00")]
        tick_positions = [i for i, time in enumerate(unique_times) if time in full_hours]

        # Create a heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            full_duration, 
            cmap="Reds", 
            annot=False, 
            cbar_kws={'label': 'Frequency of full parking occupancy'},
            yticklabels=False
        )
        plt.yticks(tick_positions, full_hours)
        plt.title(f"Full Occupancy Times - {parking_name} - {month}")
        plt.xlabel("Day of the week")
        plt.ylabel("Hour of the day")
        plt.tight_layout()
        
        output_path = os.path.join(output_folder_diagrams, f"{parking_name.replace(' ', '_')}_{month}.png")
        plt.savefig(output_path, dpi=300)
        plt.close()

        # Textual analysis for the report
        report_lines.append(f"\nMonth: {month}\n")
        report_lines.append(f"Hours of full occupancy: {len(month_data[month_data['is_full']])}\n")
        report_lines.append(f"Weekdays with the highest full occupancy counts:\n")
        day_full_counts = month_data[month_data['is_full']].groupby('day_name').size().sort_values(ascending=False)
        report_lines.append(day_full_counts.to_string() + "\n")

    # Save the textual report
    report_path = os.path.join(output_folder_reports, f"{parking_name.replace(' ', '_')}_report.txt")
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.writelines(report_lines)

print("Analysis complete. Results are available in the 'diagrams' and 'reports' folders.")
