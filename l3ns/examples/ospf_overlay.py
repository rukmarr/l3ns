from l3ns.ldc import DockerNode, DockerSubnet
from l3ns import defaults, net
from l3ns.overlays.ospf import OspfOverlay

defaults.subnet_class = DockerSubnet

routers = DockerNode.generate_routers('router', 2)
router_net = net.create_subnet('router_net', routers, size=4)

overlay = OspfOverlay(routers)

nodes = DockerNode.generate_nodes('node', 2, image='alpine', command='tail -f /dev/null')


for n, r in zip(nodes, routers):
    n.connect_to(r)

net.start(interactive=True)

