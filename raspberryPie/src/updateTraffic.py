import os
import json
import requests
from datetime import datetime, time as dt_time
import time
import pytz
import base64
import csv

from dotenv import load_dotenv

from snapshot import fetchSnapshot
from car_detection import image_detect
from email_utils import send_error_email

def log_to_csv(timestamp, result, status, message):
    log_file_path = os.getenv("LOG_FILE_PATH")
    
    if not log_file_path:
        raise ValueError("LOG_FILE_PATH environment variable is not set")

    log_exists = os.path.isfile(log_file_path)

    with open(log_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not log_exists:
            writer.writerow(["timestamp", "result", "status", "message"])
        writer.writerow([timestamp, result, status, message])

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
        if STAGE == 'PROD':
            response = requests.post(URL, headers=headers, data=json_data)
        else:
            response = requests.post(URL, headers=headers, data=json_data, verify=False)

        response.raise_for_status()
        log_to_csv(timestamp, result, "success", str(response.content))
        print(f"{timestamp}: POST request successful.\n{response.content}")
    except requests.exceptions.RequestException as e:
        error_message = f"{timestamp}: Error making POST request: {e}"
        log_to_csv(timestamp, result, "error", error_message)
        print(error_message)
        send_error_email(error_message)

def is_within_time_range(start_time_str, end_time_str):
    japan_tz = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(japan_tz).time()

    start_time = dt_time.fromisoformat(start_time_str)
    end_time = dt_time.fromisoformat(end_time_str)

    if start_time <= current_time <= end_time:
        return True
    return False

def wait_until_start_time(start_time_str):
    japan_tz = pytz.timezone('Asia/Tokyo')
    start_time = dt_time.fromisoformat(start_time_str)
    
    while True:
        current_time = datetime.now(japan_tz).time()
        if current_time >= start_time:
            break
        time.sleep(60)

if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    START_TIME = os.getenv("START_TIME")
    END_TIME = os.getenv("END_TIME")

    start_time = time.time()
    while True:
        if is_within_time_range(START_TIME, END_TIME):
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

        else:
            wait_until_start_time(START_TIME)
