


class RipOverlay:

    def __init__(self, nodes):

        self.nodes = []

        for node in nodes:
            self.add_node(node)


    def add_node(self, node):
        self.nodes.append(node)
        node.turn_into_router()

        node.add_instructions(['rip -d'])
