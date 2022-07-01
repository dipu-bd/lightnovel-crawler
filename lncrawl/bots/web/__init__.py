from . import flaskapp
from . import downloader # type: ignore
from . import reader # type: ignore

from waitress import serve
serve(flaskapp.app, port=5000)

# flaskapp.app.run()
