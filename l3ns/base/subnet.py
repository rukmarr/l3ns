from .. import defaults
from .. import utils
from . import network as base_network
from . import node as base_node


class BaseSubnet:

    def __init__(self, name: str, *args, size: int = 1024, network: 'base_network.Network' = None):
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

        ip_address = self._get_host_ip()

        self._nodes_dict[ip_address] = node
        if node not in self._network:
            self._network.add_node(node)
        node.add_interface(ip_address, self)

    def start(self):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def get_network(self):
        return self._network

    def get_gateway(self, node):
        router = None

        for ip, n in self._nodes_dict.items():

            if n is node:
                continue

            if n.is_gateway:
                return ip

            if not router and n.is_router:
                router = ip

        return router

    def get_nodes_dict(self):
        return self._nodes_dict.copy()

    def prefixlen(self):
        return self._ip_range.prefixlen

    def get_ip_range(self):
        return self._ip_range

    @property
    def nodes(self):
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
