import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from typing import List

class WaveformDisplay:
    def __init__(self, app):
        self.app = app
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.waveform_lines = None
        self.position_lines = None
        self.canvas = None
        self.anim = None

    def setup_waveform_display(self, parent):
        canvas_frame = tk.Frame(parent)
        canvas_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        plt.rcParams['animation.embed_limit'] = 2 ** 27
        plt.rcParams['figure.max_open_warning'] = 0

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

    def setup_animation(self):
        self.anim = FuncAnimation(
            self.fig,
            self.update_waveform,
            interval=33,
            blit=False,
            cache_frame_data=False,
            repeat=True
        )

    def update_waveform_static(self, track_index):
        try:
            with self.app.state_lock:
                data = self.app.audio_state.state['waveform_cache'][track_index]
                time_axis = self.app.audio_state.state['time_axes'][track_index]
                duration = self.app.audio_state.state['durations'][track_index]

            if data is not None and time_axis is not None:
                ax = self.ax1 if track_index == 0 else self.ax2
                line = self.waveform_lines[track_index]

                ax.clear()
                ax.plot(time_axis, data, color='blue' if track_index == 0 else 'red', alpha=0.7, linewidth=0.5)
                ax.set_title(f"Track {track_index + 1}")
                ax.set_ylabel("Amplitude")
                if track_index == 1:
                    ax.set_xlabel("Time (seconds)")
                ax.set_xlim(0, duration)

                self.position_lines[track_index] = ax.axvline(x=0, color='green', linestyle='--', linewidth=2,
                                                              alpha=0.8)
                self.canvas.draw_idle()

        except Exception as e:
            print(f"Error updating waveform: {e}")

    def update_waveform(self, frame):
        for track_idx in range(2):
            if (self.app.audio_state.state['data'][track_idx] is not None and
                    self.app.audio_state.state['durations'][track_idx] > 0):
                pos = self.app.audio_state.state['current_positions'][track_idx]
                pos = max(0, min(pos, self.app.audio_state.state['durations'][track_idx]))
                line = self.position_lines[track_idx]
                line.set_xdata([pos, pos])

                if self.app.audio_state.state['playing'][track_idx]:
                    color = 'green'
                elif self.app.audio_state.state['paused'][track_idx]:
                    color = 'orange'
                else:
                    color = 'red'
                line.set_color(color)
                line.set_alpha(0.8)

        self.fig.canvas.draw_idle()
        return self.position_lines
