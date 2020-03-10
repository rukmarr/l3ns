import l3ns
from l3ns import defaults

class BaseSubnet:

    def __init__(self, name: str, *args, size: int = 1024, network: 'l3ns.base.Network' = None):
        self.name = name
        self._network = network if network is not None else defaults.network
        self._network.add_subnet(self)
        self._max_size = size
        self._ip_range = self._network.get_subnet_range(self._max_size)
        self._hosts = self._ip_range.hosts()

        self._nodes = {}
        self.started = False

        try:
            nodes_list = list(args[0])
        except TypeError:
            nodes_list = list(args)

        for node in nodes_list:
            self.add_node(node)

    def add_node(self, node: 'l3ns.base.BaseNode'):

        try:
            ip_address = str(next(self._hosts))
        except StopIteration:
            raise Exception("Too many nodes in network")

        self._nodes[ip_address] = node
        self._network.add_node(node)
        node.add_interface(ip_address, self)

    def start(self):
        raise NotImplementedError()

    def get_network(self):
        return self._network

    def get_gateway(self):
        # TODO after routers
        return None
