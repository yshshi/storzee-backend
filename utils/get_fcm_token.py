import json
import google.auth
from google.oauth2 import service_account
import google.auth.transport.requests

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        r"/home/ubuntu/storezee-b5f0e-firebase-adminsdk-fbsvc-0c43f4140f.json",
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

print(get_access_token())