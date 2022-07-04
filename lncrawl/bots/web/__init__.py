from . import flaskapp
from . import downloader # type: ignore
from . import reader # type: ignore
from .lib import PORT, HOST
from waitress import serve
serve(flaskapp.app, port=PORT, host=HOST)

# flaskapp.app.run()
