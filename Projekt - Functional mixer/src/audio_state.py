import tkinter as tk
import threading
from typing import Dict, Any

class AudioState:
    def __init__(self):
        self.state_lock = threading.RLock()
        self.root = None
        self.gui = None
        self.waveform_display = None
        self.crossfader_var = tk.DoubleVar(value=50)
        self.volume_vars = [tk.DoubleVar(value=70) for _ in range(2)]
        self._initialize_state()

    def _initialize_state(self) -> Dict[str, Any]:
        self._state = {
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
            'bpm_analyzing': [False, False]
        }

    def __getitem__(self, key):
        with self.state_lock:
            return self._state[key]

    def __setitem__(self, key, value):
        with self.state_lock:
            self._state[key] = value