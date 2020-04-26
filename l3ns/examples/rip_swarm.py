from l3ns.swarm import SwarmNode, SwarmSubnet, SwarmHost
from l3ns.ldc import DockerSubnet
from l3ns import defaults
from l3ns.base import Network
from l3ns.overlays.rip import RipOverlay

defaults.network = Network('15.0.0.0/8')

host1 = SwarmHost('t2')
host2 = SwarmHost('t3')

routers = SwarmNode.generate_routers('router', 2, host1)
router_net = DockerSubnet('router_net', routers, size=4, docker_client=host1.get_docker_client())
overlay = RipOverlay(routers)

nodes = [
    SwarmNode('node1', host2, image='appropriate/curl', entrypoint='tail -f /dev/null'),
    SwarmNode('node2', host2, image='nginx:alpine')
]


for n, r in zip(nodes, routers):
    n.connect_to(r, subnet_class=SwarmSubnet)


defaults.network.start(interactive=True)
