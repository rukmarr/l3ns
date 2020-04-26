from .base import BaseOverlay

config_template = '''router rip
{}

redistribute kernel
redistribute static
redistribute connected
'''


class RipOverlay(BaseOverlay):

    protocol = 'RIP'

    def configure_node(self, node):
        config = config_template.format('\n'.join(['network {}'.format(s) for s in self._node_subnets(node)]))

        node.activate_protocol(self.protocol, config)
