
from textwrap import dedent
import time

import asyncssh
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
            "ssh -q -o StrictHostKeyChecking=no -o preferredauthentications=publickey -l {username} -i /tmp/{username}.key {remote_host}",
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

#   sim_url=Unicode("https://sim-stage.nersc.gov/graphql").tag(config=True)
    sim_url=Unicode("https://sim.nersc.gov/graphql").tag(config=True)

    async def query_sim_accounts(self, name): #rename
        query = dedent("""
        query {{
          systemInfo {{
            users(name: "{}") {{
              baseRepos {{
                computeAllocation {{
                  repoName
                }}
              }}
            }}
          }}
          systemInfo {{
            users(name: "{}") {{
              userAllocations {{
                computeAllocation {{
                  repoName
                }}
              }}
            }}
          }}
        }}""".format(name, name)).strip()
        data = await self.query_sim(query)
        user = data["data"]["systemInfo"]["users"][0]
        default_account = user["baseRepos"][0]["computeAllocation"]["repoName"]
        accounts = [a["computeAllocation"]["repoName"] for a in user["userAllocations"]]
        accounts.sort()
        accounts.remove(default_account)
        accounts.insert(0, default_account)
        return accounts

    async def query_sim(self, query):
        http_client = httpclient.AsyncHTTPClient()
        request = self.sim_request(query)
        response = await http_client.fetch(request)
        return escape.json_decode(response.body)

    def sim_request(self, query):
        return httpclient.HTTPRequest(self.sim_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=escape.json_encode({"query": query}))

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

class NERSCExclusiveSlurmSpawner(NERSCSlurmSpawner):

    batch_script = Unicode("""#!/bin/bash
#SBATCH --comment={{ cookie }}
{%- if constraint %}
#SBATCH --constraint={{ constraint }}
{%- endif %}
#SBATCH --job-name=jupyter
#SBATCH --nodes={{ nodes }}
#SBATCH --qos={{ qos }}
#SBATCH --sdn
#SBATCH --time={{ runtime }}
{{ env_text }}
unset XDG_RUNTIME_DIR
{{ cmd }}""").tag(config=True)

    # Have to override this to call get_auth_state() I think
    async def _get_batch_script(self, **subvars):
        """Format batch script from vars"""
        auth_state = await self.user.get_auth_state()
        self.userdata = auth_state["userdata"]
        uid = self.userdata["uid"]
        subvars["cookie"] = int(time.time()) ^ (uid ** 2)
        return format_template(self.batch_script, **subvars)

class NERSCBigmemSlurmSpawner(NERSCSlurmSpawner):

    batch_script = Unicode("""#!/bin/bash
#SBATCH --clusters=escori
#SBATCH --comment={{ cookie }}
#SBATCH --job-name=jupyter
#SBATCH --nodes={{ nodes }}
#SBATCH --qos=bigmem
#SBATCH --time={{ runtime }}
{{ env_text }}
unset XDG_RUNTIME_DIR
{{ cmd }}""").tag(config=True)

    batch_query_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh squeue -h -j {job_id} -o '%T\ %B-224.nersc.gov'").tag(config=True)
    batch_cancel_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh scancel {job_id}").tag(config=True)

    # Have to override this to call get_auth_state() I think
    async def _get_batch_script(self, **subvars):
        """Format batch script from vars"""
        auth_state = await self.user.get_auth_state()
        self.userdata = auth_state["userdata"]
        uid = self.userdata["uid"]
        subvars["cookie"] = int(time.time()) ^ (uid ** 2)
        return format_template(self.batch_script, **subvars)

    def parse_job_id(self, output):
        output = output.replace(" on cluster escori", "")
        return super().parse_job_id(output)

class NERSCExclusiveGPUSlurmSpawner(NERSCSlurmSpawner):

    batch_submit_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh sbatch").tag(config=True)
    batch_query_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh squeue -h -j {job_id} -o '%T\ %B-144.nersc.gov'").tag(config=True)
    batch_cancel_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh scancel {job_id}").tag(config=True)

    batch_script = Unicode("""#!/bin/bash
#SBATCH --account={{ account }}
#SBATCH --constraint=gpu
#SBATCH --gres=gpu:1
#SBATCH --job-name=jupyter
#SBATCH --nodes={{ nodes }}
#SBATCH --qos={{ qos }}
#SBATCH --time={{ runtime }}
{{ env_text }}
unset XDG_RUNTIME_DIR
{{ cmd }}""").tag(config=True)

    # Have to override this to call get_auth_state() I think
    async def _get_batch_script(self, **subvars):
        """Format batch script from vars"""
        auth_state = await self.user.get_auth_state()
        self.userdata = auth_state["userdata"]
        subvars["account"] = self.default_gpu_repo()
        subvars["qos"] = self.gpu_qos()
        return format_template(self.batch_script, **subvars)

    def default_gpu_repo(self):
        # training
        for allocation in self.user_allocations(["gpu4sci"]):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] == "gpu":
                    return allocation["computeAllocation"]["repoName"]
        # special m1759 people
        for allocation in self.user_allocations(["m1759"]):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] == "gpu_special_m1759":
                    return allocation["computeAllocation"]["repoName"]
        # training
        for allocation in self.user_allocations(["m3502"]):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] == "gpu":
                    return allocation["computeAllocation"]["repoName"]
        for allocation in self.user_allocations():
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] == "gpu":
                    return allocation["computeAllocation"]["repoName"]
        return None

    def gpu_qos(self):
        # training
        for allocation in self.user_allocations(["gpu4sci"]):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] == "gpu":
                    return "regular"
        # special m1759 people, only special people there
        for allocation in self.user_allocations(["m1759"]):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] == "gpu_special_m1759":
                    return "special"
        return "regular"

    def user_allocations(self, repos=[]):
        for allocation in self.userdata["userAllocations"]:
            if repos and allocation["computeAllocation"]["repoName"] not in repos:
                continue
            yield allocation


class NERSCConfigurableGPUSlurmSpawner(NERSCSlurmSpawner):

    batch_submit_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh sbatch").tag(config=True)
    batch_query_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh squeue -h -j {job_id} -o '%T\ %B-144.nersc.gov'").tag(config=True)
    batch_cancel_cmd = Unicode("/bin/bash -l /global/common/cori/das/jupyterhub/esslurm-wrapper.sh scancel {job_id}").tag(config=True)

#SBATCH --gres=gpu:{{ ngpus }}

    batch_script = Unicode("""#!/bin/bash
#SBATCH --account={{ account }}
#SBATCH --qos={{ qos }}
#SBATCH --constraint=gpu
#SBATCH --job-name=jupyter
#SBATCH --nodes={{ nodes }}
#SBATCH --ntasks-per-node={{ ntasks_per_node }}
#SBATCH --cpus-per-task={{ cpus_per_task }}
#SBATCH --gpus-per-task={{ gpus_per_task }}
#SBATCH --time={{ runtime }}
{{ env_text }}
unset XDG_RUNTIME_DIR
{{ cmd }}""").tag(config=True)

    async def options_form(self, spawner):
        form = ""

        # Account

        form += dedent("""
        <label for="account">Account:</label>
        <select class="form-control" name="account" required autofocus>
        """)

        for allocation in spawner.userdata["userAllocations"]:
            account = allocation["computeAllocation"]["repoName"]
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] in ["gpu", "gpu_special_m1759"]:
                    form += """<option value="{}">{}</option>""".format(account, account)

        form += dedent("""
        </select>
        """)

        # QOS, would be nice to constrain from qos

        form += dedent("""
        <label for="qos">QOS:</label>
        <select class="form-control" name="qos" required autofocus>
        <option value="gpu">gpu</option>
        <option value="special">special (m1759 only)</option>
        </select>
        """)

#       # GPUs per node, should come from model

#       form += dedent("""
#       <label for="nodes">GPUs per Node:</label>
#       <input class="form-control" type="number" name="ngpus" min="1" max="8" value="1" required autofocus>
#       """)

        # Nodes, should come from model

        form += dedent("""
        <label for="nodes">nodes:</label>
        <input class="form-control" type="number" name="nodes" min="1" max="5" value="1" required autofocus>
        """)

        # Number of tasks per node, should come from model

        form += dedent("""
        <label for="ntasks-per-node">ntasks-per-node (up to 8 tasks):</label>
        <input class="form-control" type="number" name="ntasks-per-node" min="1" max="8" value="1" required autofocus>
        """)

        # Number of CPUs per task, should come from model

        form += dedent("""
        <label for="cpus-per-task">cpus-per-task (node has 80 cores):</label>
        <input class="form-control" type="number" name="cpus-per-task" min="1" max="80" value="10" required autofocus>
        """)

        # Number of GPUs per task, should come from model

        form += dedent("""
        <label for="gpus-per-task">gpus-per-task (node has 8 GPUs):</label>
        <input class="form-control" type="number" name="gpus-per-task" min="1" max="8" value="1" required autofocus>
        """)

        # Time, should come from model

        form += dedent("""
        <label for="runtime">time (time limit in minutes):</label>
        <input class="form-control" type="number" name="runtime" min="10" max="240" value="240" step="10" required autofocus>
        """)

        return form

    def options_from_form(self, formdata):
        options = dict()
        options["account"] = formdata["account"][0]
        options["qos"] = formdata["qos"][0]
#       options["ngpus"] = formdata["ngpus"][0]
        options["ntasks_per_node"] = formdata["ntasks-per-node"][0]
        options["cpus_per_task"] = formdata["cpus-per-task"][0]
        options["gpus_per_task"] = formdata["gpus-per-task"][0]
        options["runtime"] = formdata["runtime"][0]
        return options

#     # Have to override this to call get_auth_state() I think
#     async def _get_batch_script(self, **subvars):
#         """Format batch script from vars"""
#         auth_state = await self.user.get_auth_state()
#         self.userdata = auth_state["userdata"]
# #       subvars["account"] = self.default_gpu_repo()
#         return format_template(self.batch_script, **subvars)

#   def default_gpu_repo(self):
#       for allocation in self.user_allocations(["nstaff", "m1759", "dasrepo"]):
#           for qos in allocation["userAllocationQos"]:
#               if qos["qos"]["qos"] == "gpu":
#                   return allocation["computeAllocation"]["repoName"]
#       return None

#   def user_allocations(self, repos=[]):
#       for allocation in self.userdata["userAllocations"]:
#           if repos and allocation["computeAllocation"]["repoName"] not in repos:
#               continue
#           yield allocation



class NERSCConfigurableSlurmSpawner(NERSCSlurmSpawner):

    req_image = Unicode("",
            help="Shifter image",
            config=True)

    req_reservation = Unicode("",
            help="Reservation.",
            config=True)

    async def options_form(self, spawner):
        form = ""

        # Account

        form += dedent("""
        <label for="account">Account:</label>
        <select class="form-control" name="account" required autofocus>
        """)

        accounts = await self.query_sim_accounts(spawner.user.name)
        for account in accounts:
            form += """<option value="{}">{}</option>""".format(account, account)

        form += dedent("""
        </select>
        """)

        # Nodes, should come from model

        form += dedent("""
        <label for="nodes">Nodes:</label>
        <input class="form-control" type="number" name="nodes" min="1" max="5" value="1" required autofocus>
        """)

        # Time, should come from model

        form += dedent("""
        <label for="time">Time Limit:</label>
        <input class="form-control" type="number" name="time" min="10" max="240" value="30" step="10" required autofocus>
        """)

        # QOS, should come from model

        form += dedent("""
        <label for="qos">QOS:</label>
        <select class="form-control" name="qos" required autofocus>
        <option value="regular">regular</option>
        <option value="debug">debug</option>
        <option value="jupyter">'jupyter'</option>
        </select>
        """)

        # Constraint, should come from model

        form += dedent("""
        <label for="account">Constraint:</label>
        <select class="form-control" name="constraint" required autofocus>
        <option value="haswell">haswell</option>
        <option value="knl">knl</option>
        </select>
        """)

        # Reservation

        form += dedent("""
        <label for="reservation">Reservation:</label>
        <select class="form-control" name="reservation" autofocus>
        """)

        reservations = await self.query_reservations(spawner.user.name)
        for reservation in reservations:
            form += """<option value="{}">{}</option>""".format(reservation, reservation)

        form += dedent("""
        </select>
        """)

        # Images

        form += dedent("""
        <label for="image">Shifter Image:</label>
        <select class="form-control" name="image" autofocus>
        """)

        images = await self.query_images(spawner.user.name)
        for image in images:
            form += """<option value="{}">{}</option>""".format(image, image)

        form += dedent("""
        </select>
        """)

        return form

    async def query_reservations(self, name):
        # Should filter on username
        remote_host = self.req_remote_host
        keyfile = "/certs/{}.key".format(name)
        certfile = keyfile + "-cert.pub"
        k = asyncssh.read_private_key(keyfile)
        c = asyncssh.read_certificate(certfile)
        async with asyncssh.connect(remote_host,
                username=name,
                client_keys=[(k,c)],
                known_hosts=None) as conn:
            result = await conn.run("/usr/bin/scontrol show reservation --oneliner")
        reservations = [""]
        for line in result.stdout.split("\n"):
            columns = line.split()
            for column in columns:
                key, value = column.split("=", 1)
                if key == "ReservationName":
                    reservations.append(value)
                    break
        return reservations

    async def query_images(self, name):
        # Some better filtering is needed...
        remote_host = self.req_remote_host
        keyfile = "/certs/{}.key".format(name)
        certfile = keyfile + "-cert.pub"
        k = asyncssh.read_private_key(keyfile)
        c = asyncssh.read_certificate(certfile)
        async with asyncssh.connect(remote_host,
                username=name,
                client_keys=[(k,c)],
                known_hosts=None) as conn:
            result = await conn.run("/usr/bin/shifterimg images")
        images = [""]
        for line in result.stdout.split("\n"):
            columns = line.split()
            if columns:
                image_name = columns[-1]
                if image_name.find("jupyterlab") < 0:
                    continue
                images.append(image_name)
        return images

    def options_from_form(self, formdata):
        options = dict()
        options["account"] = formdata["account"][0]
        options["constraint"] = formdata["constraint"][0]
        options["image"] = formdata["image"][0]
        options["nodes"] = formdata["nodes"][0]
        options["qos"] = formdata["qos"][0]
        options["reservation"] = formdata["reservation"][0]
        options["time"] = formdata["time"][0]
        return options

    batch_script = Unicode("""#!/bin/bash
#SBATCH --account={{ account }}
{%- if constraint %}
#SBATCH --constraint={{ constraint }}
{%- endif %}
{%- if image %}
#SBATCH --image={{ image }}
{%- endif %}
#SBATCH --job-name=jupyter
#SBATCH --nodes={{ nodes }}
#SBATCH --output=jupyter-%j.log
#SBATCH --qos={{ qos }}
{%- if reservation %}
#SBATCH --reservation={{ reservation }}
{%- endif %}
#SBATCH --sdn
#SBATCH --time={{ time }}
{{ env_text }}
unset XDG_RUNTIME_DIR
{% if image %}
shifter jupyter-labhub {{ cmd.split()[2:] | join(" ") }}
{% else %}
{{ cmd }}
{% endif %}""").tag(config=True)
