import l3ns
from l3ns import defaults
from ipaddress import IPv4Address

class BaseNode:

    def __init__(self, name, network: 'l3ns.base.Network' = defaults.network, internet_connection=False):
        self.name = name
        self._interfaces = {}
        self._routes = {}
        self._networks = [network]
        self._files = {}

        self.loaded = False
        self.started = False
        self.is_router = False
        self.is_gateway = False
        self.connect_to_internet = internet_connection

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

    def _start(self, *args, **kwargs):
        raise NotImplementedError()

    def start(self, *args, **kwargs):
        self._setup_routes()

        ret = self._start(*args, **kwargs)
        print('node', self.name, 'started')

        self._connect_subnets()
        self._deploy_routes()

        return ret

    def _connect_subnets(self):
        for ip, network in self._interfaces.items():
            self._connect_subnet(network, ip)

    def _connect_subnet(self, subnet, ip):
        raise NotImplementedError()

    def _setup_routes(self):
        max_routes_number = len(self._networks)

        # TODO: LAN routes for routers
        if self.is_router:
            return

        for subnet in self.subnets:
            network = subnet.get_network()

            ip_range = network.ip_range \
                if self.connect_to_internet or network.is_local else 'default'

            if ip_range in self._routes:
                continue

            gateway = subnet.get_gateway(self)
            if gateway:
                self._routes[ip_range] = gateway

            if len(self._routes) == max_routes_number:
                return

    def _deploy_routes(self):
        raise NotImplementedError()

    @property
    def subnets(self):
        return list(self._interfaces.values())

    def add_network(self, net):
        self._networks.append(net)

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

    def __repr__(self):
        return '<{class_name}({name}, {ip})'.format(class_name=self.__class__.__name__, name=self.name, ip=self.get_ip())

