import os


def upload(file_path, description=None):
    if os.getenv('CLOUD_DRIVE', 'GOFILE') == 'GOOGLE_DRIVE':
        from .google_drive import upload
        return upload(file_path, description)
    else:
        from .gofile import upload
        return upload(file_path, description)
    # end if
# end def
