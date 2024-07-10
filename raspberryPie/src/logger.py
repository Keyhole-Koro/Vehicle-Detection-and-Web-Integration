import os
from datetime import datetime, time as dt_time
import csv

def log_to_csv(timestamp, result, status, message):
    log_dir = os.getenv("LOG_DIR")
    if not log_dir:
        raise ValueError("LOG_DIR environment variable is not set")

    today_date = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_dir, f"log_{today_date}.csv")

    log_exists = os.path.isfile(log_file_path)

    with open(log_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not log_exists:
            writer.writerow(["timestamp", "result", "status", "message"])
        writer.writerow([timestamp, result, status, message])

