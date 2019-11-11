
### def mapper(key):
###     return "service" + key
### 
### c.ServerMapper.mapper = mapper

def hook(handler, host):
    handler.log.info("request to proxy to host " + host)
    return host == "service1"

c.ServerProxy.host_whitelist_hook = hook
