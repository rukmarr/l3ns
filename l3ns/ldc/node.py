from l3ns.base import BaseNode
from l3ns.ldc.utils import docker_client


class DockerNode(BaseNode):

    _client = docker_client

    def __init__(self, name=None, connect_to_internet=False, **docker_kwargs):
        self._docker_kwargs = docker_kwargs
        self.connect_to_internet = connect_to_internet
        self.container = None
        super(DockerNode, self).__init__(name=name)

    def start(self):
        if self.started:
            return self.container

        networking_kwargs = {}

        try:
            first_subnet = next(iter(self._interfaces.values())).docker_network
        except StopIteration:
            first_subnet = None

        if first_subnet:
            networking_kwargs['network'] = first_subnet.name

            for net in self._networks:
                gateway = self.get_gateway(net)

                if gateway:
                    self._routes[net.ip_range] = self.get_gateway(net)

        elif not self.connect_to_internet:
            networking_kwargs['networking_mode'] = 'none'

        self.container = self._client.containers.create(
            name=self.name,
            **networking_kwargs,
            **self._docker_kwargs)

        if first_subnet:
            first_subnet.disconnect(self.container)

        for ip, network in self._interfaces.items():
            network.docker_network.connect(self.container, ipv4_address=ip)

        self.container.start()

        return self.container

    # change entry point
