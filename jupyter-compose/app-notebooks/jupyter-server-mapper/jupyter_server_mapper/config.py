
from traitlets.config import Configurable
from traitlets import Any

class ServerMapper(Configurable):

    mapper = Any(
        lambda key: key,
        help="""Function that maps a key to a host.

        By default the key maps to itself.  This means that if `mapper` is not
        configured, the key is treated as a host.""",
        config=True
    )

