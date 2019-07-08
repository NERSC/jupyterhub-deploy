
from textwrap import dedent

from traitlets import default, Unicode
from tornado import escape, httpclient

from batchspawner import format_template, BatchSpawnerRegexStates

class NERSCSlurmSpawner(BatchSpawnerRegexStates):
    """Spawner that connects to a job-submit (login node) and submits a job to
    start a process running in the Slurm batch queue.
    NOTE Right now we allow the hub to pre-select a random port but when multiple
    users are on the same compute node, a la shared-interactive, we need to control
    the port selected deterministically or ensure they don't collide in some way.
    This has been done in later versions of BatchSpawner."""

    exec_prefix = Unicode(
            "ssh -q -o StrictHostKeyChecking=no -o preferredauthentications=publickey -l {username} -i /certs/{username}.key {remote_host}",
            config=True)

    req_constraint = Unicode('haswell',
            help="""Users specify which features are required by their job
            using the constraint option, which is required at NERSC on Cori/Gerty."""
            ).tag(config=True)

    req_nodes = Unicode('1',
            help="Number of nodes",
            config=True)

    req_qos = Unicode('jupyter',
            help="QoS name to submit job to resource manager"
            ).tag(config=True)

    req_remote_host = Unicode('remote_host',
                          help="""The SSH remote host to spawn sessions on."""
                          ).tag(config=True)

    hub_api_url = Unicode().tag(config=True)

    path = Unicode().tag(config=True)

    req_homedir = Unicode().tag(config=True)

    req_env_text = Unicode()

    @default("req_env_text")
    def _req_env_text(self):
        env = self.get_env()
        text = ""
        for item in env.items():
            text += 'export %s=%s\n' % item
        return text

    # outputs line like "Submitted batch job 209"
    batch_submit_cmd = Unicode("/usr/bin/sbatch").tag(config=True)
    # outputs status and exec node like "RUNNING hostname"
    batch_query_cmd = Unicode("/usr/bin/python /global/common/cori/das/jupyterhub/new-get-ip.py {job_id}").tag(config=True)
    batch_cancel_cmd = Unicode("/usr/bin/scancel {job_id}").tag(config=True)
    # use long-form states: PENDING,  CONFIGURING = pending
    #  RUNNING,  COMPLETING = running
    state_pending_re = Unicode(r'^(?:PENDING|CONFIGURING)').tag(config=True)
    state_running_re = Unicode(r'^(?:RUNNING|COMPLETING)').tag(config=True)
    state_exechost_re = Unicode(r'\s+((?:[\w_-]+\.?)+)$').tag(config=True)

    def parse_job_id(self, output):
        # make sure jobid is really a number
        try:
            id = output.split(' ')[-1]
            int(id)
        except Exception as e:
            self.log.error("SlurmSpawner unable to parse job ID from text: " + output)
            raise e
        return id

    # This is based on SSH Spawner
    def get_env(self):
        """Add user environment variables"""
        env = super().get_env()

        env.update(dict(
            JPY_USER=self.user.name,
            #JPY_BASE_URL=self.user.server.base_url,
            JPY_HUB_PREFIX=self.hub.server.base_url,
            JUPYTERHUB_PREFIX=self.hub.server.base_url,
            # PATH=self.path
            # NERSC local mod
            PATH=self.path
        ))

        if self.notebook_dir:
            env['NOTEBOOK_DIR'] = self.notebook_dir

        hub_api_url = self.hub.api_url
        if self.hub_api_url != '':
            hub_api_url = self.hub_api_url

        env['JPY_HUB_API_URL'] = hub_api_url
        env['JUPYTERHUB_API_URL'] = hub_api_url

        return env

class NERSCExclusiveGPUSlurmSpawner(NERSCSlurmSpawner):

    batch_submit_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh sbatch").tag(config=True)
    batch_query_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh squeue -h -j {job_id} -o '%T\ %B-144.nersc.gov'").tag(config=True)
    batch_cancel_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh scancel {job_id}").tag(config=True)

    batch_script = Unicode("""#!/bin/bash
#SBATCH --constraint=gpu
#SBATCH --gres=gpu:1
#SBATCH --job-name=jupyter-dl
#SBATCH --mem=30GB
#SBATCH --nodes=1
#SBATCH --time=240
{{ env_text }}
unset XDG_RUNTIME_DIR
{{ cmd }}""").tag(config=True)
