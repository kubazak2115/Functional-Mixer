import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
from typing import Dict, Any
import os

class AudioMixerGUI:
    def __init__(self, root: tk.Tk, audio_state, audio_processor, waveform_display):
        self.root = root
        self.audio_state = audio_state
        self.audio_processor = audio_processor
        self.waveform_display = waveform_display
        self.root.title("Mikser Audio DJ z Analizą BPM - Optimized")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.file_labels = {}
        self.bpm_labels = {}
        self.confidence_labels = {}
        self.volume_vars = []
        self.crossfader_var = None
        self.crossfader_label = None
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=0)
        main_frame.rowconfigure(3, weight=1)
        self._setup_file_section(main_frame)
        self._setup_control_section(main_frame)
        self.waveform_display.setup_waveform_display(main_frame)

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
        ttk.Button(parent, text="Browse", command=partial(self.audio_processor.load_file, track)).grid(row=row, column=4, padx=(5, 0))

    def _setup_control_section(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Playback Controls", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        button_configs = [
            ("Play Both", self.audio_processor.play_both, "green"),
            ("Stop Both", self.audio_processor.stop_both, "red"),
            ("Play Track 1", partial(self.audio_processor.play_track, 0), "lightgreen"),
            ("Play Track 2", partial(self.audio_processor.play_track, 1), "lightgreen"),
            ("Pause Track 1", partial(self.audio_processor.toggle_pause_track, 0), "orange"),
            ("Pause Track 2", partial(self.audio_processor.toggle_pause_track, 1), "orange"),
            ("Stop Track 1", partial(self.audio_processor.stop_track, 0), "lightcoral"),
            ("Stop Track 2", partial(self.audio_processor.stop_track, 1), "lightcoral"),
        ]
        buttons = [self._create_styled_button(control_frame, text, command, color) for text, command, color in button_configs]
        for i, btn in enumerate(buttons):
            btn.grid(row=i // 4, column=i % 4, padx=5, pady=2, sticky="ew")
        for i in range(4):
            control_frame.columnconfigure(i, weight=1)
        self._setup_volume_controls(control_frame)