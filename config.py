# config.py
import os
from dotenv import load_dotenv
from utils.string_handling import encode_base64

load_dotenv(override=True)

class JiraConfig:
    URL = os.getenv("URL")
    EMAIL = os.getenv("EMAIL")
    API_KEY = os.getenv("API_KEY")
    TOKEN = encode_base64(f"{EMAIL}:{API_KEY}")
    HEADERS = {
        "Authorization": f"Basic {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
