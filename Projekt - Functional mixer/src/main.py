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
        pygame.mixer.set_num_channels(8) #konfiguracja silnika pygame

        self.root = tk.Tk() #tworzenie okna apki z biblioteki tkinter
        self.root.title("Mikser Audio")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="AudioMixer") #zadania asynchroniczne
        self.update_queue = queue.Queue(maxsize=100) #aktualizacja gui
        self.shutdown_event = threading.Event() # zamykanie wątków
        self.state_lock = RLock() # synchronizacja do wspólnego stanu audio
        #Rlock - specjalny tryb lock który pozwala wątkowi wejść więcej niż raz do danej sekcji kodu (nie jest blokowany jak w przypadku zwykłego lock)

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

    def on_closing(self): #bezpieczne zamknięcie apki
        try:
            self.shutdown_event.set() #informacja wątków o zamknięciu
            if hasattr(self.waveform_display, 'anim') and self.waveform_display.anim:
                self.waveform_display.anim.event_source.stop() #zatrzymanie animacji
            self.executor.shutdown(wait=False)
            pygame.mixer.stop()
            self.root.destroy() # zniszczenie gui
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
