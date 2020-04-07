import l3ns
from l3ns import defaults
from ipaddress import IPv4Address

class BaseNode:

    def __init__(self, name: str = None):
        self.name = 'dunno' if name is None else name
        self._interfaces = {}
        self._routes = {}
        self._networks = []
        self._files = {}

        self.loaded = False
        self.started = False
        self.is_router = False
        self.is_gateway = False

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

    def turn_into_router(self):
        if self.is_router:
            return

        self.is_router = False
        self.add_instruction()

    def load(self):
        raise NotImplementedError()

    def add_instruction(self, cmd_list):
        raise NotImplementedError()

    # TODO: proper realisation with Subnet optional argument
    def get_ip(self, net=None):
        if net is None:
            return next(iter(self._interfaces.keys()), None)

        else:
            for ip, network in self._interfaces.items():
                if network == net:
                    return ip

            return None

