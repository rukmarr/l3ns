from .. import defaults
from .. import utils
from . import network as base_network
from . import node as base_node

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .network import Network

class BaseSubnet:
    """Base class for subnets representing IP subnets of the virtual networks"""

    def __init__(self, name: str, *args, size: int = 1024, network: 'base_network.Network' = None):
        """Create subnet with given name and size in given Network

        Names of networks need to be unique, as with Nodes.
        Size can't be anything as long as Network has free IP addresses in pool.
        However there is to caveats:
        1. Some implementation must have several IP addresses reserved, for example
        DockerNetwork reserves one IP address for virtual bridge interface.
        This will increase network size.
        2. Actual subnet IP address size must be a power of two. So actual size of network will be
        increase to a nearest power of two.

        Args:
            name: name for new subnet
            *args: nodes to add to the new network
            size: Optional; size of a new network
            network: Optional; as the name implies every subnet lies in some network.
                     If network is not provided, l3ns.defaults.network will be used.
        """
        self.name = name
        self._network = network if network is not None else defaults.network
        self._network.add_subnet(self)
        self._max_size = size
        self._ip_range = self._network.get_subnet_range(self._max_size)
        self._hosts = list(self._ip_range.hosts())

        self._nodes_dict = {}
        self.started = False
        self.loaded = False

        for node in utils.args.list_from_args(args):
            self.add_node(node)

    def __iter__(self):
        return iter(self._nodes_dict)

    def _get_host_ip(self):
        try:
            return str(self._hosts.pop(0))
        except IndexError:
            raise Exception('Network {} is too small'.format(self.name))

    def add_node(self, node: 'base_node.BaseNode'):
        """Add node to the network

        This is a main method to define network structure.
        This will also add node to subnet's network, create interface in node with an
        IP address from this subnet.
        """

        ip_address = self._get_host_ip()

        self._nodes_dict[ip_address] = node
        if node not in self._network:
            self._network.add_node(node)
        node.add_interface(ip_address, self)

    def start(self):
        """Subnet starting procedure to be implemented in resource-specific classed, like DockerSubnet"""
        raise NotImplementedError()

    def load(self):
        """Subnet loading procedure to be implemented in resource-specific classed, like DockerSubnet"""
        raise NotImplementedError()

    def stop(self):
        """Subnet stopping procedure to be implemented in resource-specific classed, like DockerSubnet"""
        raise NotImplementedError()

    def get_network(self) -> 'Network':
        """Get Network this subnet resides in."""
        return self._network

    def get_gateway(self, node):
        """Get default gateway for this network

        Returns default gateway (not LAN gateway) for nodes in this subnet
        """
        router = None

        for ip, n in self._nodes_dict.items():

            if n is node:
                continue

            if not router and n.is_router:
                router = ip

        return router

    def get_nodes_dict(self):
        """Get nodes in a dict with IP addresses as keys"""
        return self._nodes_dict.copy()

    def prefixlen(self):
        """Get subnet IP address prefix length"""
        return self._ip_range.prefixlen

    def get_ip_range(self):
        """Get subnet IP address,"""
        return self._ip_range

    @property
    def nodes(self):
        """Get a list of subnet's nodes"""
        return list(self._nodes_dict.values())

    def get_node_ip(self, node):
        for ip, n in self._nodes_dict.items():
            if n is node:
                return ip

        raise Exception('Node is not in subnet')

    def __repr__(self):
        return '{class_name}({name}, {ip_range})'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            ip_range=self._ip_range
        )

    def __contains__(self, item):
        return item in self._nodes_dict.values()

    def __str__(self):
        return str(self._ip_range)
