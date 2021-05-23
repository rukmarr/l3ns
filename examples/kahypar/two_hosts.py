from l3ns.kahypar.network import AutoClusterNetwork
from l3ns.kahypar.subnet import AutoSwarmSubnet
from l3ns import defaults
from l3ns.swarm.node import SwarmNode
from l3ns.swarm.utils import SwarmHost
from l3ns.ldc.node import DockerNode


hosts = [
    SwarmHost('swarm2', login='ubuntu'),
    SwarmHost('swarm3', login='ubuntu')
]
defaults.network = AutoClusterNetwork('23.0.0.0/16', hosts, kahypar_preset="/home/ubuntu/cut_kKaHyPar_sea20.ini")

cluster1 = SwarmNode.generate_nodes('c1_', 3, None, image='alpine', command='tail -f /dev/null')
cluster2 = SwarmNode.generate_nodes('c2_', 3, None, image='alpine', command='tail -f /dev/null')

cluster1_net = AutoSwarmSubnet('c1_net', cluster1)
cluster2_net = AutoSwarmSubnet('c2_net', cluster2)

cluster1[0].connect_to(cluster2[0], subnet_class=AutoSwarmSubnet)

# defaults.network.split_network()
for node in defaults.network._nodes:
    print(node.name, node.get_ip())

defaults.network.start(interactive=True)
