import pytest
import logging
import requests
from unittest.mock import Mock, patch
from src.clients.dad_joke_client import DadJokeClient

def test_dad_joke_client_initialization():
    """Test initialization of the Dad Joke Client."""
    # Create a mock logger for verification
    mock_logger = logging.getLogger('test_logger')
    mock_logger.setLevel(logging.INFO)

    client = DadJokeClient(logger=mock_logger)
    
    assert client.base_url == 'https://icanhazdadjoke.com/'
    assert 'Accept' in client.headers
    assert 'User-Agent' in client.headers
    assert client.logger == mock_logger

@patch('requests.get')
def test_get_random_joke_success(mock_get):
    """Test successful retrieval of a random joke."""
    # Mock a successful response
    mock_response = Mock()
    mock_response.json.return_value = {
        'id': '123abc', 
        'joke': 'A hilarious dad joke', 
        'status': 200
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Use a mock logger to verify logging
    mock_logger = logging.getLogger('test_logger')
    mock_logger.setLevel(logging.INFO)

    client = DadJokeClient(logger=mock_logger)
    joke = client.get_random_joke()

    assert 'joke' in joke
    assert joke['joke'] == 'A hilarious dad joke'
    mock_get.assert_called_once_with(client.base_url, headers=client.headers)

def test_get_random_joke_invalid_response():
    """Test handling of an invalid joke response."""
    client = DadJokeClient()
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {}  # No joke in response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid joke response"):
            client.get_random_joke()

def test_get_random_joke_request_exception():
    """Test handling of request exceptions."""
    client = DadJokeClient()
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(requests.RequestException, match="Network error"):
            client.get_random_joke()

@patch('requests.get')
def test_search_jokes_success(mock_get):
    """Test successful joke search."""
    # Mock a successful search response
    mock_response = Mock()
    mock_response.json.return_value = {
        'current_page': 1,
        'limit': 5,
        'results': [
            {'id': '1', 'joke': 'Joke 1'},
            {'id': '2', 'joke': 'Joke 2'}
        ],
        'total_jokes': 2,
        'total_pages': 1
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Use a mock logger to verify logging
    mock_logger = logging.getLogger('test_logger')
    mock_logger.setLevel(logging.INFO)

    client = DadJokeClient(logger=mock_logger)
    search_results = client.search_jokes('computer', limit=5, page=1)

    assert 'results' in search_results
    assert len(search_results['results']) == 2
    mock_get.assert_called_once_with(
        f"{client.base_url}search", 
        params={'term': 'computer', 'limit': 5, 'page': 1}, 
        headers=client.headers
    )

def test_search_jokes_invalid_term():
    """Test searching with invalid search terms."""
    client = DadJokeClient()

    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        client.search_jokes('')

    with pytest.raises(ValueError, match="Search term must be a non-empty string"):
        client.search_jokes(None)

def test_search_jokes_invalid_response():
    """Test handling of an invalid search response."""
    client = DadJokeClient()
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {}  # No results in response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid search response"):
            client.search_jokes('test')

def test_search_jokes_request_exception():
    """Test handling of request exceptions during search."""
    client = DadJokeClient()
    
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(requests.RequestException, match="Network error"):
            client.search_jokes('test')