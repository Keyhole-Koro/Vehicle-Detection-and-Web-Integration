import getpass
import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

from ring_doorbell import Auth, AuthenticationError, Requires2FAError, Ring

from email_utils import send_error_email

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

RING_EMAIL = os.getenv("RING_EMAIL")
RING_PASSWORD = os.getenv("RING_PASSWORD")

user_agent = "garage_cam-1.0"
cache_file = Path(user_agent + ".token.cache")

def token_updated(token):
    cache_file.write_text(json.dumps(token))

def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code

def do_auth():
    auth = Auth(user_agent, None, token_updated)
    try:
        auth.fetch_token(RING_EMAIL, RING_PASSWORD)
    except Requires2FAError:
        auth.fetch_token(RING_EMAIL, RING_PASSWORD, otp_callback())
        send_email("Ring Token has been updated", "If you receive 2FA code, enter the code via ssh.")
    return auth

def getSnapshot():
    if cache_file.is_file():  # auth token is cached
        auth = Auth(user_agent, json.loads(cache_file.read_text()), token_updated)
        ring = Ring(auth)
        try:
            ring.create_session()  # auth token still valid
        except AuthenticationError:  # auth token has expired
            auth = do_auth()
    else:
        auth = do_auth()  # Get new auth token
        ring = Ring(auth)

    ring.update_data()

    devices = ring.devices()
    doorbell = devices['stickup_cams'][0]

    snapshot = doorbell.get_snapshot()
    
    return [snapshot]