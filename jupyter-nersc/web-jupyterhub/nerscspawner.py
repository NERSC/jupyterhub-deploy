
from jupyterhub.spawner import LocalProcessSpawner

from tornado import httpclient, web
from traitlets import List, Dict, Unicode, observe

from wrapspawner import WrapSpawner

class NERSCSpawner(WrapSpawner):

    profiles = List(Dict(),
            help="TBD",
            config=True)

    setups = List(Dict(),
            help="TBD",
            config=True)

    systems = List(Dict(),
            help="TBD",
            config=True)

    spawners = Dict(
            help="TBD",
            config=True)

    child_profile = Unicode()

    def check_roles(self, auth_state, roles):
        """User has one or more of these roles"""
        if roles:
            for role in roles:
                if self.check_role(auth_state, role):
                    return True
            return False
        else:
            return True

    def check_role(self, auth_state, role):
        if role == "gpu":
            return self.check_role_gpu(auth_state)
        if role == "staff":
            return self.check_role_staff(auth_state)
        if role == "cori-exclusive-node-cpu":
            return self.check_role_cori_exclusive_node_cpu(auth_state)
        if role == "cmem":
            return self.check_role_cmem(auth_state)
        if role == "dgx":
            return self.check_role_dgx(auth_state)
        return False

    def check_role_cori_exclusive_node_cpu(self, auth_state):
        return self.default_jupyter_repo(auth_state) is not None

    def default_jupyter_repo(self, auth_state):
        for allocation in self.user_allocations(auth_state):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] in ["jupyter"]:
                    return allocation["computeAllocation"]["repoName"]
        return None

    def check_role_cmem(self, auth_state):
        return self.default_cmem_repo(auth_state) is not None

    def default_cmem_repo(self, auth_state):
        for allocation in self.user_allocations(auth_state):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] in ["cmem"]:
                    return allocation["computeAllocation"]["repoName"]
        return None

    def check_role_gpu(self, auth_state):
        return self.default_gpu_repo(auth_state) is not None

    def check_role_staff(self, auth_state):
        for allocation in self.user_allocations(auth_state, ["nstaff"]):
            return True
        return False

    def default_gpu_repo(self, auth_state):
        for allocation in self.user_allocations(auth_state):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] in ["gpu", "gpu_special_m1759"]:
                    return allocation["computeAllocation"]["repoName"]
        return None

    def check_role_dgx(self, auth_state):
        return self.default_dgx_repo(auth_state) is not None

    def default_dgx_repo(self, auth_state):
        for allocation in self.user_allocations(auth_state):
            for qos in allocation["userAllocationQos"]:
                if qos["qos"]["qos"] in ["dgx"]:
                    return allocation["computeAllocation"]["repoName"]
        return None

    def user_allocations(self, auth_state, repos=[]):
        for allocation in auth_state["userdata"].get("userAllocations", []):
            if repos and allocation["computeAllocation"]["repoName"] not in repos:
                continue
            yield allocation

    def start(self):
        if self.name not in self.spawners:
            raise web.HTTPError(404)
        return super().start()

    def select_profile(self, profile):
        self.log.debug("select_profile: " + profile)
        if profile == "":
            self.child_class, self.child_config = LocalProcessSpawner, {}
        else:
            try:
                self.child_class, self.child_config = self.spawners[profile]
            except KeyError:
                raise web.HTTPError(404)

    def construct_child(self):
        self.log.debug("construct_child called")
        # self.child_profile = self.user_options.get('profile', "")
        self.child_profile = self.name
        self.select_profile(self.child_profile)
        super().construct_child()
#       self.child_spawner.orm_spawner = self.orm_spawner  ### IS THIS KOSHER?!?!!?
        self.options_form = self.child_spawner.options_form # another one...
        self.options_from_form = self.child_spawner.options_from_form
        self.child_spawner.user_options = self.user_options
#       ### Think we need to do this to get JUPYTERHUB_OAUTH_CALLBACK_URL set properly

    def load_child_class(self, state):
        self.log.debug("load_child_class called")
        try:
            self.child_profile = state['profile']
        except KeyError:
            self.child_profile = ''
        self.select_profile(self.child_profile)

    def get_state(self):
        state = super().get_state()
        state['profile'] = self.child_profile
        return state

    def clear_state(self):
        super().clear_state()
        self.child_profile = ''

    @property
    def model_updated(self):
        return True

    @observe("user_options")
    def _observe_user_options(self, change): 
        self.log.debug("user_options observed: " + str(change))

