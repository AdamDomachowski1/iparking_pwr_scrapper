import pandas as pd
import os

# Path to the folder containing the files
folder_path = 'datasets/'

# Get the list of CSV files in the folder
files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Iterate over the files
for file_name in files:
    file_path = os.path.join(folder_path, file_name)
    print(f'Analyzing file: {file_path}')
    
    try:
        # Read the CSV file
        data = pd.read_csv(file_path)
        
        # Assume the "spots" column exists in the data
        if 'spots' in data.columns:
            # Calculate the number of records where spots = 0
            zero_spots_count = (data['spots'] == 0).sum()

            # Calculate the total number of records
            total_records = len(data)

            # Calculate the percentage
            zero_spots_percentage = (zero_spots_count / total_records) * 100

            # Find the maximum value in the 'spots' column
            max_spots = data['spots'].max()

            print(f'Number of records where spots = 0: {zero_spots_count}')
            print(f'Total number of records: {total_records}')
            print(f'Percentage of records where spots = 0: {zero_spots_percentage:.2f}%')
            print(f'Maximum number of spots in the parking lot (max spots): {max_spots}')
        else:
            print("The 'spots' column does not exist in the data.")
    except Exception as e:
        print(f'Error while processing file {file_name}: {e}')
    
    print('-' * 40)  # Separator between files
