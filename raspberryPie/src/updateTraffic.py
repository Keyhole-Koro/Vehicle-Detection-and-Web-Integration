import os
import json
import requests
from datetime import datetime
import time
import pytz
import base64

from dotenv import load_dotenv

from snapshot import fetchSnapshot
from car_detection import image_detect

def updateTraffic(result, imgs):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    URL = os.getenv("WEB_SERVER_ENDPOINT")
    API_KEY = os.getenv("API_KEY")
    STAGE = os.getenv("STAGE")

    japan_tz = pytz.timezone('Asia/Tokyo')
    timestamp = datetime.now(japan_tz).strftime("%Y/%m/%d %H:%M:%S")

    encoded_imgs = [base64.b64encode(image).decode('utf-8') for image in imgs]

    data = {
        "result": result,
        "timestamp": timestamp,
        "images": encoded_imgs
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    json_data = json.dumps(data)

    try:
        if (STAGE == 'PROD'):
            response = requests.post(URL, headers=headers, data=json_data)
        else:
            response = requests.post(URL, headers=headers, data=json_data, verify=False)

        response.raise_for_status()
        print(timestamp + ":" + "POST request successful.\n" + str(response.content))
    except requests.exceptions.RequestException as e:
        print(f"{timestamp}: Error making POST request: {e}")

if __name__ == '__main__':
    start_time = time.time()

    while True:
        result = 0
        image_bufs = fetchSnapshot()
        for image_buf in image_bufs:
            result += image_detect(image_buf)

        updateTraffic(result, image_bufs)

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > 60:
                start_time = time.time()
                break
            time.sleep(1)
