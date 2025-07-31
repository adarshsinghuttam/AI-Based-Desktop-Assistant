"""
AI Desktop Assistant - Configuration Module
Handles application configuration and settings.
"""

import os
import json
from pathlib import Path

class AppConfig:
    """Manages application configuration and settings."""
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str, optional): Path to the configuration file.
                If not provided, will use default location.
        """
        self.config_data = {}
        
        # Set default config file location if not provided
        if not config_file:
            app_dir = Path.home() / ".ai_assistant"
            app_dir.mkdir(exist_ok=True)
            self.config_file = app_dir / "config.json"
        else:
            self.config_file = Path(config_file)
        
        # Load config or create default
        self.load_config()
    
    def load_config(self):
        """
        Load configuration from file or create default if file doesn't exist.
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
            else:
                self.create_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """
        Create default configuration.
        """
        self.config_data = {
            "general": {
                "voice_enabled": True,
                "startup_greeting": True,
                "theme": "default"
            },
            "voice": {
                "rate": 150,
                "volume": 1.0,
                "preferred_voice": None
            },
            "weather": {
                "default_location": None,
                "units": "metric"  # metric, imperial, standard
            },
            "news": {
                "default_country": "us",
                "default_category": "general",
                "article_count": 5
            }
        }
    
    def save_config(self):
        """
        Save configuration to file.
        
        Returns:
            bool: Success status
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, section, key, default=None):
        """
        Get a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            default: Default value if section/key not found
            
        Returns:
            Value from configuration or default
        """
        return self.config_data.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """
        Set a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value: Value to set
            
        Returns:
            bool: Success status
        """
        if section not in self.config_data:
            self.config_data[section] = {}
            
        self.config_data[section][key] = value
        return self.save_config()
    
    def get_all(self):
        """
        Get all configuration data.
        
        Returns:
            dict: All configuration data
        """
        return self.config_data
