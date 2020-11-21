from .. import defaults
from . import subnet as base_subnet


class BaseNode:
    """Base class for Nodes representing computers in virtual networks"""
    lock_filepath = '/var/run/l3ns.lock'

    def __init__(self, name, internet_connection=False):
        """Create node

        Create basic node with black configuration.

        Args:
             name: unique identifier for new node
             internet_connection: Optional; whether node should be able th connect to internet
        """
        self.name = name
        self._interfaces = {}
        self._routes = {}
        self._networks = []
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
        """Create subnet that connects this node to another

        Create a subnet with that will consist of two nodes. You can specify
        specific subnet class and name. If not, name will be generated automatically
        and subnet class will be retrieved from [defaults](l3ns.defaults).

        Args:
            other_node: Node to connect
            subnet_name: Name to use for net subnet
            subnet_class: Class to use for new subnet
        """

        if subnet_class is None:
            subnet_class = defaults.subnet_class

        if subnet_name is None:
            subnet_name = self.name + '_' + other_node.name

        return subnet_class(subnet_name, self, other_node, **subnet_kwargs)

    def add_interface(self, ip_address, subnet: 'base_subnet.BaseSubnet'):
        """Add network interface to container

        Network interfaces are used to store node's IP address and names of the virtual
        network interfaces that will be created on node start (like br-xxxxxx for docker networks)
        This functions called mostly from Subnet.add_node.
        """
        self._interfaces[ip_address] = subnet

    def _start(self, *args, **kwargs):
        """Start function to be implemented in resource-specific classed, like DockerNode"""

        raise NotImplementedError()

    def start(self, *args, **kwargs):
        """Start function called from Network.start

        Start procedure starts with gathering routing information from
        node's subnets and LANs. Then Node._start is called to create the node itself,
        after that Node._connect_subnets connects node to it's subnets and
        Node._deploy_routes sets up node's routes.
        """
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
        """Function connecting node resources to virtual subnet to
        be implemented in resource-specific classed, like DockerNode"""
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
        """Function deploing routing information in node resources
        to be implemented in resource-specific classed, like DockerNode"""
        raise NotImplementedError()

    @property
    def subnets(self):
        return list(self._interfaces.values())

    @property
    def neighbors(self):
        return sum([subnet.nodes for subnet in self.subnets])

    def add_network(self, net):
        self._networks.append(net)

    def load(self):
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

    @classmethod
    def make_router(cls, *args, **kwargs):
        """Function defining router node to be implemented in resource-specific classed, like DockerNode"""
        raise NotImplementedError()

    @classmethod
    def generate_nodes(cls, name_prefix, amount, *args, **kwargs):
        return [cls(name_prefix + str(i+1), *args, **kwargs) for i in range(amount)]

    @classmethod
    def generate_routers(cls, name_prefix, amount, *args, **kwargs):
        return [cls.make_router(name_prefix + str(i+1), *args, **kwargs) for i in range(amount)]

    def activate_protocol(self, protocol, config):
        """Function activating routing protocol for node
        to be implemented in resource-specific classed, like DockerNode"""
        raise NotImplementedError()

    def __repr__(self):
        return '<{class_name}({name}, {ip})'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            ip=self.get_ip())

    def unlock(self):
        """Unlock node from waiting mode

        Node: WIP

        Starting large networks can take a long time, so if one node workload
        depends on the other node it cant be launched before the other node started.
        If you want all nodes to start simultaneously, a waiting mode before workload
        is required. For DockerNode, for example, we modify entrypoint to make
        original entrypoint and cmd to be launched only if certain file exists and
        than create that file on unlocking.

        """
        # TODO: not the best decision, but we need to avoid starting container before routes are set up
        print(f'unlocking {self.name}')
        self.put_string(self.lock_filepath, '')

    def put_string(self, path, string):
        """Put sting in file on node"""
        raise NotImplementedError()
