import pygame
import numpy as np
import librosa
from functools import partial, reduce
from tkinter import filedialog
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from utils import handle_audio_errors
import threading
import time
import queue

class AudioProcessor:
    def __init__(self, audio_state):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
        self.audio_state = audio_state
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AudioMixer")
        self.update_queue = queue.Queue(maxsize=100)
        self.shutdown_event = threading.Event()
        self.audio_processors = self._create_audio_processors()
        self.position_thread = threading.Thread(target=self._position_updater_optimized, daemon=True, name="PositionUpdater")
        self.gui_update_thread = threading.Thread(target=self._process_gui_updates, daemon=True, name="GUIUpdater")
        self.waveform_scheduler = threading.Thread(target=self._schedule_waveform_updates, daemon=True, name="WaveformScheduler")
        self.position_thread.start()
        self.gui_update_thread.start()
        self.waveform_scheduler.start()
        self.gui_update_throttle = 0.033
        self.last_gui_update = 0
        self.position_update_throttle = 0.016
        self.last_position_update = 0

    def _create_audio_processors(self) -> dict:
        return {
            'normalize': lambda x: x / np.max(np.abs(x)) if np.max(np.abs(x)) > 0 else x,
            'to_float': lambda x: x.astype(np.float32),
            'downsample': lambda x, factor: x[::max(1, len(x) // factor)],
            'to_mono': lambda x: reduce(np.add, x.T) / x.shape[1] if len(x.shape) > 1 else x,
            'apply_volume': lambda x, vol: x * vol
        }