from ipaddress import ip_network, IPv4Network
from math import log2, ceil
from l3ns import defaults

import concurrent.futures


class Network:

    def __init__(self, ip_range: str or IPv4Network, local=False):
        self.ip_range = str(ip_range)
        self._available_subnets = [ip_network(ip_range) if type(ip_range) is str else ip_range, ]
        self._subets = set()
        self._nodes = set()
        self.is_local = local

        self.loaded = False
        self.started = False

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
        max_prefix = 32 - ceil(log2(size + 2))
        #  size = 2^(32-p) - 2

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
        if self.loaded:
            raise Exception('Network already loaded!')

        for subnet in self._subets:
            subnet.start()

        for node in self._nodes:
            node.start()

        self.started = True
        self.loaded = True

    def load(self):
        for node in self._nodes:
            node.load()

        for subnet in self._subets:
            subnet.load()

    def stop(self):
        if not self.loaded:
            self.load()

        for node in self._nodes:
            node.stop()

        for subnet in self._subets:
            subnet.stop()


class NetworkConcurrent(Network):

    def __init__(self, *args, max_workers=None, **kwargs):
        self.max_workers = max_workers
        super().__init__(*args, **kwargs)

    def start(self):
        if self.loaded:
            raise Exception('Network already loaded!')

        for subnet in self._subets:
            subnet.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for node in self._nodes:
                executor.submit(node.start, dc=None)

        self.started = True
        self.loaded = True

    def stop(self):
        '''if not self.loaded:
            self.load()'''

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for node in self._nodes:
                executor.submit(node.stop, dc=None)

        for subnet in self._subets:
            subnet.stop()
