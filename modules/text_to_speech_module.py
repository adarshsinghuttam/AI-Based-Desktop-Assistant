"""
AI Desktop Assistant - Text-to-Speech Module
Handles converting text to spoken audio.
"""

import pyttsx3
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

class SpeakTask(QRunnable):
    """Runnable task for speaking text to avoid blocking the main thread."""
    def __init__(self, engine, text):
        super().__init__()
        self.engine = engine
        self.text = text

    def run(self):
        try:
            self.engine.say(self.text)
            self.engine.runAndWait()
        except RuntimeError:
            # This can happen if the engine is busy or shutdown.
            print(f"TTS engine error, could not say: {self.text}")
        except Exception as e:
            print(f"Error in speech task: {e}")

class TextToSpeechModule(QObject):
    """
    Handles text-to-speech functionality.
    Emits signals when speech starts and finishes.
    """
    speech_started = pyqtSignal()
    speech_finished = pyqtSignal()
    
    def __init__(self, config=None):
        """Initialize the text-to-speech engine."""
        super().__init__()
        self.config = config
        self.engine = pyttsx3.init()
        self.thread_pool = QThreadPool()
        self.speaking = False
        self.init_engine()
        
    def init_engine(self):
        """Initialize or reinitialize the text-to-speech engine."""
        # Configure properties from config if available
        rate = self.config.get("tts", "rate", 150) if self.config and hasattr(self.config, 'get') else 150
        volume = self.config.get("tts", "volume", 1.0) if self.config and hasattr(self.config, 'get') else 1.0
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Set voice from config if available
        voices = self.engine.getProperty('voices')
        voice_id_str = self.config.get("tts", "voice_id", None) if self.config and hasattr(self.config, 'get') else None
        
        if voice_id_str:
            self.engine.setProperty('voice', voice_id_str)
        elif voices:
            for voice in voices:
                if 'female' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break

        # Connect callbacks
        self.engine.connect('started-word', self.on_start)
        self.engine.connect('finished-flat', self.on_finish)
    
    def on_start(self, name, location, length):
        """Callback triggered when speech starts."""
        if not self.speaking:
            self.speaking = True
            self.speech_started.emit()

    def on_finish(self, name, completed):
        """Callback triggered when speech finishes."""
        if self.speaking:
            self.speaking = False
            self.speech_finished.emit()

    def speak(self, text):
        """
        Convert text to speech in a non-blocking way.
        """
        if not text:
            return
            
        print(f"Speaking: {text}")
        task = SpeakTask(self.engine, text)
        self.thread_pool.start(task)
    
    def shutdown(self):
        """
        Properly shut down the text-to-speech engine.
        """
        try:
            self.engine.stop()
        except Exception as e:
            print(f"Error stopping engine: {e}")
        self.thread_pool.waitForDone()
    
    def get_available_voices(self):
        """
        Get a list of available voices.
        
        Returns:
            list: List of available voice objects
        """
        return self.engine.getProperty('voices')
