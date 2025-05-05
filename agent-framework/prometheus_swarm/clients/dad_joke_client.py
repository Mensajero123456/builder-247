import requests

class DadJokeClient:
    """
    A client for interacting with the icanhazdadjoke.com API to fetch dad jokes.
    
    Attributes:
        base_url (str): The base URL for the Dad Joke API
        headers (dict): HTTP headers for the API request
    """
    
    def __init__(self, api_url='https://icanhazdadjoke.com/'):
        """
        Initialize the Dad Joke Client.
        
        Args:
            api_url (str, optional): Base URL for the Dad Joke API. 
                                     Defaults to 'https://icanhazdadjoke.com/'.
        """
        self.base_url = api_url
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Client (https://github.com/your-org/prometheus-swarm)'
        }
    
    def get_random_joke(self):
        """
        Fetch a random dad joke from the API.
        
        Returns:
            dict: A dictionary containing the joke details with keys 'id', 'joke', and 'status'
        
        Raises:
            requests.RequestException: If there's an error fetching the joke
            ValueError: If the API response is invalid
        """
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            joke_data = response.json()
            
            # Validate the response
            if 'joke' not in joke_data:
                raise ValueError("Invalid joke response")
            
            return joke_data
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")
    
    def search_jokes(self, term, limit=5, page=1):
        """
        Search for dad jokes containing a specific term.
        
        Args:
            term (str): Search term for jokes
            limit (int, optional): Number of jokes to return. Defaults to 5.
            page (int, optional): Page number for paginated results. Defaults to 1.
        
        Returns:
            dict: A dictionary containing search results
        
        Raises:
            requests.RequestException: If there's an error fetching jokes
            ValueError: If search parameters are invalid
        """
        if not term or not isinstance(term, str):
            raise ValueError("Search term must be a non-empty string")
        
        params = {
            'term': term,
            'limit': limit,
            'page': page
        }
        
        try:
            response = requests.get(f"{self.base_url}search", 
                                    params=params, 
                                    headers=self.headers)
            response.raise_for_status()
            
            search_results = response.json()
            
            # Validate the response
            if 'results' not in search_results:
                raise ValueError("Invalid search response")
            
            return search_results
        
        except requests.RequestException as e:
            raise requests.RequestException(f"Error searching dad jokes: {e}")