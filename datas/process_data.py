import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# Ścieżka do pliku wejściowego
data_file = "parking_history_data.csv"

# Nazwy parkingów
parking_columns = ["Polinka", "Parking Wrońskiego", "D20 - D21", "GEO LO1 Geocentrum", "Architektura"]

# Ścieżka do katalogu wynikowego
output_folder = "datasets"
os.makedirs(output_folder, exist_ok=True)

# Wczytanie danych
try:
    data = pd.read_csv(data_file)
except FileNotFoundError:
    print(f"Plik {data_file} nie został znaleziony.")
    exit()

# Sprawdzenie wymaganych kolumn
required_columns = ['Data', 'Czas'] + parking_columns
if not all(column in data.columns for column in required_columns):
    print(f"Plik {data_file} musi zawierać kolumny: {', '.join(required_columns)}.")
    exit()

# Przetwarzanie daty i czasu na datetime
data['Datetime'] = pd.to_datetime(data['Data'] + ' ' + data['Czas'], format='%Y-%m-%d %H:%M', errors='coerce')

# Usunięcie nieprawidłowych dat
data = data.dropna(subset=['Datetime'])

# Dodanie kolumny dnia tygodnia i formatu czasu
data['day_of_week'] = data['Datetime'].dt.dayofweek + 1  # Poniedziałek = 1, Niedziela = 7
data['datetime_formatted'] = data['Datetime'].dt.strftime('%Y-%m-%d %H:%M')

# Usunięcie duplikatów
data = data.drop_duplicates(subset=['Data', 'Czas'])

# Usunięcie pomiarów z weekendów (sobota i niedziela)
data = data[~data['day_of_week'].isin([6, 7])]

# Dla każdego parkingu przetwarzanie danych
for col in parking_columns:
    # Konwersja do liczbowych wartości
    data[col] = pd.to_numeric(data[col], errors='coerce')

    # Usunięcie brakujących danych dla bieżącego parkingu
    clean_data = data.dropna(subset=[col])

    # Obliczanie wartości średniej i odchylenia standardowego
    mean_spots = clean_data[col].mean()
    std_spots = clean_data[col].std()

    # Usuwanie wartości odstających (3 odchylenia standardowe od średniej)
    clean_data = clean_data[(clean_data[col] > mean_spots - 3 * std_spots) &
                            (clean_data[col] < mean_spots + 3 * std_spots)]

    # Zamiana wartości ujemnych na 0
    clean_data[col] = clean_data[col].apply(lambda x: max(x, 0))

    # Tworzenie podstawowego DataFrame
    out_data = clean_data[['datetime_formatted', 'day_of_week', col]].rename(columns={
        'datetime_formatted': 'datetime', col: 'spots'
    })

    # Sortowanie
    out_data = out_data.sort_values(by=['datetime', 'day_of_week']).reset_index(drop=True)

    # Zapisywanie do pliku
    output_file = os.path.join(output_folder, f"{col.replace(' ', '_').lower()}.csv")
    out_data.to_csv(output_file, index=False)


print("Przetwarzanie danych zakończone. Wyniki zapisano w katalogu 'datasets'.")

# Katalog z przetworzonymi danymi
parking_files = [
    "polinka.csv",
    "parking_wrońskiego.csv",
    "d20_-_d21.csv",
    # "geo_lo1_geocentrum.csv",
    # "architektura.csv"
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
output_file_path = os.path.join(output_folder, 'parking_occupancy_visualization.html')
fig.write_html(output_file_path)

print(f"Interaktywny wykres zapisano jako {output_file_path}. Otwórz ten plik w przeglądarce, aby go zobaczyć.")
