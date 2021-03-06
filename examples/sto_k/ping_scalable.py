from l3ns import defaults
from l3ns.ldc import DockerSubnet
from l3ns.swarm import SwarmNode, SwarmSubnet
from l3ns.base.network import NetworkConcurrent, Network
from l3ns.overlays.rip import RipOverlay

import sys
import random

from hosts import hosts

wanted_lab_size = int(sys.argv[1])
max_subnet_size = int(sys.argv[2])

defaults.network = NetworkConcurrent('15.0.0.0/8', max_workers=8)

swarm_size = len(hosts)

M = wanted_lab_size // max_subnet_size
N = wanted_lab_size // M
print('Количество подсетей', M)
print('Контейнеров в подсети', N)
print('Контейнеров на хосте', wanted_lab_size / swarm_size)


input('press any key to start')

routers = []
nodes = []
router_net = SwarmSubnet('l3ns_r_net', size=M)

for m in range(M):
    host = hosts[m % swarm_size]
    router = SwarmNode.make_router(f'l3ns_router{m}', host)
    routers.append(router)
    router_net.add_node(router)

    subnet = DockerSubnet(name=f'l3ns_polygonet_{m}', size=N+1, docker_client=host.get_docker_client())
    subnet.add_node(router)
    for i in range(N):
        n = SwarmNode(
            f'l3ns_node_{m}_{i}',
            host,
            image='alpine',
            command='tail -f /dev/null' if not len(nodes) else 'ping {}'.format(random.choice(nodes).get_ip()))
        nodes.append(n)
        subnet.add_node(n)

overlay = RipOverlay(routers)

if __name__ == '__main__':
    defaults.network.start(interactive=True)
    # defaults.network.stop()
