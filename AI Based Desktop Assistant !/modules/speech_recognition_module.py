"""
AI Desktop Assistant - Speech Recognition Module
Handles speech-to-text functionality for voice commands.
"""

import speech_recognition as sr
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import threading

class SpeechRecognitionThread(QThread):
    """Thread class for handling speech recognition in background"""
    
    # Define signals
    text_recognized = pyqtSignal(str)
    listening_ended = pyqtSignal()
    
    def __init__(self, recognizer, microphone, config=None):
        """Initialize the speech recognition thread"""
        super(SpeechRecognitionThread, self).__init__()
        self.recognizer = recognizer
        self.microphone = microphone
        self.config = config
        self.is_listening = False
        self.stop_event = threading.Event()
        
    def run(self):
        """Main thread execution method"""
        try:
            # Get timeout settings from config or use defaults
            listen_timeout = 5  # Reduced timeout for more responsive experience
            phrase_timeout = 3  # Time to wait for a phrase to complete
            
            # Recalibrate for ambient noise each time to adapt to changing environments
            with self.microphone as source:
                print("Listening...")
                # Quick recalibration for current ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    # Listen with reduced timeout and phrase time limit for better responsiveness
                    # This makes the assistant more responsive to timeouts
                    audio = self.recognizer.listen(
                        source, 
                        timeout=listen_timeout, 
                        phrase_time_limit=phrase_timeout
                    )
                    
                    # Check if we've been asked to stop
                    if self.stop_event.is_set():
                        print("Listening stopped during audio capture")
                        self.listening_ended.emit()
                        return
                        
                    print("Processing speech...")
                    # Try recognition with Google
                    try:
                        text = self.recognizer.recognize_google(audio)
                        print(f"Recognized: {text}")
                        
                        # Only emit recognized text if we have text
                        if text and len(text.strip()) > 0:
                            # Emit the signal with text
                            self.text_recognized.emit(text)
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results from speech recognition service; {e}")
                
                except sr.WaitTimeoutError:
                    print("No speech detected - waited too long")
                except Exception as e:
                    print(f"Error in speech recognition thread: {e}")
                    
        except Exception as e:
            print(f"Unexpected error in speech recognition thread: {e}")
        finally:
            # Always emit the listening ended signal when we're done
            self.listening_ended.emit()

class SpeechRecognitionModule(QObject):
    """Handles speech recognition functionality."""
    
    # Define signals
    text_recognized = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_ended = pyqtSignal()
    
    def __init__(self, config=None):
        """Initialize the speech recognition engine."""
        super(SpeechRecognitionModule, self).__init__()
        self.config = config
        self.recognizer = sr.Recognizer()
        
        # Configure recognition parameters
        self.recognizer.energy_threshold = 3500  # Slightly lower threshold for better detection
        self.recognizer.dynamic_energy_threshold = True  # Dynamically adjust for ambient noise
        self.recognizer.pause_threshold = 0.8  # Shorter pause threshold for quicker response
        
        # Thread management
        self.speech_thread = None
        self.timeout_count = 0
        self.max_timeouts = 3  # Maximum number of consecutive timeouts before stopping
        
        # Get default microphone
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise on startup
            with self.microphone as source:
                print("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Microphone calibrated.")
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            # Will handle microphone errors gracefully during listening
    
    def start_listening(self):
        """
        Start the listening process in a non-blocking way.
        This will be connected to the UI button.
        """
        # Don't start new thread if one is already running
        if self.speech_thread and self.speech_thread.isRunning():
            print("Already listening")
            return
            
        # Reset auto-restart counter
        self.timeout_count = 0
            
        # Emit signal that listening has started
        self.listening_started.emit()
        
        # Create and start the thread
        self.speech_thread = SpeechRecognitionThread(self.recognizer, self.microphone, self.config)
        
        # Connect signals
        self.speech_thread.text_recognized.connect(self.on_text_recognized)
        self.speech_thread.listening_ended.connect(self.on_listening_ended)
        
        # Start the thread
        self.speech_thread.start()
        
        # Enable continuous listening mode with auto-restart
        QTimer.singleShot(7000, self.check_and_restart_listening)
        
    def on_text_recognized(self, text):
        """Handle recognized text from the thread"""
        self.text_recognized.emit(text)
        
    def on_listening_ended(self):
        """Handle the end of listening from the thread"""
        self.listening_ended.emit()
        
    def check_and_restart_listening(self):
        """Check if listening has ended due to timeout and possibly restart it"""
        # Only restart if the thread has ended
        if not self.speech_thread or not self.speech_thread.isRunning():
            if self.timeout_count < self.max_timeouts:
                # Increment timeout counter
                self.timeout_count += 1
                print(f"Auto-restarting listening (timeout {self.timeout_count}/{self.max_timeouts})")
                # Restart listening
                self.start_listening()
            else:
                print(f"Reached maximum consecutive timeouts ({self.max_timeouts}). Stopping auto-restart.")
                # Reset counter for next manual start
                self.timeout_count = 0
        
    def debug_listen(self, test_text):
        """Debug method to simulate speech recognition for testing"""
        self.listening_started.emit()
        print(f"Debug mode - simulating speech: '{test_text}'")
        
        # Emit recognized text
        self.text_recognized.emit(test_text)
        self.listening_ended.emit()
        
    def stop_listening(self):
        """
        Stop the listening process by signaling the listening thread to stop.
        """
        if self.speech_thread and self.speech_thread.isRunning():
            print("Stopping listening thread")
            # Set the stop event to signal the thread to exit
            self.speech_thread.stop_event.set()
            
            # Wait a moment for the thread to clean up (non-blocking)
            QThread.msleep(100)
        else:
            print("No listening thread to stop")
            # Still emit in case UI is out of sync
            self.listening_ended.emit()
