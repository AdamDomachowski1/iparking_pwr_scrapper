import requests
import csv
import os
from datetime import datetime

# Parking Website
url = 'https://iparking.pwr.edu.pl/modules/iparking/scripts/ipk_operations.php'

# Headers required for making requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'https://iparking.pwr.edu.pl',
    'Referer': 'https://iparking.pwr.edu.pl/',
    'X-Requested-With': 'XMLHttpRequest'
}

# Path to the CSV file where parking data will be saved
csv_filename = 'datas/parking_history_data.csv'

# Function to send a POST request to the parking API for a specific parking ID
def send_request(parking_id):
    payload = {
        "o": "get_today_chart",
        "i": str(parking_id)
    }

    try:
        # Send the request with a JSON payload
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an exception if the request fails
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error while sending request for parking ID {parking_id}: {e}')
        return None

# Function to check if the CSV file already contains data for the current date
def file_has_data_for_today(filename, current_date):
    if not os.path.exists(filename):
        return False

    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Check if the first column contains today's date
            if row and row[0] == current_date:
                return True
    return False

# Function to save the scraped parking data to a CSV file
def save_to_csv(all_data):
    unique_times = set()
    
    # Collect unique time labels from the data
    for data in all_data:
        if 'slots' in data and 'labels' in data['slots']:
            unique_times.update(data['slots']['labels'])
    
    unique_times = sorted(unique_times)
    current_date = datetime.now().strftime('%Y-%m-%d')

    file_exists = os.path.exists(csv_filename)
    has_data_today = file_has_data_for_today(csv_filename, current_date)

    try:
        # Open the CSV file in append mode if it exists, otherwise create it
        with open(csv_filename, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header row if the file is new
            if not file_exists:
                headers = ['Date', 'Time', 'Polinka', 'Parking Wrońskiego', 'D20 - D21', 'GEO LO1 Geocentrum', 'Architecture']
                writer.writerow(headers)

            # Initialize data storage for each unique time slot
            data_by_time = {time: [current_date, time] + [''] * 5 for time in unique_times}

            # Populate data for each parking lot
            for idx, parking_id in enumerate([2, 4, 5, 6, 7], start=0):
                data = all_data[idx]
                if 'slots' in data and 'labels' in data['slots'] and 'data' in data['slots']:
                    history_labels = data['slots']['labels']
                    history_data = data['slots']['data']

                    # Map data to the corresponding time slot
                    for time, available_slots in zip(history_labels, history_data):
                        if time in data_by_time:
                            data_by_time[time][idx + 2] = available_slots

            # Write rows for all time slots
            for row in data_by_time.values():
                writer.writerow(row)

    except IOError as e:
        print(f'Error while saving to CSV file: {e}')

# Main function to orchestrate data scraping and saving
def main():
    all_data = []

    # Loop through the list of parking IDs and collect data
    for parking_id in [2, 4, 5, 6, 7]:
        data = send_request(parking_id)
        if data:
            all_data.append(data)
        else:
            print(f"Failed to retrieve data from server for parking ID {parking_id}.")

    # Save the collected data to the CSV file
    if all_data:
        save_to_csv(all_data)

# Entry point of the script
if __name__ == "__main__":
    main()
