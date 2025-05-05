import logging
import requests
from typing import Dict, Optional, Any

class DadJokeClient:
    """
    A client for interacting with the icanhazdadjoke.com API to fetch dad jokes.
    
    Implements comprehensive logging and robust error handling for API interactions.
    """
    
    def __init__(
        self, 
        api_url: str = 'https://icanhazdadjoke.com/', 
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_url (str, optional): Base URL for the Dad Joke API. 
                                     Defaults to 'https://icanhazdadjoke.com/'.
            logger (logging.Logger, optional): Custom logger. Creates default if not provided.
        """
        self.base_url = api_url
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Client'
        }
        
        # Configure logging
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add a console handler if no handlers exist
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def get_random_joke(self) -> Dict[str, Any]:
        """
        Fetch a random dad joke from the API.
        
        Returns:
            dict: A dictionary containing the joke details
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If the API response is invalid
        """
        try:
            self.logger.info(f"Fetching random joke from {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            joke_data = response.json()
            
            if 'joke' not in joke_data:
                self.logger.error("Invalid joke response received")
                raise ValueError("Invalid joke response")
            
            self.logger.info(f"Successfully retrieved joke: {joke_data['joke'][:30]}...")
            return joke_data
        
        except requests.RequestException as e:
            self.logger.error(f"Network error while fetching joke: {e}")
            raise
        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise
    
    def search_jokes(
        self, 
        term: str, 
        limit: int = 5, 
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term for jokes
            limit (int, optional): Number of jokes to return. Defaults to 5.
            page (int, optional): Page number for paginated results. Defaults to 1.
        
        Returns:
            dict: A dictionary containing search results
        
        Raises:
            ValueError: If search parameters are invalid
            requests.RequestException: If there's an error fetching jokes
        """
        if not term or not isinstance(term, str):
            self.logger.error(f"Invalid search term: {term}")
            raise ValueError("Search term must be a non-empty string")
        
        params = {
            'term': term,
            'limit': limit,
            'page': page
        }
        
        try:
            self.logger.info(f"Searching jokes with term: {term}")
            response = requests.get(
                f"{self.base_url}search", 
                params=params, 
                headers=self.headers
            )
            response.raise_for_status()
            
            search_results = response.json()
            
            if 'results' not in search_results:
                self.logger.error("Invalid search response received")
                raise ValueError("Invalid search response")
            
            self.logger.info(
                f"Found {len(search_results.get('results', []))} jokes"
            )
            return search_results
        
        except requests.RequestException as e:
            self.logger.error(f"Network error while searching jokes: {e}")
            raise
        except ValueError as ve:
            self.logger.error(f"Validation error: {ve}")
            raise