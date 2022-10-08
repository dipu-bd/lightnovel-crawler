import os

cloud_drive = os.getenv("CLOUD_DRIVE", "ANONFILES")


def upload(file_path, description=None):
    if cloud_drive == "GOOGLE_DRIVE":
        from .google_drive import upload

        return upload(file_path, description)
    elif cloud_drive == "GOFILE":
        from .gofile import upload

        return upload(file_path, description)
    else:
        from .anonfiles import upload

        return upload(file_path, description)
