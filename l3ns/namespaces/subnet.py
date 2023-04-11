from pyroute2.ndb.main import NDB

from .. import base


class NamespaceSubnet(base.BaseSubnet):
    def __init__(self, *args, ndb, size=1023, **kwargs,):
        self._ndb = ndb

        self.bridge = None
        super().__init__(*args, size=size + 1, **kwargs)
        # minus one address for docker gateway
        self._docker_gateway = self._get_host_ip()

    def start(self):
        self.bridge = self._ndb.interfaces.create(
            ifname=f'l3br_{self.name}',
            kind='bridge'
        ).set('state', 'up').commit()

    def load(self):
        pass

    def stop(self):
        self.bridge.remove().commit()
