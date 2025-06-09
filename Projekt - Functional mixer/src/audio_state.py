from typing import Dict, Any, List

class AudioState:
    def __init__(self):
        self.state = self._initialize_audio_state()
        self.state_lock = None 

    def _initialize_audio_state(self) -> Dict[str, Any]: #utworzenie słownika danych ścieżek audio dla apki 
        return {
            'files': [None, None],
            'filenames': [None, None],
            'data': [None, None],
            'durations': [0, 0],
            'channels': [None, None],
            'playing': [False, False],
            'paused': [False, False],
            'pause_positions': [0, 0],
            'start_times': [0, 0],
            'current_positions': [0, 0],
            'volumes': [0.5, 0.5],
            'bpm_values': [None, None],
            'beat_times': [[], []],
            'tempo_confidence': [0.0, 0.0],
            'waveform_cache': [None, None],
            'bpm_analyzing': [False, False],
            'time_axes': [None, None]
        }
