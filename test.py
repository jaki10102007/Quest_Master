import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def checkcred():
    credential = None
    if os.path.exists("token.json"):
        credential = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credential or not credential.valid:
        if credential and credential.expired and credential.refresh_token:
            credential.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credential = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(credential.to_json())

if os.path.exists("token.json"):
    os.remove("token.json")

checkcred()