from .. import utils


class BaseOverlay:
    def __init__(self, *args):

        self._nodes = utils.args.list_from_args(args)

        for node in self._nodes:
            self.configure_node(node)

    def __contains__(self, item):
        return item in self._nodes

    def __iter__(self):
        return iter(self._nodes)

    def configure_node(self, node):
        raise NotImplementedError()

    def _node_subnets(self, node):
        """get node subnets that have other nodes from overlay"""
        return [s for s in node.subnets if any([n in s for n in self._nodes if n is not node])]

    def _neighbors_ips(self, node):

        ips = []

        for subnet in node.subnets:
            for ip, n in subnet.get_nodes_dict().items():
                if n in self and n is not node:
                    ips.append(ip)

        return ips
