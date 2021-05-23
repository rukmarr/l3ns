from ipaddress import ip_network, IPv4Network
from math import log2, ceil
from typing import Union, Optional, TYPE_CHECKING, List
from .. import defaults

import concurrent.futures
import traceback

import time

if TYPE_CHECKING:
    from .node import BaseNode
    from .subnet import BaseSubnet


class Network:
    """Base class for forming local and wide area networks"""

    def __init__(self, ip_range: Union[str, IPv4Network], local=False):
        """Creates network with given ip range.

        Creates local or wide area nerwork with a given ip range that will be
        distributed to subnetworks that will be created in this network.

        Args:
            ip_range: IP address range for the networks
            local: Optional; Set to True to create local network

        """
        self.ip_range = str(ip_range)
        self._available_subnets = [ip_network(ip_range) if type(ip_range) is str else ip_range, ]
        self._subnets: List['BaseSubnet'] = []
        self._nodes: List['BaseNode'] = []
        self.is_local = local
        self.lan_gateway: Optional['BaseNode'] = None

        self.loaded = False
        self.started = False

    def start(self, interactive=False):
        """Launches all the subnetworks and nodes in this network

        This function calls appropriate functions for subnets first
        and for nodes later. Even nodes that are not connected to
        any subnets will be started.

        Interactive mode allows user to start and stop the network
        with a simpler script, locking at the shell prompt
        after the network is started and shutting it down on user
        input. Non-interactive mode doesn't lock code execution, so
        you can create more complex testing scripts.


        Args:
             interactive: Optional; Sets whether interactive mode will be used

        """
        if self.loaded:
            raise Exception('Network already loaded!')

        if not interactive:
            for subnet in self._subnets:
                subnet.start()

            for node in self._nodes:
                if node is not self.lan_gateway:
                    node.start()

            for node in self._nodes:
                if node is not self.lan_gateway:
                    node.unlock()

            self.started = True
            self.loaded = True

        else:
            try:
                self.start(interactive=False)
            except:
                print('\nException while starting:\n_________________\n\n',
                      traceback.format_exc(), '\n_________________\n', sep='')

            i = ''
            while i not in ('y', 'n', 'yes', 'no'):
                i = input('Stop? (y/n): ')

            if i[0] == 'y':
                self.stop()

    def load(self, *args):
        """Loads network resources

        Loads network resources (i.e. containers and
        docker networks in l3ns.ldc) that were previously
        launched in a different script back in the memory.


        Note that this will not load network stricture, it
        needs to be already defined. This allows you to work
        with network resources from several scripts.

        """
        for node in self._nodes:
            node.load(*args)

        for subnet in self._subnets:
            subnet.load(*args)

    def stop(self, *args):
        """Stops the network"""
        if not self.loaded:
            self.load(*args)

        for node in self._nodes:
            if node is not self.lan_gateway:
                node.stop(*args)

        for subnet in self._subnets:
            subnet.stop(*args)

        self.started = False

    def __contains__(self, item):
        return item in self._nodes or item in self._subnets

    def add_node(self, node: 'BaseNode'):
        """Add node to the network"""
        if not node.in_net(node):
            self._nodes.append(node)
        node.add_network(self)

    def add_subnet(self, subnet):
        """Add subnet to the network"""
        if subnet not in self._subnets:
            self._subnets.append(subnet)

    def create_subnet(self, subnet_name, *args, subnet_type: type = None, **kwargs):
        """Create subnet in this network"""
        if subnet_type is None:
            subnet_type = defaults.subnet_class

        return subnet_type(subnet_name, *args, network=self, **kwargs)

    def get_subnet_range(self, size: int):
        """Retrieve an IP range of given size for subnet and remove it from available addresses"""
        max_prefix = 32 - ceil(log2(size + 2))
        #  size = 2^(32-p) - 2

        try:
            subnet = [net for net in self._available_subnets if net.prefixlen <= max_prefix][0]
        except IndexError:
            raise Exception('Network address pool is empty')

        self._available_subnets.remove(subnet)

        if subnet.prefixlen == max_prefix:
            return subnet

        try:
            smaller_subnet = next(subnet.subnets(new_prefix=max_prefix))
        except ValueError or StopIteration as e:
            raise Exception('Error while splitting net: {}'.format(e))

        self._available_subnets.extend(subnet.address_exclude(smaller_subnet))
        self._available_subnets.sort(key=lambda n: 32 - n.prefixlen)

        return smaller_subnet

    def connect_lan(self, lan_network: 'Network', gateway: 'BaseNode'):
        return gateway.crete_gateway(lan_network, self)

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class NetworkConcurrent(Network):
    """WIP-interface to launch large networks (500+ nodes) concurrently."""

    def __init__(self, *args, max_workers=None, **kwargs):
        self.max_workers = max_workers
        super().__init__(*args, **kwargs)

    def start(self, interactive=False):
        """Starts the network concurrently using ThreadPoolExecutor"""
        # TODO: debug & interactive realisation

        if self.loaded:
            raise Exception('Network already loaded!')

        if not interactive:
            for subnet in self._subnets:
                subnet.start()

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for node in self._nodes:
                    executor.submit(node.start, dc=None)

            print('start time:', time.strftime('[%H:%M:%S]', time.gmtime()))

            # TODO: executor here too
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for node in self._nodes:
                    executor.submit(node.unlock)

            for node in self._nodes:
                node.unlock()

            self.started = True
            self.loaded = True

        else:
            try:
                self.start(interactive=False)
            except:
                print('\nException while starting:\n_________________\n\n',
                      traceback.format_exc(), '\n_________________\n', sep='')

            i = ''
            while i not in ('y', 'n', 'yes', 'no'):
                i = input('Stop? (y/n): ')

            if i[0] == 'y':
                self.stop()

    def stop(self):
        """Stops the network concurrently using ThreadPoolExecutor"""
        if not self.loaded:
            self.load()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for node in self._nodes:
                executor.submit(node.stop, dc=None)

        for subnet in self._subnets:
            subnet.stop()

        self.started = False
