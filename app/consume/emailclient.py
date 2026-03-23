import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import sys
import json

class EmailAPI():
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
        self.credentials = None
        if getattr(sys, 'frozen', False):
            # Ruta base: la carpeta donde está el exe
            self.base_path = os.path.dirname(sys.executable)
        else:
            # Ruta base: la carpeta del script
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tokenPath = os.path.join(self.base_path, "token.json")
        self.credentialPath = os.path.join(self.base_path, "credentials.json")
        self.logger = logging.getLogger("email_organizer")
    def getCredentials(self):
        tokenStr = os.getenv("GMAIL_JSON")
        if tokenStr:
            token_info = json.loads(tokenStr)
            self.credentials = Credentials.from_authorized_user_info(token_info, self.SCOPES)
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                client_config = {
                "installed": {
                    "client_id": os.getenv("GMAIL_CLIENT_ID"),
                    "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                    "project_id": os.getenv("GMAIL_PROJECT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config=client_config,
                                                                 scopes=self.SCOPES)
                self.credentials = flow.run_local_server(port=0)
                print(self.credentials.to_json())
        
    def getEmailClient(self):
        if not self.credentials:
            self.getCredentials()
        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=self.credentials)
            return service

        except HttpError as error:
            #Handle errors from gmail API.
            self.logger.error(f"An error occurred: {error}")