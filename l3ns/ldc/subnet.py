from .. import base
from . import utils

import docker


class DockerSubnet(base.BaseSubnet):

    _client = utils.docker_client

    def __init__(self, *args, size=1023, docker_client=None, **kwargs):
        self.docker_network = None
        if docker_client:
            self._client = docker_client

        super().__init__(*args, size=size + 1, **kwargs)
        # minus one address for docker gateway
        self._docker_gateway = self._get_host_ip()

    def _make_ipam_config(self):
        ipam_pool = docker.types.IPAMPool(subnet=str(self._ip_range), gateway=self._docker_gateway)
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool, ])

        return ipam_config

    def start(self):
        if self.started:
            return self.docker_network

        # for some reason IPAM configuration in docker-py break swarm networks, so we'll use CLI for now
        self.docker_network = self._client.networks.create(
            self.name,
            ipam=self._make_ipam_config())

        self.started = True
        self.loaded = True

        print('[ldc] subnet', self.name, 'started')

        return self.docker_network

    def load(self):
        try:
            self.docker_network = self._client.networks.get(self.name)
            self.loaded = True
        except docker.errors.NotFound:
            pass

    def stop(self):
        if not self.loaded:
            self.load()

        try:
            self.docker_network.remove()
            print('[ldc] subnet', self.name, 'stopped')
        except Exception as e:
            print('error while removing subnet {}: {}'.format(self.name, e))
