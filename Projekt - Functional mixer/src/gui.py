import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import numpy as np
from functools import partial
from itertools import starmap
import os
import time

class GUI:
    def __init__(self, app):
        self.app = app
        self.file_labels = {}
        self.bpm_labels = {}
        self.confidence_labels = {}
        self.volume_vars = []
        self.crossfader_var = None
        self.crossfader_label = None
        self.bpm_sync_label = None

    def setup_gui(self):
        main_frame = ttk.Frame(self.app.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=1)

        self._setup_file_section(main_frame)
        self._setup_control_section(main_frame)
        self.app.waveform_display.setup_waveform_display(main_frame)

    def _setup_file_section(self, parent):
        file_frame = ttk.LabelFrame(parent, text="Audio Files & BPM Analysis", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        track_configs = [
            {"track": 0, "label": "Track 1:", "row": 0},
            {"track": 1, "label": "Track 2:", "row": 1}
        ]

        for config in track_configs:
            self._create_track_controls(file_frame, config)

    def _create_track_controls(self, parent, config):
        row, track = config["row"], config["track"]
        ttk.Label(parent, text=config["label"]).grid(row=row, column=0, sticky=tk.W)
        file_label = ttk.Label(parent, text="No file selected")
        file_label.grid(row=row, column=1, sticky="ew", padx=(10, 5))
        self.file_labels[track] = file_label
        bpm_label = ttk.Label(parent, text="BPM: N/A", width=10)
        bpm_label.grid(row=row, column=2, sticky=tk.W, padx=(5, 5))
        self.bpm_labels[track] = bpm_label
        conf_label = ttk.Label(parent, text="Conf: N/A", width=10)
        conf_label.grid(row=row, column=3, sticky=tk.W, padx=(5, 5))
        self.confidence_labels[track] = conf_label
        ttk.Button(parent, text="Browse", command=partial(self.load_file, track)).grid(row=row, column=4, padx=(5, 0))

    def _setup_control_section(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Playback Controls", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        button_configs = [ #dane wejściowe do poźniejszych funckji
            ("Play Both", self.play_both, "green"),
            ("Stop Both", self.stop_both, "red"),
            ("Play Track 1", partial(self.play_track, 0), "lightgreen"),
            ("Play Track 2", partial(self.play_track, 1), "lightgreen"),
            ("Pause Track 1", partial(self.toggle_pause_track, 0), "orange"),
            ("Pause Track 2", partial(self.toggle_pause_track, 1), "orange"),
            ("Stop Track 1", partial(self.stop_track, 0), "lightcoral"),
            ("Stop Track 2", partial(self.stop_track, 1), "lightcoral"),
        ]

        buttons = list(starmap( #rozpakowuje wszytkie elementy, aplikuje je do funkcji lambda, a lambda tworzy button
            lambda text, command, color: self._create_styled_button(control_frame, text, command, color),
            button_configs
        ))

        list(starmap(
            lambda i, btn: btn.grid(row=i // 4, column=i % 4, padx=5, pady=2, sticky="ew"), # dla każdego buttona wywołuje funkcje grid i rozmieszcza w gridzie elementy
            enumerate(buttons) # enumerate tworzy parę - numeruje buttony
        ))

        for i in range(4):
            control_frame.columnconfigure(i, weight=1)

        self._setup_volume_controls(control_frame)

    def _setup_volume_controls(self, parent):
        volume_frame = ttk.LabelFrame(parent, text="Volume Controls", padding="5")
        volume_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.volume_vars = list(map(lambda _: tk.DoubleVar(value=70), range(2)))
        self.crossfader_var = tk.DoubleVar(value=50)

        for i in range(2):
            ttk.Label(volume_frame, text=f"Track {i + 1} Volume").grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            scale = ttk.Scale(volume_frame, from_=0, to=100, variable=self.volume_vars[i],
                              command=partial(self.adjust_individual_volume, track=i))
            scale.grid(row=i, column=1, sticky="ew", padx=(10, 10))
            vol_label = ttk.Label(volume_frame, text="70%")
            vol_label.grid(row=i, column=2, sticky=tk.W, padx=(10, 0))
            self.volume_vars[i].trace('w', lambda *args, idx=i, lbl=vol_label: lbl.config(
                text=f"{int(self.volume_vars[idx].get())}%"))

        ttk.Label(volume_frame, text="Crossfader", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W,
                                                                                    padx=(0, 10), pady=(15, 5))
        ttk.Label(volume_frame, text="Track 1", foreground="blue").grid(row=3, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Label(volume_frame, text="Track 2", foreground="red").grid(row=3, column=2, sticky=tk.E, padx=(0, 20))
        crossfader_scale = ttk.Scale(volume_frame, from_=0, to=100, variable=self.crossfader_var,
                                     command=self.adjust_crossfader, length=300)
        crossfader_scale.grid(row=3, column=1, sticky="ew", padx=(10, 10), pady=(5, 5))
        self.crossfader_label = ttk.Label(volume_frame, text="50% (Balanced)")
        self.crossfader_label.grid(row=4, column=1, pady=(0, 5))
        self.crossfader_var.trace('w', self._update_crossfader_label)
        volume_frame.columnconfigure(1, weight=1)

    def _create_styled_button(self, parent, text, command, bg_color):
        return tk.Button(parent, text=text, command=command, bg=bg_color, font=("Arial", 9), relief="raised",
                         borderwidth=2, padx=10, pady=3)

    def _update_crossfader_label(self, *args):
        value = int(self.crossfader_var.get())
        if value < 25:
            text = f"{100 - value}% Track 1"
        elif value > 75:
            text = f"{value}% Track 2"
        else:
            text = f"{value}% (Balanced)"
        self.crossfader_label.config(text=text)

    def adjust_individual_volume(self, value, track: int):
        with self.app.state_lock:
            volume = float(value) / 100.0
            self.app.audio_state.state['volumes'][track] = volume
        self._apply_crossfaded_volume()

    def adjust_crossfader(self, value):
        self._apply_crossfaded_volume()

    def _apply_crossfaded_volume(self):
        with self.app.state_lock:
            crossfader_pos = self.crossfader_var.get() / 100.0
            track1_curve = np.cos(crossfader_pos * np.pi / 2)
            track2_curve = np.sin(crossfader_pos * np.pi / 2)
            for i in range(2):
                base_volume = self.volume_vars[i].get() / 100.0
                final_volume = base_volume * (track1_curve if i == 0 else track2_curve)
                if (self.app.audio_state.state['files'][i] and
                        self.app.audio_state.state['playing'][i] and
                        self.app.audio_state.state['channels'][i]):
                    self.app.audio_state.state['channels'][i].set_volume(final_volume)

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
            if self.app.audio_state.state['playing'][track_index]:
                self.stop_track(track_index)
            with self.app.state_lock:
                self.app.audio_state.state['data'][track_index] = None
                self.app.audio_state.state['waveform_cache'][track_index] = None
                self.app.audio_state.state['time_axes'][track_index] = None
                self.app.audio_state.state['filenames'][track_index] = filename
                sound = pygame.mixer.Sound(filename)
                self.app.audio_state.state['files'][track_index] = sound
                self.app.audio_state.state['durations'][track_index] = sound.get_length()
                self.app.audio_state.state['bpm_analyzing'][track_index] = True
            self.app.update_queue.put(('file_loaded', (track_index, filename)))
            self.bpm_labels[track_index].config(text="BPM: Analyzing...")
            self.app.executor.submit(self._process_audio_async, sound, track_index)
            self.app.executor.submit(self._analyze_bpm_async, filename, track_index)

    def _process_audio_async(self, sound, track_index):
        try:
            processed_data = self.app.audio_processor.process_audio(sound)
            duration = self.app.audio_state.state['durations'][track_index]
            time_axis = np.linspace(0, duration, len(processed_data))
            with self.app.state_lock:
                self.app.audio_state.state['data'][track_index] = processed_data
                self.app.audio_state.state['waveform_cache'][track_index] = processed_data
                self.app.audio_state.state['time_axes'][track_index] = time_axis
            self.app.update_queue.put(('waveform_update', track_index))
        except Exception as e:
            print(f"Error processing audio: {e}")

    def _analyze_bpm_async(self, filename, track_index):
        try:
            bpm, beats, confidence = self.app.audio_processor.calculate_bpm_advanced(filename)
            with self.app.state_lock:
                self.app.audio_state.state['bpm_values'][track_index] = bpm
                self.app.audio_state.state['beat_times'][track_index] = beats
                self.app.audio_state.state['tempo_confidence'][track_index] = confidence
                self.app.audio_state.state['bpm_analyzing'][track_index] = False
            self.app.update_queue.put(('bpm_update', (track_index, bpm, confidence)))
        except Exception as e:
            print(f"Error analyzing BPM: {e}")
            with self.app.state_lock:
                self.app.audio_state.state['bpm_analyzing'][track_index] = False

    def play_both(self):
        valid_tracks = list(filter(lambda i: self.app.audio_state.state['files'][i] is not None, range(2)))
        list(map(self.play_track, valid_tracks))

    def stop_both(self):
        list(map(self.stop_track, range(2)))

    def play_track(self, track_index: int):
        with self.app.state_lock:
            if (self.app.audio_state.state['files'][track_index] and
                    not self.app.audio_state.state['playing'][track_index]):
                sound = self.app.audio_state.state['files'][track_index]
                channel = pygame.mixer.find_channel()
                if channel:
                    self.app.audio_state.state['channels'][track_index] = channel
                    if self.app.audio_state.state['paused'][track_index]:
                        channel.play(sound)
                        self.app.audio_state.state['paused'][track_index] = False
                        self.app.audio_state.state['start_times'][track_index] = (
                            time.time() - self.app.audio_state.state['pause_positions'][track_index]
                        )
                    else:
                        channel.play(sound)
                        self.app.audio_state.state['pause_positions'][track_index] = 0
                        self.app.audio_state.state['start_times'][track_index] = time.time()
                    self.app.audio_state.state['playing'][track_index] = True
                    self._apply_crossfaded_volume()

    def toggle_pause_track(self, track_index: int):
        if self.app.audio_state.state['playing'][track_index]:
            self._pause_track(track_index)
        elif self.app.audio_state.state['paused'][track_index]:
            self.play_track(track_index)

    def _pause_track(self, track_index: int):
        if (self.app.audio_state.state['playing'][track_index] and
                self.app.audio_state.state['channels'][track_index]):
            current_time = time.time()
            self.app.audio_state.state['pause_positions'][track_index] = (
                current_time - self.app.audio_state.state['start_times'][track_index]
            )
            self.app.audio_state.state['channels'][track_index].stop()
            self.app.audio_state.state['playing'][track_index] = False
            self.app.audio_state.state['paused'][track_index] = True

    def stop_track(self, track_index: int):
        if self.app.audio_state.state['channels'][track_index]:
            self.app.audio_state.state['channels'][track_index].stop()
        state_resets = {
            'playing': False,
            'paused': False,
            'pause_positions': 0,
            'current_positions': 0,
            'start_times': 0
        }
        for key, value in state_resets.items():
            self.app.audio_state.state[key][track_index] = value

    def analyze_all_bpm(self):
        for i in range(2):
            if self.app.audio_state.state['files'][i]:
                filename = self.app.audio_state.state['filenames'][i]
                bpm, beats, confidence = self.app.audio_processor.calculate_bpm_advanced(filename)
                self.app.audio_state.state['bpm_values'][i] = bpm
                self.app.audio_state.state['beat_times'][i] = beats
                self.app.audio_state.state['tempo_confidence'][i] = confidence
                self.bpm_labels[i].config(text=f"BPM: {bpm if bpm else 'N/A'}")
                self.confidence_labels[i].config(text=f"Conf: {int(confidence * 100)}%")
        self.bpm_sync_label.config(text="BPM Analysis Complete")

    def sync_to_track(self, reference_track: int):
        if self.app.audio_state.state['bpm_values'][reference_track]:
            self.bpm_sync_label.config(
                text=f"Synced to Track {reference_track + 1} BPM: {self.app.audio_state.state['bpm_values'][reference_track]}")
        else:
            self.bpm_sync_label.config(text="No BPM data for reference track")
