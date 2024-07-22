## Commands to daemonize the python program
```
sudo systemctl enable traffic_update

sudo systemctl start traffic_update
```
## Set up libraries
```
pip install -r requirements.txt --break-system-packages

```
## update service
```
sudo systemctl daemon-reload
sudo systemctl restart traffic_update.service
sudo systemctl status traffic_update.service
```
## For debugging
```
journalctl -u traffic_update.service -f
```

## setup email
1. Go to your Google Account.
2. Navigate to the Security section.
3. Under "Signing in to Google," select "App Passwords."
4. You might need to sign in again.
5. At the bottom, choose "Select app" and pick the app you're using.
6. Select the device and choose "Generate."
7. You'll see a 16-character password.

## replace get_snapshot() in doorbell.py with the below
```
def get_snapshot(self, retries=3, delay=1):
    """Take a snapshot and download it"""
    try:
        url = SNAPSHOT_TIMESTAMP_ENDPOINT
        payload = {"doorbot_ids": [self._attrs.get("id")]}
        self._ring.query(url, method="POST", json=payload)
        request_time = time.time()
        for _ in range(retries):
            time.sleep(delay)
            response = self._ring.query(url, method="POST", json=payload).json()
            return self._ring.query(
                SNAPSHOT_ENDPOINT.format(self._attrs.get("id"))
                ).content
        return False
    except:
        return False
```