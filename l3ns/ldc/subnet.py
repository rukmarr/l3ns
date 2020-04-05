from l3ns.base import BaseSubnet
from l3ns.ldc.utils import docker_client
import docker


class DockerSubnet(BaseSubnet):

    _client = docker_client

    def __init__(self, *args, size=1023, **kwargs):
        self.docker_network = None

        super(DockerSubnet, self).__init__(*args, size=size + 1, **kwargs)
        # minus one address for docker gateway
        self._docker_gateway = str(next(self._hosts))

    def start(self):
        if self.started:
            return self.docker_network

        ipam_pool = docker.types.IPAMPool(subnet=str(self._ip_range), gateway=self._docker_gateway)
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool, ])

        self.docker_network = self._client.networks.create(self.name, ipam=ipam_config)
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


