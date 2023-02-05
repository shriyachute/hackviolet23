from __future__ import print_function

import os.path

import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def draft_text(email_address):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        drafts = service.users().drafts().list(userId=email_address).execute()
        dr = drafts['drafts'][0]
        d = service.users().drafts().get(userId=email_address, id=dr['id']).execute()
        body = d['message']['payload']['parts'][0]['body']
        if(body['size'] > 0):
            message = body['data']
            message = base64.urlsafe_b64decode(message.encode())
            return message.decode('utf-8').strip()

    except HttpError as error:
        print(f'An error occurred: {error}')
