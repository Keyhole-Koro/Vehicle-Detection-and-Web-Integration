import os
import json
import requests
from datetime import datetime
import time

from dotenv import load_dotenv

from snapshot import fetchSnapshot
from car_detection import image_detect


def updateTraffic(result):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    URL = os.getenv("WEB_SERVER_ENDPOINT")
    API_KEY = os.getenv("API_KEY")

    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    data = {
        "result": result,
        "timestamp": timestamp
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    json_data = json.dumps(data)

    try:
        response = requests.post(URL, headers=headers, data=json_data, verify=False)  # Remove verify=False in production
        response.raise_for_status()
        print("POST request successful.")
    except requests.exceptions.RequestException as e:
        print(f"Error making POST request: {e}")

if __name__ == '__main__':
    while True:
        image_buf = fetchSnapshot()

        result = image_detect(image_buf)

        updateTraffic(result)

        time.sleep(60)