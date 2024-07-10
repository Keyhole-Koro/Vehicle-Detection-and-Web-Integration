import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

def upload_to_gdrive(file_path, folder_id, user_email):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
    
    CREDENTIAL_JSON_PATH = os.getenv("CREDENTIAL_JSON_PATH")

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIAL_JSON_PATH, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(user_email)

    service = build('drive', 'v3', credentials=delegated_credentials)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"File ID: {file.get('id')}")
    except Exception as e:
        print(f"Failed to upload file to Google Drive: {e}")

def check_folder_existence(folder_name, user_email):
    SCOPES = ['https://www.googleapis.com/auth/drive']

    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    CREDENTIAL_JSON_PATH = os.getenv("CREDENTIAL_JSON_PATH")

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIAL_JSON_PATH,
        scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(user_email)

    service = build('drive', 'v3', credentials=delegated_credentials)

    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = service.files().list(q=query).execute()
        folders = response.get('files', [])

        if folders:
            return folders[0]['id']
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def create_folder_if_not_exists(folder_name, user_email):
    folder_id = check_folder_existence(folder_name, user_email)

    if folder_id:
        print(f"Folder '{folder_name}' already exists. Folder ID: {folder_id}")
        return folder_id
    else:
        return create_folder(folder_name, user_email)

def create_folder(folder_name, user_email):
    SCOPES = ['https://www.googleapis.com/auth/drive']

    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)

    CREDENTIAL_JSON_PATH = os.getenv("CREDENTIAL_JSON_PATH")

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIAL_JSON_PATH,
        scopes=SCOPES
    )
    delegated_credentials = credentials.with_subject(user_email)

    service = build('drive', 'v3', credentials=delegated_credentials)

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    try:
        folder = service.files().create(body=file_metadata, fields='id').execute()
        print(f"Folder '{folder_name}' created successfully. Folder ID: {folder.get('id')}")
        return folder.get('id')
    except Exception as e:
        print(f"Failed to create folder: {e}")
        return None

if __name__ == "__main__":
    user_email = "korokororin47@gmail.com"
    folder_name = "car-detection-test-folder"
    folder_id = create_folder_if_not_exists(folder_name, user_email)

    if folder_id:
        print(f"Folder ID: {folder_id}")
        file_path = "../result/logfile.csv"
        upload_to_gdrive(file_path, folder_id, user_email)
    else:
        print("Failed to create or retrieve folder.")
