"""
Gmail API Authentication with 2FA support
"""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

from config import SCOPES

logger = logging.getLogger(__name__)

class GmailAuthenticator:
    def __init__(self, credentials_file=None, token_file='token.pickle'):
        """
        Initialize Gmail authenticator
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials JSON file
            token_file (str): Path to store/load the access token
        """
        self.credentials_file = credentials_file or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.token_file = token_file
        self.service = None
        
    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth2 with 2FA support
        
        Returns:
            googleapiclient.discovery.Resource: Gmail service object
        """
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                if not self.credentials_file:
                    raise ValueError("No credentials file specified. Please set GOOGLE_APPLICATION_CREDENTIALS environment variable or pass credentials_file parameter.")
                
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
                
                logger.info("Starting OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("Credentials saved successfully")
        
        # Build the Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail service initialized successfully")
        return self.service
    
    def get_service(self):
        """
        Get the Gmail service object
        
        Returns:
            googleapiclient.discovery.Resource: Gmail service object
        """
        if not self.service:
            return self.authenticate()
        return self.service

