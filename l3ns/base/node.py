from typing import List, TYPE_CHECKING

from .. import defaults
from . import subnet as base_subnet

if TYPE_CHECKING:
    from .network import Network
    from .subnet import BaseSubnet


class BaseNode:
    """Base class for Nodes representing computers in virtual networks"""
    lock_filepath = '/var/run/l3ns.lock'

    def __init__(self, name):
        """Create node

        Create basic node with black configuration.

        Args:
             name: unique identifier for new node
        """
        self.name = name
        self._interfaces = {}
        self._routes = {}
        self._networks: List['Network'] = []
        self._files = {}

        self.loaded = False
        self.started = False
        self.stopped = False
        self.is_router = False
        self._gateways = []
        self.connect_to_internet = False

    @property
    def is_gateway(self):
        return bool(self._gateways)

    def connect_to(self,
                   other_node: 'BaseNode',
                   subnet_name: str = None,
                   subnet_class: type = None,
                   **subnet_kwargs):
        """Create subnet that connects this node to another

        Create a subnet with that will consist of two nodes. You can specify
        specific subnet class and name. If not, name will be generated automatically
        and subnet class will be retrieved from [defaults](l3ns/defaults).

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

    def crete_gateway(self, from_network: 'Network', to_network: 'Network'):
        """Create a gateway from from_network to to_network on this node

        From_network is always a local network and
        to_network can be global or local.
        Gateway node needs to be connected to at least one subnet
        in each network before calling this function.
        """
        if not from_network.is_local:
            raise Exception('from_network must be local!')

        if from_network not in self._networks or to_network not in self._networks:
            raise Exception('Gateway node needs to be connected to at least one subnet in each network')

        from_network.lan_gateway = self
        self._gateways.append((from_network, to_network))

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

        if self.started:
            return

        ret = self._start(*args, **kwargs)
        self.started = True
        print('node', self.name, 'started')

        self._setup_routes()
        if self.is_gateway:
            for network in self._networks:
                if self is network.lan_gateway and not network.started:
                    network.start()

        self._connect_subnets()
        self._deploy_routes()
        if self.is_gateway:
            self._setup_lan_gateway()

        return ret

    def _stop(self, *args, **kwargs):
        """Stop function to be implemented in resource-specific classed, like DockerNode"""

        raise NotImplementedError()

    def stop(self, *args, **kwargs):
        """
        Stop function called from Network.start
        """
        if self.stopped:
            return

        self._stop(*args, **kwargs)
        self.stopped = True

        if self.is_gateway:
            for network in self._networks:
                if self is network.lan_gateway:
                    network.stop()

    def _connect_subnets(self):
        for ip, network in self._interfaces.items():
            self._connect_subnet(network, ip)

    def _connect_subnet(self, subnet, ip):
        """Function connecting node resources to virtual subnet to
        be implemented in resource-specific classed, like DockerNode"""
        raise NotImplementedError()

    def _setup_routes(self):
        for network in sorted(self._networks, key=lambda n: n.is_local, reverse=True):

            # for routes we can only find neighbor gateway
            # intentionally not doing this for nodes
            if self.is_router and network.is_local:
                for subnet in self.subnets:
                    if network.lan_gateway in subnet:
                        for ip_range in network.lan_gateway.get_gateway_ranges(network):
                            if ip_range not in self._routes:
                                self._routes[ip_range] = network.lan_gateway.get_ip(subnet)

            # for gateways and nodes find neighbor router (or gateway for plain node)
            elif not self.is_router:

                ip_ranges = ['default', ]
                if network.is_local:
                    if self == network.lan_gateway:
                        ip_ranges = [network.ip_range, ]

                    elif self.connect_to_internet or 'default' in self._routes:
                        ip_ranges = network.lan_gateway.get_gateway_ranges(network)

                elif self.connect_to_internet:
                    ip_ranges = [network.ip_range, ]

                for subnet in self.subnets:
                    if subnet in network:
                        gateway = subnet.get_gateway(self)
                        if gateway:
                            for ip_range in ip_ranges:
                                if ip_range not in self._routes:
                                    self._routes[ip_range] = gateway

    def get_gateway_ranges(self, network):
        """Returns ip ranges for all the networks accessible via this gateway"""
        # TODO: not sure if it works
        if self.is_gateway:
            return sum(
                [
                    to_network.ip_range,
                    *(to_network.lan_gateway.get_gateway_ranges(network) if network.lan_gateway else [])
                ] for from_network, to_network in self._gateways
                if from_network is network and self is not network.lan_gateway
            )
        else:
            return []

    def _deploy_routes(self):
        """Function deploing routing information in node resources
        to be implemented in resource-specific classed, like DockerNode"""
        raise NotImplementedError()

    def _setup_lan_gateway(self):
        """Function setting up LAN gateway on this node
        to be implemented in resource-specific classed, like DockerNode"""
        raise NotImplementedError()

    @property
    def subnets(self) -> List['BaseSubnet']:
        return list(self._interfaces.values())

    @property
    def neighbors(self):
        return sum([subnet.nodes for subnet in self.subnets])

    def add_network(self, net: 'Network'):
        if net in self._networks:
            return
        if not net.is_local and any(filter(lambda n: not n.is_local, self._networks)):
            raise Exception('Node cannot reside in two global networks at the same time!')
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
        # temporary bypass

        # print(f'unlocking {self.name}')
        self.put_string(self.lock_filepath, '')

    def put_string(self, path, string):
        """Put sting in file on node"""
        raise NotImplementedError()

    def in_net(self, net):
        return net in self._networks
