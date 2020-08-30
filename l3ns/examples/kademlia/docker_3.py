from l3ns.ldc import DockerNode, DockerSubnet
from l3ns import defaults

subnet = DockerSubnet('l3ns_kademlia')

n1 = DockerNode('kademlia1', image='l3ns/kademlia')
subnet.add_node(n1)
n2 = DockerNode('kademlia2', image='l3ns/kademlia', command=n1.get_ip())
subnet.add_node(n2)

defaults.network.start(interactive=True)
