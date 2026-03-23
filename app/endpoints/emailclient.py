import os
from fastapi import APIRouter, HTTPException, Depends
from core.dependencies import getEmailService
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from fastapi import Request
router = APIRouter(
    prefix="",
    tags=["Get oauth code"]
)
logger = logging.getLogger("email_organizer")
@router.get("/callback")
def callback(request: Request):
    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    
    redirect_uri = os.getenv("REDIRECT_URI") 
    
    client_config = {
        "web": { #
            "client_id": os.getenv("GMAIL_CLIENT_ID"),
            "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = redirect_uri
    
    authorization_response = str(request.url)
    
    if "http://" in authorization_response:
        authorization_response = authorization_response.replace("http://", "https://")

    flow.fetch_token(authorization_response=authorization_response)
    
    creds_json = flow.credentials.to_json()
    print(f"\n{'='*20}\nGMAIL JSON:\n{creds_json}\n{'='*20}\n")
    
    return {"status": "Log in successful. Check Render logs for GMAIL_JSON"}
