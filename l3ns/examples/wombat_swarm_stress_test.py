from l3ns.swarm import SwarmNode, SwarmSubnet, SwarmHost
from l3ns.ldc import DockerSubnet
from l3ns import defaults
from l3ns.base import Network
from l3ns.overlays.rip import RipOverlay

import sys

N = int(sys.argv[1])
N1 = int(N/2)

defaults.network = Network('15.0.0.0/8')

host1 = SwarmHost('w1', login='ojakushkin_w1')
host2 = SwarmHost('w3', login='ojakushkin_w3')

r1 = SwarmNode.make_router('l3ns_router1', host1)
r2 = SwarmNode.make_router('l3ns_router2', host2)

r1.connect_to(r2, subnet_class=SwarmSubnet)

overlay = RipOverlay(r1, r2)

nodes = []

s1 = DockerSubnet(name='polygon1', size=N1+10, docker_client=host1.get_docker_client())
s1.add_node(r1)
s2 = DockerSubnet(name='polygon2', size=N1+10, docker_client=host2.get_docker_client())
s2.add_node(r2)

for i in range(N1):
    n = SwarmNode(
        'l3ns_node_' + str(i + 1),
        host1,
        image='alpine',
        command='tail -f /dev/null' if not len(nodes) else 'ping {}'.format(nodes[0].get_ip()))
    nodes.append(n)
    s1.add_node(n)

for i in range(N-N1):
    n = SwarmNode(
        'l3ns_node_' + str(N1 + i + 1),
        host2,
        image='alpine',
        command='ping {}'.format(nodes[0].get_ip()))
    nodes.append(n)
    s2.add_node(n)

print(r1)
print(r2)

for n in nodes:
    print(n)

defaults.network.start(interactive=True)

