from .. import ldc
from .node import SwarmNode


class SwarmSubnet(ldc.DockerSubnet):

    def __init__(self, *args, size: int = 510, **kwargs):
        self._cluster_hosts = {}
        self._offset = size
        super().__init__(*args, size=size*2, **kwargs)

    def add_node(self, node: 'SwarmNode'):

        ip_address = self._get_host_ip()

        # docker swarm overlay requires additional ip address for lode balancer each cluster node (cluster_host in l3ns)
        if not isinstance(node, ldc.DockerNode) and node.cluster_host.address not in self._hosts:
            self._cluster_hosts[node.cluster_host.address] = self._hosts.pop(0)

        self._nodes_dict[ip_address] = node
        if node not in self._network:
            self._network.add_node(node)
        node.add_interface(ip_address, self)

    def _get_host_ip(self):
        # Since we don't have control over ip management for lode balancers, first free ip of the docker network
        # ip range will be used for each swarm node. Since it's not possible to control starting order of the nodes,
        # it's easier to just make network twice as large and give out addresses only from the second half
        return str(self._hosts.pop(self._offset+1))

    def start(self):
        if self.started:
            return self.docker_network

        self.docker_network = self._client.networks.create(
            self.name,
            driver='overlay',
            attachable=True,
            ipam=self._make_ipam_config())

        if not self.docker_network.attrs['Driver']:
            raise Exception('Error: IPAM customisation failed for swarm network {}, check if other networks overlap ip pool'.format(self.name))

        self.started = True
        self.loaded = True

        print('[swarm] subnet', self.name, 'started')

        return self.docker_network
