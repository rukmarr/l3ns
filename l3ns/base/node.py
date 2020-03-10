import l3ns
from l3ns import defaults
from ipaddress import IPv4Address

class BaseNode:

    def __init__(self, name: str = None):
        self.name = 'dunno' if name is None else name
        self._interfaces = {}
        self.started = False
        self._routes = {}
        self._networks = []

    def connect_to(self,
                   other_node: 'BaseNode',
                   subnet_name: str = None,
                   subnet_class: type = None,
                   **subnet_kwargs):

        if subnet_class is None:
            subnet_class = defaults.subnet_class

        if subnet_name is None:
            subnet_name = self.name + '_' + other_node.name

        return subnet_class(subnet_name, self, other_node, **subnet_kwargs)

    def add_interface(self, ip_address, subnet: 'l3ns.base.BaseSubnet'):
        self._interfaces[ip_address] = subnet

    def start(self):
        raise NotImplementedError()

    def get_gateway(self, net):
        for subnet in self._interfaces.values():
            if subnet.get_network() is not net: continue

            gateway = subnet.get_gateway()
            if gateway:
                return gateway

        return None

    def add_network(self, net):
        self._networks.append(net)
