import docker
import tarfile
import io
import os
import time

from pyroute2.nslink.nspopen import NSPopen

from .. import base
from ..cluster.utils import my_hash


class NamespaceNode(base.BaseNode):

    def __init__(self, name, args, *, ndb, **popen_kwargs):
        self._args = args
        self._ndb = ndb
        self._ns_name = name
        self._veths = {}
        self._popen = None
        self._popen_kwargs = popen_kwargs
        super().__init__(name=name)

    def _connect_subnet(self, subnet, ip):
        ifc_hash = my_hash(subnet.name, self.name)
        ifc = self._ndb.interfaces.create(
            ifname=f'l3eth_{ifc_hash}',
            kind='veth',
            peer=f'l3br_{ifc_hash}',
        ).commit()

        self._ndb.interfaces[ifc['ifname']].set(
            'target', self._ns_name
        ).commit()

        veth_ns = self._ndb.interfaces[{
            'target': self._ns_name,
            'ifname': ifc['ifname']
        }].add_ip(
            f'{ip}/{subnet._ip_range.prefixlen}'
        ).set('state', 'up').commit()

        veth_br = self._ndb.interfaces[ifc['peer']].set(
            'master', subnet.bridge['index']
        ).set('state', 'up').commit()

        self._veths[subnet] = (veth_br, veth_ns)

    def _start(self):
        self._ns = self._ndb.netns.create(self._ns_name).commit()
        self._ndb.sources.add(netns=self._ns_name)

        self._popen = NSPopen(self._ns_name, self._args, **self._popen_kwargs)

    def load(self):
        pass

    def stop(self):
        # TODO: not sure if both are necessary
        self._popen.terminate()
        self._popen.release()

        for veth_br, veth_ns in self._veths.values():
            veth_br.remove().commit()

        self._ns.remove().commit()

    def put_string(self, path, string):
        raise NotImplementedError('Network namespace has access to the local filesystem!')

    def _deploy_routes(self):
        for ip_range, gateway in self._routes.items():
            self._ndb.route.create(
                dst=ip_range,
                gateway=gateway,
                target=self._ns_name
            ).commit()

    @classmethod
    def make_router(cls, *args, **kwargs):

        kwargs = kwargs.copy()

        # TODO: frr should be accessible in the system
        kwargs['image'] = 'frrouting/frr'

        router = cls(*args, **kwargs)

        router.is_router = True

        return router

    def activate_protocol(self, protocol: str, config: str):
        # TODO: how to run multiple FRR in the same system?
        daemon_name = protocol.lower() + 'd'
        cmd = "sed -i 's/{daemon}=no/{daemon}=yes/' /etc/frr/daemons &&".format(daemon=daemon_name)
        self._docker_kwargs['entrypoint'] = cmd + self._docker_kwargs['entrypoint']

        self.put_string('/etc/frr/{}.conf'.format(daemon_name), config)
