"""
AI Desktop Assistant - Main Window
Implements the primary UI for the desktop assistant application.
"""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

class MainWindow(QMainWindow):
    """Main application window for the AI Desktop Assistant."""
    
    # Define signals
    start_listening_signal = pyqtSignal()
    stop_listening_signal = pyqtSignal()
    process_text_signal = pyqtSignal(str)
    
    def __init__(self, config, parent=None):
        super(MainWindow, self).__init__(parent)
        self.config = config
        self.setWindowTitle("AI Desktop Assistant")
        self.setMinimumSize(800, 600)
        
        # Set window properties
        self.setWindowIcon(QIcon("resources/icon.png"))
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Set up UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main user interface components."""
        # Header
        header_label = QLabel("AI Desktop Assistant")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.layout.addWidget(header_label)
        
        # Placeholder for assistant interface
        self.assistant_widget = QWidget()
        self.assistant_layout = QVBoxLayout(self.assistant_widget)
        
        # Assistant response area
        self.response_label = QLabel("Hello! How can I help you today?")
        self.response_label.setAlignment(Qt.AlignCenter)
        self.response_label.setFont(QFont("Arial", 14))
        self.response_label.setWordWrap(True)
        self.assistant_layout.addWidget(self.response_label)
        
        # Microphone button
        self.mic_button = QPushButton("Press to Speak")
        self.mic_button.setFixedSize(QSize(200, 50))
        self.mic_button.clicked.connect(self.on_mic_button_clicked)
        self.assistant_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        
        self.layout.addWidget(self.assistant_widget)
    
    def update_response(self, text):
        """Update the assistant's response text."""
        self.response_label.setText(text)
        
    def on_speech_recognized(self, text):
        """Handle recognized speech."""
        if not text:
            return
            
        # Update the UI with the recognized text
        self.update_response(f"You said: {text}\n\nProcessing...")
        
        # Emit signal to process the text
        self.process_text_signal.emit(text)
    
    def on_listening_started(self):
        """Handle when the assistant starts listening."""
        # Update UI to show that the assistant is listening
        self.update_response("Listening...")
        self.mic_button.setEnabled(False)
        self.mic_button.setText("Listening...")
        
        # You could also update visuals or play a sound here
        
    def on_listening_ended(self):
        """Handle when the assistant stops listening."""
        # Reset the microphone button
        self.mic_button.setEnabled(True)
        self.mic_button.setText("Press to Speak")
    
    def on_mic_button_clicked(self):
        """Handle microphone button click."""
        # Emit signal to start listening
        self.start_listening_signal.emit()
        
    def add_assistant_message(self, message):
        """Add an assistant message to the conversation."""
        if not message:
            return
        
        # Update the response label with the assistant's message
        self.update_response(message)
        
    def add_user_message(self, message):
        """Add a user message to the conversation."""
        if not message:
            return
            
        # Update the response label with the user's message
        # In a more complex UI, this would add to a conversation view
        self.update_response(f"You: {message}")
    
    def set_light_theme(self):
        """Apply light theme to the application."""
        # Set light theme colors and styles
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                color: #333333;
            }
        """)
    
    def set_dark_theme(self):
        """Apply dark theme to the application."""
        # Set dark theme colors and styles
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #333333;
                color: #f5f5f5;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #505050;
                color: #aaaaaa;
            }
            QLabel {
                color: #f5f5f5;
            }
        """)
