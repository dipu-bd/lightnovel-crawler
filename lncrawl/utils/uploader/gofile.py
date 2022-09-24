from requests import Session


# API Docs: https://gofile.io/api
def upload(file_path, description=""):
    with Session() as sess:
        response = sess.get("https://api.gofile.io/getServer")
        response.raise_for_status()
        server_name = response.json()["data"]["server"]

        with open(file_path, "rb") as fp:
            response = sess.post(
                f"https://{server_name}.gofile.io/uploadFile",
                files={"file": fp},
                stream=True,
            )
            response.raise_for_status()
            return response.json()["data"]["downloadPage"]
