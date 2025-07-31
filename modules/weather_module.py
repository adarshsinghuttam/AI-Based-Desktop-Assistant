"""
AI Desktop Assistant - Weather Module
Fetches and processes weather data.
"""

import requests
import json
import os
from datetime import datetime

class WeatherModule:
    """Handles fetching and processing of weather data."""
    
    def __init__(self, config=None, api_key=None):
        """
        Initialize the weather module.
        
        Args:
            config (AppConfig, optional): Application configuration object
            api_key (str, optional): OpenWeatherMap API key. If not provided, will try to get from environment.
        """
        self.config = config
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv('WEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            print("Warning: No OpenWeatherMap API key provided. Weather functionality will be limited.")
    
    def get_current_weather(self, city=None, lat=None, lon=None, units="metric"):
        """
        Get current weather for a location.
        
        Args:
            city (str, optional): City name (e.g., "London,UK")
            lat (float, optional): Latitude coordinate
            lon (float, optional): Longitude coordinate
            units (str): Units of measurement (metric, imperial, standard)
            
        Returns:
            dict: Weather data dictionary or None if failed
        """
        if not self.api_key:
            print("Error: No OpenWeatherMap API key available.")
            return self._get_dummy_weather()
            
        try:
            url = f"{self.base_url}/weather"
            params = {
                'appid': self.api_key,
                'units': units
            }
            
            # Set location parameter
            if city:
                params['q'] = city
            elif lat is not None and lon is not None:
                params['lat'] = lat
                params['lon'] = lon
            else:
                print("Error: No location provided.")
                return self._get_dummy_weather()
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return self._get_dummy_weather()
    
    def get_forecast(self, city=None, lat=None, lon=None, units="metric", days=5):
        """
        Get weather forecast for a location.
        
        Args:
            city (str, optional): City name (e.g., "London,UK")
            lat (float, optional): Latitude coordinate
            lon (float, optional): Longitude coordinate
            units (str): Units of measurement (metric, imperial, standard)
            days (int): Number of days to forecast (max 5)
            
        Returns:
            dict: Forecast data dictionary or None if failed
        """
        if not self.api_key:
            print("Error: No OpenWeatherMap API key available.")
            return None
            
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'appid': self.api_key,
                'units': units
            }
            
            # Set location parameter
            if city:
                params['q'] = city
            elif lat is not None and lon is not None:
                params['lat'] = lat
                params['lon'] = lon
            else:
                print("Error: No location provided.")
                return None
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def _get_dummy_weather(self):
        """
        Get dummy weather data when API is unavailable.
        
        Returns:
            dict: Dummy weather data dictionary
        """
        return {
            'name': 'Example City',
            'main': {
                'temp': 20,
                'feels_like': 19,
                'temp_min': 18,
                'temp_max': 22,
                'humidity': 70
            },
            'weather': [
                {
                    'main': 'Clear',
                    'description': 'clear sky'
                }
            ],
            'wind': {
                'speed': 3.5
            }
        }
    
    def format_weather_for_speech(self, weather_data):
        """
        Format weather data for speech output.
        
        Args:
            weather_data (dict): Weather data dictionary
            
        Returns:
            str: Formatted text for speech output
        """
        if not weather_data:
            return "I couldn't retrieve the weather information at the moment."
            
        try:
            city = weather_data.get('name', 'Unknown location')
            temp = weather_data.get('main', {}).get('temp', 'unknown')
            feels_like = weather_data.get('main', {}).get('feels_like', 'unknown')
            conditions = weather_data.get('weather', [{}])[0].get('description', 'unknown conditions')
            humidity = weather_data.get('main', {}).get('humidity', 'unknown')
            wind_speed = weather_data.get('wind', {}).get('speed', 'unknown')
            
            return (
                f"The current weather in {city} is {temp} degrees with {conditions}. "
                f"It feels like {feels_like} degrees. "
                f"Humidity is at {humidity}% and wind speed is {wind_speed} meters per second."
            )
        except Exception as e:
            print(f"Error formatting weather data: {e}")
            return "I'm having trouble interpreting the weather data right now."
            
    def get_weather(self, location, callback=None):
        """
        Get weather for a location and process it using a callback.
        
        Args:
            location (str): Location to get weather for
            callback (function): Optional callback function to handle the response
            
        Returns:
            dict: Weather information dictionary
        """
        try:
            # Get units setting from config or use default
            units = "metric"  # Default units
            if self.config:
                units = self.config.get("weather", "units", "metric")
                
            # Get the current weather
            weather_data = self.get_current_weather(city=location, units=units)
            
            if not weather_data:
                raise Exception("Failed to retrieve weather data")
                
            # Extract relevant information
            temperature = weather_data.get('main', {}).get('temp', 'N/A')
            description = weather_data.get('weather', [{}])[0].get('description', 'N/A')
            
            # Create response dictionary
            weather_info = {
                "success": True,
                "location": location,
                "temperature": temperature,
                "description": description,
                "full_data": weather_data
            }
            
            # Add forecast if available
            try:
                forecast_data = self.get_forecast(city=location, units=units, days=1)
                if forecast_data and 'list' in forecast_data and len(forecast_data['list']) > 0:
                    tomorrow = forecast_data['list'][4]  # Roughly 24 hours from now
                    weather_info["forecast"] = tomorrow.get('weather', [{}])[0].get('description', 'N/A')
            except Exception as e:
                print(f"Error getting forecast: {e}")
            
            # Call the callback if provided
            if callback:
                callback(weather_info)
                
            return weather_info
            
        except Exception as e:
            print(f"Error getting weather: {e}")
            
            # Create error response with dummy data
            dummy_data = self._get_dummy_weather()
            error_response = {
                "success": False,
                "location": location,
                "temperature": dummy_data.get('main', {}).get('temp', 'N/A'),
                "description": dummy_data.get('weather', [{}])[0].get('description', 'N/A'),
                "error": str(e)
            }
            
            # Call the callback if provided
            if callback:
                callback(error_response)
                
            return error_response
