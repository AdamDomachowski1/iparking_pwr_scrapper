import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# List of files to analyze
files = [
    ('datasets/d20_-_d21.csv', 'Parking D20-D21'),
    ('datasets/parking_wrońskiego.csv', 'Parking Wrońskiego'),
    ('datasets/polinka.csv', 'Parking Polinka')
]

# Loop to process data for each file
for file_path, parking_name in files:
    # Read the data from the CSV file
    data = pd.read_csv(file_path)
    
    # Convert the 'datetime' column to datetime format
    data['datetime'] = pd.to_datetime(data['datetime'])
    
    # Add a column with the month-year period and the day of the week in text (Polish names)
    data['month_year'] = data['datetime'].dt.to_period('M')
    data['day_name'] = data['datetime'].dt.day_name(locale='pl_PL')
    
    # Filter out data from January
    data = data[data['month_year'].dt.month != 1]
    
    # Define a "problem" as a situation where the number of spots is zero
    data['is_problem'] = data['spots'] == 0
    
    # Group data by month and day of the week
    problem_analysis = (
        data.groupby(['month_year', 'day_name'])['is_problem']
        .mean() * 100  # Calculate the percentage of "problems"
    )
    
    # Convert results into a DataFrame with a multi-level index
    problem_analysis_df = problem_analysis.unstack(level=-1).fillna(0)
    
    # Ensure the correct order of weekdays
    ordered_days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
    problem_analysis_df = problem_analysis_df.reindex(columns=ordered_days)
    
    # Generate a heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(
        problem_analysis_df.T,  # Transpose to place months on the X-axis and days of the week on the Y-axis
        annot=True,  # Display values in the cells
        fmt=".1f",  # Format the values
        cmap="Reds",  # Color palette for the heatmap
        cbar_kws={'label': 'Percentage of problematic cases (%)'}  # Label for the color bar
    )
    plt.title(f"Heatmap of problem occurrence - {parking_name}")
    plt.xlabel("Month")
    plt.ylabel("Day of the week")
    plt.tight_layout()
    plt.show()

    # Display the tabular results for the parking lot
    print(f"Problem analysis for parking {parking_name}:")
    print(problem_analysis_df)
