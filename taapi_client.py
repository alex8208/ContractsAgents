import requests

class TaapiClient:
    API_URL = "https://api.taapi.io/"

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key is required to use the TaapiClient")
        self.api_key = api_key

    def get_indicator(self, indicator, exchange, symbol, interval, **kwargs):
        endpoint = f"{self.API_URL}{indicator}"
        params = {
            'api_key': self.api_key,
            'exchange': exchange,
            'symbol': symbol,
            'interval': interval
        }
        params.update(kwargs)

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            print(f"An error occurred: {e}")
            return None
        except ValueError:
            # Handle JSON decoding errors
            print("Failed to decode JSON from response")
            return None