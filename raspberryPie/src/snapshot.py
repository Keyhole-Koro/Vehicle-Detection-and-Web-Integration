import getpass
import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

from ring_doorbell import Auth, AuthenticationError, Requires2FAError, Ring

from email_utils import send_email

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

RING_EMAIL = os.getenv("RING_EMAIL")
RING_PASSWORD = os.getenv("RING_PASSWORD")

target_device_ids = os.getenv("TARGET_DEVICE_IDS").split(',')


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
        send_email("Ring Token has been updated", "If you receive 2FA code, enter the code via ssh.")
        auth.fetch_token(RING_EMAIL, RING_PASSWORD, otp_callback())
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

    try:
        ring.update_data()
        devices = ring.devices()
        doorbells = []
        for device_type in ['stickup_cams', 'chimes', 'doorbots', 'authorized_doorbots']:
            for cam in devices[device_type]:
                if str(cam.id) in target_device_ids:
                    doorbells.append(cam)

        if not doorbells:
            raise Exception(f"No devices found with IDs {target_device_ids}")

        snapshots = []
        for doorbell in doorbells:
            snapshot = doorbell.get_snapshot()
            if snapshot:
                snapshots.append(snapshot)
            else:
                raise Exception(f"Failed to fetch a snapshot for device ID {doorbell.id}")
        return snapshots
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"An error occurred:\n{tb}"
        send_email("Error Notification: Snapshot Error", error_message)
        return []

def getAllCameraDeviceIDs():
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

    try:
        ring.update_data()
        devices = ring.devices()
        all_devices = []
        for device_type in ['stickup_cams', 'chimes', 'doorbots', 'authorized_doorbots']:
            for cam in devices[device_type]:
                all_devices.append({"id": cam.id, "name": cam.name})

        if not all_devices:
            raise Exception("No camera devices found.")

        print(all_devices)
        return all_devices
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"An error occurred:\n{tb}"
        send_email("Error Notification: Get All Camera Device IDs Error", error_message)
        return []