from l3ns.swarm import SwarmNode, SwarmSubnet, SwarmHost
from l3ns.ldc import DockerSubnet
from l3ns import defaults
from l3ns.base import Network
from l3ns.overlays.rip import RipOverlay

defaults.network = Network('15.0.0.0/8')

host1 = SwarmHost('swarm2', login='ubuntu')
host2 = SwarmHost('swarm3', login='ubuntu')

router1 = SwarmNode.make_router('router1', host1)
router2 = SwarmNode.make_router('router2', host2)
router_net = SwarmSubnet('router_net', router1, router2, size=4)
overlay = RipOverlay(router1, router2)

nodes = [
    SwarmNode('node1', host1, image='appropriate/curl', entrypoint='tail -f /dev/null'),
    SwarmNode('node2', host2, image='nginx:alpine')
]


for n, r in zip(nodes, (router1, router2)):
    n.connect_to(r, subnet_class=SwarmSubnet)


defaults.network.start(interactive=True)
