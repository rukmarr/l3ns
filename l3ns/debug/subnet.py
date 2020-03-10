from ..base import BaseSubnet


class DebugSubnet(BaseSubnet):

    def start(self):
        print(self.name, 'started', self._ip_range)
