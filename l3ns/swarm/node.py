from .. import ldc
from .utils import SwarmHost


class SwarmNode(ldc.DockerNode):

    def __init__(self, name, cluster_host: 'SwarmHost', **kwargs):
        self.cluster_host = cluster_host

        super().__init__(name, **kwargs)

        self._client = cluster_host.get_docker_client()

    def _connect_subnet(self, subnet, ip):
        self._client.api.connect_container_to_network(self.container.name, subnet.docker_network.name, ipv4_address=ip)

    def __repr__(self):
        return '<{class_name}({name}@{hostname}, {ip})'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            ip=self.get_ip(),
            hostname=self.cluster_host.address)
