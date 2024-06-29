import requests
import numpy as np

def fetchSnapshot(url = ''):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return np.frombuffer(response.content, np.uint8)
        else:
            print("failed to fetch")
    except Exception as e:
        print(f"an error occured: {e}")