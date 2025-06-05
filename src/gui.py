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
            ("Play Track 1", partial(self.audio_processor.play_track, 0), "lightblue"),
            ("Play Track 2", partial(self.audio_processor.play_track, 1), "lightblue"),
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

        def _setup_volume_controls(self, parent):
            volume_frame = ttk.LabelFrame(parent, text="Volume Controls", padding="5")
            volume_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
            self.volume_vars = [tk.DoubleVar(value=70) for _ in range(2)]
            self.crossfader_var = tk.DoubleVar(value=50)
            for i in range(2):
                ttk.Label(volume_frame, text=f"Track {i + 1} Volume").grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
                scale = ttk.Scale(volume_frame, from_=0, to=100, variable=self.volume_vars[i],
                                  command=partial(self.audio_processor.adjust_individual_volume, track=i))
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
                                         command=self.audio_processor.adjust_crossfader, length=300)
            crossfader_scale.grid(row=3, column=1, sticky="ew", padx=(10, 10), pady=(5, 5))
            self.crossfader_label = ttk.Label(volume_frame, text="50% (Balanced)")
            self.crossfader_label.grid(row=4, column=1, pady=(0, 5))
            self.crossfader_var.trace('w', self._update_crossfader_label)
            volume_frame.columnconfigure(1, weight=1)

        def _update_crossfader_label(self, *args):
            value = int(self.crossfader_var.get())
            text = f"{100 - value}% Track 1" if value < 25 else f"{value}% Track 2" if value > 75 else f"{value}% (Balanced)"
            self.crossfader_label.config(text=text)

        def _create_styled_button(self, parent, text, command, bg_color):
            return tk.Button(parent, text=text, command=command, bg=bg_color, font=("Arial", 9), relief="raised",
                             borderwidth=2, padx=10, pady=3)

        def update_gui(self, update_type: str, data: Any):
            try:
                if update_type == 'error':
                    messagebox.showerror("Audio Error", data)
                elif update_type == 'stop_track':
                    self.audio_processor.stop_track(data)
                elif update_type == 'bpm_update':
                    track_idx, bpm, confidence = data
                    self.bpm_labels[track_idx].config(text=f"BPM: {bpm if bpm else 'N/A'}")
                    self.confidence_labels[track_idx].config(text=f"Conf: {int(confidence * 100)}%")
                elif update_type == 'file_loaded':
                    track_idx, filename = data
                    self.file_labels[track_idx].config(text=os.path.basename(filename)[:30])
                elif update_type == 'waveform_update':
                    track_idx = data
                    self.waveform_display.update_waveform_static(track_idx)
            except Exception as e:
                print(f"Error executing GUI update: {e}")