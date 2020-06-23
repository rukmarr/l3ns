import subprocess
import socket
import time
import os
from contextlib import closing

import docker
import paramiko

# TODO: move to config
vpn_server_address = 't1'

known_hosts_path = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))
private_key_path = os.path.expanduser(os.path.join("~", ".ssh", "id_rsa"))


def generate_wg_keys():
    cmd = 'wg genkey | tee /dev/stderr | wg pubkey'

    ret = subprocess.run(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)

    return ret.stderr.strip(), ret.stdout.strip()


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class ClusterHost:

    def __init__(self, address, login='root', port=22):
        self.address = address
        self.port = port
        self.login = login
        self.docker_port = find_free_port()

        cmd = 'ssh -p {port} -NL {docker_port}:/var/run/docker.sock {login}@{address}'.format(
            docker_port=self.docker_port,
            login=login,
            address=address,
            port=port
        )

        self.forwarder = subprocess.Popen(cmd,
                                          shell=True,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          stdin=subprocess.PIPE,
                                          universal_newlines=True)

        self.ssh = paramiko.SSHClient()
        self.ssh.load_host_keys(known_hosts_path)
        self.ssh.connect(self.address, port=self.port, username=self.login, key_filename=private_key_path)

        self.sftp = self.ssh.open_sftp()

        timeout = 60
        while not self.test_client() and timeout > 0:
            time.sleep(0.5)
            timeout -= 0.5

        self._client = self.get_docker_client(cached=False)


    def get_docker_client(self, cached=True) -> docker.DockerClient:
        if cached:
            return self._client
        else:
            return docker.DockerClient(base_url='tcp://127.0.0.1:{}'.format(self.docker_port))

    def test_client(self):

        try:
            self.get_docker_client(cached=False).version()
            return True
        except:
            return False

    def upload_config(self, path, text):
        with self.sftp.open(os.path.join('/tmp/madt', path), 'w') as config_file:
            config_file.write(text)

    def exec_command(self, cmd):

        stdin, stdout, stderr = self.ssh.exec_command(cmd)

        return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()


def my_hash(*args):
    return str(hash(tuple(args)) % 10 ** 8)
