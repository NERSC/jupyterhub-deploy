## Setup

```
pip install python-dateutil
pip install tornado
```

## Running

```
export JUPYTERHUB_API_TOKEN=XXXXXXX
python cull_idle_servers.py --timeout=44000 --url=https://jupyter-dev.nersc.gov/hub/api
```

Or run sync to avoid timeout issues
```
python cull_idle_servers_sync.py --timeout=44000 --url=https://jupyter-dev.nersc.gov/hub/api
```
