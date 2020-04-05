import docker

from l3ns.base import BaseNode
from l3ns.ldc.utils import docker_client


class DockerNode(BaseNode):

    def __init__(self, name=None, connect_to_internet=False, **docker_kwargs):
        self._client = docker_client
        self._docker_kwargs = docker_kwargs
        self.connect_to_internet = connect_to_internet
        self.container = None
        super(DockerNode, self).__init__(name=name)

    def _connect_network(self, network, ip, dc=None):
        dc = dc or self._client

        dc.networks.get(network.name).connect(self.container, ipv4_address=ip)

    def _make_entrypoint(self):
        # TODO: analyse image, etc...

        waiting_cmd = 'while [ ! -f /tmp/sleep.txt ]; do sleep 1; done\n'

        if 'command' in self._docker_kwargs:
            return self._docker_kwargs['command']




    def start(self, dc=None):

        dc = dc or self._client

        if self.started:
            return self.container

        networking_kwargs = {}

        for net in self._networks:
            gateway = self.get_gateway(net)

            if gateway:
                self._routes[net.ip_range] = self.get_gateway(net)

        self.container = dc.containers.run(
            name=self.name,
            detach=True,
            **networking_kwargs,
            **self._docker_kwargs)
        self.started = True
        self.loaded = True

        try:
            default_net = next(iter(self.container.attrs['NetworkSettings']['Networks'].keys()))
        except StopIteration:
            raise Exception('Container {} has no initial net, check docker config')

        if not self._interfaces and not self.connect_to_internet:
            dc.networks.get(default_net).disconnect(self.container)

        for ip, network in self._interfaces.items():
            self._connect_network(network, ip, dc=dc)

        print('node', self.name, 'started')

        return self.container

    def load(self, dc=None):

        dc = dc or self._client

        try:
            self.container = dc.containers.get(self.name)
            self.loaded = True
        except docker.errors.NotFound:
            pass

    def stop(self, dc=None):

        dc = dc or self._client

        if not self.loaded:
            self.load(dc=dc)

        try:
            self.container.remove(force=True)
            print('node', self.name, 'stopped')
        except Exception as e:
            print('error while removing node {}: {}'.format(self.name, e))
