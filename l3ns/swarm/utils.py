from .. import cluster
import subprocess
import re

check_swarm_cmd = 'docker swarm join-token worker'
start_swarm_cmd = 'docker swarm init --advertise-addr {}'
list_nodes_cmd = "docker node ls --format '{{.Hostname}}:{{.Status}}'"


class SwarmHost(cluster.ClusterHost):

    swarm_token = None
    new_swarm = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.swarm_token is None:
            self._init_swarm()

        dc = self.get_docker_client()

        if not self.new_swarm:

            # check if node in swarm if one exists
            ret = subprocess.run(list_nodes_cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, universal_newlines=True)
            if not ret.returncode:
                nodes = [n.split(':') for n in ret.stdout.split('\n')]
                for node in nodes:
                    if self.address == node[0] and node[1] == "Ready":
                        return
        try:
            dc.join_swarm([self._get_manager_ip()], self.swarm_token)

        except AttributeError:
            dc.api.join_swarm([self._get_manager_ip()], self.swarm_token)

    def _init_swarm(self):
        ret = subprocess.run(check_swarm_cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, universal_newlines=True)

        if ret.returncode:
            print('checking for swarm\nreturn code:', ret.returncode)
            print(ret.stdout)
        else:
            token = self._find_token(ret.stdout)

            if token:
                self.swarm_token = token
                self.new_swarm = False
                return

        ip = self._get_manager_ip()

        ret = subprocess.run(start_swarm_cmd.format(ip), shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, universal_newlines=True)

        if not ret.returncode:
            token = self._find_token(ret.stdout)

            if token:
                self.swarm_token = token
                self.new_swarm = True
                return

        raise Exception("Couldn't join the swarm, docker output:\n" + ret.stdout)

    @staticmethod
    def _find_token(s):
        match = re.search('--token ([^ ]*) ', s)

        if match:
            return match.group(1)

        else:
            raise Exception('Error while parsing output for docker swarm token:\n' + s)

    @staticmethod
    def _get_manager_ip():
        # TODO: socket?? hostname?? I dunno
        return '192.168.122.119'

# new swarm no swarm       - v
# old swarm no swarm       - v
# old swarm has same swarm - v

# new swarm has swarm      - ?
# old swarm has another swarm - ?


if __name__ == "__main__":

    sh = SwarmHost('t2')

    print([n.name for n in sh.get_docker_client().networks.list()])
