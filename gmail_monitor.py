"""To monitor your Gmail for an email attachment that you download on a daily basis, you can use the Google API for Python to access your Gmail account. This script will periodically check your mailbox for new emails with attachments, and if it finds a matching email, it downloads the attachments to a specified folder.

To use the script, follow these steps:

Set up a Google Cloud project and enable the Gmail API: 

https://developers.google.com/gmail/api/quickstart/python

Download the credentials.json file and place it in the same folder as the script.
Install the required packages by running: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client


"""


import os
import time
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText

# Set up the Gmail API client
def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.modify'])
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

# Check for new emails with attachments and download them
def download_daily_attachments():
    service = get_gmail_service()
    query = "has:attachment is:unread"  # Modify the query as needed, e.g., add "from:<sender@example.com>"
    
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print('No new messages with attachments found.')
        else:
            print(f'Found {len(messages)} new messages with attachments:')
            
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                print(f"  - {msg['snippet']}")
                
                for part in msg['payload']['parts']:
                    if part.get('filename') and part.get('body') and part.get('body').get('attachmentId'):
                        attachment = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=part['body']['attachmentId']).execute()
                        data = attachment['data']
                        file_data = urlsafe_b64decode(data)
                        path = os.path.join('downloaded_attachments', part['filename'])

                        with open(path, 'wb') as f:
                            f.write(file_data)
                            print(f'Saved attachment to {path}')

                # Mark the email as read
                service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    while True:
        print('Checking for new messages with attachments...')
        download_daily_attachments()
        time.sleep(86400)  # Check every 24 hours (
