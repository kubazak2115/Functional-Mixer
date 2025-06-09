import numpy as np
from functools import reduce, partial
from typing import Callable, Dict, Any
import librosa
import pygame

class AudioProcessor: #tworzy słownik fukcji przetwarzających dzwięk i oblicza bpm
    def __init__(self): 
        self.processors = self._create_audio_processors()

    def _create_audio_processors(self) -> Dict[str, Callable]: #słownik z lambdami które przetwarzaja
        return {                                               #dzwięk, tylko utworzenie
            'normalize': lambda x: x / np.max(np.abs(x)) if np.max(np.abs(x)) > 0 else x,
            'to_float': lambda x: x.astype(np.float32),
            'downsample': lambda x, factor: x[::max(1, len(x) // factor)],
            'to_mono': lambda x: reduce(np.add, x.T) / x.shape[1] if len(x.shape) > 1 else x,
            'apply_volume': lambda x, vol: x * vol
        }

    def process_audio(self, sound, factor=20000): #modyfikacja załadowanej przez nas ścieżki
        raw_data = pygame.sndarray.array(sound)   #na podstawie tych funkcji z słownika
        processing_pipeline = [
            self.processors['to_float'], # tutaj mamy pipeline - funckje wykonują sie po kolei
            self.processors['to_mono'],
            self.processors['normalize'],
            partial(self.processors['downsample'], factor=factor) #partial - factor jest wartościa przypisana na stale
        ]
        return reduce(lambda data, func: func(data), processing_pipeline, raw_data) #reduce - zmieniamy wsztko w jeden ciąg

    def calculate_bpm_advanced(self, filename: str) -> tuple[any, list, float]: #wyliczenie bpm na podstawie funkcjiz librosa
        try:
            y, sr = librosa.load(filename, duration=60)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=1024)
            tempo_scalar = float(tempo.item() if hasattr(tempo, 'item') else tempo)
            confidence = 0.8
            beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=1024) #podział pliku na ramki czasowe odpowiadające jednemu uderzeniu
            filtered_beats = list(filter(lambda t: 0.5 <= t, beat_times))
            return round(tempo_scalar, 1), filtered_beats, round(confidence, 2) #zwracamy bpm , te ramki(podziały czasowe) i wartość confidence
        except Exception as e:
            print(f"Error in BPM calculation: {e}")
            return None, [], 0.0
