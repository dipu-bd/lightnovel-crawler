from requests import Session


# API Docs: https://anonfiles.com/docs/api
def upload(file_path, description):
    with Session() as sess:
        with open(file_path, "rb") as fp:
            response = sess.post(
                "https://api.anonfiles.com/upload",
                files={"file": fp},
                stream=True,
            )
            response.raise_for_status()
            return response.json()["data"]["file"]["url"]["full"]
