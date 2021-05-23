from l3ns.swarm import SwarmNode, SwarmSubnet, SwarmHost
from l3ns import defaults

host1 = SwarmHost('swarm2', login='ubuntu')
host2 = SwarmHost('swarm3', login='ubuntu')

n1 = SwarmNode('node1', host1, image='appropriate/curl', entrypoint='tail -f /dev/null')
n2 = SwarmNode('node2', host2, image='nginx:alpine')

n1.connect_to(n2, subnet_class=SwarmSubnet)

print(n1.get_ip())
print(n2.get_ip())

defaults.network.start(interactive=True)
