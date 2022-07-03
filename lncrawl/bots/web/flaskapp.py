from flask import Flask, send_file, send_from_directory  # type: ignore
from .lib import LIGHTNOVEL_FOLDER, WEBSITE_URL
import pathlib
from flask_minify import Minify  # type: ignore
language_dict = {
    "en": "English",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "tr": "Turkish",
    "ar": "Arabic",
    "el": "Greek",
    "he": "Hebrew",
    "id": "Indonesian",
    "pl": "Polish",
    "th": "Thai",
    "vi": "Vietnamese",
}

app = Flask(__name__)
Minify(app=app, html=True, js=True, cssless=True)

@app.context_processor
def inject_stage_and_region():
    return dict(LIGHTNOVEL_FOLDER=LIGHTNOVEL_FOLDER, WEBSITE_URL=WEBSITE_URL, language_dict=language_dict)

@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/favicon.ico")
def favicon():
    return send_file("static/assets/favicon.png", mimetype="image/x-icon")


@app.route("/image/<path:file>")
def image(file: pathlib.Path):
    path: pathlib.Path = LIGHTNOVEL_FOLDER / file
    if path.exists() and path.name == "cover.jpg":
        return send_from_directory(LIGHTNOVEL_FOLDER, file)
    else:
        print(path)
        print(path.name)
    return "", 404


# --------------------------------------------------------------

# @app.route()
# ----------------------------------------------------------------------------------------------------------------------


# @app.route("/lncrawl/download/<int:id>/")
# @app.route("/lncrawl/download/<int:id>/<string:job_id>")
# def download():
#     data = request.json
#     pass


# @app.route("/lncrawl/status/<string:job_id>")
# def job_status(job_id):
#     pass


# @app.route("/lncrawl/cancel/<string:job_id>")
# def cancel_job(job_id):
#     pass


# @app.route("/lncrawl/list")
# def list_downloaded():
#     pass
