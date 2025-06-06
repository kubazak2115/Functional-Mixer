import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
from tkinter import ttk
import threading

class WaveformDisplay:
    def __init__(self, root, audio_state):
        self.root = root
        self.audio_state = audio_state
        self.audio_state.waveform_display = self
        self.beat_grid_visible = False
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.canvas = None
        self.waveform_lines = None
        self.position_lines = None
        self.anim = None
        plt.rcParams['animation.embed_limit'] = 2 ** 27
        plt.rcParams['figure.max_open_warning'] = 0

    def setup_waveform_display(self, parent):
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6),
                                                      gridspec_kw={'height_ratios': [1, 1]},
                                                      tight_layout=True)
        self.ax1.set_title("Track 1")
        self.ax2.set_title("Track 2")
        self.ax1.set_ylabel("Amplitude")
        self.ax2.set_ylabel("Amplitude")
        self.ax2.set_xlabel("Time (seconds)")
        self.waveform_lines = [
            self.ax1.plot([], [], color='blue', alpha=0.7, linewidth=0.5)[0],
            self.ax2.plot([], [], color='red', alpha=0.7, linewidth=0.5)[0]
        ]
        self.position_lines = [
            self.ax1.axvline(x=0, color='green', linestyle='--', linewidth=2, alpha=0.8),
            self.ax2.axvline(x=0, color='green', linestyle='--', linewidth=2, alpha=0.8)
        ]
        self.ax1.beat_grid_lines = []
        self.ax2.beat_grid_lines = []
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._setup_animation()