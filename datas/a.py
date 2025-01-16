import pandas as pd

# Wczytanie danych
file_path = 'datasets/d20_-_d21.csv'
data = pd.read_csv(file_path)

# Konwersja kolumny 'datetime' na format datetime
data['datetime'] = pd.to_datetime(data['datetime'])

# Dodanie kolumny z nazwą miesiąca oraz dniem tygodnia w formie tekstowej
data['month_year'] = data['datetime'].dt.to_period('M')
data['day_name'] = data['datetime'].dt.day_name(locale='pl_PL')  # polskie nazwy dni tygodnia

# Filtrowanie danych - usunięcie stycznia
data = data[data['month_year'].dt.month != 1]

# Zdefiniowanie problemu jako sytuacji, w której liczba miejsc wynosi 0
data['is_problem'] = data['spots'] == 0

# Grupowanie danych po miesiącu i dniu tygodnia
problem_analysis = (
    data.groupby(['month_year', 'day_name'])['is_problem']
    .mean() * 100  # Obliczanie procentu \"problemów\"
)

# Konwersja wyników na DataFrame z wielopoziomowym indeksem
problem_analysis_df = problem_analysis.unstack(level=-1).fillna(0)

# Wymuszenie kolejności dni tygodnia
ordered_days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
problem_analysis_df = problem_analysis_df.reindex(columns=ordered_days)

# Wyświetlenie wyników
print("Analiza problemów w podziale na miesiące i dni tygodnia (bez stycznia):")
print(problem_analysis_df)