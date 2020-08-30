from l3ns.ldc import DockerNode, DockerSubnet
from l3ns.swarm import SwarmSubnet, SwarmHost, SwarmNode
from l3ns.base.network import Network, NetworkConcurrent
from l3ns.overlays.rip import RipOverlay
from l3ns import defaults

import sys
import random

if sys.argv[2] == 'c':
    defaults.network = NetworkConcurrent('15.0.0.0/16', max_workers=2)
else:
    defaults.network = Network('15.0.0.0/16')

host1 = SwarmHost('w1', login='ojakushkin_w1')
host2 = SwarmHost('w3', login='ojakushkin_w3')

hosts = [None, host1, host2]

N = int(sys.argv[1])
nodes = []
inteerconnect = 2
subnet_max_size = 10


m = N // subnet_max_size + 1  # количество подсетей

N = N // m  # количество контейнеров в подсети

cluster_size = 3  # количество узлов кластера


print('Максимальный размер подсети', subnet_max_size)
print('Роутеров в подсети', inteerconnect)
print(f'Количество подсетей: {m} (+1)')
print('Роутеров вcего', inteerconnect*m)
print('Размер кластера', cluster_size)
print('Количество нод:', (N+inteerconnect)*m)
print(f'Нод на узел кластера {(N+inteerconnect)*m / cluster_size}')


routers = []
router_net = SwarmSubnet('l3ns_router_net', [], size=m*inteerconnect+10)
lans = []


for i in range(m):

    ii = i // cluster_size

    lan_nodes = []
    lans.append(lan_nodes)

    if ii == 0:
        lan_routers = DockerNode.generate_routers(f'l3ns_router{i}_', inteerconnect)
    else:
        lan_routers = SwarmNode.generate_routers(f'l3ns_router{i}_', inteerconnect, hosts[ii])

    routers += lan_routers
    for r in lan_routers:
        router_net.add_node(r)
    lan_nodes.extend(lan_routers)

    if ii == 0:
        lan_nodes.extend([
            DockerNode(f'l3ns_node_{i}_{j + 1}', image='alpine',
                       command=f'ping {random.choice(random.choice(lans)).get_ip()}')
            for j in range(N)])

        lan_net = DockerSubnet(f'net_{i}', lan_nodes)
    else:
        lan_nodes.extend([
            SwarmNode(f'l3ns_node_{i}_{j+1}', hosts[ii], image='alpine',
                       command=f'ping {random.choice(random.choice(lans)).get_ip()}')
            for j in range(N)])

        lan_net = DockerSubnet(f'l3ns_net_{i}', lan_nodes, docker_client=hosts[ii].get_docker_client())


overlay = RipOverlay(routers)


defaults.network.start(interactive=True)
