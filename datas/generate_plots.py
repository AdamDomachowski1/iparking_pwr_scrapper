import pandas as pd
import plotly.express as px
import os

# Katalog z przetworzonymi danymi
output_folder = "datasets"

# Lista plików wynikowych
parking_files = [
    "polinka.csv",
    "parking_wrońskiego.csv",
    "d20_-_d21.csv",
    "geo_lo1_geocentrum.csv",
    "architektura.csv"
]

# Wczytanie danych z plików i ich połączenie
all_data = []
for file in parking_files:
    file_path = os.path.join(output_folder, file)
    if os.path.exists(file_path):
        parking_data = pd.read_csv(file_path)
        parking_data['Parking Location'] = file.replace("_", " ").replace(".csv", "").title()
        all_data.append(parking_data)
    else:
        print(f"Plik {file} nie istnieje w katalogu {output_folder}.")

# Łączenie wszystkich danych w jeden DataFrame
if not all_data:
    print("Brak danych do wizualizacji.")
    exit()

data_combined = pd.concat(all_data, ignore_index=True)

# Konwersja kolumny datetime na typ datetime
data_combined['datetime'] = pd.to_datetime(data_combined['datetime'], format='%Y-%m-%d %H:%M', errors='coerce')

# Usunięcie nieprawidłowych dat
data_combined = data_combined.dropna(subset=['datetime'])

# Tworzenie interaktywnego wykresu
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

# Aktualizacja układu wykresu
fig.update_layout(
    xaxis_title='Time',
    yaxis_title='Occupancy',
    xaxis=dict(tickformat="%a\n%b %d"),
    template='plotly_white'
)

# Zapisanie wykresu jako pliku HTML
output_file_path = 'parking_occupancy_visualization.html'
fig.write_html(output_file_path)

print(f"Interaktywny wykres zapisano jako {output_file_path}. Otwórz ten plik w przeglądarce, aby go zobaczyć.")
