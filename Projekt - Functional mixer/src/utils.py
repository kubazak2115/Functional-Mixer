import threading
import time
import queue
import os
from tkinter import messagebox
from functools import wraps
from typing import Tuple

class Utils:
    def __init__(self, app):
        self.app = app
        self.gui_update_throttle = 0.033
        self.last_gui_update = 0
        self.position_update_throttle = 0.016
        self.last_position_update = 0

    def handle_audio_errors(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.app.update_queue.put(('error', f"Error in {func.__name__}: {str(e)}"))
                return None
        return wrapper

    def start_background_threads(self):
        self.position_thread = threading.Thread(
            target=self._position_updater_optimized,
            daemon=True,
            name="PositionUpdater"
        )
        self.position_thread.start()

        self.gui_update_thread = threading.Thread(
            target=self._process_gui_updates,
            daemon=True,
            name="GUIUpdater"
        )
        self.gui_update_thread.start()

        self.waveform_scheduler = threading.Thread(
            target=self._schedule_waveform_updates,
            daemon=True,
            name="WaveformScheduler"
        )
        self.waveform_scheduler.start()

    def _position_updater_optimized(self):
        while not self.app.shutdown_event.is_set():
            try:
                current_time = time.time()
                if current_time - self.last_position_update < self.position_update_throttle:
                    time.sleep(0.001)
                    continue
                self.last_position_update = current_time

                with self.app.state_lock:
                    for i in range(2):
                        if self.app.audio_state.state['playing'][i]:
                            elapsed = current_time - self.app.audio_state.state['start_times'][i]
                            self.app.audio_state.state['current_positions'][i] = elapsed
                            if (elapsed >= self.app.audio_state.state['durations'][i] and
                                    self.app.audio_state.state['durations'][i] > 0):
                                self.app.update_queue.put(('stop_track', i))
                time.sleep(0.005)
            except Exception as e:
                print(f"Error in position_updater_optimized: {e}")
                time.sleep(0.1)

    def _process_gui_updates(self):
        while not self.app.shutdown_event.is_set():
            try:
                updates_processed = 0
                while not self.app.update_queue.empty() and updates_processed < 10:
                    try:
                        update_type, data = self.app.update_queue.get_nowait()
                        self.app.root.after_idle(self._execute_gui_update, update_type, data)
                        updates_processed += 1
                    except queue.Empty:
                        break
                time.sleep(0.016)
            except Exception as e:
                print(f"Error in _process_gui_updates: {e}")
                time.sleep(0.1)

    def _execute_gui_update(self, update_type, data):
        try:
            if update_type == 'error':
                messagebox.showerror("Audio Error", data)
            elif update_type == 'stop_track':
                self.app.gui.stop_track(data)
            elif update_type == 'bpm_update':
                track_idx, bpm, confidence = data
                self.app.gui.bpm_labels[track_idx].config(text=f"BPM: {bpm if bpm else 'N/A'}")
                self.app.gui.confidence_labels[track_idx].config(text=f"Conf: {int(confidence * 100)}%")
            elif update_type == 'file_loaded':
                track_idx, filename = data
                self.app.gui.file_labels[track_idx].config(text=os.path.basename(filename)[:30])
            elif update_type == 'waveform_update':
                track_idx = data
                self.app.waveform_display.update_waveform_static(track_idx)
        except Exception as e:
            print(f"Error executing GUI update: {e}")

    def _schedule_waveform_updates(self):
        while not self.app.shutdown_event.is_set():
            try:
                current_time = time.time()
                if current_time - self.last_gui_update < self.gui_update_throttle:
                    time.sleep(0.01)
                    continue
                self.last_gui_update = current_time

                needs_update = False
                with self.app.state_lock:
                    for i in range(2):
                        if self.app.audio_state.state['playing'][i]:
                            needs_update = True
                            break
                if needs_update:
                    self.app.root.after_idle(self._trigger_waveform_update)
                time.sleep(0.033)
            except Exception as e:
                print(f"Error in _schedule_waveform_updates: {e}")
                time.sleep(0.1)

    def _trigger_waveform_update(self):
        try:
            pass
        except Exception as e:
            print(f"Error in _trigger_waveform_update: {e}")
