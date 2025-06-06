# Mikser Audio DJ z Analizą BPM

## Opis

Profesjonalny mikser audio DJ napisany w Pythonie, który łączy tradycyjne funkcje miksowania z nowoczesną analizą BPM. Aplikacja wykorzystuje programowanie funkcyjne do wydajnego przetwarzania audio i oferuje intuicyjny interfejs graficzny do miksowania dwóch ścieżek audio w czasie rzeczywistym.

## 🎵 Kluczowe Funkcje

### 1. Analiza BPM w Czasie Rzeczywistym
- **Automatyczna detekcja tempa**: Wykorzystuje bibliotekę `librosa` do precyzyjnej analizy BPM
- **Czas rzeczywisty**: Analiza odbywa się asynchronicznie w tle, nie blokując interfejsu
- **Wskaźnik pewności**: Wyświetla poziom pewności wykrytego BPM
- **Optymalizacja wydajności**: Przetwarzanie ograniczone do pierwszych 60 sekund utworu dla szybszej analizy

### 2. Miksowanie Na Żywo Dwóch Utworów
- **Równoczesne odtwarzanie**: Możliwość jednoczesnego odtwarzania dwóch ścieżek audio
- **Crossfader**: Płynne przejścia między utworami z krzywą kosinusoidalną
- **Indywidualne kontrole głośności**: Niezależna regulacja głośności każdej ścieżki
- **Kontrola odtwarzania**: Play, pause, stop dla każdej ścieżki osobno
- **Wizualizacja fal dźwiękowych**: Graficzne przedstawienie amplitudy z wskaźnikami pozycji

### 3. Programowanie Funkcyjne
- **Przetwarzanie funkcyjne**: Wykorzystanie `map`, `filter`, `reduce` do transformacji danych
- **Kompozycja funkcji**: Pipeline przetwarzania audio z użyciem `functools.partial`
- **Niezmienność danych**: Minimalizacja efektów ubocznych w przetwarzaniu audio
- **Funkcje wyższego rzędu**: Dekoratory do obsługi błędów i optymalizacji
- **Lazy evaluation**: Efektywne przetwarzanie dużych zbiorów danych audio

## 📋 Wymagania

```
python >= 3.7
pygame >= 2.0
numpy >= 1.19
matplotlib >= 3.3
librosa >= 0.8
tkinter (standardowo w Pythonie)
```

## 🚀 Instalacja

1. Sklonuj repozytorium:
```bash
git clone [url-repo]
cd mikser-audio-dj
```

2. Zainstaluj wymagane biblioteki:
```bash
pip install pygame numpy matplotlib librosa
```

3. Uruchom aplikację:
```bash
python main.py
```

## 🎛️ Instrukcja Użycia

### Ładowanie Utworów
1. Kliknij przycisk "Browse" dla Track 1 lub Track 2
2. Wybierz plik audio (MP3, WAV, OGG, FLAC, M4A)
3. Aplikacja automatycznie rozpocznie analizę BPM w tle

### Miksowanie
1. **Odtwarzanie**: Użyj przycisków "Play Track 1/2" lub "Play Both"
2. **Crossfader**: Przeciągnij suwak crossfadera dla płynnego przejścia między utworami
3. **Głośność**: Dostosuj indywidualną głośność każdej ścieżki
4. **Pauza/Stop**: Kontroluj odtwarzanie każdej ścieżki niezależnie

### Wizualizacja
- **Fale dźwiękowe**: Każdy utwór ma swoją wizualizację amplitudy
- **Wskaźnik pozycji**: Zielona linia pokazuje aktualną pozycję odtwarzania
- **Status odtwarzania**: Kolory wskaźników informują o stanie (play/pause/stop)
