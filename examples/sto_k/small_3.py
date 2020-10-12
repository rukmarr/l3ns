from l3ns import defaults
from l3ns.swarm import SwarmNode, SwarmSubnet
from l3ns.base.network import NetworkConcurrent

from hosts import hosts


defaults.network = NetworkConcurrent('15.0.0.0/8', max_workers=8)


net = SwarmSubnet('l3ns_100k_net', size=4)

n1 = SwarmNode(
    f'l3ns_node_1',
    hosts[0],
    image='alpine',
    command='tail -f /dev/null'
)
net.add_node(n1)

n2 = SwarmNode(
    f'l3ns_node_2',
    hosts[1],
    image='alpine',
    command='ping {}'.format(n1.get_ip())
)
net.add_node(n2)

n3 = SwarmNode(
    f'l3ns_node_3',
    hosts[2],
    image='alpine',
    command='ping {}'.format(n1.get_ip())
)
net.add_node(n3)


if __name__ == '__main__':
    defaults.network.start(interactive=True)
    # defaults.network.stop()


