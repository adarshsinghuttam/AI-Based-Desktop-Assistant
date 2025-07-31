"""
AI Desktop Assistant - AI Module
Handles AI functionality and natural language processing.
"""

import os

# Handle openai import conditionally
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI package not installed. Using fallback responses.")

class AIModule:
    """Handles AI functionality using OpenAI's GPT models."""
    
    def __init__(self, config=None, api_key=None):
        """
        Initialize the AI module.
        
        Args:
            config (AppConfig, optional): Application configuration object
            api_key (str, optional): OpenAI API key. If not provided, will try to get from environment.
        """
        self.config = config
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # Only set API key if OpenAI is available
        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
        else:
            if not OPENAI_AVAILABLE:
                print("OpenAI package not available. Using fallback responses.")
            if not self.api_key:
                print("Warning: No OpenAI API key provided. AI functionality will be limited.")
    
    def generate_response(self, prompt, max_tokens=150):
        """
        Generate a response to a prompt using OpenAI API.
        
        Args:
            prompt (str): The user's input prompt
            max_tokens (int): Maximum number of tokens to generate
            
        Returns:
            str: Generated response or error message
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            return self._get_fallback_response(prompt)
            
        try:
            # Use the OpenAI ChatCompletions API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Using the model specified in the curl example
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,  # Add some creative variation
                store=True  # As specified in the curl example
            )
            
            # Extract the response content
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return "I'm not sure how to respond to that."
                
        except Exception as e:
            print(f"Error in OpenAI API call: {e}")
            return self._get_fallback_response(prompt)
    
    def process_command(self, command):
        """
        Process a user command and determine intent.
        
        Args:
            command (str): The user's command
            
        Returns:
            dict: Command intent and parameters
        """
        # Simple rule-based intent recognition
        command = command.lower()
        
        if any(word in command for word in ['weather', 'temperature', 'forecast']):
            return {'intent': 'weather', 'params': {'location': self._extract_location(command)}}
            
        elif any(word in command for word in ['news', 'headlines', 'articles']):
            return {'intent': 'news', 'params': {'category': self._extract_category(command)}}
            
        elif any(word in command for word in ['time', 'date', 'day']):
            return {'intent': 'time', 'params': {}}
            
        # Add more intents as needed
            
        return {'intent': 'general', 'params': {'query': command}}
    
    def _extract_location(self, text):
        """
        Extract location from text using simple heuristics.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Extracted location or None
        """
        # This is a very basic implementation
        # In a real app, you'd use NLP techniques like NER
        
        # Check for "in [location]" pattern
        if 'in ' in text:
            parts = text.split('in ')
            if len(parts) > 1:
                location = parts[1].strip().split(' ')[0]
                return location
                
        return None
    
    def _extract_category(self, text):
        """
        Extract news category from text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Extracted category or None
        """
        categories = ['business', 'entertainment', 'general', 'health', 
                      'science', 'sports', 'technology']
                      
        for category in categories:
            if category in text.lower():
                return category
                
        return None
    
    def _get_fallback_response(self, prompt):
        """
        Get a fallback response when AI service is unavailable.
        
        Args:
            prompt (str): The user's input prompt
            
        Returns:
            str: Fallback response
        """
        fallback_responses = [
            "I'm sorry, I can't access my AI services right now.",
            "I'm having trouble connecting to my knowledge base at the moment.",
            "I apologize, but I'm unable to process that request right now.",
            "My advanced AI capabilities are currently unavailable. Can I help with something basic instead?"
        ]
        
        import random
        return random.choice(fallback_responses)
        
    def process_query(self, query, callback=None):
        """
        Process a general query and return an answer.
        
        Args:
            query (str): The user's query
            callback (function): Optional callback function to handle the response
            
        Returns:
            dict: Response information dictionary
        """
        try:
            # Process the query and generate a response
            if self.api_key:
                # For now, use a simple fallback since OpenAI integration is commented out
                response = self.generate_response(query)
            else:
                response = self._get_fallback_response(query)
                
            # Create response dictionary
            response_info = {
                "success": True,
                "query": query,
                "response": response
            }
            
            # Call the callback if provided
            if callback:
                callback(response_info)
                
            return response_info
            
        except Exception as e:
            print(f"Error processing query: {e}")
            
            # Create error response
            error_response = {
                "success": False,
                "query": query,
                "error": str(e),
                "response": "I encountered an error processing your request."
            }
            
            # Call the callback if provided
            if callback:
                callback(error_response)
                
            return error_response
