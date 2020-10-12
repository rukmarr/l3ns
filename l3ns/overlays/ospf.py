from .base import BaseOverlay

config_template = '''router ospf

{}

redistribute kernel
redistribute static
redistribute connected
'''


class OspfOverlay(BaseOverlay):

    protocol = 'OSPF'

    def configure_node(self, node):
        config = config_template.format('\n'.join([
            f'network {s.get_ip_range()} area 0.0.0.0' for s in self._node_subnets(node)
        ]))

        node.activate_protocol(self.protocol, config)
