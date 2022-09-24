"""[DEPRECATED] Uploader for google drive"""
import logging
import os

logger = logging.getLogger(__name__)


try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
except Exception:
    logger.error("`pydrive` was not setup properly")


def upload(file_path, description=None) -> str:
    gauth = GoogleAuth()
    # gauth.LocalWebserverAuth()

    # Try to load saved client credentials
    credential_file = os.getenv("GOOGLE_DRIVE_CREDENTIAL_FILE")
    gauth.LoadCredentialsFile(credential_file)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile(credential_file)

    drive = GoogleDrive(gauth)
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    filename_w_ext = os.path.basename(file_path)
    filename, file_extension = os.path.splitext(filename_w_ext)

    # Upload file to folder
    f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
    f["title"] = filename_w_ext

    # Make sure to add the path to the file to upload below.
    f.SetContentFile(file_path)
    f.Upload()

    logger.info("Uploaded file id: {}", f["id"])
    return "https://drive.google.com/open?id=" + f["id"]
