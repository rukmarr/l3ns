from ..swarm.subnet import SwarmSubnet
from ..swarm.node import SwarmNode
from .network import AutoClusterNetwork

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..swarm.utils import SwarmHost


class AutoSwarmSubnet(SwarmSubnet):
    _network: AutoClusterNetwork

    def add_node(self, node: 'SwarmNode'):

        ip_address = self._get_host_ip()

        # docker swarm overlay requires additional ip address for lode balancer each cluster node (cluster_host in l3ns)
        if len(self._cluster_hosts) < len(self._network.hosts):
            self._cluster_hosts[self._network.hosts[len(self._cluster_hosts)]] = self._hosts.pop(0)

        self._nodes_dict[ip_address] = node
        if node not in self._network:
            self._network.add_node(node)
        node.add_interface(ip_address, self)

    def start(self):
        if self.started:
            return self.docker_network

        one_host = self.is_one_host()
        if one_host:
            self._client = one_host.get_docker_client()

        self.docker_network = self._client.networks.create(
            self.name,
            driver='overlay' if not one_host else None,
            attachable=True,
            ipam=self._make_ipam_config())

        if not self.docker_network.attrs['Driver']:
            raise Exception('Error: IPAM customisation failed for swarm network {}, check if other networks overlap ip pool'.format(self.name))

        self.started = True
        self.loaded = True

        print('[swarm] subnet', self.name, 'started')

        return self.docker_network

    def load(self):
        one_host = self.is_one_host()
        if one_host:
            self._client = one_host.get_docker_client()

        return super().load()

    def is_one_host(self) -> Union[bool, 'SwarmHost']:
        nodes = self.nodes
        first = nodes[0].cluster_host
        return first if all(n.cluster_host is first for n in nodes) else False
