import getpass
import json
from pathlib import Path

from ring_doorbell import Auth, AuthenticationError, Requires2FAError, Ring

user_agent = "YourProjectName-1.0"  # Change this
cache_file = Path(user_agent + ".token.cache")


def token_updated(token):
    cache_file.write_text(json.dumps(token))


def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code


def do_auth():
    username = "korokororin47@gmail.com"
    password = "EFDN&BfF7j@8w3u"
    auth = Auth(user_agent, None, token_updated)
    try:
        auth.fetch_token(username, password)
    except Requires2FAError:
        auth.fetch_token(username, password, otp_callback())
    return auth


def main():
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
    print(devices)

    camera = devices['stickup_cams'][0]

    image = camera.livestream().image()

    file_path = os.path.join(os.path.dirname(__file__), 'result', 'snapshot.jpg')
        
    with open(file_path, 'wb') as f:
        f.write(image)

    print(f'Snapshot saved to {file_path}')



if __name__ == "__main__":
    main()