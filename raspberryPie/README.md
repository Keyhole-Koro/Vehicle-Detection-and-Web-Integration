## Commands to daemonize the python program
```
sudo systemctl enable traffic_update

sudo systemctl start traffic_update
```

## download chrome
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## setup email
1. Go to your Google Account.
2. Navigate to the Security section.
3. Under "Signing in to Google," select "App Passwords."
4. You might need to sign in again.
5. At the bottom, choose "Select app" and pick the app you're using.
6. Select the device and choose "Generate."
7. You'll see a 16-character password.

## setup google drive
```
pip install google-auth google-auth-oauthlib google-auth-httplib2
```
1. Go to the Google Cloud Console.
2. Create a new project or select an existing one.
3. Enable the Google Drive API for your project.
4. Create OAuth 2.0 credentials (OAuth client ID).
5. Download the credentials.json file and place it in your project directory.
6. Add scope

7. Open Cloud Shell Terminal
8. Aquire credentials.json
9. Run
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

python3 quickstart.py
```

