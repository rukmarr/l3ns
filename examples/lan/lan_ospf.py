from l3ns.ldc import DockerNode, DockerSubnet
from l3ns.base.network import Network
from l3ns import defaults, net
from l3ns.overlays.ospf import OspfOverlay

defaults.subnet_class = DockerSubnet

local_net = Network('10.10.0.0/16', local=True)

routers = DockerNode.generate_routers('L3NS_router', 2)
router_net = local_net.create_subnet('L3NS_router_net', routers, size=4)
overlay = OspfOverlay(routers)

nodes = DockerNode.generate_nodes('L3NS_node', 2, image='alpine', command='tail -f /dev/null')
for n, r in zip(nodes, routers):
    n.connect_to(r, network=local_net)

server = DockerNode('L3NS_server', image='nginx')
gateway = DockerNode('L3NS_gateway', image='alpine', command='tail -f /dev/null')

gateway.connect_to(server, network=net)
gateway.connect_to(routers[0], network=local_net)

net.start(interactive=True)

