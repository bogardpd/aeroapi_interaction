"""Class for interacting with AeroAPI."""
from dotenv import load_dotenv
import os

class AeroAPIWrapper:
    """Class for interacting with AeroAPI version 4."""
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_KEY_AEROAPI_4')
        self.server = "https://aeroapi.flightaware.com/aeroapi"

        # Set a wait time in seconds to avoid rate limiting on the
        # Personal tier. If your account has a higher rate limit,
        # you can set this to 0.
        self.wait_time = 8