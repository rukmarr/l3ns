from ipaddress import ip_network, IPv4Network
from math import log2
from l3ns import defaults


class Network:

    def __init__(self, ip_range: str or IPv4Network, local=False):
        self.ip_range = str(ip_range)
        self._available_subnets = [ip_network(ip_range) if type(ip_range) is str else ip_range, ]
        self._subets = set()
        self._nodes = set()
        self.is_local = local

    def add_node(self, node):
        self._nodes.add(node)
        node.add_network(self)

    def add_subnet(self, subnet):
        self._subets.add(subnet)

    def create_subnet(self, subnet_name, *args, subnet_type: type = None, **kwargs):
        if subnet_type is None:
            subnet_type = defaults.subnet_class

        subnet_type(subnet_name, *args, netork=self, **kwargs)

    def get_subnet_range(self, size: int):
        max_prefix = 32 - int(log2(size + 2))

        try:
            subnet = [net for net in self._available_subnets if net.prefixlen <= max_prefix][0]
        except IndexError:
            raise Exception('Network address pool is empty')

        if subnet.prefixlen == max_prefix:
            return subnet

        self._available_subnets.remove(subnet)

        try:
            smaller_subnet = next(subnet.subnets(new_prefix=max_prefix))
        except ValueError or StopIteration as e:
            raise Exception('Error while splitting net: {}'.format(e))

        self._available_subnets.extend(subnet.address_exclude(smaller_subnet))
        self._available_subnets.sort(key=lambda n: 32 - n.prefixlen)

        return smaller_subnet

    def start(self):

        for subnet in self._subets:
            subnet.start()

        for node in self._nodes:
            node.start()

