from l3ns.ldc import DockerNode, DockerSubnet
from l3ns.base.network import Network, NetworkConcurrent
from l3ns import defaults

import sys

if sys.argv[2] == 'c':
    defaults.network = NetworkConcurrent('15.0.0.0/16', max_workers=2)
else:
    defaults.network = Network('15.0.0.0/16')

N = int(sys.argv[1])
nodes = []
N1 = int(N/2)

s1 = DockerSubnet(name='polygon1', size=N1+10)
s2 = DockerSubnet(name='polygon2', size=N1+10)

for i in range(N1):
    n = DockerNode(image='alpine', command='tail -f /dev/null' if not len(nodes) else 'ping {}'.format(nodes[-1].get_ip()), name='l3ns_node_' + str(i+1))
    nodes.append(n)
    s1.add_node(n)

for i in range(N-N1):
    n = DockerNode(image='alpine', command='tail -f /dev/null' if len(nodes) == N1 else 'ping {}'.format(nodes[N1].get_ip()), name='l3ns_node_' + str(N1+i+1))
    nodes.append(n)
    s2.add_node(n)

defaults.network.start(interactive=True)
