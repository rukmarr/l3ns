from l3ns import defaults
from l3ns.cluster import RemoteNode, WgSubnet, ClusterHost

host1 = ClusterHost('t2')
host2 = ClusterHost('t3')

n1 = RemoteNode('test1', host1, image='alpine', command='tail -f /dev/null')
n2 = RemoteNode('test2', host1, image='alpine', command='tail -f /dev/null')

r = RemoteNode('test3', host2, image='alpine', command='tail -f /dev/null')

r.connect_to(n1, subnet_class=WgSubnet)
r.connect_to(n2, subnet_class=WgSubnet)

defaults.network.start(interactive=True)

