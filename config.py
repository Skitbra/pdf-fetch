"""
Configuration settings for PDF fetcher
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API Configuration
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './downloads')
EMAIL_QUERY = os.getenv('EMAIL_QUERY', 'has:attachment')

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Create download directory if it doesn't exist
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)

