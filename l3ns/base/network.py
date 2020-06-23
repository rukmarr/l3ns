from ipaddress import ip_network, IPv4Network
from math import log2, ceil
from .. import defaults

import concurrent.futures
import traceback

import time


class Network:

    def __init__(self, ip_range: str or IPv4Network, local=False):
        self.ip_range = str(ip_range)
        self._available_subnets = [ip_network(ip_range) if type(ip_range) is str else ip_range, ]
        self._subnets = set()
        self._nodes = []
        self.is_local = local

        self.loaded = False
        self.started = False

    def add_node(self, node):
        self._nodes.append(node)
        node.add_network(self)

    def add_subnet(self, subnet):
        self._subnets.add(subnet)

    def create_subnet(self, subnet_name, *args, subnet_type: type = None, **kwargs):
        if subnet_type is None:
            subnet_type = defaults.subnet_class

        return subnet_type(subnet_name, *args, network=self, **kwargs)

    def get_subnet_range(self, size: int):
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

    def start(self, interactive=False):
        if self.loaded:
            raise Exception('Network already loaded!')

        if not interactive:
            for subnet in self._subnets:
                subnet.start()

            for node in self._nodes:
                node.start()

            for node in self._nodes:
                # node.unlock()
                pass

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
        for node in self._nodes:
            node.load(*args)

        for subnet in self._subnets:
            subnet.load(*args)

    def stop(self, *args):
        if not self.loaded:
            self.load(*args)

        for node in self._nodes:
            node.stop(*args)

        for subnet in self._subnets:
            subnet.stop(*args)

    def __contains__(self, item):
        return item in self._nodes or item in self._subnets


class NetworkConcurrent(Network):

    def __init__(self, *args, max_workers=None, **kwargs):
        self.max_workers = max_workers
        super().__init__(*args, **kwargs)

    def start(self, interactive=False):
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
            '''
            for node in self._nodes:
                node.unlock()
            '''


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
        if not self.loaded:
            self.load()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for node in self._nodes:
                executor.submit(node.stop, dc=None)

        for subnet in self._subnets:
            subnet.stop()
