"""
AI Desktop Assistant - News Module
Fetches and processes news from various sources.
"""

import requests
import json
import os
from datetime import datetime

class NewsModule:
    """Handles fetching and processing of news content."""
    
    def __init__(self, config=None, api_key=None):
        """
        Initialize the news module.
        
        Args:
            config (AppConfig, optional): Application configuration object
            api_key (str, optional): NewsAPI key. If not provided, will try to get from environment.
        """
        self.config = config
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
        
        if not self.api_key:
            print("Warning: No NewsAPI key provided. News functionality will be limited.")
    
    def get_headlines(self, country="us", category=None, count=5):
        """
        Get top headlines.
        
        Args:
            country (str): Country code for headlines (default: 'us')
            category (str, optional): News category (business, entertainment, general, health, etc.)
            count (int): Number of headlines to fetch
            
        Returns:
            list: List of news article dictionaries or empty list if failed
        """
        if not self.api_key:
            print("Error: No NewsAPI key available.")
            return self._get_dummy_headlines()
            
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'country': country,
                'pageSize': count,
                'apiKey': self.api_key
            }
            
            if category:
                params['category'] = category
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._get_dummy_headlines()
    
    def search_news(self, query, count=5, sort_by="relevancy"):
        """
        Search for news articles by keyword.
        
        Args:
            query (str): Search query
            count (int): Number of results to return
            sort_by (str): Sort order (relevancy, popularity, publishedAt)
            
        Returns:
            list: List of news article dictionaries or empty list if failed
        """
        if not self.api_key:
            print("Error: No NewsAPI key available.")
            return self._get_dummy_headlines()
            
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'pageSize': count,
                'sortBy': sort_by,
                'apiKey': self.api_key
            }
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            print(f"Error searching news: {e}")
            return self._get_dummy_headlines()
    
    def _get_dummy_headlines(self):
        """
        Get dummy headlines when API is unavailable.
        
        Returns:
            list: List of dummy news article dictionaries
        """
        return [
            {
                'title': 'Sample News Headline 1',
                'description': 'This is a placeholder news article description.',
                'url': 'https://example.com/news/1',
                'publishedAt': datetime.now().isoformat(),
                'source': {'name': 'Sample News Source'}
            },
            {
                'title': 'Sample News Headline 2',
                'description': 'Another placeholder news article for demonstration.',
                'url': 'https://example.com/news/2',
                'publishedAt': datetime.now().isoformat(),
                'source': {'name': 'Sample News Source'}
            }
        ]
    
    def format_articles_for_speech(self, articles, include_description=False):
        """
        Format articles for speech output.
        
        Args:
            articles (list): List of news article dictionaries
            include_description (bool): Whether to include article descriptions
            
        Returns:
            str: Formatted text for speech output
        """
        if not articles:
            return "I couldn't find any news articles at the moment."
            
        result = "Here are the top headlines: "
        
        for i, article in enumerate(articles, 1):
            result += f"{i}. {article.get('title', 'Untitled')} from {article.get('source', {}).get('name', 'Unknown source')}. "
            
            if include_description and article.get('description'):
                result += f"{article.get('description')} "
                
        return result
        
    def get_news(self, category="general", callback=None):
        """
        Get top news headlines and process them using a callback.
        
        Args:
            category (str): News category (business, entertainment, general, etc.)
            callback (function): Optional callback function to handle the response
            
        Returns:
            dict: News information dictionary
        """
        try:
            # Get country setting from config or use default
            country = "us"  # Default country
            if self.config:
                country = self.config.get("news", "default_country", "us")
                
            # Get number of articles from config or use default
            count = 5  # Default count
            if self.config:
                count = self.config.get("news", "article_count", 5)
                
            # Get the headlines
            articles = self.get_headlines(country=country, category=category, count=count)
            
            # Create response dictionary
            news_info = {
                "success": True,
                "category": category,
                "articles": articles
            }
            
            # Call the callback if provided
            if callback:
                callback(news_info)
                
            return news_info
            
        except Exception as e:
            print(f"Error getting news: {e}")
            
            # Create error response
            error_response = {
                "success": False,
                "category": category,
                "error": str(e),
                "articles": self._get_dummy_headlines()  # Provide dummy headlines as fallback
            }
            
            # Call the callback if provided
            if callback:
                callback(error_response)
                
            return error_response
