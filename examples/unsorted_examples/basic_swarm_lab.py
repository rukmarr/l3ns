from l3ns.swarm import SwarmNode, SwarmSubnet, SwarmHost
from l3ns import defaults
from l3ns.base import Network

defaults.network = Network('15.0.0.0/8')

host1 = SwarmHost('t2')
host2 = SwarmHost('t3')

n1 = SwarmNode('test1', host1, image='alpine', command='tail -f /dev/null')
n2 = SwarmNode('test2', host2, image='alpine', command='tail -f /dev/null')

n1.connect_to(n2, subnet_class=SwarmSubnet)

defaults.network.start(interactive=True)
