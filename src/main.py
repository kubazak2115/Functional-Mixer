import tkinter as tk
from gui import AudioMixerGUI
from audio_processor import AudioProcessor
from audio_state import AudioState
from waveform_display import WaveformDisplay

class FunctionalAudioMixer:
    def __init__(self):
        self.root = tk.Tk()
        self.audio_state = AudioState()
        self.audio_processor = AudioProcessor(self.audio_state)
        self.waveform_display = WaveformDisplay(self.root, self.audio_state)
        self.gui = AudioMixerGUI(self.root, self.audio_state, self.audio_processor, self.waveform_display)

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.waveform_display.cleanup()
            self.audio_processor.cleanup()

if __name__ == "__main__":
    try:
        app = FunctionalAudioMixer()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {str(e)}")
