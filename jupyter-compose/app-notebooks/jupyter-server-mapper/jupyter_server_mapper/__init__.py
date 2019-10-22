
from .config import ServerMapper
from .handlers import setup_handlers

def _jupyter_server_extension_paths():
    return [{
        "module": "jupyter_server_mapper"
    }]

def load_jupyter_server_extension(nbapp):
    server_mapper = ServerMapper(parent=nbapp)

    setup_handlers(nbapp.web_app, server_mapper)
