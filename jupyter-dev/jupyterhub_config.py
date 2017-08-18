import os

c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8082

bindir = '/global/common/cori/software/python/3.5-anaconda/bin/'
if 'BASE_PATH' in os.environ:
    bindir = os.environ['BASE_PATH']+'/bin/'
c.Spawner.cmd = [bindir + 'jupyterhub-singleuser']

c.Spawner.ip = '0.0.0.0'

c.Spawner.environment = {"OMP_NUM_THREADS" : "2"}

c.Spawner.default_url = '/tree/global/homes/{username[0]}/{username}'

c.JupyterHub.authenticator_class = 'gsiauthenticator.auth.GSIAuthenticator'
if 'ADMINS' in os.environ:
    c.Authenticator.admin_users = os.environ['REMOTE_HOST'].split(',')

c.GSIAuthenticator.server = 'nerscca1.nersc.gov'


if 'SSL_KEY' in os.environ and 'SSL_CERT' in os.environ:
  c.JupyterHub.ssl_key = os.environ['SSL_KEY']
  c.JupyterHub.ssl_cert = os.environ['SSL_CERT']
else:
  c.JupyterHub.confirm_no_ssl = False



c.JupyterHub.spawner_class = 'sshspawner.sshspawner.SSHSpawner'

c.SSHSpawner.remote_host = 'cori19-224.nersc.gov'
c.SSHSpawner.remote_port = '2222'
c.SSHSpawner.ssh_command = 'gsissh'
if 'REMOTE_HOST' in os.environ:
    (host, port) = os.environ['REMOTE_HOST'].split(':')
    c.SSHSpawner.remote_host = host
    c.SSHSpawner.remote_port = port

c.SSHSpawner.hub_api_url='http://jupyter-dev.nersc.gov:8082/hub/api'
if 'HUB_API_URL' in os.environ:
    c.SSHSpawner.hub_api_url = os.environ['HUB_API_URL']

c.SSHSpawner.use_gsi = True
c.SSHSpawner.path = bindir+':/global/common/cori/das/jupyterhub/:/usr/common/usg/bin:/usr/bin:/bin'
c.SSHSpawner.remote_port_command = '/global/common/cori/das/jupyterhub/get_port.py'

c.JupyterHub.cookie_max_age_days = 0.5
