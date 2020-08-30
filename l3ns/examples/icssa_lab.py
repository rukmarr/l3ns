from l3ns.ldc import DockerNode, DockerSubnet
from l3ns.base.network import Network, NetworkConcurrent
from l3ns.overlays.rip import RipOverlay
from l3ns import defaults

import sys
import random

if sys.argv[2] == 'c':
    defaults.network = NetworkConcurrent('15.0.0.0/16', max_workers=2)
else:
    defaults.network = Network('15.0.0.0/16')


N = int(sys.argv[1])
nodes = []

inteerconnect = 10

m = N // 500 + 1  # количество подсетей


N = N // m  # количество контейнеров в подсети


print(m, N, m*N)
routers = []
router_net = DockerSubnet('router_net', [], size=m*inteerconnect+10)
lans = []


for i in range(m):
    lan_nodes = []
    lans.append(lan_nodes)

    lan_routers = DockerNode.generate_routers(f'router{i}_', inteerconnect)
    routers += lan_routers
    for r in lan_routers:
        router_net.add_node(r)
    lan_nodes.extend(lan_routers)

    lan_nodes.extend([
        DockerNode(f'node_{i}_{j+1}', image='alpine',
                   command=f'ping {random.choice(random.choice(lans)).get_ip()}')
        for j in range(N)])

    lan_net = DockerSubnet(f'net_{i}', lan_nodes)


overlay = RipOverlay(routers)


defaults.network.stop()
