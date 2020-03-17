
from jupyterhub.proxy import ConfigurableHTTPProxy

class ConfigurableHTTPProxySpin(ConfigurableHTTPProxy):

    def add_hub_route(self, hub):
        """Add the default route for the Hub"""
        self.log.debug("url %s, api_url %s", hub.url, hub.api_url)
        host = "http://web-jupyterhub:8081"
        self.log.info("Adding default route for Hub: %s => %s", hub.routespec, host)
        return self.add_route(hub.routespec, host, {'hub': True})
#       self.log.info("Adding default route for Hub: %s => %s", hub.routespec, hub.host)
#       return self.add_route(hub.routespec, self.hub.host, {'hub': True})
