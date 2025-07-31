# # This is a sample Python script.
#
# # Press Shift+F10 to execute it or replace it with your code.
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
#
# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
"""
AI Desktop Assistant - Main Application
A modern Siri-inspired desktop assistant with voice interaction, news, weather, and more.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QRect, QDateTime
from PyQt5.QtGui import QFont, QIcon
from dotenv import load_dotenv

# Import custom modules
from ui.main_window import MainWindow
from modules.speech_recognition_module import SpeechRecognitionModule
from modules.text_to_speech_module import TextToSpeechModule
from modules.news_module import NewsModule
from modules.weather_module import WeatherModule
from modules.ai_module import AIModule
from utils.config import AppConfig

# Load environment variables
load_dotenv()


class AIAssistantApp:
    """Main application class that initializes and connects all modules"""

    def __init__(self):
        # Initialize application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AI Desktop Assistant")
        self.app.setStyle("Fusion")  # Use Fusion style for a modern look

        # Load configuration
        self.config = AppConfig()

        # Initialize main window
        self.main_window = MainWindow(self.config)

        # Initialize modules
        self.init_modules()

        # Connect signals and slots
        self.connect_signals()

        # Set application icon
        self.app.setWindowIcon(QIcon(os.path.join("assets", "icons", "app_icon.png")))

        # Command tracking
        self.command_history = []
        self.max_history_size = 20  # Store last 20 commands
        self.recent_intents = {}

        # Listening state management
        self.is_listening_enabled = False
        
        # Apply theme
        self.apply_theme()

    def init_modules(self):
        """Initialize all assistant modules"""
        # Speech recognition module
        self.speech_module = SpeechRecognitionModule(self.config)

        # Text-to-speech module
        self.tts_module = TextToSpeechModule(self.config)

        # News module
        self.news_module = NewsModule(self.config)

        # Weather module
        self.weather_module = WeatherModule(self.config)

        # AI module for answering questions
        self.ai_module = AIModule(self.config)

    def connect_signals(self):
        """Connect signals and slots between UI and modules"""
        # Connect speech recognition signals
        self.speech_module.text_recognized.connect(self.main_window.on_speech_recognized)
        self.speech_module.listening_started.connect(self.main_window.on_listening_started)
        self.speech_module.listening_ended.connect(self.main_window.on_listening_ended)

        # Connect UI signals to control listening state
        self.main_window.start_listening_signal.connect(self.enable_listening)
        self.main_window.stop_listening_signal.connect(self.disable_listening)
        self.main_window.process_text_signal.connect(self.process_command)

        # Connect TTS signals to pause/resume listening
        self.tts_module.speech_started.connect(self.speech_module.stop_listening)
        self.tts_module.speech_finished.connect(self.resume_listening_after_tts)

        # Connect window close event
        self.main_window.closeEvent = self.handle_close_event

    def apply_theme(self):
        """Apply the current theme to the application"""
        if self.config.get("dark_theme", False):
            self.main_window.set_dark_theme()
        else:
            self.main_window.set_light_theme()

    def process_command(self, text):
        """Process a command or query from the user"""
        # Guard against empty or None text
        if not text:
            self.handle_assistant_response("I didn't catch that. Could you please speak again?")
            return
            
        # Add user message to the conversation
        self.main_window.add_user_message(text)
        
        # Track this command in history
        self.add_to_command_history(text)
        
        # First check for direct system commands
        if self.process_system_command(text):
            return
            
        # Check for specific command types
        command_intent = self.get_command_intent(text)
        
        # Update intent frequency
        self.update_intent_frequency(command_intent)
        
        # Process based on intent
        if command_intent == "weather":
            self.process_weather_command(text)
            
        elif command_intent == "news":
            self.process_news_command(text)
            
        elif command_intent == "reminder":
            self.process_reminder_command(text)
            
        else:
            # Use AI module for general queries
            self.ai_module.process_query(text, self.handle_ai_response)
            
    def get_command_intent(self, text):
        """Determine the intent of a command"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["weather", "temperature", "forecast"]):
            return "weather"
            
        elif any(word in text_lower for word in ["news", "headlines", "latest"]):
            return "news"
            
        elif any(word in text_lower for word in ["remind", "reminder", "schedule"]):
            return "reminder"
            
        elif any(word in text_lower for word in ["time", "date", "day"]):
            return "time"
            
        elif any(word in text_lower for word in ["help", "command", "what can you do"]):
            return "help"
            
        return "general"
        
    def process_system_command(self, text):
        """Process system commands like exit, shutdown, etc."""
        text_lower = text.lower()
        
        # Check for command prefixes
        command_prefixes = ["computer", "assistant", "hey assistant", "execute", "run"]
        is_direct_command = any(text_lower.startswith(prefix) for prefix in command_prefixes)
        
        # If it's a direct command, strip the prefix
        if is_direct_command:
            for prefix in command_prefixes:
                if text_lower.startswith(prefix):
                    # Remove prefix and trim whitespace
                    command_text = text_lower[len(prefix):].strip()
                    return self.execute_direct_command(command_text)
        
        # Exit commands
        if any(cmd in text_lower for cmd in ["exit", "quit", "close", "shutdown"]):
            self.handle_assistant_response("Shutting down. Goodbye!")
            QTimer.singleShot(2000, self.app.quit)
            return True
            
        # Help command
        elif any(cmd in text_lower for cmd in ["help", "what can you do", "commands"]):
            self.show_help()
            return True
            
        # History command
        elif any(cmd in text_lower for cmd in ["history", "previous commands", "what did i say"]):
            self.show_command_history()
            return True
            
        return False
        
    def execute_direct_command(self, command_text):
        """Execute a direct command from the user"""
        # Simple command mapping
        if command_text in ["time", "current time", "what time is it"]:
            current_time = QDateTime.currentDateTime().toString("hh:mm AP")
            self.handle_assistant_response(f"The current time is {current_time}")
            return True
            
        elif command_text in ["date", "today", "what day is it", "current date"]:
            current_date = QDateTime.currentDateTime().toString("dddd, MMMM d, yyyy")
            self.handle_assistant_response(f"Today is {current_date}")
            return True
            
        elif command_text in ["repeat", "repeat last", "say that again"]:
            if self.command_history and len(self.command_history) > 1:
                last_command = self.command_history[-2]["command"]
                self.handle_assistant_response(f"Your last command was: {last_command}")
            else:
                self.handle_assistant_response("You haven't made any previous commands.")
            return True
            
        elif command_text in ["start listening", "listen"]:
            self.speech_module.start_listening()
            self.handle_assistant_response("I'm listening now.")
            return True
            
        elif command_text in ["stop listening", "stop"]:
            self.speech_module.stop_listening()
            self.handle_assistant_response("I've stopped listening.")
            return True
            
        # Try to process as a general command if no direct match
        return False
        
    def add_to_command_history(self, command):
        """Add a command to the history"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.command_history.append({
            "command": command,
            "timestamp": timestamp,
            "intent": self.get_command_intent(command)
        })
        
        # Limit history size
        if len(self.command_history) > self.max_history_size:
            self.command_history.pop(0)
            
    def update_intent_frequency(self, intent):
        """Update the frequency counter for intents"""
        if intent in self.recent_intents:
            self.recent_intents[intent] += 1
        else:
            self.recent_intents[intent] = 1
            
    def show_help(self):
        """Show available commands"""
        help_text = (
            "Here are the things I can help you with:\n"
            "- Weather information (e.g., 'What's the weather today?')\n"
            "- News headlines (e.g., 'Show me the latest news')\n"
            "- Reminders (e.g., 'Remind me to call mom')\n"
            "- General questions (e.g., 'Who is the president?')\n"
            "- System commands (e.g., 'exit', 'history')\n\n"
            "You can also ask me about your command history."
        )
        self.handle_assistant_response(help_text)
        
    def show_command_history(self):
        """Show the command history"""
        if not self.command_history:
            self.handle_assistant_response("You haven't given me any commands yet.")
            return
            
        # Show the last 5 commands
        num_to_show = min(5, len(self.command_history))
        history_items = self.command_history[-num_to_show:]
        
        response = "Here are your recent commands:\n"
        for i, item in enumerate(reversed(history_items), 1):
            response += f"{i}. {item['command']} ({item['timestamp']})\n"
            
        self.handle_assistant_response(response)

    def process_weather_command(self, text):
        """Process a weather-related command"""
        # Extract location from the command if specified, otherwise use default
        location = self.config.get("default_location", "Lucknow")
        self.weather_module.get_weather(location, self.handle_weather_response)

    def process_news_command(self, text):
        """Process a news-related command"""
        # Extract category from the command if specified, otherwise use top headlines
        category = "general"
        if "technology" in text.lower() or "tech" in text.lower():
            category = "technology"
        elif "sports" in text.lower():
            category = "sports"
        elif "business" in text.lower():
            category = "business"

        self.news_module.get_news(category, self.handle_news_response)

    def process_reminder_command(self, text):
        """Process a reminder-related command"""
        # Simple reminder implementation - would be expanded in a real application
        response = "I've set a reminder for you"
        self.handle_assistant_response(response)

    def handle_weather_response(self, weather_info):
        """Handle the response from the weather module"""
        if weather_info["success"]:
            response = f"The weather in {weather_info['location']} is {weather_info['description']} with a temperature of {weather_info['temperature']}°C."
            if "forecast" in weather_info:
                response += f" Tomorrow's forecast: {weather_info['forecast']}"
        else:
            response = "Sorry, I couldn't get the weather information. Please try again later."

        self.handle_assistant_response(response)

    def handle_news_response(self, news_info):
        """Handle the response from the news module"""
        if news_info["success"]:
            news_items = news_info["articles"][:3]  # Get top 3 articles

            response = "Here are the latest headlines: "
            for i, article in enumerate(news_items, 1):
                response += f"{i}. {article['title']}. "
        else:
            response = "Sorry, I couldn't get the latest news. Please try again later."

        self.handle_assistant_response(response)

    def handle_ai_response(self, response_info):
        """Handle the response from the AI module"""
        if response_info["success"]:
            response = response_info["response"]
        else:
            response = "Sorry, I couldn't process your request. Please try again."

        self.handle_assistant_response(response)

    def handle_assistant_response(self, response):
        """Process and display the assistant's response"""
        # Add assistant message to the conversation UI
        self.main_window.add_assistant_message(response)

        # Speak the response
        self.tts_module.speak(response)

    def enable_listening(self):
        """Enable listening mode and start recognition."""
        self.is_listening_enabled = True
        self.speech_module.start_listening()

    def disable_listening(self):
        """Disable listening mode and stop recognition."""
        self.is_listening_enabled = False
        self.speech_module.stop_listening()

    def resume_listening_after_tts(self):
        """Resume listening if it was enabled before TTS started."""
        if self.is_listening_enabled:
            self.speech_module.start_listening()

    def handle_close_event(self, event):
        """Handle application close event"""
        # Shut down all modules properly
        self.speech_module.stop_listening()
        self.tts_module.shutdown()
        event.accept()
        
    def run(self):
        """Run the application main loop"""
        # Show the main window
        self.main_window.show()
        
        # Start with a greeting if enabled
        if self.config.get("general", "startup_greeting", True):
            greeting = "Hello! I'm your AI desktop assistant. How can I help you today?"
            self.main_window.add_assistant_message(greeting)
            self.tts_module.speak(greeting)
        
        # Automatically start listening after the greeting
        self.enable_listening()

        # Execute the application
        return self.app.exec_()


if __name__ == "__main__":
    app = AIAssistantApp()
    sys.exit(app.run())
