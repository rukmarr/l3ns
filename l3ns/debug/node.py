from ..base import BaseNode

class DebugNode(BaseNode):

    def _start(self):
        print(self.name, 'started', *self._interfaces.keys())
