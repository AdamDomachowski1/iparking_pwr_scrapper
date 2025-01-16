import pandas as pd
import os

# Ścieżka do folderu z plikami
folder_path = 'datasets/'

# Pobierz listę plików CSV w folderze
files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Iteracja po plikach
for file_name in files:
    file_path = os.path.join(folder_path, file_name)
    print(f'Analizuję plik: {file_path}')
    
    try:
        # Wczytaj plik CSV
        data = pd.read_csv(file_path)
        
        # Zakładamy, że kolumna "spots" istnieje w danych
        if 'spots' in data.columns:
            # Oblicz liczbę rekordów, gdzie spots = 0
            zero_spots_count = (data['spots'] == 0).sum()

            # Oblicz całkowitą liczbę rekordów
            total_records = len(data)

            # Oblicz procent
            zero_spots_percentage = (zero_spots_count / total_records) * 100

            # Znajdź maksymalną wartość w kolumnie 'spots'
            max_spots = data['spots'].max()

            print(f'Liczba rekordów, gdzie spots = 0: {zero_spots_count}')
            print(f'Całkowita liczba rekordów: {total_records}')
            print(f'Procent rekordów, gdzie spots = 0: {zero_spots_percentage:.2f}%')
            print(f'Maksymalna liczba miejsc na parkingu (max spots): {max_spots}')
        else:
            print("Kolumna 'spots' nie istnieje w danych.")
    except Exception as e:
        print(f'Błąd podczas przetwarzania pliku {file_name}: {e}')
    
    print('-' * 40)  # Separator między plikami
