from . import flaskapp
from . import downloader
from . import reader

from waitress import serve
serve(flaskapp.app, port=5000)

# flaskapp.app.run()
