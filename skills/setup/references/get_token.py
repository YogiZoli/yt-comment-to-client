#!/usr/bin/env python3
"""
One-time OAuth authorization for YT Comment-to-Client.
Run once during setup — opens browser for Google sign-in.
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import os, json

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/spreadsheets',
]
script_dir = os.path.dirname(os.path.abspath(__file__))
creds_file = os.path.join(script_dir, 'client_secrets.json')
token_file = os.path.join(script_dir, 'token.json')

print("Opening browser for Google authorization...")
print("Sign in with the Google account that OWNS your YouTube channel.")
flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
creds = flow.run_local_server(port=0)

with open(token_file, 'w') as f:
    f.write(creds.to_json())

print("\nSUCCESS — Authorization complete!")
print("Valid:", creds.valid)
print("Has refresh token:", creds.refresh_token is not None)
