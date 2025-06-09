import pygame
import tkinter as tk
from threading import RLock
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
from gui import GUI
from audio_processor import AudioProcessor
from audio_state import AudioState
from waveform_display import WaveformDisplay
from utils import Utils

class FunctionalAudioMixer:
    def __init__(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)

        self.root = tk.Tk()
        self.root.title("Mikser Audio DJ z Analizą BPM")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AudioMixer")
        self.update_queue = queue.Queue(maxsize=100)
        self.shutdown_event = threading.Event()
        self.state_lock = RLock()

        self.audio_state = AudioState()
        self.audio_state.state_lock = self.state_lock
        self.audio_processor = AudioProcessor()
        self.utils = Utils(self)
        self.waveform_display = WaveformDisplay(self)
        self.gui = GUI(self)

        self.gui.setup_gui()
        self.waveform_display.setup_animation()
        self.utils.start_background_threads()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        try:
            self.shutdown_event.set()
            if hasattr(self.waveform_display, 'anim') and self.waveform_display.anim:
                self.waveform_display.anim.event_source.stop()
            self.executor.shutdown(wait=False)
            pygame.mixer.stop()
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = FunctionalAudioMixer()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
