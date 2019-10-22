
from jupyter_server_proxy.handlers import ProxyHandler
from notebook.utils import url_path_join


class RemoteProxyHandler(ProxyHandler):
    """
    A tornado request handler that proxies HTTP and websockets
    from a port on a remote system.
    """
    async def http_get(self, host, port, proxied_path):
        return await self.proxy(host, port, proxied_path)

    async def open(self, host, port, proxied_path):
        return await self.proxy_open(host, port, proxied_path)

    def post(self, host, port, proxied_path):
        return self.proxy(host, port, proxied_path)

    def put(self, host, port, proxied_path):
        return self.proxy(host, port, proxied_path)

    def delete(self, host, port, proxied_path):
        return self.proxy(host, port, proxied_path)

    def head(self, host, port, proxied_path):
        return self.proxy(host, port, proxied_path)

    def patch(self, host, port, proxied_path):
        return self.proxy(host, port, proxied_path)

    def options(self, host, port, proxied_path):
        return self.proxy(host, port, proxied_path)

    def proxy(self, host, port, proxied_path):
        return super().proxy(host, port, proxied_path)


class MapperHandler(RemoteProxyHandler):

    def __init__(self, *args, **kwargs):
        self.mapper = kwargs.pop('mapper', lambda key: key)
        self.mappings = dict()
        super().__init__(*args, **kwargs)

    def proxy(self, key, port, proxied_path):
        return super().proxy(
            self.mappings.setdefault(key, self.mapper(key)),
            port, proxied_path)


def setup_handlers(web_app, config):
    host_pattern = '.*$'
    web_app.add_handlers('.*', [
        (url_path_join(web_app.settings['base_url'], r'/mapper/(.+):(\d+)(.*)'),
            MapperHandler, {'absolute_url': False, 'mapper': config.mapper}),
        (url_path_join(web_app.settings['base_url'], r'/mapper/absolute/(.+):(\d+)(.*)'),
            MapperHandler, {'absolute_url': True, 'mapper': config.mapper}),
    ])
