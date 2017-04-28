import os
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8082

c.Spawner.cmd = ['/global/common/cori/software/python/3.5-anaconda/bin/jupyterhub-singleuser']

c.Spawner.ip = '0.0.0.0'

c.JupyterHub.authenticator_class = 'gsiauthenticator.auth.GSIAuthenticator'
#c.Authenticator.admin_users = {'rthomas', 'canon', 'shreyas'}
if 'ADMINS' in os.environ:
    c.Authenticator.admin_users = os.environ['REMOTE_HOST'].split(',')

c.GSIAuthenticator.server = 'nerscca1.nersc.gov'


#c.JupyterHub.ssl_key = '/ssl/server.key'
#c.JupyterHub.ssl_cert = '/ssl/server.crt'
#c.JupyterHub.no_ssl = True


c.JupyterHub.spawner_class = 'sshspawner.sshspawner.SSHSpawner'

c.SSHSpawner.remote_host = 'cori19-224.nersc.gov'
c.SSHSpawner.remote_port = '2222'
c.SSHSpawner.ssh_command = 'gsissh'
if 'REMOTE_HOST' in os.environ:
    (host,port) = os.environ['REMOTE_HOST'].split(':')
    c.SSHSpawner.remote_host = host
    c.SSHSpawner.remote_port = port

c.SSHSpawner.hub_api_url='http://jupyter-dev.nersc.gov:8082/hub/api'
if 'HUB_API_URL' in os.environ:
    c.SSHSpawner.hub_api_url=os.environ['HUB_API_URL']

c.SSHSpawner.use_gsi = True
c.SSHSpawner.path = '/global/common/cori/software/python/3.5-anaconda/bin:/global/common/cori/das/jupyterhub/:/usr/common/usg/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/usr/lib/mit/bin:/usr/lib/mit/sbin'
c.SSHSpawner.remote_port_command = '/global/common/cori/das/jupyterhub/get_port.py'

c.JupyterHub.cookie_max_age_days = 0.5
