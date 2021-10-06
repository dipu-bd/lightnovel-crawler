import os

from requests import Session


# API Docs: https://gofile.io/api
def upload(file_path, description):
    with Session() as sess:
        response = sess.get('https://api.gofile.io/getServer')
        response.raise_for_status()
        server_name = response.json()['data']['server']

    with open(file_path, "rb") as fp:
        upload_url = f'https://{server_name}.gofile.io/uploadFile'
        response = sess.post(
            upload_url,
            data={
                'description': description,
                #'token': os.getenv('GOFILE_TOKEN'),
                #'folderId': os.getenv('GOFILE_FOLDER_ID'),
            },
            files={
                'upload_file': fp,
            },
            stream=True,
        )
        response.raise_for_status()
        return response.json()['data']['directLink']
