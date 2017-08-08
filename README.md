# Jupyterhub Deployment

This contains the Dockerfile and supporting files (currently certs) for the NERSC deployment of JupyterHub.

BASE_PATH    The path to the python install on the remote system
ADMINS       A comma seperated list of admin usernames
SSL_KEY      Path to the SSL key (if SSL should be enabled).
SSL_CERT     Path to the SSL cert  (if SSL should be enabled).
REMOTE_HOST  Host:Port of the GSI SSH running on the remote system
HUB_API_URL  URL of the HUB API (e.g. http://jupyter-dev.nersc.gov:8082/hub/api)

