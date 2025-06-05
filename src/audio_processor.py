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

    @handle_audio_errors
    def load_file(self, track_index: int):
        filetypes = (
            ('Audio files', '*.mp3 *.wav *.ogg *.flac *.m4a'),
            ('MP3 files', '*.mp3'),
            ('WAV files', '*.wav'),
            ('OGG files', '*.ogg'),
            ('FLAC files', '*.flac'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(title=f'Select audio file for Track {track_index + 1}',
                                              filetypes=filetypes)
        if filename:
            with self.audio_state.state_lock:
                self.audio_state['filenames'][track_index] = filename
                sound = pygame.mixer.Sound(filename)
                self.audio_state['files'][track_index] = sound
                self.audio_state['durations'][track_index] = sound.get_length()
                self.audio_state['bpm_analyzing'][track_index] = True
            self.update_queue.put(('file_loaded', (track_index, filename)))
            self.executor.submit(self._process_audio_async, sound, track_index)
            self.executor.submit(self._analyze_bpm_async, filename, track_index)

    def _process_audio_async(self, sound, track_index):
        try:
            raw_data = pygame.sndarray.array(sound)
            processing_pipeline = [
                self.audio_processors['to_float'],
                self.audio_processors['to_mono'],
                self.audio_processors['normalize'],
                partial(self.audio_processors['downsample'], factor=20000)
            ]
            processed_data = reduce(lambda data, func: func(data), processing_pipeline, raw_data)
            with self.audio_state.state_lock:
                self.audio_state['data'][track_index] = processed_data
                self.audio_state['waveform_cache'][track_index] = processed_data
            self.update_queue.put(('waveform_update', track_index))
        except Exception as e:
            print(f"Error processing audio: {e}")

    @handle_audio_errors
    def calculate_bpm_advanced(self, filename: str) -> Tuple[Optional[float], List[float], float]:
        y, sr = librosa.load(filename, duration=60)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=1024)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=1024)
        tempo_scalar = float(tempo.item() if hasattr(tempo, 'item') else tempo)
        confidence = 0.8
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=1024)
        filtered_beats = list(filter(lambda t: 0.5 <= t, beat_times))
        return round(tempo_scalar, 1), filtered_beats, round(confidence, 2)

    def _analyze_bpm_async(self, filename, track_index):
        try:
            bpm, beats, confidence = self.calculate_bpm_advanced(filename)
            with self.audio_state.state_lock:
                self.audio_state['bpm_values'][track_index] = bpm
                self.audio_state['beat_times'][track_index] = beats
                self.audio_state['tempo_confidence'][track_index] = confidence
                self.audio_state['bpm_analyzing'][track_index] = False
            self.update_queue.put(('bpm_update', (track_index, bpm, confidence)))
        except Exception as e:
            print(f"Error analyzing BPM: {e}")
            with self.audio_state.state_lock:
                self.audio_state['bpm_analyzing'][track_index] = False

    def play_both(self):
        valid_tracks = [i for i in range(2) if self.audio_state['files'][i] is not None]
        for track in valid_tracks:
            self.play_track(track)

    def stop_both(self):
        for i in range(2):
            self.stop_track(i)

    def play_track(self, track_index: int):
        with self.audio_state.state_lock:
            if self.audio_state['files'][track_index] and not self.audio_state['playing'][track_index]:
                sound = self.audio_state['files'][track_index]
                channel = pygame.mixer.find_channel()
                if channel:
                    self.audio_state['channels'][track_index] = channel
                    if self.audio_state['paused'][track_index]:
                        channel.play(sound)
                        self.audio_state['paused'][track_index] = False
                        self.audio_state['start_times'][track_index] = time.time() - \
                                                                       self.audio_state['pause_positions'][track_index]
                    else:
                        channel.play(sound)
                        self.audio_state['pause_positions'][track_index] = 0
                        self.audio_state['start_times'][track_index] = time.time()
                    self.audio_state['playing'][track_index] = True
                    self._apply_crossfaded_volume()

    def toggle_pause_track(self, track_index: int):
        if self.audio_state['playing'][track_index]:
            self._pause_track(track_index)
        elif self.audio_state['paused'][track_index]:
            self.play_track(track_index)

    def _pause_track(self, track_index: int):
        if self.audio_state['playing'][track_index] and self.audio_state['channels'][track_index]:
            current_time = time.time()
            self.audio_state['pause_positions'][track_index] = current_time - self.audio_state['start_times'][
                track_index]
            self.audio_state['channels'][track_index].stop()
            self.audio_state['playing'][track_index] = False
            self.audio_state['paused'][track_index] = True

    def stop_track(self, track_index: int):
        if self.audio_state['channels'][track_index]:
            self.audio_state['channels'][track_index].stop()
        state_resets = {
            'playing': False,
            'paused': False,
            'pause_positions': 0,
            'current_positions': 0,
            'start_times': 0
        }
        for key, value in state_resets.items():
            self.audio_state[key][track_index] = value

    def adjust_individual_volume(self, value, track: int):
        with self.audio_state.state_lock:
            volume = float(value) / 100.0
            self.audio_state['volumes'][track] = volume
        self._apply_crossfaded_volume()

    def adjust_crossfader(self, value):
        self._apply_crossfaded_volume()